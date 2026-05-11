from datetime import datetime
from textwrap import dedent
import html
from pathlib import Path
import queue
import sys
import threading
import time

import streamlit as st


ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from modern_ui.styles import CSS
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

    st.session_state.analysis_status = "stopping"
    st.session_state.analysis_stop_event.set()

    st.session_state.logs.append("[system] Stop requested by user")
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": "Ehi, hai stoppato tu la run. Sto chiudendo il processo Ollama adesso.",
        }
    )

    st.toast("Run stoppata da te. Sto chiudendo Ollama.")
    st.rerun()


def build_quality_markdown(quality_result: dict | None) -> str:
    if not quality_result:
        return ""

    quality_markdown = "## JSON Completeness Check\n\n"
    quality_markdown += f"**Status:** `{quality_result.get('quality_status', 'unknown')}`\n\n"

    missing_fields = quality_result.get("missing_fields", [])
    warnings = quality_result.get("warnings", [])
    suggested_questions = quality_result.get("suggested_questions", [])

    if missing_fields:
        quality_markdown += "### Missing Fields\n\n"
        for field in missing_fields:
            quality_markdown += f"- {field}\n"

    if warnings:
        quality_markdown += "\n### Warnings\n\n"
        for warning in warnings:
            quality_markdown += f"- {warning}\n"

    if suggested_questions:
        quality_markdown += "\n### Suggested Questions\n\n"
        for question in suggested_questions:
            quality_markdown += f"- {question}\n"

    return quality_markdown


def render_quality_panel(quality_result: dict | None) -> None:
    if not quality_result:
        st.info("No JSON quality check available yet.")
        return

    status = quality_result.get("quality_status", "unknown")

    if status == "complete":
        st.success("JSON quality: complete")
    elif status == "partial":
        st.warning("JSON quality: partial")
    elif status == "insufficient":
        st.error("JSON quality: insufficient")
    else:
        st.info(f"JSON quality: {status}")

    missing_fields = quality_result.get("missing_fields", [])
    warnings = quality_result.get("warnings", [])
    suggested_questions = quality_result.get("suggested_questions", [])

    if missing_fields:
        with st.expander("Missing Fields", expanded=False):
            for field in missing_fields:
                st.write(f"- {field}")

    if warnings:
        with st.expander("Warnings", expanded=False):
            for warning in warnings:
                st.write(f"- {warning}")

    if suggested_questions:
        with st.expander("Suggested Questions", expanded=True):
            for question in suggested_questions:
                st.write(f"- {question}")


def build_analysis_response(result: dict) -> str:
    if result.get("ok"):
        quality_markdown = build_quality_markdown(result.get("quality_result"))

        response = (
            "Analisi completata.\n\n"
            f"**JSON generato:** `{result['json_path']}`\n\n"
        )

        if result.get("quality_path"):
            response += f"**Quality check generato:** `{result['quality_path']}`\n\n"

        response += (
            f"**Report generato:** `{result['report_path']}`\n\n"
            f"{quality_markdown}\n\n"
            "## Report\n\n"
            f"{result['risk_report']}"
        )

        return response

    if result.get("cancelled"):
        return "Run stoppata correttamente."

    quality_result = result.get("quality_result")

    if quality_result:
        return build_quality_markdown(quality_result)

    return (
        "Errore durante l'analisi.\n\n"
        f"```text\n{result.get('error')}\n```"
    )


st.set_page_config(
    page_title="Virtual Hacker",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(CSS, unsafe_allow_html=True)


# -----------------------------
# Session state initialization
# -----------------------------

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

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "last_user_input" not in st.session_state:
    st.session_state.last_user_input = ""

if "last_quality_result" not in st.session_state:
    st.session_state.last_quality_result = None

if "last_report_validation" not in st.session_state:
    st.session_state.last_report_validation = None

if "analysis_status" not in st.session_state:
    st.session_state.analysis_status = "idle"

if "analysis_queue" not in st.session_state:
    st.session_state.analysis_queue = queue.Queue()

if "analysis_thread" not in st.session_state:
    st.session_state.analysis_thread = None

if "analysis_stop_event" not in st.session_state:
    st.session_state.analysis_stop_event = None

if "analysis_input" not in st.session_state:
    st.session_state.analysis_input = None


# -----------------------------
# Poll background analysis result
# -----------------------------

if st.session_state.analysis_status in {"running", "stopping"}:
    try:
        result = st.session_state.analysis_queue.get_nowait()

        st.session_state.last_result = result
        st.session_state.last_quality_result = result.get("quality_result")
        st.session_state.last_report_validation = result.get("report_validation_result")

        response = build_analysis_response(result)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response,
            }
        )

        if result.get("ok"):
            quality_status = result.get("quality_result", {}).get(
                "quality_status",
                "unknown",
            )
            st.session_state.logs.append(
                f"[system] JSON quality check: {quality_status}"
            )
            st.session_state.logs.append(
                "[assistant] JSON, quality check and report generated"
            )
        elif result.get("cancelled"):
            st.session_state.logs.append("[system] Analysis cancelled")
        else:
            if result.get("quality_result"):
                quality_status = result.get("quality_result", {}).get(
                    "quality_status",
                    "unknown",
                )
                st.session_state.logs.append(
                    f"[system] JSON quality check: {quality_status}"
                )
                st.session_state.logs.append("[assistant] JSON quality insufficient")
            else:
                st.session_state.logs.append("[assistant] Backend error")

        st.session_state.analysis_status = "idle"
        st.session_state.analysis_thread = None
        st.session_state.analysis_stop_event = None
        st.session_state.analysis_input = None

        st.rerun()

    except queue.Empty:
        pass


# -----------------------------
# Sidebar
# -----------------------------

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
        "gemma3:27b",
        "magistral:24b",
        "qwen2.5:32b",
        "qwen2.5:7b",
        "mistral:7b",
    ]

    st.session_state.model = st.selectbox(
        "Modello",
        model_options,
        index=(
            model_options.index(st.session_state.model)
            if st.session_state.model in model_options
            else 0
        ),
    )

    st.markdown("### Session")
    st.text_input("Session ID", value=st.session_state.session_id, disabled=True)

    clear_chat = st.button("Clear chat", use_container_width=True)
    add_sample = st.button("Load sample prompt", use_container_width=True)

    st.markdown("### State")

    status_label = st.session_state.analysis_status.upper()

    st.markdown(
        f"""
<div class="status-card">
<p>Backend: <span class="status-ok">ONLINE</span></p>
<p>UI: <span class="status-ok">ACTIVE</span></p>
<p>Mode: <span class="status-ok">{st.session_state.mode}</span></p>
<p>Model: <span class="status-ok">{st.session_state.model}</span></p>
<p>Run: <span class="status-ok">{status_label}</span></p>
</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-stop-spacer"></div>', unsafe_allow_html=True)

    sidebar_stop_requested = st.button(
        "Stop run",
        key="sidebar_stop_run",
        use_container_width=True,
        disabled=st.session_state.analysis_status not in {"running", "stopping"},
    )

    if sidebar_stop_requested:
        _request_stop_run()


# -----------------------------
# Sidebar actions
# -----------------------------

if clear_chat:
    if st.session_state.analysis_stop_event is not None:
        st.session_state.analysis_stop_event.set()

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

    st.session_state.last_result = None
    st.session_state.last_user_input = ""
    st.session_state.last_quality_result = None

    st.session_state.analysis_status = "idle"
    st.session_state.analysis_thread = None
    st.session_state.analysis_stop_event = None
    st.session_state.analysis_input = None

    while not st.session_state.analysis_queue.empty():
        try:
            st.session_state.analysis_queue.get_nowait()
        except queue.Empty:
            break

    st.rerun()


if add_sample:
    sample_prompt = (
        "Analyze a customer support chatbot called HelpBot. "
        "It is used by authenticated customers and internal support agents. "
        "The system uses a web UI, Python backend, local LLM through Ollama, "
        "RAG knowledge base with policy documents, and a local database for short conversation history. "
        "It handles customer questions, short conversation history, policy documents, and non-sensitive account data. "
        "The chatbot must not reveal internal prompts, other users' data, or unauthorized knowledge base content. "
        "The attacker is an authenticated customer with chat access. "
        "The attacker can send messages and view chatbot responses, but cannot access admin panels, databases, source code, or model configuration. "
        "Analyze prompt injection, privacy leakage, hallucination, unauthorized access, and information disclosure."
    )

    st.session_state.messages.append({"role": "user", "content": sample_prompt})
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": "Sample prompt loaded. Send it again or paste your own target description to run the analysis.",
        }
    )
    st.session_state.logs.append("[system] Sample prompt loaded")

    st.rerun()


# -----------------------------
# Header
# -----------------------------

if LOGO_PATH.exists():
    logo_left, logo_center, logo_right = st.columns([0.36, 0.28, 0.36])

    with logo_center:
        st.image(str(LOGO_PATH), width=260)
else:
    st.markdown(
        '<div class="page-title"><h2>Virtual Hacker</h2></div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="page-title page-subtitle"><p>Defensive AI security assistant</p></div>',
    unsafe_allow_html=True,
)


# -----------------------------
# Metrics (centered)
# -----------------------------

metrics_html = f"""
<div class="metrics-container">
    <div class="metric-card">
        <div class="metric-label">Messages</div>
        <div class="metric-value">{len(st.session_state.messages)}</div>
        <div class="metric-subtitle">Conversation turns</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Mode</div>
        <div class="metric-value">{st.session_state.mode}</div>
        <div class="metric-subtitle">Current workflow</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Model</div>
        <div class="metric-value">{st.session_state.model}</div>
        <div class="metric-subtitle">Backend target</div>
    </div>
</div>
"""

st.markdown(metrics_html, unsafe_allow_html=True)


left_spacer, center_col, right_spacer = st.columns([0.01, 0.98, 0.01])




# -----------------------------
# Main chat
# -----------------------------

with center_col:
    st.markdown('<div class="chat-column">', unsafe_allow_html=True)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if st.session_state.analysis_status == "running":
        st.info("Analisi in corso. Puoi fermarla dalla sidebar con **Stop run**.")

    elif st.session_state.analysis_status == "stopping":
        st.warning("Stop richiesto. Sto aspettando la chiusura della run.")

    user_input = st.chat_input(
        "Describe the target chatbot...",
        disabled=st.session_state.analysis_status in {"running", "stopping"},
    )

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.logs.append(f"[user] {user_input}")
        st.session_state.last_user_input = user_input

        with st.chat_message("user"):
            st.markdown(user_input)

        model_map = {
            "gemma3:27b": "gemma3:27b",
            "magistral:24b": "magistral:24b",
            "qwen2.5:32b": "qwen2.5:32b",
            "qwen2.5:7b": "qwen2.5:7b",
            "mistral:7b": "mistral:7b",
        }

        if st.session_state.model == "Demo Mode":
            response = (
                "Demo Mode attiva.\n\n"
                "Seleziona uno dei modelli configurati nella sidebar "
                "per generare JSON, completeness check e report reali."
            )

            st.session_state.logs.append("[assistant] Demo response generated")
            st.session_state.messages.append({"role": "assistant", "content": response})

            st.rerun()

        else:
            if st.session_state.analysis_status in {"running", "stopping"}:
                response = (
                    "Una run è già in corso. "
                    "Puoi fermarla con **Stop run** dalla sidebar."
                )

                st.session_state.logs.append("[system] Run already active")
                st.session_state.messages.append({"role": "assistant", "content": response})

                with st.chat_message("assistant"):
                    st.markdown(response)

            else:
                ollama_model = model_map.get(st.session_state.model, "qwen2.5:7b")

                st.session_state.analysis_status = "running"
                st.session_state.analysis_stop_event = threading.Event()
                st.session_state.analysis_input = user_input

                while not st.session_state.analysis_queue.empty():
                    try:
                        st.session_state.analysis_queue.get_nowait()
                    except queue.Empty:
                        break

                worker = threading.Thread(
                    target=_analysis_worker,
                    args=(
                        st.session_state.analysis_queue,
                        user_input,
                        ollama_model,
                        st.session_state.analysis_stop_event,
                    ),
                    daemon=True,
                )

                st.session_state.analysis_thread = worker
                worker.start()

                response = (
                    "Analisi avviata.\n\n"
                    "Sto generando JSON, quality check e report. "
                    "Puoi usare **Stop run** dalla sidebar per interrompere."
                )

                st.session_state.logs.append("[system] Analysis started")
                st.session_state.messages.append({"role": "assistant", "content": response})

                with st.chat_message("assistant"):
                    st.markdown(response)

                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# =============================================================================
# RIGHT SIDEBAR
# =============================================================================

escaped_logs = html.escape("\n".join(st.session_state.logs[-8:]))

quality_result = st.session_state.get("last_quality_result")

quality_status = "unknown"
quality_badge_color = "#67e8f9"
quality_content = '<p class="right-muted">No quality check yet.</p>'

if quality_result:
    quality_status = quality_result.get("quality_status", "unknown")

    if quality_status == "complete":
        quality_badge_color = "#86efac"
    elif quality_status == "partial":
        quality_badge_color = "#fbbf24"
    elif quality_status == "insufficient":
        quality_badge_color = "#fb7185"

    missing_fields = quality_result.get("missing_fields", [])
    warnings = quality_result.get("warnings", [])
    suggested_questions = quality_result.get("suggested_questions", [])

    quality_lines = [
        f'<p><strong>Status:</strong> {html.escape(str(quality_status))}</p>'
    ]

    if missing_fields:
        quality_lines.append(f'<p><strong>Missing fields:</strong> {len(missing_fields)}</p>')
        for field in missing_fields[:5]:
            quality_lines.append(f'<div class="quality-item">• {html.escape(str(field))}</div>')

    if warnings:
        quality_lines.append(f'<p><strong>Warnings:</strong> {len(warnings)}</p>')
        for warning in warnings[:5]:
            quality_lines.append(f'<div class="quality-item">• {html.escape(str(warning))}</div>')

    if suggested_questions:
        quality_lines.append(f'<p><strong>Suggested questions:</strong> {len(suggested_questions)}</p>')
        for question in suggested_questions[:3]:
            quality_lines.append(f'<div class="quality-item">• {html.escape(str(question))}</div>')

    quality_content = "\n".join(quality_lines)


right_sidebar_html = dedent(f"""
<div class="right-sidebar-fixed">
<div class="panel-card system-log-panel">
<div class="panel-title">
<h3>System Log</h3>
<span>Last 8 events</span>
</div>
<div class="log-box">{escaped_logs}</div>
</div>

<div class="panel-card">
<div class="panel-title">
<h3>Latest JSON Quality</h3>
<span style="color: {quality_badge_color}; font-weight: 700;">● {html.escape(str(quality_status))}</span>
</div>
<div class="quality-box">
{quality_content}
</div>
</div>
""").strip()

# Build report validation block separately so we can inject dynamic values
report_validation = st.session_state.get("last_report_validation")

if not report_validation:
    report_block = "<p class=\"right-muted\">No report validation available yet.</p>"
else:
    score = report_validation.get("coherence_score", None)
    status = report_validation.get("report_status", "unknown")
    recommended = report_validation.get("recommended_action", "")
    summary = html.escape(str(report_validation.get("summary", "")))

    try:
        score_val = float(score) if score is not None else None
    except Exception:
        score_val = None

    if score_val is None:
        score_display = "N/A"
        score_color = "#9ca3af"
    else:
        score_display = f"{score_val * 100:.1f}%"
        if score_val >= 0.85:
            score_color = "#86efac"
        elif score_val >= 0.75:
            score_color = "#fbbf24"
        else:
            score_color = "#fb7185"

    report_block_lines = [
        f'<p><strong>Score:</strong> <span style="color: {score_color}; font-weight:700;">{score_display}</span></p>',
        f'<p><strong>Status:</strong> {html.escape(str(status))}</p>',
    ]

    if recommended:
        report_block_lines.append(f'<p><strong>Action:</strong> {html.escape(str(recommended))}</p>')

    if summary:
        report_block_lines.append(f'<div class="quality-item">{summary}</div>')

    report_block = "\n".join(report_block_lines)

right_sidebar_html += dedent(f"""

<div class="panel-card">
<div class="panel-title">
<h3>Report Coherence</h3>
<span>Validation</span>
</div>
<div class="quality-box">
{report_block}
</div>
</div>

<div class="panel-card">
<div class="panel-title">
<h3>Quick Actions</h3>
<span>Ready</span>
</div>
<p class="right-muted">Actions available after a real analysis run.</p>
</div>
</div>
""")

st.markdown(right_sidebar_html, unsafe_allow_html=True)

# -----------------------------
# Footer + auto refresh
# -----------------------------

st.markdown(
    '<div class="footer">Virtual Hacker · Streamlit UI concept · Separate file edition</div>',
    unsafe_allow_html=True,
)

if st.session_state.analysis_status in {"running", "stopping"}:
    time.sleep(0.5)
    st.rerun()