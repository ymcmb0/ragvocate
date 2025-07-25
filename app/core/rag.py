# app/core/rag.py
import os
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from app.core.embedding_loader import load_vectorstore


def setup_qa_chain():
    llm = ChatOpenAI(
    model="gpt-3.5-turbo",  # or "gpt-4" if you have access
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")  # Reads from your .env
    )

    vectorstores = {
        "statutes": load_vectorstore("statutes"),
        "precedents": load_vectorstore("precedents"),
    }

    retrievers = {
        name: vs.as_retriever(search_kwargs={"k": 4})
        for name, vs in vectorstores.items()
    }

    qa_chains = {
        name: RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
        for name, retriever in retrievers.items()
    }

    return qa_chains
