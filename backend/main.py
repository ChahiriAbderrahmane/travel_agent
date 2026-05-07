from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import os

import sys
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

import os
from pathlib import Path

# Chemin absolu vers le serveur, peu importe d'où tu lances le script
BASE_DIR = Path(__file__).parent.parent  # remonte de backend/ vers travel_agent/
SERVER_PATH = str(BASE_DIR / "mcp_servers" / "travel_agent_server.py")

app = FastAPI(title="Travel Agent API")

class ChatRequest(BaseModel):
    user_message: str
    session_id: str

class ChatResponse(BaseModel):
    bot_message: str

agent = None
chat_histories = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent

    # Le client lance le serveur MCP comme sous-processus
    # et communique avec lui via le protocole stdio
    mcp_client = MultiServerMCPClient(
        {
            "travel": {
                "command": "python",
                "args": [SERVER_PATH],
                "transport": "stdio",
            }
        }
    )
    tools = await mcp_client.get_tools()  # Récupère les outils via MCP

    llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            api_key=os.getenv("GROQ_API_KEY")
        )

    system_prompt = """You are a helpful travel assistant that provides information about tourist attractions, landmarks, activities, and budget estimates for various destinations around the world. You can use the following tools to assist you in providing accurate and up-to-date information:
1. search_destination: Retrieves tourist attractions, landmarks, and activities for a given destination.
2. estimate_budget: Estimates travel budget in USD based on destination and duration of stay.
3. get_weather: Provides typical or forecasted weather conditions.
4. currency_converter: Converts currency.
5. calculator_tool: Evaluates math expressions.
6. search_flights: Searches for flights based on user criteria.
7. search_hotels: Searches for hotels based on user criteria.
8. search_anything: A general search tool for any other queries.

When a user asks about a destination, use the tools to fetch relevant information. Always provide clear and concise responses, and ensure that you utilize the tools effectively to enhance your answers. If the user asks for something that is not directly related to travel, use the search_anything tool to find the information."""


    agent = create_react_agent(model=llm, tools=tools, prompt=system_prompt)
    yield  # L'app tourne ici

app = FastAPI(title="Travel Agent API", lifespan=lifespan)

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    session_id = request.session_id
    if session_id not in chat_histories:
        chat_histories[session_id] = []

    chat_histories[session_id].append(HumanMessage(content=request.user_message))

    try:
        result = await agent.ainvoke({"messages": chat_histories[session_id]})  # ← await + ainvoke
        response = result["messages"][-1].content
        chat_histories[session_id].append(AIMessage(content=response))
        return ChatResponse(bot_message=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)