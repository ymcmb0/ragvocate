import os
from langchain_community.llms import LlamaCpp
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.chains import StuffDocumentsChain
from langchain.chains import AnalyzeDocumentChain
from langchain.chains.retrieval_qa.base import BaseRetrievalQA

# === Initialize LLM ===
llm = LlamaCpp(
    model_path="models/tinyllama.gguf",
    n_ctx=2048,
    temperature=0.6,
    max_tokens=512,
    top_p=0.95,
    verbose=True
)

# === Embeddings ===
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# === Load FAISS vectorstores ===
vectorstore_paths = {
    "statutes": "C:/Users/RizwanNisar/PycharmProjects/ragvocate/data/processed/embeddings/statutes",
    "precedents": "C:/Users/RizwanNisar/PycharmProjects/ragvocate/data/processed/embeddings/precedents"
}

def load_vectorstore(name):
    path = vectorstore_paths[name]
    if not os.path.exists(f"{path}/index.faiss"):
        raise FileNotFoundError(f"⚠️ Vectorstore for {name} not found. Run embedding script first.")
    return FAISS.load_local(path, embeddings=embedding_model, allow_dangerous_deserialization=True)

vectorstores = {
    "statutes": load_vectorstore("statutes"),
    "precedents": load_vectorstore("precedents")
}

# === Setup retrievers ===
retrievers = {
    name: vs.as_retriever(search_kwargs={"k": 4})
    for name, vs in vectorstores.items()
}

# === Setup QA chains ===
qa_chains = {
    name: RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    for name, retriever in retrievers.items()
}

# === Start Q&A ===
print("\n🧠 RAGvocate is ready. Ask legal questions below!")
print("Choose source: (1) Statutes (2) Precedents (3) Both")

while True:
    query = input("\nAsk a legal question (or type 'exit'): ").strip()
    if query.lower() == "exit":
        print("👋 Exiting RAGvocate.")
        break
    if not query:
        print("❗ Please enter a valid question.")
        continue

    source = input("Select source [1-Statutes, 2-Precedents, 3-Both]: ").strip()
    if source == "1":
        result = qa_chains["statutes"].invoke({"query": query})
    elif source == "2":
        result = qa_chains["precedents"].invoke({"query": query})
    elif source == "3":
        result1 = qa_chains["statutes"].invoke({"query": query})
        result2 = qa_chains["precedents"].invoke({"query": query})
        # Combine results (simple concat, you can use custom logic)
        combined_answer = f"[From Statutes]\n{result1['result']}\n\n[From Precedents]\n{result2['result']}"
        result = {"result": combined_answer}
    else:
        print("❗ Invalid source choice. Try again.")
        continue

    print("\n📜 RAGvocate:\n", result["result"])
