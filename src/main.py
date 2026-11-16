import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

from src.config import get_api_key  # noqa: F401  (importing src.config also loads .env)
from utils.file_readers import process_uploaded_document, UnsupportedFileError
from src.vectordb.vector_store import build_vector_index
from src.agent.agent_workflow import answer_question

st.set_page_config(page_title="PLC - Code Commissioning Auditor", page_icon="⚙️", layout="centered")
st.title("⚙️ PLC - Code Commissioning Auditor")
st.markdown("### Validates industrial automation logic and safety interlocks from uploaded PLC code, I/O lists, and safety documents.")

# Session state: remembers things between Streamlit reruns
defaults = {"vector_db": None, "chat_history": [], "file_signature": None, "index_problems": None}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---- File ingestion ----
st.sidebar.header("📁 Document Ingestion Panel")
uploaded_files = st.sidebar.file_uploader(
    "Upload industrial assets simultaneously (PDF, TXT, CSV, XLSX):",
    accept_multiple_files=True,
)

if not uploaded_files:
    st.session_state.vector_db = None
    st.session_state.chat_history = []
    st.session_state.file_signature = None
    st.session_state.index_problems = None
else:
    # Only re-parse and re-index when the set of uploaded files actually changes
    signature = tuple(sorted((f.name, f.size) for f in uploaded_files))
    if signature != st.session_state.file_signature:
        st.session_state.file_signature = signature
        st.session_state.vector_db = None
        parsed_files, problems = [], []

        for file in uploaded_files:
            try:
                if file.size == 0:
                    raise ValueError("File is empty. Please upload a valid document.")
                text = process_uploaded_document(file.getvalue(), file.name)
                parsed_files.append((file.name, text))
            except (UnsupportedFileError, ValueError) as error:
                problems.append(f"{file.name}: {error}")

        if parsed_files:
            try:
                with st.spinner("Processing documents..."):
                    st.session_state.vector_db = build_vector_index(parsed_files)
            except Exception as error:
                problems.append(f"Document processing failed: {error}")

        st.session_state.index_problems = problems or None

    for problem in st.session_state.index_problems or []:
        st.sidebar.error(f"⚠️ {problem}")
    if st.session_state.vector_db is not None:
        st.sidebar.success("✅ Audit Knowledge Base Ready!")

# ---- Chat ----
st.markdown("---")
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_query = st.chat_input("Ask about safety interlocks, missing I/O tags, or logic checks...")

if user_query:
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        sources = []
        if st.session_state.vector_db is None:
            output_text = "🔒 System Idle: please upload valid documents in the sidebar to begin the audit."
        else:
            try:
                with st.spinner("Auditing logic configurations..."):
                    output_text, sources = answer_question(st.session_state.vector_db, user_query)
            except Exception as error:
                output_text = f"💥 The AI request failed: {error}"

        st.markdown(output_text)
        if sources:
            with st.expander("📎 Sources used for this answer"):
                for doc in sources:
                    st.caption(doc.metadata.get("source", "unknown"))
                    st.code(doc.page_content, language=None)

        st.session_state.chat_history.append({"role": "assistant", "content": output_text})