import html

import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="InfoCite AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        color-scheme: dark;
        --canvas: #060711;
        --canvas-deep: #03040a;
        --surface: rgba(14, 16, 34, 0.88);
        --surface-strong: rgba(18, 20, 43, 0.96);
        --surface-soft: rgba(31, 27, 61, 0.58);
        --line: rgba(166, 150, 255, 0.18);
        --line-bright: rgba(176, 140, 255, 0.42);
        --text: #f6f5ff;
        --text-soft: #b8b7ce;
        --text-faint: #7e8099;
        --violet: #8b5cf6;
        --violet-bright: #a970ff;
        --cyan: #6de5ff;
        --success: #4ee5a8;
        --danger: #ff7890;
        --shadow: 0 24px 70px rgba(0, 0, 0, 0.38);
        --glow: 0 0 0 1px rgba(139, 92, 246, 0.08), 0 18px 55px rgba(94, 49, 185, 0.18);
        --radius-lg: 22px;
        --radius-md: 14px;
        --radius-sm: 10px;
    }

    html, body, [class*="css"] {
        font-family: "Inter", "Segoe UI", system-ui, sans-serif;
    }

    body {
        background: var(--canvas);
    }

    .stApp {
        color: var(--text);
        background:
            radial-gradient(circle at 52% -15%, rgba(104, 61, 180, 0.20), transparent 35%),
            linear-gradient(145deg, var(--canvas-deep) 0%, var(--canvas) 48%, #09081a 100%);
    }

    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        opacity: 0.26;
        background-image:
            linear-gradient(rgba(255, 255, 255, 0.018) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.018) 1px, transparent 1px);
        background-size: 42px 42px;
        mask-image: linear-gradient(to bottom, black, transparent 74%);
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stToolbar"] {
        color: var(--text-soft);
    }

    .main .block-container {
        max-width: 1180px;
        padding: 2.1rem 2.25rem 4rem;
    }

    section[data-testid="stSidebar"] {
        width: 330px !important;
        background: rgba(7, 8, 18, 0.94);
        border-right: 1px solid var(--line);
        box-shadow: 16px 0 60px rgba(0, 0, 0, 0.28);
    }

    section[data-testid="stSidebar"] > div {
        background:
            radial-gradient(circle at 10% 0%, rgba(130, 76, 228, 0.16), transparent 30%),
            transparent;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        padding: 1.25rem 1rem 2rem;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        padding: 0.45rem 0.35rem 1.25rem;
        margin-bottom: 0.85rem;
        border-bottom: 1px solid var(--line);
    }

    .brand-mark {
        display: grid;
        place-items: center;
        width: 2.55rem;
        height: 2.55rem;
        flex: 0 0 auto;
        border: 1px solid var(--line-bright);
        border-radius: 12px;
        color: var(--text);
        background: linear-gradient(145deg, rgba(151, 102, 255, 0.92), rgba(86, 44, 175, 0.92));
        box-shadow: 0 0 28px rgba(139, 92, 246, 0.32);
        font-size: 1.15rem;
        font-weight: 800;
    }

    .brand-name {
        color: var(--text);
        font-size: 1.05rem;
        font-weight: 760;
        line-height: 1.1;
    }

    .brand-tagline {
        margin-top: 0.25rem;
        color: var(--text-faint);
        font-size: 0.73rem;
    }

    .eyebrow {
        color: var(--violet-bright);
        font-size: 0.72rem;
        font-weight: 750;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    .sidebar-heading {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        margin: 0.25rem 0 0.2rem;
        color: var(--text);
        font-size: 0.94rem;
        font-weight: 720;
    }

    .sidebar-copy {
        margin: 0 0 0.95rem;
        color: var(--text-faint);
        font-size: 0.76rem;
        line-height: 1.5;
    }

    .hero {
        position: relative;
        overflow: hidden;
        min-height: 190px;
        display: flex;
        align-items: flex-end;
        padding: 2.15rem 2.25rem;
        margin-bottom: 1.55rem;
        border: 1px solid var(--line);
        border-radius: var(--radius-lg);
        background:
            linear-gradient(100deg, rgba(13, 15, 33, 0.98) 0%, rgba(18, 15, 44, 0.90) 58%, rgba(48, 24, 90, 0.82) 100%);
        box-shadow: var(--shadow), inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }

    .hero::after {
        content: "";
        position: absolute;
        top: -45%;
        right: -8%;
        width: 370px;
        height: 250px;
        transform: rotate(-14deg);
        border: 1px solid rgba(170, 123, 255, 0.22);
        border-radius: 42%;
        background: linear-gradient(145deg, rgba(115, 72, 206, 0.18), transparent 60%);
        box-shadow: 0 0 90px rgba(111, 62, 214, 0.22);
    }

    .hero-content {
        position: relative;
        z-index: 1;
        max-width: 700px;
    }

    .hero-title {
        margin: 0.45rem 0 0.55rem;
        color: var(--text);
        font-size: clamp(2rem, 4vw, 3.3rem);
        font-weight: 780;
        line-height: 1.05;
        text-shadow: 0 0 34px rgba(186, 142, 255, 0.20);
    }

    .hero-subtitle {
        margin: 0;
        color: var(--text-soft);
        font-size: 0.96rem;
        line-height: 1.6;
    }

    .section-heading {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin: 0 0 0.85rem;
    }

    .section-heading h2 {
        margin: 0;
        color: var(--text);
        font-size: 1.02rem;
        font-weight: 720;
    }

    .ready-pill, .confidence-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.42rem;
        padding: 0.38rem 0.62rem;
        border: 1px solid rgba(78, 229, 168, 0.25);
        border-radius: 999px;
        color: var(--success);
        background: rgba(78, 229, 168, 0.08);
        font-size: 0.67rem;
        font-weight: 750;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    .ready-dot {
        width: 0.42rem;
        height: 0.42rem;
        border-radius: 50%;
        background: var(--success);
        box-shadow: 0 0 12px rgba(78, 229, 168, 0.8);
    }

    .document-list {
        margin: 0.85rem 0 0;
        display: grid;
        gap: 0.55rem;
    }

    .document-row {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        min-width: 0;
        padding: 0.72rem 0.8rem;
        border: 1px solid var(--line);
        border-radius: var(--radius-sm);
        background: rgba(19, 20, 40, 0.7);
    }

    .document-icon {
        color: var(--violet-bright);
        font-size: 0.92rem;
    }

    .document-name {
        overflow: hidden;
        color: var(--text-soft);
        font-size: 0.76rem;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .status-card {
        padding: 1rem;
        margin-top: 0.8rem;
        border: 1px solid var(--line);
        border-radius: var(--radius-md);
        background: linear-gradient(145deg, rgba(22, 23, 47, 0.92), rgba(13, 14, 30, 0.96));
        box-shadow: var(--glow);
    }

    .status-title {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 0.8rem;
        margin-bottom: 0.25rem;
        border-bottom: 1px solid var(--line);
    }

    .status-title strong {
        color: var(--text);
        font-size: 0.73rem;
        letter-spacing: 0.08em;
    }

    .status-row {
        display: grid;
        grid-template-columns: minmax(78px, 0.8fr) minmax(0, 1.2fr);
        gap: 0.75rem;
        align-items: start;
        padding: 0.58rem 0;
        border-bottom: 1px solid rgba(166, 150, 255, 0.09);
    }

    .status-row:last-child {
        padding-bottom: 0;
        border-bottom: 0;
    }

    .status-label {
        color: var(--text-faint);
        font-size: 0.72rem;
    }

    .status-value {
        overflow-wrap: anywhere;
        color: var(--text-soft);
        font-size: 0.73rem;
        font-weight: 650;
        text-align: right;
    }

    .composer-shell {
        padding: 1.15rem 1.2rem 0.25rem;
        margin-bottom: 1.35rem;
        border: 1px solid var(--line-bright);
        border-radius: var(--radius-lg);
        background: linear-gradient(145deg, rgba(19, 20, 44, 0.92), rgba(10, 11, 25, 0.96));
        box-shadow: var(--glow);
    }

    .composer-label {
        margin-bottom: 0.15rem;
        color: var(--text);
        font-size: 0.84rem;
        font-weight: 680;
    }

    .composer-hint {
        color: var(--text-faint);
        font-size: 0.72rem;
    }

    div[data-testid="stTextInput"] input {
        min-height: 3.2rem;
        color: var(--text) !important;
        caret-color: var(--violet-bright);
        background: rgba(7, 8, 20, 0.86) !important;
        border: 1px solid var(--line) !important;
        border-radius: 12px !important;
        box-shadow: inset 0 1px 6px rgba(0, 0, 0, 0.26) !important;
    }

    div[data-testid="stTextInput"] input:focus {
        border-color: var(--line-bright) !important;
        box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.13) !important;
    }

    div[data-testid="stTextInput"] input::placeholder {
        color: var(--text-faint);
    }

    .stButton > button,
    .stFormSubmitButton > button {
        min-height: 2.65rem;
        border: 1px solid rgba(190, 160, 255, 0.32) !important;
        border-radius: 11px !important;
        color: var(--text) !important;
        background: linear-gradient(135deg, var(--violet-bright), #6736db) !important;
        box-shadow: 0 10px 28px rgba(101, 56, 203, 0.28) !important;
        font-weight: 720 !important;
        transition: transform 160ms ease, box-shadow 160ms ease, filter 160ms ease;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        transform: translateY(-1px);
        filter: brightness(1.08);
        box-shadow: 0 14px 34px rgba(101, 56, 203, 0.38) !important;
    }

    .stButton > button:active,
    .stFormSubmitButton > button:active {
        transform: translateY(0);
    }

    [data-testid="stFileUploader"] {
        padding: 0.2rem 0 0.45rem;
    }

    [data-testid="stFileUploaderDropzone"] {
        min-height: 116px;
        border: 1px dashed rgba(166, 150, 255, 0.32) !important;
        border-radius: var(--radius-md) !important;
        background: rgba(18, 19, 39, 0.74) !important;
        transition: border-color 160ms ease, background 160ms ease;
    }

    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: var(--line-bright) !important;
        background: rgba(29, 26, 57, 0.78) !important;
    }

    [data-testid="stFileUploaderDropzone"] button {
        border: 1px solid var(--line) !important;
        border-radius: 9px !important;
        color: var(--text-soft) !important;
        background: var(--surface-soft) !important;
    }

    [data-testid="stFileUploaderFile"] {
        border-radius: 10px;
        background: rgba(20, 21, 42, 0.72);
    }

    .answer-card {
        position: relative;
        overflow: hidden;
        padding: 1.65rem 1.75rem 1.8rem;
        margin: 0.25rem 0 1.15rem;
        border: 1px solid var(--line-bright);
        border-radius: var(--radius-lg);
        background:
            radial-gradient(circle at 100% 0%, rgba(127, 74, 220, 0.13), transparent 30%),
            linear-gradient(145deg, rgba(18, 19, 40, 0.97), rgba(9, 10, 23, 0.98));
        box-shadow: var(--shadow), var(--glow);
        animation: answer-in 320ms ease-out both;
    }

    .answer-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 1.75rem;
        width: 96px;
        height: 2px;
        background: linear-gradient(90deg, var(--violet-bright), var(--cyan));
        box-shadow: 0 0 16px rgba(139, 92, 246, 0.62);
    }

    .answer-topline {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 1rem;
    }

    .answer-title {
        color: var(--text);
        font-size: 1.08rem;
        font-weight: 740;
    }

    .answer-copy {
        color: #d9d8e8;
        font-size: 0.94rem;
        line-height: 1.78;
        white-space: pre-wrap;
    }

    .sources-header {
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
        gap: 1rem;
        margin: 1.4rem 0 0.75rem;
    }

    .sources-header h2 {
        margin: 0;
        color: var(--text);
        font-size: 1.02rem;
        font-weight: 720;
    }

    .sources-count {
        color: var(--text-faint);
        font-size: 0.72rem;
    }

    div[data-testid="stExpander"] {
        overflow: hidden;
        margin-bottom: 0.65rem;
        border: 1px solid var(--line) !important;
        border-radius: var(--radius-md) !important;
        background: rgba(14, 15, 31, 0.86) !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    }

    div[data-testid="stExpander"] details summary {
        color: var(--text-soft) !important;
        font-size: 0.84rem;
        font-weight: 620;
    }

    div[data-testid="stExpander"] details[open] {
        background: rgba(22, 20, 45, 0.62);
    }

    div[data-testid="stExpander"] details[open] summary {
        border-bottom: 1px solid var(--line);
    }

    .evidence-label {
        display: inline-block;
        margin: 0.35rem 0 0.6rem;
        color: var(--violet-bright);
        font-size: 0.7rem;
        font-weight: 750;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .empty-state {
        display: grid;
        place-items: center;
        min-height: 265px;
        padding: 2rem;
        border: 1px solid var(--line);
        border-radius: var(--radius-lg);
        color: var(--text-faint);
        background: rgba(10, 11, 24, 0.58);
        text-align: center;
    }

    .empty-icon {
        width: 3rem;
        height: 3rem;
        display: grid;
        place-items: center;
        margin: 0 auto 0.9rem;
        border: 1px solid var(--line);
        border-radius: 14px;
        color: var(--violet-bright);
        background: var(--surface-soft);
        box-shadow: 0 0 30px rgba(139, 92, 246, 0.12);
        font-size: 1.2rem;
    }

    .empty-title {
        margin-bottom: 0.35rem;
        color: var(--text-soft);
        font-size: 0.9rem;
        font-weight: 650;
    }

    .empty-copy {
        max-width: 330px;
        font-size: 0.76rem;
        line-height: 1.55;
    }

    [data-testid="stAlert"] {
        border: 1px solid var(--line);
        border-radius: 12px;
        background: var(--surface-strong);
    }

    hr {
        border-color: var(--line) !important;
    }

    @keyframes answer-in {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @media (max-width: 900px) {
        .main .block-container {
            padding: 1.25rem 1rem 3rem;
        }

        .hero {
            min-height: 160px;
            padding: 1.5rem;
        }

        .hero-title {
            font-size: 2rem;
        }
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            scroll-behavior: auto !important;
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Session State
# ----------------------------

if "indexed" not in st.session_state:
    st.session_state.indexed = False

if "documents" not in st.session_state:
    st.session_state.documents = []

if "index_stats" not in st.session_state:
    st.session_state.index_stats = {}

if "last_result" not in st.session_state:
    st.session_state.last_result = None

# ----------------------------
# Sidebar: documents and index status
# ----------------------------

with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-mark">IC</div>
            <div>
                <div class="brand-name">InfoCite AI</div>
                <div class="brand-tagline">Document intelligence</div>
            </div>
        </div>
        <div class="eyebrow">Knowledge workspace</div>
        <div class="sidebar-heading"><span>▤</span> Documents</div>
        <p class="sidebar-copy">Add up to three PDF files, then index them to begin your research.</p>
        """,
        unsafe_allow_html=True,
    )

    uploaded_files = st.file_uploader(
        "Upload PDF documents",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload up to 3 PDFs to index and query. Maximum 200 MB per file.",
        label_visibility="collapsed",
    )

    if st.button("Index documents", use_container_width=True):
        if not uploaded_files:
            st.warning("Please upload at least one PDF.")
        elif len(uploaded_files) > 3:
            st.error("Maximum of 3 PDFs allowed.")
        else:
            with st.spinner("Indexing documents..."):
                files = [
                    (
                        "files",
                        (
                            file.name,
                            file.getvalue(),
                            "application/pdf",
                        ),
                    )
                    for file in uploaded_files
                ]

                try:
                    response = requests.post(
                        f"{API_URL}/upload",
                        files=files,
                        timeout=15,
                    )
                except requests.exceptions.RequestException as exc:
                    st.error(
                        "Unable to connect to the API backend. Please make sure the server is running on http://127.0.0.1:8000."
                    )
                    st.write(f"Error: {exc}")
                    response = None

            if response is not None and response.status_code == 200:
                data = response.json()
                st.session_state.indexed = True
                st.session_state.documents = data["documents"]
                st.session_state.index_stats = data["index_stats"]
                st.session_state.last_result = None
                st.success(data["message"])
            elif response is not None:
                st.error(response.json().get("detail", "Indexing failed."))

    if st.session_state.documents:
        document_rows = "".join(
            f"""
            <div class="document-row">
                <span class="document-icon">▧</span>
                <span class="document-name" title="{html.escape(str(document))}">{html.escape(str(document))}</span>
            </div>
            """
            for document in st.session_state.documents
        )
        st.markdown(
            f"""
            <div style="margin-top: 1.3rem;">
                <div class="section-heading"><h2>Indexed documents</h2></div>
                <div class="document-list">{document_rows}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.session_state.index_stats:
        stats = st.session_state.index_stats
        status_rows = [
            ("Documents", stats.get("documents", "—")),
            ("Chunks", stats.get("chunks", "—")),
            ("Retriever", stats.get("retriever", "—")),
            ("Embeddings", stats.get("embeddings", "—")),
            ("LLM", stats.get("llm", "—")),
        ]
        rows_html = "".join(
            f"""
            <div class="status-row">
                <span class="status-label">{html.escape(str(label))}</span>
                <span class="status-value">{html.escape(str(value))}</span>
            </div>
            """
            for label, value in status_rows
        )
        st.markdown(
            f"""
            <div style="margin-top: 1.35rem;">
                <div class="section-heading"><h2>Index status</h2></div>
                <div class="status-card">
                    <div class="status-title">
                        <strong>INDEX READY</strong>
                        <span class="ready-pill"><span class="ready-dot"></span>Online</span>
                    </div>
                    {rows_html}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ----------------------------
# Main workspace: ask, answer, sources
# ----------------------------

st.markdown(
    """
    <div class="hero">
        <div class="hero-content">
            <div class="eyebrow">Cited answers from your files</div>
            <h1 class="hero-title">Research with clarity.</h1>
            <p class="hero-subtitle">Ask your documents a question and get a focused answer backed by page-level evidence.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="composer-shell">
        <div class="composer-label">Ask a question</div>
        <div class="composer-hint">Search across your indexed PDFs</div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("question_form", clear_on_submit=False):
    question = st.text_input(
        "Question",
        key="question_input",
        placeholder="What would you like to know from these documents?",
        label_visibility="collapsed",
    )
    ask_submitted = st.form_submit_button("Ask InfoCite", use_container_width=True)

if ask_submitted:
    if not st.session_state.indexed:
        st.warning("Please upload and index documents first.")
    elif not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Reviewing your documents..."):
            try:
                response = requests.post(
                    f"{API_URL}/ask",
                    json={"question": question},
                    timeout=15,
                )
            except requests.exceptions.RequestException as exc:
                st.error(
                    "Unable to connect to the API backend. Please make sure the server is running on http://127.0.0.1:8000."
                )
                st.write(f"Error: {exc}")
                response = None

        if response is not None and response.status_code == 200:
            st.session_state.last_result = response.json()
        elif response is not None:
            st.error(response.json().get("detail", "Unable to get an answer."))

result = st.session_state.last_result

if result:
    answer = html.escape(str(result.get("answer", "")))
    evidence = result.get("evidence", [])
    sources = result.get("sources", [])
    source_count = len(sources) if sources else len(evidence)

    st.markdown(
        f"""
        <div class="answer-card">
            <div class="answer-topline">
                <div class="answer-title">Answer</div>
            </div>
            <div class="answer-copy">{answer}</div>
        </div>
        <div class="sources-header">
            <h2>Sources</h2>
            <span class="sources-count">{source_count} cited source{'s' if source_count != 1 else ''}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for item in evidence:
        source = str(item.get("source", "Unknown document"))
        page = item.get("page")
        text = str(item.get("text", ""))
        page_label = f"Page {page}" if page is not None else "Page unavailable"

        with st.expander(f"▧  {source}  —  {page_label}"):
            st.markdown(
                '<span class="evidence-label">Retrieved evidence</span>',
                unsafe_allow_html=True,
            )
            st.write(text)
else:
    state_title = "Your answer will appear here"
    state_copy = (
        "Index your PDFs from the document panel, then ask a question to see a cited response."
        if not st.session_state.indexed
        else "Your document index is ready. Ask a question to begin."
    )
    st.markdown(
        f"""
        <div class="empty-state">
            <div>
                <div class="empty-icon">✦</div>
                <div class="empty-title">{state_title}</div>
                <div class="empty-copy">{state_copy}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
