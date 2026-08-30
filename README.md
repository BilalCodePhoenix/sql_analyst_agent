# SQL Analyst Agent

An AI agent that answers natural-language questions about a relational database by generating, safety-checking, and executing SQL — then explaining the result in plain English. Built with **LangGraph**, **FastAPI**, and **Streamlit**.

The demo dataset models a generic ride-hailing platform (users, drivers, vehicles, rides, payments, ratings) — synthetic data, not affiliated with or sourced from any real company.

---

## 🚀 What it does

Ask a question like *"What are the top 5 drivers by average rating?"* and the agent will:

1. **Curate/clean** the question.
2. **Introspect** the live database schema (tables, columns, sample rows) to ground the query.
3. **Generate** a Postgres SQL query with an LLM.
4. Run the query through a **safety-judge node** that blocks anything except read-only `SELECT` queries (no `DROP`, `DELETE`, `UPDATE`, etc.).
5. **Execute** the query if it passes, or cancel with an explanation if it doesn't.
6. **Summarize** the result back in plain English.

---

## 🏗️ Architecture

Built as a LangGraph state graph with conditional routing based on the safety judge's verdict.

```text
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
```

---

## 🛠️ Tech Stack

* **LangGraph** — Agent orchestration / state graph
* **FastAPI** — HTTP API layer (`POST /query`) around the agent
* **Streamlit** — Chat-style frontend
* **PostgreSQL** — The queried database
* **Google Gemini** (`gemini-2.5-flash`, via `langchain-google-genai`) — The LLM

---

## 📂 Project Structure

```text
.
├── agents/
│   └── sql_analyst.py       # The LangGraph agent
├── models/
│   └── schema.py            # Pydantic state schemas (AgentSchema, JudgeSchema)
├── utils/
│   ├── database.py          # Postgres connection, schema introspection, query execution
│   └── llm_pick.py          # LLM selection helper
├── data/                    # Seed CSVs
├── feed_db.py               # One-time script: creates tables + loads CSVs into Postgres
├── main.py                  # FastAPI app (POST /query)
├── app.py                   # Streamlit frontend
├── requirements.txt
└── .env                     # Not committed (ignored)
```

---

## ⚙️ Setup & Installation

### 1. Clone the repo and create a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # macOS/Linux
pip install -r requirements.txt
```

### 2. Create a `.env` file in the project root:
```env
host=localhost
port=5432
user=your_postgres_user
password=your_postgres_password
database=your_database_name
GOOGLE_API_KEY=your_gemini_api_key
```

### 3. Seed the database:
Make sure PostgreSQL is running, place your CSVs in `data/` first, then run:
```bash
python feed_db.py
```

### 4. Start the API:
```bash
uvicorn main:app --reload
```

### 5. Start the frontend:
In a separate terminal, run:
```bash
streamlit run app.py
```
Open the Streamlit URL shown in your terminal and start asking questions!

---

## 💡 Example Questions

* *"What are the top 5 drivers by average rating?"*
* *"What is the total revenue collected by each payment method?"*
* *"Which vehicle makes are most common among drivers rated above 4.5?"*
* *"How many rides were cancelled, and what are the most common reasons?"*

> 🛑 **Try a destructive-sounding question too** (e.g., *"delete all rides with a rating below 3"*) to see the safety-judge node block it instead of executing it.

---

## 📝 Notes

* **Dynamic Introspection:** The database schema is introspected dynamically on every query, so adding new tables/columns to the database doesn't require any code changes.
* **Read-Only Enforcement:** All destructive SQL is blocked by design. The agent is read-only by policy, enforced strictly by the safety-judge node before any query ever reaches the database.
