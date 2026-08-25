# Legal Intelligence Platform (AI-234)

An AI-powered platform that lets users upload legal documents (contracts, NDAs, service agreements), analyze clause risks, and ask natural-language questions about their content. The system retrieves relevant clauses and generates accurate, source-attributed answers using Retrieval-Augmented Generation (RAG).


## Features Implemented

- **Document Processing & Storage** — Accepts PDF, DOCX, and TXT files, splits them into semantic chunks, and stores metadata in PostgreSQL.
- **Vector Embeddings & Semantic Search** — Uses HuggingFace sentence embeddings (`all-mpnet-base-v2`) with a FAISS vector index for fast similarity search.
- **AI Legal Copilot** — A RAG pipeline that answers natural-language questions about uploaded documents with exact source attribution.
- **Clause Extraction & Risk Breakdown** — Analyzes contract clauses (Payment, Termination, Liability, etc.) and tags risk levels (High, Medium, Low, Unrated).
- **Executive Dashboard UI** — Interactive Streamlit frontend to view uploaded documents, explore risk breakdowns, and chat with the AI Copilot.
- **Containerized Infrastructure** — PostgreSQL, Neo4j, and Redis run via Docker Compose.


## Tech Stack

| Layer | Technology |
|---|---|
| Frontend Dashboard | Streamlit |
| Backend Framework | FastAPI |
| LLM Orchestration | LangChain (LCEL) |
| LLM Provider | OpenRouter (`openai/gpt-oss-20b:free`) |
| Embeddings | HuggingFace Sentence Transformers |
| Vector Store | FAISS |
| Relational DB | PostgreSQL |
| Graph DB | Neo4j (provisioned) |
| Cache | Redis (provisioned) |
| Containerization | Docker Compose |


## Architecture

                  ┌──────────────────────┐
                  │  Streamlit Dashboard  │
                  └──────────┬───────────┘
                             │
                    HTTP API Requests
                             │
                             ▼
                  ┌──────────────────────┐
Upload File ────> │      FastAPI App      │
                  └──────────┬───────────┘
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
  │  Document     │  │  FAISS Vector │  │  PostgreSQL   │
  │  Chunking     │  │  Index        │  │  (metadata &  │
  │  (LangChain)  │  └───────┬───────┘  │  clauses)     │
  └───────────────┘          │          └───────────────┘
                             │
Ask Question ────────────────┤
                             ▼
                     ┌───────────────┐
                     │  RAG Chain    │
                     │  (Retriever   │
                     │   + LLM)      │
                     └───────┬───────┘
                             ▼
                     Answer + Sources
```

## Project Structure

`ai234-legal-platform/
├── app/
│   ├── main.py                 # FastAPI backend entry point
│   ├── config.py               # Environment settings
│   ├── database.py             # PostgreSQL session & engine setup
│   ├── api/v1/
│   │   └── documents.py        # Upload, clause, & Ask endpoints
│   ├── core/
│   │   ├── embeddings.py       # Document loading & chunking
│   │   ├── vector_store.py     # FAISS index management
│   │   └── rag.py              # RAG chain logic
│   └── models/
│       └── db_models.py        # Database models
├── dashboard.py                # Streamlit Executive Dashboard UI
├── docker-compose.yml          # Postgres, Neo4j, Redis setup
├── Procfile                    # Deployment configuration
├── requirements.txt            # Python dependencies
└── .env                        # Environment variables (not committed)
```

---

## Setup & Running Locally

### Prerequisites

Python 3.12, Docker Desktop, and an OpenRouter API key.

### 1. Clone & Setup Virtual Environment

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure `.env` File

```
DATABASE_URL=postgresql://legaluser:legalpass@localhost:5432/legaldb
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=legalpass
REDIS_URL=redis://localhost:6379/0
OPENROUTER_API_KEY=your_openrouter_api_key
```

### 3. Start Database Containers

```powershell
docker compose up -d
```

### 4. Run FastAPI Backend

```powershell
uvicorn app.main:app --reload
```

### 5. Run Streamlit Dashboard (in a separate terminal)

```powershell
python -m streamlit run dashboard.py
```

---

## Key API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/documents` | Retrieve all uploaded document records |
| POST | `/api/v1/documents/upload` | Upload document, parse chunks, generate vector embeddings |
| GET | `/api/v1/documents/{id}/clauses` | Retrieve extracted clauses and risk ratings for a document |
| POST | `/api/v1/documents/ask` | Query document content via RAG pipeline with cited sources |

---

## Example Usage

**Upload:**

POST /api/v1/documents/upload
→ { "message": "Indexed contract.txt – 12 chunks added", "document_id": 1 }
```

**Ask:**


POST /api/v1/documents/ask?question=What are the payment terms in this agreement?
→ {
    "answer": "Total fee: USD 180,000, payable in monthly installments of USD 15,000...",
    "sources": ["uploads/contract.txt", ...]
  }
```

---

## Future Roadmap

- **Knowledge Graph Integration** — Populate Neo4j with relationships between contracts, signing parties, and obligations.
- **Compliance Policy Engine** — Automated compliance scoring against corporate internal policies.
- **Obligation Deadline Tracker** — Automated reminder triggers for contract renewals and expiration dates.

---

## Notes

- The vector index (FAISS) is cumulative across uploads within a session — all uploaded documents are searchable together via the Ask endpoint.
- Neo4j and Redis containers are provisioned via Docker Compose and available for future integration.