from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import os

embeddings = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")
INDEX_PATH = "faiss_index"

def get_index(chunks=None):
    if os.path.exists(INDEX_PATH):
        return FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    elif chunks:
        index = FAISS.from_documents(chunks, embeddings)
        index.save_local(INDEX_PATH)
        return index
    raise ValueError("No index found and no chunks provided.")