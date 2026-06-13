import streamlit as st
import sqlite3
from llm_chain import run_text_to_sql_pipeline

# 1. Page Configuration
st.set_page_config(
    page_title="SaaS Metric AI Analytics Dashboard",
    page_icon="📊",
    layout="wide", # Shifts from centered to widescreen layout
    initial_sidebar_state="expanded"
)

# 2. Modern Custom Styling (Injecting CSS for custom card shadows & alerts)
st.markdown("""
<style>
    .metric-card {
        background-color: rgba(28, 131, 225, 0.1);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #00c6ff;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 3. Helper Function to grab high-level telemetry KPIs for our UI headers
def get_quick_kpis():
    try:
        conn = sqlite3.connect("saas_dashboard.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM subscriptions WHERE status='active'")
        active_subs = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(price) FROM subscriptions WHERE status='active'")
        mrr = cursor.fetchone()[0] or 0.0
        
        conn.close()
        return total_users, active_subs, mrr
    except:
        return 0, 0, 0.0

total_users, active_subs, mrr = get_quick_kpis()

# --- SIDEBAR: Database Schema Explorer ---
with st.sidebar:
    st.header("🗄️ Connected Database")
    st.info("Target engine: **SQLite (Serverless)**")
    
    st.subheader("Schema Structural Context")
    with st.expander("👤 Table: users"):
        st.code("""id (INTEGER, PK)\nname (TEXT)\nemail (TEXT, UNIQUE)\ncreated_at (TEXT)""", language="text")
    with st.expander("💳 Table: subscriptions"):
        st.code("""id (INTEGER, PK)\nuser_id (INTEGER, FK)\nplan_name (TEXT)\nstatus (TEXT)\nprice (REAL)\nstarted_at (TEXT)""", language="text")
    with st.expander("📈 Table: usage_logs"):
        st.code("""id (INTEGER, PK)\nuser_id (INTEGER, FK)\naction (TEXT)\nunits_used (INTEGER)\ntimestamp (TEXT)""", language="text")
    
    st.markdown("---")
    st.caption("🤖 Model Powered by Gemini 2.5 Flash via LangChain")

# --- MAIN DASHBOARD INTERFACE ---
st.title("📊 SaaS Business Intelligence AI Agent")
st.markdown("Interact natively with complex clickstream usage and subscription billing datasets through plain English questions.")

# Executive KPI Ribbon
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="metric-card"><p>Total Registrations</p><p class="metric-value">{total_users}</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><p>Active Subscriptions</p><p class="metric-value">{active_subs}</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><p>Current MRR Run Rate</p><p class="metric-value">${mrr:,.2f}</p></div>', unsafe_allow_html=True)

st.markdown("### 💬 Conversational Query Engine")

# Chat session container
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am optimized to write aggregate analytical scripts. Try asking me: \n* *'Which subscription plan has generated the most active accounts?'*\n* *'Show me the monthly registration trends for our platform.'*"}
    ]

# Render historic message strings
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept transactional questions
if user_query := st.chat_input("Ask an analytical question about database operations..."):
    
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        with st.spinner("Compiling contextual layout and executing SQL pipeline..."):
            try:
                bot_response = run_text_to_sql_pipeline(user_query)
                response_placeholder.markdown(bot_response)
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
            except Exception as e:
                error_msg = f"Pipeline execution failed: `{str(e)}`"
                response_placeholder.markdown(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})