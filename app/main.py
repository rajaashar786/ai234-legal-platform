from fastapi import FastAPI
from app.api.v1 import documents
from app.database import init_db

app = FastAPI(title="Legal Intelligence Platform")

@app.on_event("startup")
def startup_event():
    init_db()

app.include_router(documents.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"status": "Legal AI Platform is running"}