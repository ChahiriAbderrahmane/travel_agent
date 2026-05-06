from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from langchain.tools import tool

from mcp_servers.travel_agent_server import search_destination, estimate_budget, get_weather, currency_converter, calculator_tool

load_dotenv()

app = FastAPI(title="Travel Agent API", description="Backend for the Travel Agent application")

class ChatRequest(BaseModel):
    user_message: str
    session_id: str

class ChatResponse(BaseModel):
    bot_message: str

lc_search_destination = tool(search_destination)
lc_estimate_budget = tool(estimate_budget)
lc_get_weather = tool(get_weather)
lc_currency_converter = tool(currency_converter)
lc_calculator_tool = tool(calculator_tool)

tools = [
    lc_search_destination, 
    lc_estimate_budget, 
    lc_get_weather, 
    lc_currency_converter, 
    lc_calculator_tool
]
 
def get_travel_agent():
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

When a user asks about a destination, use the tools to fetch relevant information. Always provide clear and concise responses, and ensure that you utilize the tools effectively to enhance your answers."""

    agent = create_react_agent(model=llm, tools=tools, prompt=system_prompt)

    return agent

agent = None

@app.on_event("startup")
def startup_event():
    global agent
    agent = get_travel_agent()

chat_histories = {}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    session_id = request.session_id

    if session_id not in chat_histories:
        chat_histories[session_id] = []

    chat_histories[session_id].append(
        HumanMessage(content=request.user_message)
    )

    try:
        result = agent.invoke({
            "messages": chat_histories[session_id]
        })

        response = result["messages"][-1].content
        chat_histories[session_id].append(AIMessage(content=response))  # ← bien indenté dans le try
        return ChatResponse(bot_message=response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)