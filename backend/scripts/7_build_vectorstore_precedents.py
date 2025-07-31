import json
import os

from dotenv import load_dotenv
from langchain.docstore.document import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

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

# Create embeddings using HuggingFace model
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=embedding_model,
    collection_name="precedents",
    persist_directory=output_vectorstore_dir,
)

print(f"Precedents Chroma vectorstore saved to: {output_vectorstore_dir}")
