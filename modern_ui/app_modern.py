from datetime import datetime
import html
from pathlib import Path
import queue
import sys
import threading
import time

import streamlit as st

from modern_ui.styles import CSS


ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from interactive import run_virtual_hacker_analysis


LOGO_PATH = ROOT_DIR / "Logo.png"


def _analysis_worker(output_queue, natural_description, model_name, stop_event):
    try:
        result = run_virtual_hacker_analysis(
            natural_description=natural_description,
            model_name=model_name,
            stop_event=stop_event,
        )
    except Exception as exc:
        if stop_event is not None and stop_event.is_set():
            result = {
                "ok": False,
                "cancelled": True,
                "error": "Analysis stopped by user.",
            }
        else:
            result = {
                "ok": False,
                "error": str(exc),
            }

    output_queue.put(result)


def _request_stop_run():
    if st.session_state.analysis_stop_event is None:
        return

    st.session_state.analysis_stop_event.set()
    st.session_state.analysis_status = "idle"
    st.session_state.logs.append("[system] Stop requested by user")
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": "Ehi, hai stoppato tu la run. Sto chiudendo il processo Ollama adesso.",
        }
    )
    st.toast("Run stoppata da te. Sto chiudendo Ollama.")
    st.rerun()


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
            "content": (
                "Ciao, sono **Virtual Hacker**. Descrivi il sistema LLM o chatbot che vuoi analizzare: "
                "nome del sistema, scopo, architettura, utenti, componenti, dati trattati, assunzioni di sicurezza, "
                "possibile attaccante e rischi da valutare. Userò queste informazioni per generare un JSON strutturato "
                "e un report difensivo sulle potenziali vulnerabilità."
            ),
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

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "last_user_input" not in st.session_state:
    st.session_state.last_user_input = ""

if "analysis_status" not in st.session_state:
    st.session_state.analysis_status = "idle"

if "analysis_thread" not in st.session_state:
    st.session_state.analysis_thread = None

if "analysis_queue" not in st.session_state:
    st.session_state.analysis_queue = None

if "analysis_stop_event" not in st.session_state:
    st.session_state.analysis_stop_event = None

if "analysis_model_label" not in st.session_state:
    st.session_state.analysis_model_label = ""

if st.session_state.analysis_queue is not None:
    try:
        analysis_result = st.session_state.analysis_queue.get_nowait()
    except queue.Empty:
        if (
            st.session_state.analysis_thread is not None
            and not st.session_state.analysis_thread.is_alive()
        ):
            st.session_state.logs.append("[system] Analysis stopped")
            st.session_state.analysis_status = "idle"
            st.session_state.analysis_thread = None
            st.session_state.analysis_queue = None
            st.session_state.analysis_stop_event = None
            st.session_state.analysis_model_label = ""
    else:
        st.session_state.analysis_thread = None
        st.session_state.analysis_queue = None
        st.session_state.analysis_stop_event = None
        st.session_state.analysis_status = "idle"
        st.session_state.analysis_model_label = ""

        if analysis_result.get("ok"):
            st.session_state.last_result = analysis_result

            response = (
                "Analisi completata.\n\n"
                f"**JSON generato:** `{analysis_result['json_path']}`\n\n"
                f"**Report generato:** `{analysis_result['report_path']}`\n\n"
                "## Report\n\n"
                f"{analysis_result['risk_report']}"
            )

            st.session_state.logs.append("[assistant] JSON and report generated")

        elif analysis_result.get("cancelled"):
            response = "Ehi, hai stoppato tu la run. Analisi interrotta e processo Ollama fermato."
            st.session_state.logs.append("[system] Analysis stopped by user")

        else:
            response = (
                "Errore durante l'analisi.\n\n"
                f"```text\n{analysis_result.get('error')}\n```"
            )

            st.session_state.logs.append("[assistant] Backend error")

        st.session_state.messages.append({"role": "assistant", "content": response})


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

    st.session_state.mode = "Chat Assistant"
    st.markdown(f"**Mode:** {st.session_state.mode}")

    model_options = [
        "Demo Mode",
        "Qwen 2.5 7B",
        "Mistral 7B",
    ]

    st.session_state.model = st.selectbox(
        "Modello",
        model_options,
        index=model_options.index(st.session_state.model)
        if st.session_state.model in model_options
        else 0,
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
            <p>Run: <span class="status-ok">{st.session_state.analysis_status.upper()}</span></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

if clear_chat:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Ciao, sono **Virtual Hacker**. Descrivi il sistema LLM o chatbot che vuoi analizzare: "
                "nome del sistema, scopo, architettura, utenti, componenti, dati trattati, assunzioni di sicurezza, "
                "possibile attaccante e rischi da valutare. Userò queste informazioni per generare un JSON strutturato "
                "e un report difensivo sulle potenziali vulnerabilità."
            ),
        }
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

metric_col_1, metric_col_2, metric_col_3, _metric_spacer = st.columns(4)

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

left_spacer, center_col, right_col = st.columns([0.01, 0.72, 0.27])

with center_col:
    st.markdown('<div class="chat-column">', unsafe_allow_html=True)

    analysis_running = st.session_state.analysis_status == "running"

    st.markdown('<div class="chat-scroll">', unsafe_allow_html=True)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    user_input = st.chat_input(
        "Analisi in corso, attendi la fine della run..."
        if analysis_running
        else "Descrivi il sistema LLM da analizzare...",
        disabled=analysis_running,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.logs.append(f"[user] {user_input}")
        st.session_state.last_user_input = user_input

        model_map = {
            "Qwen 2.5 7B": "qwen2.5:7b",
            "Mistral 7B": "mistral:7b",
        }

        if st.session_state.model == "Demo Mode":
            response = (
                "Demo Mode attiva.\n\n"
                "Seleziona **Qwen 2.5 7B** o **Mistral 7B** nella sidebar per generare JSON e report reali."
            )
            st.session_state.logs.append("[assistant] Demo response generated")
        elif st.session_state.analysis_status == "running":
            response = (
                "C'e' gia' un'analisi Ollama in corso.\n\n"
                "Usa **Stop run** prima di avviarne un'altra."
            )
            st.session_state.logs.append("[system] Analysis already running")
        else:
            ollama_model = model_map.get(st.session_state.model, "qwen2.5:7b")
            st.session_state.analysis_status = "running"
            st.session_state.analysis_model_label = st.session_state.model
            st.session_state.analysis_queue = queue.Queue()
            st.session_state.analysis_stop_event = threading.Event()
            st.session_state.analysis_thread = threading.Thread(
                target=_analysis_worker,
                args=(
                    st.session_state.analysis_queue,
                    user_input,
                    ollama_model,
                    st.session_state.analysis_stop_event,
                ),
                daemon=True,
            )
            st.session_state.analysis_thread.start()
            st.session_state.logs.append("[system] Ollama run started")

            response = (
                f"**Modello in esecuzione:** {st.session_state.analysis_model_label}\n\n"
                "Elaborazione in corso..."
            )

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    
    # Always scroll to chat input to keep it visible
    st.markdown(
        """
        <script>
            setTimeout(function() {
                const chatInput = document.querySelector('[data-testid="stChatInput"]');
                if (chatInput) {
                    chatInput.scrollIntoView({ behavior: 'smooth', block: 'end' });
                }
            }, 100);
        </script>
        """,
        unsafe_allow_html=True,
    )

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
        """.format(html.escape("\n".join(st.session_state.logs[-8:]))),
        unsafe_allow_html=True,
    )

    model_label = html.escape(st.session_state.analysis_model_label or st.session_state.model)
    run_status = html.escape(st.session_state.analysis_status.upper())

    if st.session_state.analysis_status == "running":
        action_text = '<span class="status-ok"><span class="loading-dot"></span> Loading...</span>'
        run_label = model_label
    else:
        action_text = '<span class="status-ok">Ready</span>'
        run_label = "Idle"

    st.markdown(
        f"""
        <div class="panel-card">
            <div class="panel-title">
                <h3>Ollama Run</h3>
                <span>{run_label}</span>
            </div>
            <div class="status-card">
                <p>State: <span class="status-ok">{run_status}</span></p>
                <p>Action: {action_text}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    stop_requested = st.button(
        "Stop run",
        key="panel_stop_run",
        use_container_width=True,
        disabled=st.session_state.analysis_status != "running",
    )

    if stop_requested:
        _request_stop_run()

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

    generate_report = st.button("Generate report", use_container_width=True)

    if generate_report:
        st.session_state.logs.append("[system] Generate report clicked")
        st.toast("Hook this to the report pipeline next.")

    export_markdown = st.button("Export markdown", use_container_width=True)

    if export_markdown:
        st.session_state.logs.append("[system] Export markdown clicked")
        st.toast("Add file export wiring next.")

    run_scan = st.button("Run scan", use_container_width=True)

    if run_scan:
        st.session_state.logs.append("[system] Run scan clicked")
        st.toast("Connect this to the analysis backend next.")

st.markdown(
    '<div class="footer">Virtual Hacker · Streamlit UI concept · Separate file edition</div>',
    unsafe_allow_html=True,
)
