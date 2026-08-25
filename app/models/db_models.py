from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base
import datetime

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    chunk_count = Column(Integer, default=0)

class Clause(Base):
    __tablename__ = "clauses"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, nullable=False)
    clause_type = Column(String)   # e.g. "termination", "payment", "liability"
    content = Column(Text)
    risk_level = Column(String, default="unrated")  # low / medium / high