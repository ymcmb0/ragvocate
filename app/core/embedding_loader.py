from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import os
load_dotenv()
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
statutes_vectorstore_path = os.getenv("STATUTES_VECTORSTORE")
precedents_vectorstore_path = os.getenv("PRECEDENTS_VECTORSTORE")   
vectorstore_paths = {
    "statutes": statutes_vectorstore_path,
    "precedents": precedents_vectorstore_path
}

def load_vectorstore(name):
        path = vectorstore_paths[name]
        if not os.path.exists(f"{path}/index.faiss"):
            raise FileNotFoundError(f"Vectorstore for {name} not found.")
        return FAISS.load_local(path, embeddings=embedding_model, allow_dangerous_deserialization=True)
