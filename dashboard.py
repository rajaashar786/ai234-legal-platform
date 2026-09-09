import os
import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
API_BASE = f"{BACKEND_URL}/api/v1"

st.set_page_config(page_title="Legal Intelligence Dashboard", layout="wide")
st.title("📄 Legal Intelligence Platform — Executive Dashboard")

# Safe API Request Helper
def fetch_json(url, method="GET", **kwargs):
    try:
        response = requests.request(method, url, timeout=15, **kwargs)
        if response.status_code == 200:
            return response.json(), None
        return None, f"Backend Error ({response.status_code}): {response.text}"
    except Exception as e:
        return None, f"Could not reach API: {str(e)}"

# Fetch Documents
docs, err = fetch_json(f"{API_BASE}/documents")
if err:
    st.error(f"Make sure uvicorn and your tunnel are running. Details: {err}")
    st.stop()

st.metric("Total Documents", len(docs))

if not docs:
    st.info("No documents uploaded yet. Upload one via /docs, then refresh this page.")
    st.stop()

st.subheader("Uploaded Documents")
st.table(docs)

st.subheader("Clause Risk Breakdown")

selected_doc = st.selectbox(
    "Select a document to view its clauses",
    options=[d["id"] for d in docs],
    format_func=lambda doc_id: next(
        (d["filename"] for d in docs if d["id"] == doc_id), f"Doc {doc_id}"
    ),
)

# Fetch Clauses
clauses, clause_err = fetch_json(f"{API_BASE}/documents/{selected_doc}/clauses")

if clause_err:
    st.error(clause_err)
elif not clauses:
    st.warning("No clauses extracted for this document yet.")
else:
    risk_colors = {"low": "🟢", "medium": "🟡", "high": "🔴", "unrated": "⚪"}
    for c in clauses:
        icon = risk_colors.get(c.get("risk_level", "unrated"), "⚪")
        with st.expander(
            f"{icon} {c.get('clause_type', 'clause').replace('_', ' ').title()} — "
            f"{c.get('risk_level', 'unrated').upper()} risk"
        ):
            st.write(c.get("content", ""))

# Ask AI Copilot Section
st.subheader("Ask the AI Copilot")
question = st.text_input("Ask a question about your documents:")

if st.button("Ask") and question:
    with st.spinner("Thinking..."):
        resp_data, ask_err = fetch_json(
            f"{API_BASE}/documents/ask", 
            method="POST", 
            params={"question": question}
        )
        
        if ask_err:
            st.error(ask_err)
        else:
            if isinstance(resp_data, dict):
                st.write("**Answer:**", resp_data.get("answer", "No answer returned."))
                sources = resp_data.get("sources", [])
                if sources:
                    st.write("**Sources:**", sources)
            else:
                st.write(resp_data)