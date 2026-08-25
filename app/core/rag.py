from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from app.config import settings

llm = ChatOpenAI(
    model="openrouter/free",
    temperature=0,
    openai_api_key=settings.openrouter_api_key,
    openai_api_base="https://openrouter.ai/api/v1"
)

template = """Use the following context to answer the question.
If you don't know, say you don't know.

{context}

Question: {question}
Answer:"""

def ask_question(index, query: str):
    retriever = index.as_retriever(search_kwargs={"k": 4})

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | PromptTemplate.from_template(template)
        | llm
        | StrOutputParser()
    )

    answer = rag_chain.invoke(query)
    docs = retriever.invoke(query)
    sources = [doc.metadata.get("source", "") for doc in docs]
    return {"answer": answer, "sources": sources}