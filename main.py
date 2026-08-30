from fastapi import FastAPI
from pydantic import BaseModel
from agents.sql_analyst import sql_analyst
import os 
import sys 
from dotenv import load_dotenv
load_dotenv()


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.schema import QueryRequest

app = FastAPI(title="SQL Analyst Agent")

#class QueryRequest(BaseModel):
#   question: str

@app.post("/query")
def query(request: QueryRequest):
    input_schema = {
        "messages": [],
        "user_question": request.question,
        "curated_ques": "",
        "prompt_query_context": "",
        "generated_sql_query": "",
        "is_safe": "No",
        "comments": "",
        "sql_query_execution_result": "",
        "final_answer": ""
    }
    response = sql_analyst.invoke(input_schema)
    return {
        "question": request.question,
        "generated_sql_query": response["generated_sql_query"],
        "sql_query_execution_result": response["sql_query_execution_result"],
        "final_answer": response["final_answer"],
    }
