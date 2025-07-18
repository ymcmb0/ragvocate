# app/core/rag.py
import os
from langchain_community.llms import LlamaCpp
from langchain.chains import RetrievalQA
from app.core.embedding_loader import load_vectorstore

def setup_qa_chain():
    llm = LlamaCpp(
        model_path="models/tinyllama.gguf",
        n_ctx=2048,
        temperature=0.6,
        max_tokens=512,
        top_p=0.95,
        verbose=True
    )

    vectorstores = {
        "statutes": load_vectorstore("statutes"),
        "precedents": load_vectorstore("precedents")
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
