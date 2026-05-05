CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        --bg: #050b14;
        --bg-soft: #091120;
        --panel: rgba(8, 15, 27, 0.82);
        --panel-strong: rgba(8, 14, 24, 0.96);
        --panel-soft: rgba(13, 22, 38, 0.72);
        --line: rgba(148, 163, 184, 0.16);
        --line-strong: rgba(103, 232, 249, 0.24);
        --text: #edf4ff;
        --muted: #97a6bb;
        --accent: #67e8f9;
        --accent-2: #86efac;
        --warn: #fbbf24;
        --danger: #fb7185;
        --shadow: 0 22px 52px rgba(0, 0, 0, 0.22);
    }

    .stApp {
        background:
            radial-gradient(circle at 22% 12%, rgba(103, 232, 249, 0.10), transparent 24%),
            linear-gradient(135deg, #030712 0%, #07101d 48%, #02050b 100%);
        color: var(--text);
        font-family: 'Inter', sans-serif;
    }

    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        background-image: linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px);
        background-size: 58px 58px;
        mask-image: linear-gradient(to bottom, rgba(0,0,0,0.85), transparent 88%);
        opacity: 0.18;
    }

    [data-testid="stDecoration"] {
        display: none;
    }

    section.main > div {
        padding-top: 0.9rem;
        padding-bottom: 1.7rem;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(4, 9, 18, 0.99), rgba(5, 11, 21, 0.98));
        border-right: 1px solid rgba(148, 163, 184, 0.13);
        box-shadow: inset -1px 0 0 rgba(255, 255, 255, 0.03);
    }

    [data-testid="stSidebar"] * {
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stSidebar"] .material-icons,
    [data-testid="stSidebar"] .material-icons-round,
    [data-testid="stSidebar"] .material-symbols-rounded,
    [data-testid="stSidebar"] .material-symbols-outlined,
    [data-testid="stSidebar"] [data-testid="stIconMaterial"] {
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
        font-weight: normal !important;
        font-style: normal !important;
        line-height: 1 !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        white-space: nowrap !important;
        word-wrap: normal !important;
        direction: ltr !important;
        -webkit-font-feature-settings: 'liga' !important;
        -webkit-font-smoothing: antialiased !important;
        font-feature-settings: 'liga' !important;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 0.9rem;
        margin-bottom: 1.35rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(148, 163, 184, 0.1);
    }

    .brand-mark {
        width: 3.15rem;
        height: 3.15rem;
        border-radius: 0.85rem;
        display: grid;
        place-items: center;
        background: linear-gradient(135deg, rgba(103, 232, 249, 0.2), rgba(134, 239, 172, 0.15));
        border: 1px solid rgba(103, 232, 249, 0.28);
        box-shadow: 0 0 24px rgba(103, 232, 249, 0.13);
        font-size: 1.28rem;
    }

    .brand-copy h1 {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.2rem;
        line-height: 1.1;
        margin: 0;
        font-weight: 700;
        color: var(--text);
    }

    .brand-copy p {
        margin: 0.2rem 0 0;
        color: var(--muted);
        font-size: 0.82rem;
    }

    .hero {
        padding: 1rem 1.1rem;
        border-radius: 1.4rem;
        background:
            linear-gradient(135deg, rgba(13, 26, 44, 0.95), rgba(8, 15, 27, 0.92)),
            radial-gradient(circle at top right, rgba(103, 232, 249, 0.11), transparent 36%);
        border: 1px solid rgba(148, 163, 184, 0.13);
        box-shadow: var(--shadow);
        position: relative;
        overflow: hidden;
        margin: 0 auto 0.9rem;
        max-width: 980px;
    }

    .page-title {
        text-align: center;
        margin: 0 0 0.85rem;
    }

    .page-logo {
        display: block;
        width: min(390px, 42vw);
        height: auto;
        margin: 0 auto;
        filter: drop-shadow(0 0 18px rgba(103, 232, 249, 0.16));
    }

    .page-title h2 {
        margin: 0;
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(1.55rem, 2.4vw, 2.15rem);
        font-weight: 700;
        letter-spacing: 0;
        color: var(--text);
    }

    .page-title p {
        margin: 0.15rem 0 0;
        color: var(--muted);
        font-size: 0.88rem;
    }

    .hero::after {
        content: "";
        position: absolute;
        inset: auto -12% -70% auto;
        width: 18rem;
        height: 18rem;
        border-radius: 999px;
        background: radial-gradient(circle, rgba(110, 231, 255, 0.16), transparent 60%);
        filter: blur(10px);
    }

    .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.35rem 0.7rem;
        border-radius: 999px;
        background: rgba(103, 232, 249, 0.08);
        color: var(--accent);
        border: 1px solid rgba(103, 232, 249, 0.18);
        font-size: 0.78rem;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        font-weight: 700;
        margin-bottom: 0.9rem;
    }

    .hero h2 {
        margin: 0;
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(1.7rem, 2.8vw, 2.65rem);
        line-height: 1.02;
        letter-spacing: -0.04em;
        font-weight: 700;
        color: var(--text);
    }

    .hero p {
        margin: 0.55rem 0 0;
        max-width: 62ch;
        color: var(--muted);
        font-size: 0.95rem;
        line-height: 1.5;
    }

    .metric-row {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.55rem;
        margin: 0.4rem 0 0.8rem;
    }

    .metric-card,
    .panel-card {
        background: linear-gradient(180deg, rgba(13, 22, 38, 0.86), rgba(7, 13, 24, 0.88));
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 0.85rem;
        box-shadow: 0 14px 34px rgba(0, 0, 0, 0.18);
    }

    .metric-card {
        padding: 0.85rem 0.9rem;
        max-width: none;
        width: 100%;
        margin: 0;
        min-height: 104px;
        position: relative;
        overflow: hidden;
    }

    .metric-card::after {
        content: "";
        position: absolute;
        inset: auto -18% -36% auto;
        width: 8rem;
        height: 8rem;
        border-radius: 999px;
        background: radial-gradient(circle, rgba(103, 232, 249, 0.06), transparent 62%);
    }

    .metric-label {
        color: var(--muted);
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.5rem;
    }

    .metric-value {
        color: var(--text);
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(1.05rem, 1.3vw, 1.32rem);
        font-weight: 700;
        line-height: 1.05;
        overflow-wrap: anywhere;
    }

    .metric-subtitle {
        color: var(--muted);
        margin-top: 0.35rem;
        font-size: 0.8rem;
    }

    .status-card {
        padding: 0.85rem 0.95rem;
        border-radius: 0.85rem;
        background: linear-gradient(180deg, rgba(13, 22, 38, 0.86), rgba(7, 13, 24, 0.88));
        border: 1px solid rgba(124, 219, 138, 0.15);
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.15);
    }

    .status-card p {
        margin: 0.3rem 0;
        color: var(--text);
        font-size: 0.88rem;
    }

    .status-ok {
        color: var(--accent-2);
        font-weight: 700;
    }

    .loading-dot {
        display: inline-block;
        width: 0.72rem;
        height: 0.72rem;
        margin-right: 0.45rem;
        border-radius: 999px;
        border: 2px solid rgba(103, 232, 249, 0.24);
        border-top-color: var(--accent);
        vertical-align: -0.08rem;
        animation: loading-spin 0.85s linear infinite;
    }

    @keyframes loading-spin {
        from {
            transform: rotate(0deg);
        }

        to {
            transform: rotate(360deg);
        }
    }

    .panel-card {
        padding: 0.9rem;
        margin-bottom: 0.75rem;
        margin-left: 2rem;
    }

    .system-log-panel {
        margin-top: 0.9rem;
        margin-left: 2rem;
    }

    [data-testid="stHorizontalBlock"]:has(.chat-column) > [data-testid="column"]:nth-child(3) {
        position: fixed;
        top: 5.6rem;
        right: 2.8rem;
        width: min(22.5vw, 360px) !important;
        max-height: calc(100vh - 6.5rem);
        overflow-y: auto;
        overflow-x: hidden;
        padding: 0.25rem 0.25rem 0.8rem 0.75rem;
        border-left: 1px solid rgba(134, 239, 172, 0.10);
        background:
            linear-gradient(180deg, rgba(4, 12, 18, 0.72), rgba(5, 10, 18, 0.20));
        backdrop-filter: blur(10px);
        z-index: 20;
        scrollbar-width: thin;
        scrollbar-color: rgba(134, 239, 172, 0.28) rgba(255, 255, 255, 0.03);
    }

    [data-testid="stHorizontalBlock"]:has(.chat-column) > [data-testid="column"]:nth-child(3)::-webkit-scrollbar {
        width: 8px;
    }

    [data-testid="stHorizontalBlock"]:has(.chat-column) > [data-testid="column"]:nth-child(3)::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 999px;
    }

    [data-testid="stHorizontalBlock"]:has(.chat-column) > [data-testid="column"]:nth-child(3)::-webkit-scrollbar-thumb {
        background: rgba(134, 239, 172, 0.22);
        border-radius: 999px;
        border: 2px solid rgba(5, 10, 18, 0.94);
    }

    [data-testid="stHorizontalBlock"]:has(.chat-column) > [data-testid="column"]:nth-child(3) .panel-card,
    [data-testid="stHorizontalBlock"]:has(.chat-column) > [data-testid="column"]:nth-child(3) .system-log-panel {
        margin-left: 0;
    }

    [data-testid="stHorizontalBlock"]:has(.chat-column) > [data-testid="column"]:nth-child(3) .system-log-panel {
        margin-top: 0;
    }

    .right-rail-fixed {
        position: fixed;
        top: 5.6rem;
        right: 2.8rem;
        width: min(22.5vw, 360px);
        max-height: calc(100vh - 6.5rem);
        overflow-y: auto;
        overflow-x: hidden;
        padding: 0.25rem 0.25rem 0.8rem 0.75rem;
        border-left: 1px solid rgba(134, 239, 172, 0.10);
        background:
            linear-gradient(180deg, rgba(4, 12, 18, 0.72), rgba(5, 10, 18, 0.20));
        backdrop-filter: blur(10px);
        z-index: 20;
        scrollbar-width: thin;
        scrollbar-color: rgba(134, 239, 172, 0.28) rgba(255, 255, 255, 0.03);
    }

    .right-rail-fixed::-webkit-scrollbar {
        width: 8px;
    }

    .right-rail-fixed::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 999px;
    }

    .right-rail-fixed::-webkit-scrollbar-thumb {
        background: rgba(134, 239, 172, 0.22);
        border-radius: 999px;
        border: 2px solid rgba(5, 10, 18, 0.94);
    }

    .right-rail-fixed .panel-card,
    .right-rail-fixed .system-log-panel {
        margin-left: 0;
    }

    .right-rail-fixed .system-log-panel {
        margin-top: 0;
    }

    .rail-button {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 2.5rem;
        width: 100%;
        margin: 0 0 0.75rem;
        border-radius: 0.72rem;
        border: 1px solid rgba(148, 163, 184, 0.16);
        background: linear-gradient(180deg, rgba(13, 22, 38, 0.92), rgba(6, 12, 22, 0.98));
        color: var(--text) !important;
        text-decoration: none !important;
        font-weight: 600;
        box-shadow: 0 8px 18px rgba(0, 0, 0, 0.14);
        transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
    }

    .rail-button:hover {
        transform: translateY(-1px);
        border-color: rgba(134, 239, 172, 0.30);
        box-shadow: 0 10px 22px rgba(0, 0, 0, 0.18);
    }

    .rail-button.disabled {
        opacity: 0.48;
        pointer-events: none;
        cursor: default;
    }

    .panel-title {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.6rem;
        margin-bottom: 0.85rem;
    }

    .panel-title h3 {
        margin: 0;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.05rem;
        color: var(--text);
        font-weight: 700;
    }

    .panel-title span {
        color: var(--muted);
        font-size: 0.8rem;
    }

    .log-box {
        background: linear-gradient(180deg, rgba(2, 7, 14, 0.98), rgba(5, 10, 18, 0.94));
        border: 1px solid rgba(103, 232, 249, 0.14);
        border-radius: 0.75rem;
        padding: 1.05rem 1.1rem;
        font-family: 'JetBrains Mono', monospace;
        color: #b4f1d0;
        max-height: 285px;
        overflow-y: auto;
        overflow-x: hidden;
        white-space: pre-wrap;
        line-height: 1.68;
        font-size: 0.98rem;
        font-weight: 500;
    }

    .log-box::-webkit-scrollbar {
        width: 10px;
    }

    .log-box::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 999px;
    }

    .log-box::-webkit-scrollbar-thumb {
        background: rgba(103, 232, 249, 0.22);
        border-radius: 999px;
        border: 2px solid rgba(5, 10, 18, 0.94);
    }

    .log-box::-webkit-scrollbar-thumb:hover {
        background: rgba(103, 232, 249, 0.34);
    }

    .chat-shell {
        background: linear-gradient(180deg, rgba(8, 15, 27, 0.96), rgba(6, 12, 22, 0.95));
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 0.95rem;
        padding: 1rem;
        box-shadow: var(--shadow);
    }

    .chat-column {
        max-width: 900px;
        margin: 0 auto;
    }

    .chat-scroll {
        max-height: calc(100vh - 330px);
        overflow-y: auto;
        overflow-x: hidden;
        padding-right: 0.4rem;
        margin-right: -0.15rem;
        scrollbar-width: thin;
        scrollbar-color: rgba(103, 232, 249, 0.28) rgba(255, 255, 255, 0.03);
    }

    .chat-scroll::-webkit-scrollbar {
        width: 10px;
    }

    .chat-scroll::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 999px;
    }

    .chat-scroll::-webkit-scrollbar-thumb {
        background: rgba(103, 232, 249, 0.22);
        border-radius: 999px;
        border: 2px solid rgba(5, 10, 18, 0.94);
    }

    .chat-scroll::-webkit-scrollbar-thumb:hover {
        background: rgba(103, 232, 249, 0.34);
    }

    [data-testid="stChatMessage"] {
        background: rgba(13, 22, 38, 0.64);
        border: 1px solid rgba(148, 163, 184, 0.13);
        border-radius: 0.75rem;
        padding: 0.9rem 1rem;
        margin-bottom: 0.72rem;
        backdrop-filter: blur(8px);
    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
        font-size: 1.08rem;
        line-height: 1.68;
    }

    [data-testid="stChatMessage"] p {
        font-size: 1.08rem;
        line-height: 1.68;
        margin-bottom: 0.35rem;
    }

    [data-testid="stChatMessage"] strong {
        color: var(--text);
        font-weight: 800;
    }

    [data-testid="stChatInput"] {
        margin-top: 0.85rem;
    }

    .stChatInput textarea {
        background: rgba(2, 7, 14, 0.96) !important;
        color: var(--text) !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 0.8rem !important;
        font-size: 1rem !important;
        line-height: 1.5 !important;
        min-height: 3.2rem !important;
        padding: 0.78rem 3.1rem 0.78rem 1rem !important;
    }

    .stTextInput input,
    .stSelectbox div[data-baseweb="select"] {
        background: rgba(2, 7, 14, 0.95) !important;
        color: var(--text) !important;
        border-color: rgba(148, 163, 184, 0.16) !important;
    }

    .stButton button {
        border-radius: 0.72rem;
        border: 1px solid rgba(148, 163, 184, 0.16);
        background: linear-gradient(180deg, rgba(13, 22, 38, 0.92), rgba(6, 12, 22, 0.98));
        color: var(--text);
        transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease;
        box-shadow: 0 8px 18px rgba(0, 0, 0, 0.14);
    }

    .stButton button:hover {
        transform: translateY(-1px);
        border-color: rgba(103, 232, 249, 0.28);
        box-shadow: 0 10px 22px rgba(0, 0, 0, 0.18);
    }

    .stButton button:focus-visible {
        outline: 2px solid rgba(103, 232, 249, 0.35);
        outline-offset: 2px;
    }

    .stInfo {
        border-radius: 0.8rem;
        background: rgba(103, 232, 249, 0.08);
        border: 1px solid rgba(103, 232, 249, 0.16);
        color: var(--text);
    }

    [data-testid="stSelectbox"] label,
    [data-testid="stTextInput"] label {
        color: var(--muted) !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
    }

    .status-dot {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        color: var(--accent-2);
        font-weight: 700;
        font-size: 0.85rem;
    }

    .status-dot::before {
        content: "";
        width: 0.55rem;
        height: 0.55rem;
        border-radius: 999px;
        background: var(--accent-2);
        box-shadow: 0 0 12px rgba(124, 219, 138, 0.65);
    }

    .quick-actions {
        display: grid;
        gap: 0.55rem;
    }

    .hint {
        color: var(--muted);
        font-size: 0.86rem;
        line-height: 1.55;
    }

    .footer {
        color: var(--muted);
        font-size: 0.78rem;
        text-align: center;
        padding: 0.6rem 0 0.15rem;
        opacity: 0.9;
    }

    @media (max-width: 1100px) {
        .metric-row {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }

        .metric-card {
            width: 100%;
        }

        .right-rail-fixed {
            position: static;
            width: auto;
            max-height: none;
            overflow: visible;
            padding: 0;
            border-left: 0;
            background: transparent;
            backdrop-filter: none;
        }

        [data-testid="stHorizontalBlock"]:has(.chat-column) > [data-testid="column"]:nth-child(3) {
            position: static;
            width: auto !important;
            max-height: none;
            overflow: visible;
            padding: 0;
            border-left: 0;
            background: transparent;
            backdrop-filter: none;
        }
    }

    @media (max-width: 768px) {
        .metric-row {
            grid-template-columns: 1fr;
        }

        .right-rail-fixed {
            position: static;
            max-height: none;
            overflow: visible;
            padding: 0;
            border-left: 0;
            background: transparent;
        }

        [data-testid="stHorizontalBlock"]:has(.chat-column) > [data-testid="column"]:nth-child(3) {
            position: static;
            width: auto !important;
            max-height: none;
            overflow: visible;
            padding: 0;
            border-left: 0;
            background: transparent;
        }

        .right-rail-fixed .panel-card,
        .right-rail-fixed .system-log-panel,
        [data-testid="stHorizontalBlock"]:has(.chat-column) > [data-testid="column"]:nth-child(3) .panel-card,
        [data-testid="stHorizontalBlock"]:has(.chat-column) > [data-testid="column"]:nth-child(3) .system-log-panel {
            margin-left: 0;
        }

        .chat-scroll {
            max-height: calc(100vh - 360px);
        }

        .hero h2 {
            font-size: 2rem;
        }

        .chat-column {
            max-width: 100%;
        }
    }
</style>
"""
