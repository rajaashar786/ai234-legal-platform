from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from app.config import settings

llm = ChatOpenAI(
    model="openrouter/free",
    temperature=0,
    openai_api_key=settings.openrouter_api_key,
    openai_api_base="https://openrouter.ai/api/v1"
)

risk_prompt = PromptTemplate.from_template(
    """You are a contract risk analyst. Rate the risk level of the following clause
for the party receiving/signing the contract. Respond with EXACTLY one word: low, medium, or high.

Clause type: {clause_type}
Clause text: {content}

Risk level:"""
)

def score_clause_risk(clause_type: str, content: str) -> str:
    """Returns 'low', 'medium', or 'high' risk rating for a single clause."""
    chain = risk_prompt | llm
    result = chain.invoke({"clause_type": clause_type, "content": content})
    answer = result.content.strip().lower()

    for level in ["low", "medium", "high"]:
        if level in answer:
            return level
    return "unrated"