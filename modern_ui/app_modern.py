from datetime import datetime
from pathlib import Path

import streamlit as st

from modern_ui.styles import CSS


ROOT_DIR = Path(__file__).resolve().parent.parent
LOGO_PATH = ROOT_DIR / "Logo.png"


st.set_page_config(
    page_title="Virtual Hacker",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(CSS, unsafe_allow_html=True)


if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Ciao, sono **Virtual Hacker**. Descrivi il target, il contesto o l'obiettivo dell'analisi.",
        }
    ]

if "logs" not in st.session_state:
    st.session_state.logs = [
        "[system] Virtual Hacker UI loaded",
        "[system] Defensive mode ready",
        "[system] Awaiting user input",
    ]

if "mode" not in st.session_state:
    st.session_state.mode = "Chat Assistant"

if "model" not in st.session_state:
    st.session_state.model = "Demo Mode"

if "session_id" not in st.session_state:
    st.session_state.session_id = datetime.now().strftime("%Y%m%d-%H%M%S")


with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-mark">🛡️</div>
            <div class="brand-copy">
                <h1>Virtual Hacker</h1>
                <p>Defensive AI security assistant</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Control Room")

    st.session_state.mode = st.selectbox(
        "Modalità",
        ["Chat Assistant", "Risk Analysis", "OSINT Helper", "Report Generator"],
        index=["Chat Assistant", "Risk Analysis", "OSINT Helper", "Report Generator"].index(st.session_state.mode),
    )

    st.session_state.model = st.selectbox(
        "Modello",
        ["Demo Mode", "Qwen 2.5 7B", "Local LLM", "API Model"],
        index=["Demo Mode", "Qwen 2.5 7B", "Local LLM", "API Model"].index(st.session_state.model),
    )

    st.markdown("### Session")
    st.text_input("Session ID", value=st.session_state.session_id, disabled=True)

    clear_chat = st.button("Clear chat", use_container_width=True)
    add_sample = st.button("Load sample prompt", use_container_width=True)

    st.markdown("### State")
    st.markdown(
        f"""
        <div class="status-card">
            <p>Backend: <span class="status-ok">ONLINE</span></p>
            <p>UI: <span class="status-ok">ACTIVE</span></p>
            <p>Mode: <span class="status-ok">{st.session_state.mode}</span></p>
            <p>Model: <span class="status-ok">{st.session_state.model}</span></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hint">
            This view is intentionally defensive-only. Wire the chat input to your Ollama or report pipeline when you want live responses.
        </div>
        """,
        unsafe_allow_html=True,
    )


if clear_chat:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Ciao, sono **Virtual Hacker**. Descrivi il target, il contesto o l'obiettivo dell'analisi.",
        }
    ]
    st.session_state.logs = [
        "[system] Chat cleared",
        "[system] Awaiting user input",
    ]
    st.rerun()

if add_sample:
    sample_prompt = (
        "Analyze a customer support chatbot that uses an LLM, retrieves policy documents, "
        "and stores short conversation history in a local database."
    )
    st.session_state.messages.append({"role": "user", "content": sample_prompt})
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": "Sample prompt loaded. I can now structure this into a defensive risk analysis flow.",
        }
    )
    st.session_state.logs.append("[system] Sample prompt loaded")
    st.rerun()


if LOGO_PATH.exists():
    logo_left, logo_center, logo_right = st.columns([0.36, 0.28, 0.36])
    with logo_center:
        st.image(str(LOGO_PATH), use_container_width=True)
else:
    st.markdown('<div class="page-title"><h2>Virtual Hacker</h2></div>', unsafe_allow_html=True)
st.markdown('<div class="page-title page-subtitle"><p>Defensive AI security assistant</p></div>', unsafe_allow_html=True)

metric_col_1, metric_col_2, metric_col_3, metric_col_4 = st.columns(4)

with metric_col_1:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-label">Messages</div>
            <div class="metric-value">{}</div>
            <div class="metric-subtitle">Conversation turns</div>
        </div>
        """.format(len(st.session_state.messages)),
        unsafe_allow_html=True,
    )

with metric_col_2:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-label">Mode</div>
            <div class="metric-value">{}</div>
            <div class="metric-subtitle">Current workflow</div>
        </div>
        """.format(st.session_state.mode),
        unsafe_allow_html=True,
    )

with metric_col_3:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-label">Model</div>
            <div class="metric-value">{}</div>
            <div class="metric-subtitle">Backend target</div>
        </div>
        """.format(st.session_state.model),
        unsafe_allow_html=True,
    )

with metric_col_4:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-label">Status</div>
            <div class="metric-value">Live</div>
            <div class="metric-subtitle">Demo backend ready</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

left_spacer, center_col, right_col = st.columns([0.01, 0.72, 0.27])

with center_col:
    st.markdown('<div class="chat-column">', unsafe_allow_html=True)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Describe the target chatbot...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.logs.append(f"[user] {user_input}")

        with st.chat_message("user"):
            st.markdown(user_input)

        response = (
            f"I received your request for **{st.session_state.mode}**.\n\n"
            f"Model selected: **{st.session_state.model}**\n\n"
            "For now this screen is a polished demo shell. The next step is to connect the input "
            "to the Ollama pipeline in [main.py](main.py) or the interactive flow in [interactive.py](interactive.py)."
        )

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.logs.append("[assistant] Demo response generated")

        with st.chat_message("assistant"):
            st.markdown(response)

    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown(
        """
        <div class="panel-card system-log-panel">
            <div class="panel-title">
                <h3>System Log</h3>
                <span>Last 8 events</span>
            </div>
            <div class="log-box">{}</div>
        </div>
        """.format("\n".join(st.session_state.logs[-8:])),
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="panel-card">
            <div class="panel-title">
                <h3>Quick Actions</h3>
                <span>Static for now</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    button_indent_1, button_col_1 = st.columns([0.06, 0.95])
    with button_col_1:
        generate_report = st.button("Generate report", use_container_width=True)

    if generate_report:
        st.session_state.logs.append("[system] Generate report clicked")
        st.toast("Hook this to the report pipeline next.")

    button_indent_2, button_col_2 = st.columns([0.06, 0.95])
    with button_col_2:
        export_markdown = st.button("Export markdown", use_container_width=True)

    if export_markdown:
        st.session_state.logs.append("[system] Export markdown clicked")
        st.toast("Add file export wiring next.")

    button_indent_3, button_col_3 = st.columns([0.06, 0.95])
    with button_col_3:
        run_scan = st.button("Run scan", use_container_width=True)

    if run_scan:
        st.session_state.logs.append("[system] Run scan clicked")
        st.toast("Connect this to the analysis backend next.")


st.markdown(
    '<div class="footer">Virtual Hacker · Streamlit UI concept · Separate file edition</div>',
    unsafe_allow_html=True,
)
