

# Legal Intelligence Platform (AI-234)

**Live Demo:** [ai234-legal-platform-hfgsnksfindw4uqltfhayb.streamlit.app](https://ai234-legal-platform-hfgsnksfindw4uqltfhayb.streamlit.app) *(live only while the developer's local backend + tunnel are running — see [Deployment](#deployment))*

An AI-powered platform that lets users upload legal documents (contracts, NDAs, service agreements), analyze clause risks, and ask natural-language questions about their content. The system retrieves relevant clauses and generates accurate, source-attributed answers using Retrieval-Augmented Generation (RAG).


## Features Implemented

- **Document Processing & Storage** — Accepts PDF, DOCX, and TXT files, splits them into semantic chunks, and stores metadata in PostgreSQL.
- **Vector Embeddings & Semantic Search** — Uses HuggingFace sentence embeddings (`all-mpnet-base-v2`) with a FAISS vector index for fast similarity search.
- **AI Legal Copilot** — A RAG pipeline that answers natural-language questions about uploaded documents with exact source attribution.
- **Clause Extraction & Risk Breakdown** — Analyzes contract clauses (Payment, Termination, Liability, etc.) and tags risk levels (High, Medium, Low, Unrated).
- **Executive Dashboard UI** — Interactive Streamlit frontend to view uploaded documents, explore risk breakdowns, and chat with the AI Copilot.
- **Knowledge Graph** — Documents and clauses are linked in Neo4j so relationships between them can be queried.
- **Answer Caching** — Repeated questions are served from Redis instead of re-running the RAG pipeline.
- **Cloud-Hosted Infrastructure** — PostgreSQL, Neo4j, and Redis run as managed cloud services; no local containers or Docker required.


## Tech Stack

| Layer | Technology |
|---|---|
| Frontend Dashboard | Streamlit |
| Backend Framework | FastAPI |
| LLM Orchestration | LangChain (LCEL) |
| LLM Provider | OpenRouter (`openai/gpt-oss-20b:free`) |
| Embeddings | HuggingFace Sentence Transformers |
| Vector Store | FAISS |
| Relational DB | PostgreSQL (cloud-hosted, e.g. Neon) |
| Graph DB | Neo4j (cloud-hosted, e.g. Aura) |
| Cache | Redis (cloud-hosted, e.g. Upstash) |


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
     ┌───────────────┬───────┼───────┬──────────────────┐
     ▼                ▼               ▼                  ▼
┌───────────┐  ┌──────────────┐  ┌───────────┐  ┌────────────────┐
│ Document  │  │ FAISS Vector │  │PostgreSQL │  │ Neo4j Knowledge│
│ Chunking  │  │ Index        │  │(metadata &│  │ Graph          │
│(LangChain)│  └──────┬───────┘  │ clauses)  │  └────────────────┘
└───────────┘         │          └───────────┘
                       │
Ask Question ──────────┤                        ┌───────────┐
                       ▼                         │  Redis    │
               ┌───────────────┐                 │  Cache    │
               │  RAG Chain    │ <───────────────┤(answers)  │
               │  (Retriever   │                 └───────────┘
               │   + LLM)      │
               └───────┬───────┘
                       ▼
               Answer + Sources


All three data stores (PostgreSQL, Neo4j, Redis) are managed cloud services — nothing runs locally except the FastAPI app and the Streamlit dashboard.

## Project Structure


ai234-legal-platform/
├── app/
│   ├── main.py                 # FastAPI backend entry point
│   ├── config.py                # Environment settings
│   ├── database.py              # PostgreSQL session & engine setup
│   ├── cache.py                 # Redis-backed answer caching
│   ├── api/v1/
│   │   └── documents.py         # Upload, clause, ask, & graph endpoints
│   ├── core/
│   │   ├── embeddings.py        # Document loading & chunking
│   │   ├── vector_store.py      # FAISS index management
│   │   ├── rag.py               # RAG chain logic
│   │   ├── clause_extractor.py  # Clause extraction from document text
│   │   └── risk_analyzer.py     # Clause risk scoring
│   ├── graph/
│   │   └── neo4j_client.py      # Neo4j knowledge graph read/write
│   └── models/
│       └── db_models.py         # Database models
├── dashboard.py                 # Streamlit Executive Dashboard UI
├── Procfile                     # Deployment configuration
├── requirements.txt             # Python dependencies
└── .env                         # Environment variables (not committed)



## Setup & Running Locally

### Prerequisites

Python 3.12, an OpenRouter API key, and accounts/connection strings for a cloud PostgreSQL, Neo4j, and Redis instance (e.g. Neon, Aura, Upstash — free tiers work fine). Docker is **not** required.

### 1. Clone & Setup Virtual Environment

powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

### 2. Configure `.env` File

Point each variable at your cloud-hosted instance's connection details:


DATABASE_URL=postgresql://<user>:<password>@<neon-host>/<db>?sslmode=require
NEO4J_URI=neo4j+s://<your-aura-instance>.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=<your-aura-password>
REDIS_URL=<your-upstash-redis-url>
OPENROUTER_API_KEY=your_openrouter_api_key


### 3. Run FastAPI Backend

powershell
uvicorn app.main:app --reload


Since PostgreSQL, Neo4j, and Redis are all cloud-hosted, there's no local database step to run first.

### 4. Run Streamlit Dashboard (in a separate terminal)

```powershell
python -m streamlit run dashboard.py
```

---

## Deployment

The dashboard is deployed on **Streamlit Community Cloud**. The FastAPI backend runs locally (on the developer's machine) and is exposed to the deployed frontend through a **Cloudflare Tunnel**. PostgreSQL, Neo4j, and Redis are already cloud-hosted, so only the FastAPI app itself needs tunneling.

### How it's wired up

```
Streamlit Cloud (dashboard.py)  ──HTTPS──>  Cloudflare Tunnel  ──>  localhost:8000 (FastAPI, local machine)  ──>  Cloud PostgreSQL / Neo4j / Redis
```

`dashboard.py` reads the backend location from an environment variable:

```python
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
```

### Steps to deploy / re-deploy

1. **Start the backend locally:**
```powershell
   venv\Scripts\activate
   uvicorn app.main:app --reload
```

2. **Start a Cloudflare Tunnel** pointing at the local backend:
```powershell
   & "C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --url http://localhost:8000
```
   This prints a public URL like `https://<random-words>.trycloudflare.com`. Copy it.

3. **Set the Streamlit secret.** In the Streamlit Cloud app settings → **Secrets**, set:
```toml
   BACKEND_URL = "https://<random-words>.trycloudflare.com"
```
   (No trailing path — `dashboard.py` appends `/api/v1` itself.)

4. **Reboot the app** from the Streamlit Cloud dashboard so it picks up the new secret.

### ⚠️ Known limitation

This setup only works while **both** the local `uvicorn` process and the `cloudflared` tunnel keep running on the developer's machine. If the laptop sleeps, loses network, or either terminal is closed, the tunnel URL dies and the deployed dashboard will fail to reach the backend. Since the databases are already cloud-hosted, the remaining step for a fully "always-on" deployment is moving the FastAPI backend itself to a hosted environment (e.g. Render, Railway, Fly.io) instead of tunneling from a local machine.

---

## Key API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/documents` | Retrieve all uploaded document records |
| POST | `/api/v1/documents/upload` | Upload document, parse chunks, generate vector embeddings, extract & score clauses |
| GET | `/api/v1/documents/{id}/clauses` | Retrieve extracted clauses and risk ratings for a document |
| POST | `/api/v1/documents/ask` | Query document content via RAG pipeline with cited sources (cached in Redis) |
| GET | `/api/v1/documents/{id}/graph` | Retrieve the Neo4j knowledge graph (nodes & edges) for a document |

---

## Example Usage

**Upload:**

```
POST /api/v1/documents/upload
→ {
    "message": "Indexed contract.txt - 12 chunks added",
    "document_id": 1,
    "clauses_extracted": 5,
    "clauses": [{"clause_type": "payment", "risk_level": "medium"}, ...]
  }
```

**Ask:**

```
POST /api/v1/documents/ask?question=What are the payment terms in this agreement?
→ {
    "answer": "Total fee: USD 180,000, payable in monthly installments of USD 15,000...",
    "sources": ["uploads/contract.txt", ...],
    "cached": false
  }
```

---

## Future Roadmap

- **Compliance Policy Engine** — Automated compliance scoring against corporate internal policies.
- **Obligation Deadline Tracker** — Automated reminder triggers for contract renewals and expiration dates.
- **Always-on Backend Hosting** — Move FastAPI off the local-machine + tunnel setup onto a hosted platform (Render/Railway/Fly.io) so the deployment doesn't depend on a laptop staying on.

---

## Notes

- The vector index (FAISS) is cumulative across uploads within a session — all uploaded documents are searchable together via the Ask endpoint.
- PostgreSQL, Neo4j, and Redis are managed cloud services — no Docker or local database setup is needed to run the project.
