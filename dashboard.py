import os
import requests
import streamlit as st


BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
API_BASE = f"{BACKEND_URL}/api/v1"

st.set_page_config(page_title="Legal Intelligence Dashboard", layout="wide")
st.title("📄 Legal Intelligence Platform — Executive Dashboard")

try:
    docs = requests.get(f"{API_BASE}/documents").json()
except Exception as e:
    st.error(f"Could not reach the API. Make sure uvicorn is running. ({e})")
    st.stop()

st.metric("Total Documents", len(docs))

if not docs:
    st.info(
        "No documents uploaded yet. Upload one via /docs, then refresh this"
        " page."
    )
    st.stop()

st.subheader("Uploaded Documents")
st.table(docs)

st.subheader("Clause Risk Breakdown")

selected_doc = st.selectbox(
    "Select a document to view its clauses",
    options=[d["id"] for d in docs],
    format_func=lambda doc_id: next(
        d["filename"] for d in docs if d["id"] == doc_id
    ),
)

clauses = requests.get(f"{API_BASE}/documents/{selected_doc}/clauses").json()

if not clauses:
    st.warning("No clauses extracted for this document yet.")
else:
    risk_colors = {"low": "🟢", "medium": "🟡", "high": "🔴", "unrated": "⚪"}
    for c in clauses:
        icon = risk_colors.get(c["risk_level"], "⚪")
        with st.expander(
            f"{icon} {c['clause_type'].replace('_', ' ').title()} —"
            f" {c['risk_level'].upper()} risk"
        ):
            st.write(c["content"])

    st.subheader("Ask the AI Copilot")
    question = st.text_input("Ask a question about your documents:")
    if st.button("Ask") and question:
        with st.spinner("Thinking..."):
            resp = requests.post(
                f"{API_BASE}/documents/ask", params={"question": question}
            ).json()
        st.write("**Answer:**", resp.get("answer", "No answer returned."))
        st.write("**Sources:**", resp.get("sources", []))