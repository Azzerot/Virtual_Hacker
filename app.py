import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Virtual Hacker",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# CSS CUSTOM
# -----------------------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #050505 0%, #0b1117 45%, #020617 100%);
        color: #e5e7eb;
    }

    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #22c55e, #38bdf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }

    .subtitle {
        color: #9ca3af;
        font-size: 1rem;
        margin-top: 0.25rem;
        margin-bottom: 2rem;
    }

    .status-card {
        padding: 1rem;
        border-radius: 1rem;
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(34, 197, 94, 0.25);
        box-shadow: 0 0 20px rgba(34, 197, 94, 0.08);
        margin-bottom: 1rem;
    }

    .status-ok {
        color: #22c55e;
        font-weight: 700;
    }

    .terminal-box {
        background: #020617;
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 1rem;
        padding: 1rem;
        font-family: Consolas, monospace;
        color: #22c55e;
        box-shadow: inset 0 0 20px rgba(34, 197, 94, 0.05);
    }

    .footer {
        color: #6b7280;
        font-size: 0.8rem;
        text-align: center;
        margin-top: 2rem;
    }

    [data-testid="stSidebar"] {
        background: #020617;
        border-right: 1px solid rgba(34, 197, 94, 0.2);
    }

    [data-testid="stChatMessage"] {
        background: rgba(15, 23, 42, 0.65);
        border-radius: 1rem;
        padding: 0.75rem;
        border: 1px solid rgba(148, 163, 184, 0.15);
    }

    .stTextInput > div > div > input {
        background-color: #020617;
        color: #e5e7eb;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:
    st.markdown("## 🛡️ Virtual Hacker")
    st.markdown("AI Security Assistant")

    st.divider()

    mode = st.selectbox(
        "Modalità",
        [
            "Chat Assistant",
            "Risk Analysis",
            "OSINT Helper",
            "Report Generator"
        ]
    )

    model = st.selectbox(
        "Modello",
        [
            "Demo Mode",
            "Qwen 2.5 7B",
            "Local LLM",
            "API Model"
        ]
    )

    st.divider()

    st.markdown("### Stato sistema")

    st.markdown("""
    <div class="status-card">
        <p>Backend: <span class="status-ok">ONLINE</span></p>
        <p>UI: <span class="status-ok">ACTIVE</span></p>
        <p>Mode: <span class="status-ok">DEMO</span></p>
    </div>
    """, unsafe_allow_html=True)

    clear_chat = st.button("🧹 Pulisci chat", use_container_width=True)


# -----------------------------
# SESSION STATE
# -----------------------------
if "messages" not in st.session_state or clear_chat:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Ciao, sono **Virtual Hacker**. Descrivi il target, il contesto o il problema da analizzare."
        }
    ]

if "logs" not in st.session_state or clear_chat:
    st.session_state.logs = [
        "[system] Virtual Hacker UI initialized",
        "[system] Demo mode active",
        "[system] Waiting for user input"
    ]


# -----------------------------
# HEADER
# -----------------------------
left_col, right_col = st.columns([0.7, 0.3])

with left_col:
    st.markdown('<h1 class="main-title">Virtual Hacker</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">AI-powered security assistant for analysis, reasoning and reporting.</p>',
        unsafe_allow_html=True
    )

with right_col:
    st.markdown(f"""
    <div class="status-card">
        <strong>Session</strong><br>
        {datetime.now().strftime("%d/%m/%Y %H:%M")}<br><br>
        <span class="status-ok">● Active</span>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------
# MAIN LAYOUT
# -----------------------------
chat_col, info_col = st.columns([0.68, 0.32])

with chat_col:
    st.markdown("### 💬 Chat")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Scrivi un messaggio...")

    if user_input:
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        st.session_state.logs.append(f"[user] {user_input}")

        with st.chat_message("user"):
            st.markdown(user_input)

        response = f"""
Ho ricevuto la richiesta:

> {user_input}

Per ora sono in **Demo Mode**.  
Nel prossimo step collegheremo questa interfaccia alla logica reale di `interactive.py` o `main.py`.

Modalità selezionata: **{mode}**  
Modello selezionato: **{model}**
"""

        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })

        st.session_state.logs.append("[assistant] Demo response generated")

        with st.chat_message("assistant"):
            st.markdown(response)


with info_col:
    st.markdown("### 🧠 Control Panel")

    st.markdown("""
    <div class="status-card">
        <strong>Current Mode</strong><br>
        Chat Assistant<br><br>
        <strong>Security Level</strong><br>
        Educational / Defensive<br><br>
        <strong>Output</strong><br>
        Markdown Report Ready
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🖥️ System Log")

    log_text = "\n".join(st.session_state.logs[-8:])

    st.markdown(f"""
    <div class="terminal-box">
        {log_text.replace(chr(10), "<br>")}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ⚡ Quick Actions")

    col1, col2 = st.columns(2)

    with col1:
        st.button("Scan", use_container_width=True)

    with col2:
        st.button("Report", use_container_width=True)

    st.button("Export Markdown", use_container_width=True)


st.markdown(
    '<div class="footer">Virtual Hacker AISE · Streamlit Interface · Demo Build</div>',
    unsafe_allow_html=True
)