import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma   # <-- we are using Chroma now

load_dotenv()

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

statutes_vectorstore_path   = os.getenv("STATUTES_VECTORSTORE")
precedents_vectorstore_path = os.getenv("PRECEDENTS_VECTORSTORE")

vectorstore_paths = {
    "statutes": statutes_vectorstore_path,
    "precedents": precedents_vectorstore_path,
}

def load_vectorstore(name: str) -> Chroma:
    """
    Load an existing Chroma collection from disk.
    """
    path = vectorstore_paths[name]

    # Chroma stores its files directly in the folder; we just check the folder exists
    if not os.path.isdir(path):
        raise FileNotFoundError(f"Vectorstore for '{name}' not found at {path}")

    return Chroma(
        persist_directory=path,
        embedding_function=embedding_model,
        collection_name=name,      # optional but keeps things tidy
    )