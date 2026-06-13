import streamlit as st
import sqlite3
from agent_graph import run_agentic_pipeline as run_text_to_sql_pipeline

# 1. Premium Page Setup
st.set_page_config(
    page_title="SaaS Intelligence Hub",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Balanced Cyber-Professional CSS Theme Layer
st.markdown("""
<style>
    /* Global Base Settings */
    .stApp {
        background-color: #0b0d12 !important;
        color: #e5e7eb !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Elegant Sidebar Paneling */
    section[data-testid="stSidebar"] {
        background-color: #121620 !important;
        border-right: 1px solid rgba(99, 102, 241, 0.15) !important;
    }
    
    /* Sleek Hybrid Metric Grid Cards */
    .metric-grid {
        display: flex;
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        flex: 1;
        background: linear-gradient(145deg, #121620, #161b26);
        padding: 1.2rem;
        border-radius: 8px;
        border: 1px solid rgba(99, 102, 241, 0.15);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .metric-title {
        font-size: 0.75rem;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.4rem;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #f3f4f6;
        font-family: 'Courier New', monospace;
    }
    
    /* Interactive Messaging Component Mechanics */
    .chat-wrapper {
        display: flex;
        align-items: flex-end;
        gap: 0.75rem;
        margin-bottom: 1.2rem;
        width: 100%;
    }
    .chat-wrapper.user-alignment {
        justify-content: flex-end;
    }
    .chat-wrapper.agent-alignment {
        justify-content: flex-start;
    }
    
    /* Chat Avatars Indicators */
    .avatar-icon {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.9rem;
        font-weight: bold;
    }
    .user-avatar {
        background-color: #4f46e5;
        color: white;
        box-shadow: 0 0 8px rgba(79, 70, 229, 0.4);
    }
    .agent-avatar {
        background-color: #1f2937;
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    
    /* Premium Asymmetric Text Bubbles */
    .bubble {
        padding: 0.9rem 1.3rem;
        border-radius: 12px;
        max-width: 70%;
        font-size: 0.95rem;
        line-height: 1.5;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
    }
    .user-bubble {
        background-color: #6366f1 !important;
        color: #ffffff !important;
        border-bottom-right-radius: 2px;
    }
    .agent-bubble {
        background-color: #181d2a !important;
        color: #f3f4f6 !important;
        border-bottom-left-radius: 2px;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. Background Database Metric Queries
def fetch_system_metrics():
    try:
        conn = sqlite3.connect("saas_dashboard.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        u_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM subscriptions WHERE status='active'")
        s_count = cursor.fetchone()[0]
        cursor.execute("SELECT SUM(price) FROM subscriptions WHERE status='active'")
        mrr_val = cursor.fetchone()[0] or 0.0
        conn.close()
        return u_count, s_count, mrr_val
    except:
        return 0, 0, 0.0

total_users, active_subs, mrr = fetch_system_metrics()

# --- SIDEBAR CONTROL CENTER PANEL ---
with st.sidebar:
    st.markdown("### 🖥️ Agent Core Controls")
    st.caption("Deployment Node: Gemini-2.5 • Status: Live")
    st.markdown("---")
    
    st.markdown("📂 **Relational Knowledge Graph**")
    st.caption("Active data layouts mapped in memory context:")
    
    with st.expander("• Table Schema: users"):
        st.markdown("`id` • `name` • `email` • `created_at`")
    with st.expander("• Table Schema: subscriptions"):
        st.markdown("`id` • `user_id` • `plan_name` • `status` • `price` • `started_at`")
    with st.expander("• Table Schema: usage_logs"):
        st.markdown("`id` • `user_id` • `action` • `units_used` • `timestamp`")
        
    st.markdown("---")
    st.caption("🔒 Sandbox mode executing read-only semantic routing queries.")

# --- MAIN WORKSPACE PANEL ---
st.markdown("### 🌐 ENTERPRISE AGENT ARCHITECTURE")
st.title("SaaS Intelligence Advisor")
st.markdown("Interact directly with your platform's live data. The agent contextually routes requests, addresses complex structural joins, and auto-corrects code loops on demand.")
st.markdown("---")

# Styled Executive Data Ribbon
st.markdown(f"""
<div class="metric-grid">
    <div class="metric-card">
        <div class="metric-title">👥 Total Platform Accounts</div>
        <div class="metric-value">{total_users:,}</div>
    </div>
    <div class="metric-card">
        <div class="metric-title">💳 Active Subscriptions</div>
        <div class="metric-value">{active_subs:,}</div>
    </div>
    <div class="metric-card">
        <div class="metric-title">💰 Monthly Recurring Run-Rate</div>
        <div class="metric-value">${mrr:,.2f}</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Setup clean history state registers
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "is_user": False, 
            "text": "Core analytics memory arrays loaded. Relational layout indexes stand ready. Submit computational strings or business metrics objectives when prepared.", 
            "sql": None, 
            "loops": None
        }
    ]

# Render historic message strings using structural hybrid containers
for message in st.session_state.chat_history:
    if message["is_user"]:
        st.markdown(f"""
        <div class="chat-wrapper user-alignment">
            <div class="bubble user-bubble">{message['text']}</div>
            <div class="avatar-icon user-avatar">U</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-wrapper agent-alignment">
            <div class="avatar-icon agent-avatar">AI</div>
            <div class="bubble agent-bubble">{message['text']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Keep technical logs tucked into a clean developer tab under the AI answer
        if message.get("sql"):
            with st.expander("🛠️ View Agent Execution Logs"):
                st.code(message["sql"], language="sql")
                st.caption(f"Graph Self-Correction Cycles Executed: {message['loops']}")

# User Chat Prompt Target
if user_input := st.chat_input("Submit query requirements to the agent..."):
    
    # 1. Output User prompt layout card to UI instantly
    st.markdown(f"""
    <div class="chat-wrapper user-alignment">
        <div class="bubble user-bubble">{user_input}</div>
        <div class="avatar-icon user-avatar">U</div>
    </div>
    """, unsafe_allow_html=True)
    st.session_state.chat_history.append({"is_user": True, "text": user_input})
    
    # 2. Invoke Background Graph Execution Node
    with st.spinner("Compiling constraints and querying execution pipeline..."):
        try:
            agent_result = run_text_to_sql_pipeline(user_input)
            clean_text = agent_result["final_answer"]
            query_compiled = agent_result["generated_sql"]
            loop_count = agent_result["retry_count"] - 1
            
            # Print response blocks with clean left-side structures
            st.markdown(f"""
            <div class="chat-wrapper agent-alignment">
                <div class="avatar-icon agent-avatar">AI</div>
                <div class="bubble agent-bubble">{clean_text}</div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("🛠️ View Agent Execution Logs"):
                st.code(query_compiled, language="sql")
                st.caption(f"Graph Self-Correction Cycles Executed: {loop_count}")
                
            # Log metrics tracking history
            st.session_state.chat_history.append({
                "is_user": False,
                "text": clean_text,
                "sql": query_compiled,
                "loops": loop_count
            })
            
        except Exception as err:
            error_msg = f"Pipeline Operational Interruption: {str(err)}"
            st.markdown(f"""
            <div class="chat-wrapper agent-alignment">
                <div class="avatar-icon agent-avatar" style="color: #ef4444;">⚠</div>
                <div class="bubble agent-bubble" style="color: #ef4444; border-color: rgba(239, 68, 68, 0.3) !important;">{error_msg}</div>
            </div>
            """, unsafe_allow_html=True)
            st.session_state.chat_history.append({"is_user": False, "text": error_msg})