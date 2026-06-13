import os
import sqlite3
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
# 1. Correct import for Gemini
from langchain_google_genai import ChatGoogleGenerativeAI 

# Load environment variables from your local .env file
load_dotenv()

def get_db_schema():
    """Extracts the local SQLite schema structure."""
    db = SQLDatabase.from_uri("sqlite:///saas_dashboard.db")
    return db.get_table_info()

def execute_sql_query(query: str):
    """Executes the SQL query safely against the database."""
    conn = sqlite3.connect("saas_dashboard.db")
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        conn.close()
        return {"columns": column_names, "data": results}
    except Exception as e:
        conn.close()
        return {"error": str(e)}

def run_text_to_sql_pipeline(user_question: str):
    # 2. Initialize Gemini 2.5 Flash with temperature 0 for exact SQL generation
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    db_schema = get_db_schema()

    # 3. Prompt setup for SQL generation
    sql_generation_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a brilliant data analyst specializing in SaaS database systems. 
Given the following SQLite database schema, translate the user's natural language question into a clean, valid SQL query.

---
SCHEMA:
{schema}
---

CRITICAL RULES:
- Output ONLY the raw executable SQL query string. 
- Do NOT wrap it in markdown code blocks (like ```sql) or any introductory text.
- Use correct SQLite functions (e.g., use strftime for dates instead of MySQL's DATE_FORMAT).
- Only read data using SELECT. Do NOT perform any mutations."""),
        ("human", "Question: {question}")
    ])

    # Combine prompt with Gemini
    chain = sql_generation_prompt | llm
    
    # Generate the query
    response = chain.invoke({"schema": db_schema, "question": user_question})
    generated_sql = response.content.strip()
    
    # 4. Cleanup guardrail: strip away markdown backticks if Gemini accidentally includes them
    if generated_sql.startswith("```"):
        generated_sql = generated_sql.split("```")[1]
        if generated_sql.startswith("sql"):
            generated_sql = generated_sql[3:]
        generated_sql = generated_sql.strip()
    
    # Execute the generated SQL query
    db_result = execute_sql_query(generated_sql)
    
    if "error" in db_result:
        return f"Database Execution Error: {db_result['error']}"

    # 5. Synthesis prompt to convert database outputs back into friendly sentences
    synthesis_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful SaaS dashboard assistant. Take the raw database execution results and clearly explain the answer to the user's original question in plain English."),
        ("human", "User Question: {question}\nExecuted SQL: {sql}\nRaw Results: {results}")
    ])
    
    synthesis_chain = synthesis_prompt | llm
    final_answer = synthesis_chain.invoke({
        "question": user_question,
        "sql": generated_sql,
        "results": str(db_result["data"])
    })
    
    return final_answer.content