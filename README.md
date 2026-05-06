# Travel Agent

A travel assistant project built with:
- `FastAPI` backend in `backend/main.py`
- `Streamlit` frontend in `frontend/app.py`
- Custom travel tools in `mcp_servers/travel_agent_server.py`
- Language agent orchestration via `langchain-groq`, `langgraph`, and `FastMCP`

> Note: `backend/main1.py` is a draft and should not be used as the main backend entrypoint.

## Project overview

This project provides a chat-based travel assistant that can:
- Search for destination attractions and points of interest
- Estimate travel budgets
- Fetch weather information
- Convert currencies
- Evaluate math expressions
- Search for flights and hotels
- Perform general search queries

The backend exposes a `/chat` endpoint that accepts user messages and returns agent responses. The Streamlit frontend sends chat requests to the backend and displays responses in a conversational UI.

## Requirements

Install dependencies from `requirements.txt`.

```bash
pip install -r requirements.txt
```

## Environment variables

Create a `.env` file in the project root with the following values:

```env
GROQ_API_KEY=your_groq_api_key_here
Serp_API=your_serpapi_api_key_here
```

The backend uses `GROQ_API_KEY` for the Groq language model and `Serp_API` for SerpApi search queries.

## Run the project

1. Start the backend API:

```bash
cd travel_agent/ #dir
python backend/main.py
```

The backend runs on `http://127.0.0.1:8000` by default.

2. Start the Streamlit frontend:

```bash
cd travel_agent/frontend
streamlit run app.py
```

Open the Streamlit app in the browser at the URL shown by Streamlit (usually `http://localhost:8501`).

## Notes

- The frontend expects the backend at `http://localhost:8000/chat`.
- If the backend is unavailable, the Streamlit UI will return an "Unable to reach the backend" error.
- `backend/main1.py` is included as a draft version and should not be used for normal operation.


## Future improvements

- Add authentication or session persistence
- Add richer error handling for tool responses
- Improve the frontend session management and input validation
- Add unit tests for backend and MCP tools
