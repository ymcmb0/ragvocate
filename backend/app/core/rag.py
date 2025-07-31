# app/core/rag.py
import os

from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

from app.core.embedding_loader import load_vectorstore
from app.core.langgraph_basic import build_graph
from app.core.langgraph_report_agent import build_immigration_graph


def setup_langgraph():
    retriever = load_vectorstore("statutes").as_retriever()
    return build_graph(retriever)


def setup_report_graph():
    retriever = load_vectorstore("statutes").as_retriever()
    return build_immigration_graph(retriever)


def setup_qa_chain():
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",  # or "gpt-4" if you have access
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY"),  # Reads from your .env
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
