import json
import os

from dotenv import load_dotenv
from langchain.docstore.document import Document
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

load_dotenv()
# Input file (chunked statutes)
input_chunks_path = os.getenv("STATUTES_PROCESSED_TEXT")

# Output FAISS vectorstore directory
output_vectorstore_dir = os.getenv("STATUTES_VECTORSTORE")
# Ensure output directory exists
os.makedirs(output_vectorstore_dir, exist_ok=True)

# Load chunked documents
docs = []
# Ensure the input file's folder exists before reading
input_dir = os.path.dirname(input_chunks_path)
if not os.path.exists(input_dir):
    os.makedirs(input_dir, exist_ok=True)

try:
    with open(input_chunks_path, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            docs.append(
                Document(page_content=item["text"], metadata=item.get("metadata", {}))
            )
except PermissionError as e:
    print(f"Permission denied when trying to read '{input_chunks_path}': {e}")
    exit(1)

# Create embeddings using HuggingFace model
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Create FAISS vectorstore and save it locally
vectorstore = FAISS.from_documents(docs, embedding_model)
vectorstore.save_local(output_vectorstore_dir)

print(f"Statutes vectorstore saved to: {output_vectorstore_dir}")
