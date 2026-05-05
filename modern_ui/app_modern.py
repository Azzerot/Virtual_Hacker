from datetime import datetime

from pathlib import Path

import sys
 
import streamlit as st
 
 
ROOT_DIR = Path(__file__).resolve().parent.parent
 
if str(ROOT_DIR) not in sys.path:

    sys.path.append(str(ROOT_DIR))
 
from modern_ui.styles import CSS

from interactive import run_virtual_hacker_analysis
 
 
LOGO_PATH = ROOT_DIR / "Logo.png"
 
 
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
 
if "last_result" not in st.session_state:

    st.session_state.last_result = None
 
if "last_user_input" not in st.session_state:

    st.session_state.last_user_input = ""
 
if "last_quality_result" not in st.session_state:

    st.session_state.last_quality_result = None
 
 
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

    st.session_state.last_result = None

    st.session_state.last_user_input = ""

    st.session_state.last_quality_result = None

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
 
 
metric_col_1, metric_col_2, metric_col_3 = st.columns(3)
 
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
 
    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])
 
    user_input = st.chat_input("Describe the target chatbot...")
 
    if user_input:

        st.session_state.messages.append({"role": "user", "content": user_input})

        st.session_state.logs.append(f"[user] {user_input}")

        st.session_state.last_user_input = user_input
 
        with st.chat_message("user"):

            st.markdown(user_input)
 
        model_map = {

            "Qwen 2.5 7B": "qwen2.5:7b",

            "Mistral 7B": "mistral:7b",

        }
 
        if st.session_state.model == "Demo Mode":

            response = (

                "Demo Mode attiva.\n\n"

                "Seleziona **Qwen 2.5 7B** o **Mistral 7B** nella sidebar "

                "per generare JSON, completeness check e report reali."

            )

            st.session_state.logs.append("[assistant] Demo response generated")
 
        else:

            ollama_model = model_map.get(st.session_state.model, "qwen2.5:7b")
 
            with st.spinner("Virtual Hacker sta generando JSON, quality check e report..."):

                result = run_virtual_hacker_analysis(

                    natural_description=user_input,

                    model_name=ollama_model,

                )
 
            st.session_state.last_result = result

            st.session_state.last_quality_result = result.get("quality_result")
 
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
 
                quality_status = result.get("quality_result", {}).get(

                    "quality_status", "unknown"

                )

                st.session_state.logs.append(

                    f"[system] JSON quality check: {quality_status}"

                )

                st.session_state.logs.append(

                    "[assistant] JSON, quality check and report generated"

                )
 
            else:

                response = (

                    "Errore durante l'analisi.\n\n"

                    f"```text\n{result.get('error')}\n```"

                )
 
                quality_result = result.get("quality_result")
 
                if quality_result:

                    response += "\n\n"

                    response += build_quality_markdown(quality_result)
 
                st.session_state.logs.append("[assistant] Backend error")
 
        st.session_state.messages.append({"role": "assistant", "content": response})
 
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
 
    st.markdown("### Latest JSON Quality")

    render_quality_panel(st.session_state.last_quality_result)
 
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

        st.toast("Report generation is already connected to the chat workflow.")
 
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
 