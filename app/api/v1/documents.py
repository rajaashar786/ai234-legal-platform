from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
import shutil, os
from app.core.embeddings import load_and_chunk
from app.core.vector_store import get_index
from app.core.rag import ask_question
from app.core.clause_extractor import extract_clauses
from app.core.risk_analyzer import score_clause_risk
from app.database import get_db
from app.models.db_models import Document, Clause
from app.graph.neo4j_client import add_document_node, add_clause_node, get_document_graph
from app.cache import get_cached_answer, set_cached_answer

router = APIRouter()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    chunks = load_and_chunk(file_path)
    index = get_index(chunks)

    # Save document record in PostgreSQL
    doc_record = Document(filename=file.filename, chunk_count=len(chunks))
    db.add(doc_record)
    db.commit()
    db.refresh(doc_record)

    # Add document node to Neo4j knowledge graph (safely)
    try:
        add_document_node(doc_record.id, file.filename)
    except Exception as e:
        print(f"Neo4j Warning: Could not create document graph node ({e})")

    # Extract clauses and score risk
    full_text = "\n".join(c.page_content for c in chunks)
    extracted = extract_clauses(full_text)

    saved_clauses = []
    for item in extracted:
        risk = score_clause_risk(item["clause_type"], item["content"])

        clause_record = Clause(
            document_id=doc_record.id,
            clause_type=item["clause_type"],
            content=item["content"],
            risk_level=risk,
        )
        db.add(clause_record)

        # Add clause node + relationship to Neo4j (safely)
        try:
            add_clause_node(doc_record.id, item["clause_type"], risk, item["content"])
        except Exception as e:
            print(f"Neo4j Warning: Could not create clause graph node ({e})")

        saved_clauses.append({"clause_type": item["clause_type"], "risk_level": risk})

    db.commit()

    return {
        "message": f"Indexed {file.filename} - {len(chunks)} chunks added",
        "document_id": doc_record.id,
        "clauses_extracted": len(saved_clauses),
        "clauses": saved_clauses,
    }


@router.post("/documents/ask")
async def query_documents(question: str):
    cached = get_cached_answer(question)
    if cached:
        cached["cached"] = True
        return cached

    index = get_index()
    result = ask_question(index, question)
    result["cached"] = False
    set_cached_answer(question, result)
    return result


@router.get("/documents/{document_id}/clauses")
async def get_document_clauses(document_id: int, db: Session = Depends(get_db)):
    clauses = db.query(Clause).filter(Clause.document_id == document_id).all()
    return [
        {"clause_type": c.clause_type, "content": c.content, "risk_level": c.risk_level}
        for c in clauses
    ]


@router.get("/documents/{document_id}/graph")
async def get_knowledge_graph(document_id: int):
    try:
        return get_document_graph(document_id)
    except Exception as e:
        return {"error": f"Neo4j Graph query failed: {str(e)}", "nodes": [], "edges": []}


@router.get("/documents")
async def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "chunk_count": d.chunk_count,
            "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None,
        }
        for d in docs
    ]