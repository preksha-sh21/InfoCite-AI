import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="InfoCite AI",
    page_icon="📚",
    layout="wide",
)

st.markdown(
    """
    <style>
    :root { color-scheme: dark; }

    body {
        background: radial-gradient(circle at top left, #3b005d 0%, #090617 40%, #02050f 100%);
    }

    .stApp {
        background: transparent;
    }

    .css-1d391kg {
        background: transparent;
    }

    .css-18e3th9 {
        padding: 1rem 1rem 1rem 1rem;
        background: transparent;
    }

    .main .block-container {
        background: transparent;
        padding: 1.5rem 1.5rem 1.5rem 1.5rem;
    }

    .stSidebar {
        background: rgba(8, 6, 21, 0.92);
        border: 1px solid rgba(172, 110, 255, 0.16);
        box-shadow: 0 20px 80px rgba(96, 0, 148, 0.18);
        border-radius: 28px;
    }

    .stSidebar .css-1d391kg {
        padding-top: 1.5rem;
    }

    .stSidebar .stMarkdown h1,
    .stSidebar .stMarkdown h2,
    .stSidebar .stMarkdown p {
        color: #f2f0ff;
    }

    .block-container h1,
    .block-container h2,
    .block-container h3 {
        color: #f8f7ff;
    }

    .block-container p,
    .block-container span,
    .block-container label {
        color: #dcd6ff;
    }

    .hero-card {
        padding: 2rem;
        margin-bottom: 1.5rem;
        background: linear-gradient(180deg, rgba(51, 0, 95, 0.78) 0%, rgba(9, 5, 28, 0.98) 100%);
        border: 1px solid rgba(178, 95, 255, 0.25);
        border-radius: 28px;
        box-shadow: 0 30px 80px rgba(121, 56, 255, 0.14);
    }

    .hero-title {
        font-size: clamp(2.7rem, 3.2vw, 3.8rem);
        font-weight: 800;
        letter-spacing: -0.04em;
        margin-bottom: 0.5rem;
        color: #fdfcff;
        text-shadow: 0 0 30px rgba(204, 110, 255, 0.25);
    }

    .hero-subtitle {
        color: #c8b9ff;
        font-size: 1rem;
        margin-bottom: 1.7rem;
    }

    .styled-card {
        background: rgba(9, 7, 27, 0.88);
        border: 1px solid rgba(151, 83, 255, 0.18);
        border-radius: 28px;
        padding: 1.8rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 18px 60px rgba(81, 21, 156, 0.12);
        backdrop-filter: blur(14px);
    }

    .styled-card h2 {
        color: #fdfcff;
        margin-bottom: 0.75rem;
    }

    .stTextInput>div>div>input {
        background: rgba(18, 9, 47, 0.96);
        color: #f7f2ff;
        border: 1px solid rgba(178, 95, 255, 0.35);
        border-radius: 18px;
        padding: 1rem 1.15rem;
    }

    .stButton button {
        background: linear-gradient(135deg, #ae5eff 0%, #4b1fc8 100%) !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 18px 40px rgba(154, 69, 255, 0.22) !important;
        border-radius: 18px !important;
        padding: 0.95rem 1.8rem !important;
        font-weight: 700 !important;
    }

    .stButton button:hover {
        transform: translateY(-1px);
    }

    .source-item {
        background: rgba(18, 10, 49, 0.88);
        border: 1px solid rgba(107, 54, 217, 0.18);
        border-radius: 18px;
        padding: 1rem 1rem;
        margin-bottom: 0.9rem;
        color: #e5dcff;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">Welcome to InfoCite AI</div>
        <div class="hero-subtitle">Ask anything from your documents. Get answers with citations.</div>
    </div>
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

# ----------------------------
# Layout
# ----------------------------

left_col, right_col = st.columns([1, 2], gap="large")

with left_col:
    st.markdown("### 📄 Documents")

    uploaded_files = st.file_uploader(
        "Drag and drop files here\nLimit 200MB per file • PDF",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload up to 3 PDFs to index and query.",
    )

    if st.button("Index Documents"):
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
                st.success(data["message"])
            elif response is not None:
                st.error(response.json().get("detail", "Indexing failed."))

    st.markdown("---")

    if st.session_state.documents:
        st.markdown("#### Indexed Documents")
        for doc in st.session_state.documents:
            st.markdown(f"- ✅ {doc}")

with right_col:
    st.markdown("## Ask a question")
    question = st.text_input("", key="question_input")

    if st.button("Ask"):
        if not st.session_state.indexed:
            st.warning("Please upload and index documents first.")
        elif not question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Thinking..."):
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
                result = response.json()
                st.markdown(
                    "<div class='styled-card'><h2>Answer</h2><p>" 
                    + result["answer"] + "</p></div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    "<div class='styled-card'><h2>Sources</h2></div>",
                    unsafe_allow_html=True,
                )
                for source in result["sources"]:
                    st.markdown(f"<div class='source-item'>{source}</div>", unsafe_allow_html=True)
            elif response is not None:
                st.error(response.json().get("detail", "Unable to get an answer."))
