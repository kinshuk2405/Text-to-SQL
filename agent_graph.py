import os
import sqlite3
from typing import TypedDict, Optional
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

load_dotenv()

# 1. Define the Shared State of the Agent
class AgentState(TypedDict):
    question: str
    schema: str
    generated_sql: Optional[str]
    db_results: Optional[str]
    error_log: Optional[str]
    retry_count: int
    final_answer: Optional[str]

# Helper utilities
def get_db_schema():
    return SQLDatabase.from_uri("sqlite:///saas_dashboard.db").get_table_info()

def execute_sql(query: str):
    conn = sqlite3.connect("saas_dashboard.db")
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return {"data": str(results), "error": None}
    except Exception as e:
        conn.close()
        return {"data": None, "error": str(e)}

# --- NODES: The Operational Blocks of our Agent ---

def generate_sql_node(state: AgentState) -> dict:
    """Node 1: Prompts Gemini to write or repair SQL based on error feedback."""
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    
    if state.get("error_log"):
        system_msg = f"""You previously generated an invalid SQL query. Your task is to fix it based on the database error log.
        
SCHEMA:
{state['schema']}

FAILED QUERY: {state['generated_sql']}
ERROR TRACKBACK: {state['error_log']}

CRITICAL: Return ONLY the corrected raw SQL string. Do NOT use markdown code blocks or backticks."""
    else:
        system_msg = f"""You are a master data analyst. Given this schema, write a valid SQLite query to answer the user's question.
        
SCHEMA:
{state['schema']}

CRITICAL: Return ONLY the raw SQL query. Do NOT use markdown code blocks or backticks."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_msg),
        ("human", "Question: {question}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"question": state["question"]})
    
    # Clean up any rogue markdown wrappers if they leak out
    clean_sql = response.content.strip().replace("```sql", "").replace("```", "").strip()
    return {"generated_sql": clean_sql, "retry_count": state.get("retry_count", 0) + 1}


def execute_sql_node(state: AgentState) -> dict:
    """Node 2: Executes the query and logs failures to state history."""
    query_to_test = state["generated_sql"]
    execution = execute_sql(query_to_test)
    return {
        "db_results": execution["data"],
        "error_log": execution["error"]
    }


def synthesize_answer_node(state: AgentState) -> dict:
    """Node 3: Compiles operational outputs into user insights."""
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an AI SaaS Insights executive assistant. Explain the raw database metrics clearly in conversational English."),
        ("human", "User Question: {question}\nExecuted SQL: {sql}\nRaw Data Rows: {results}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({
        "question": state["question"],
        "sql": state["generated_sql"],
        "results": state["db_results"]
    })
    return {"final_answer": response.content}

# --- EDGES: Conditional Decision Boundaries ---

def should_continue(state: AgentState):
    """Dynamic routing boundary checking execution accuracy."""
    if state["error_log"] is not None:
        if state["retry_count"] >= 3:
            return "synthesize" # Cap retries to prevent infinite API billing loops
        print(f"⚠️ Agent caught an execution error: {state['error_log']}. Routing back to self-correct...")
        return "generate"
    return "synthesize"

# --- COMPILING THE WORKFLOW GRAPH ---

workflow = StateGraph(AgentState)

# Define Nodes
workflow.add_node("generate_sql", generate_sql_node)
workflow.add_node("execute_sql", execute_sql_node)
workflow.add_node("synthesize", synthesize_answer_node)

# Construct Workflow Paths
workflow.set_entry_point("generate_sql")
workflow.add_edge("generate_sql", "execute_sql")

# Add Conditional Route from execution step
workflow.add_conditional_edges(
    "execute_sql",
    should_continue,
    {
        "generate": "generate_sql",
        "synthesize": "synthesize"
    }
)
workflow.add_edge("synthesize", END)

# Compile the final graph execution pipeline
agent_executor = workflow.compile()

def run_agentic_pipeline(user_question: str) -> dict:
    """Main interface function for the frontend UI app.
    Returns a dictionary containing both the final answer and telemetry metadata.
    """
    initial_state = {
        "question": user_question,
        "schema": get_db_schema(),
        "generated_sql": None,
        "db_results": None,
        "error_log": None,
        "retry_count": 0,
        "final_answer": None
    }
    
    # Run the LangGraph state machine execution loop
    output_state = agent_executor.invoke(initial_state)
    
    # FIX: Return structured data instead of a single massive string
    return {
        "final_answer": output_state['final_answer'],
        "generated_sql": output_state['generated_sql'],
        "retry_count": output_state['retry_count']
    }