import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from app.config import settings

llm = ChatOpenAI(
    model="openrouter/free",
    temperature=0,
    openai_api_key=settings.openrouter_api_key,
    openai_api_base="https://openrouter.ai/api/v1"
)

CLAUSE_TYPES = [
    "payment", "termination", "confidentiality", "liability",
    "force_majeure", "renewal", "governing_law", "arbitration"
]

extraction_prompt = PromptTemplate.from_template(
    """You are a legal document analyst. Read the contract text below and extract any clauses
that match these categories: payment, termination, confidentiality, liability, force_majeure,
renewal, governing_law, arbitration.

For each clause you find, respond with one JSON object per line (JSON Lines format), like this:
{{"clause_type": "payment", "content": "the exact relevant text or a tight summary of it"}}

Only include categories that are actually present in the text. Do not invent content.
Return ONLY the JSON lines, nothing else — no markdown, no explanation.

Contract text:
{text}
"""
)

def extract_clauses(full_text: str):
    """Runs the LLM over document text and returns a list of {clause_type, content} dicts."""
    chain = extraction_prompt | llm
    result = chain.invoke({"text": full_text[:6000]})  # keep prompt within token limits
    raw = result.content.strip()

    clauses = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if "clause_type" in obj and "content" in obj:
                clauses.append(obj)
        except json.JSONDecodeError:
            continue  # skip lines that aren't valid JSON

    return clauses