SQL Analyst Agent

An AI agent that answers natural-language questions about a relational database by generating, safety-checking, and executing SQL — then explaining the result in plain English. Built with LangGraph, FastAPI, and Streamlit.

The demo dataset models a generic ride-hailing platform (users, drivers, vehicles, rides, payments, ratings) — synthetic data, not affiliated with or sourced from any real company.


What it does

Ask a question like "What are the top 5 drivers by average rating?" and the agent will:

Curate/clean the question
Introspect the live database schema (tables, columns, sample rows) to ground the query
Generate a Postgres SQL query with an LLM
Run the query through a safety-judge node that blocks anything except read-only SELECT queries (no DROP, DELETE, UPDATE, etc.)
Execute the query if it passes, or cancel with an explanation if it doesn't
Summarize the result back in plain English
Architecture
User question
     │
     ▼
curate_ques ──▶ prompt_query_context ──▶ generate_sql ──▶ is_safe_sql
                                                               │
                                          ┌────────────────────┴────────────────────┐
                                          ▼                                         ▼
                                    execute_sql                               canceled_sql
                                          │                                         │
                                          ▼                                         ▼
                                represent_final_answer ─────────────────────────▶  END

Built as a LangGraph state graph with conditional routing based on the safety judge's verdict.

Tech stack
LangGraph — agent orchestration / state graph
FastAPI — HTTP API layer (POST /query) around the agent
Streamlit — chat-style frontend
PostgreSQL — the queried database
Google Gemini (gemini-2.5-flash, via langchain-google-genai) — the LLM
Project structure
.
├── agents/
│   └── sql_analyst.py       # the LangGraph agent
├── models/
│   └── schema.py            # Pydantic state schemas (AgentSchema, JudgeSchema)
├── utils/
│   ├── database.py          # Postgres connection, schema introspection, query execution
│   └── llm_pick.py          # LLM selection helper
├── data/                    # seed CSVs
├── feed_db.py                # one-time script: creates tables + loads CSVs into Postgres
├── main.py                  # FastAPI app (POST /query)
├── app.py                   # Streamlit frontend
├── requirements.txt
└── .env                     # not committed — see below
Setup
Clone the repo and create a virtual environment:
   python -m venv .venv
   .venv\Scripts\activate      # Windows
   pip install -r requirements.txt
Create a .env file in the project root:
   host=localhost
   port=5432
   user=your_postgres_user
   password=your_postgres_password
   database=your_database_name
   GOOGLE_API_KEY=your_gemini_api_key
Make sure PostgreSQL is running, then seed the database (place your CSVs in data/ first):
   python feed_db.py
Start the API:
   uvicorn main:app --reload
In a separate terminal, start the frontend:
   streamlit run app.py
Open the Streamlit URL shown in the terminal and start asking questions.
Example questions
"What are the top 5 drivers by average rating?"
"What is the total revenue collected by each payment method?"
"Which vehicle makes are most common among drivers rated above 4.5?"
"How many rides were cancelled, and what are the most common reasons?"

Try a destructive-sounding question too (e.g. "delete all rides with a rating below 3") to see the safety-judge node block it instead of executing.

Notes
The database schema is introspected dynamically on every query, so adding new tables/columns to the database doesn't require any code changes.
All destructive SQL is blocked by design — the agent is read-only by policy, enforced by the safety-judge node before any query reaches the database.