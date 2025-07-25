import json
import os

from dotenv import load_dotenv
from langchain.docstore.document import Document
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

load_dotenv()
input_chunks_path = os.getenv("PRECEDENTS_PROCESSED_TEXT")
output_vectorstore_dir = os.getenv("PRECEDENTS_VECTORSTORE")
# Load chunks
docs = []
with open(input_chunks_path, "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line)
        docs.append(
            Document(page_content=item["text"], metadata=item.get("metadata", {}))
        )

# Create embeddings
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Create FAISS vector store
vectorstore = FAISS.from_documents(docs, embedding_model)
vectorstore.save_local(output_vectorstore_dir)

print(f"✅ Saved vectorstore to: {output_vectorstore_dir}")
