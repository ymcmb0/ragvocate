# Ragvocate – AI-Powered RAG Assistant

Ragvocate is an AI-based application that uses LangChain, LangGraph, and FastAPI to provide intelligent, context-aware answers from uploaded documents. It uses Retrieval-Augmented Generation (RAG) with OpenAI and supports conversational memory. The backend is built with FastAPI, and the frontend is developed in Next.js for a modern, responsive experience.

---

## 🛠️ TECH STACK

**Backend:**
- FastAPI
- LangChain
- LangGraph (for stateful chat flows)
- ChromaDB (vector store)

**Frontend:**
- Next.js (React-based)
- TypeScript

**Tooling:**
- Python 3.10+
- Poetry (for dependency and environment management)
- PyPDFLoader
- Tiktoken

---

## ✨ FEATURES

- Upload PDF documents
- Automatic text chunking and embedding via LangChain
- Retrieval-Augmented Generation (RAG) with OpenAI LLM
- LangGraph support for structured conversation flows
- Conversational memory and history tracking
- Decoupled frontend/backend architecture

---

## ⚙️ SETUP INSTRUCTIONS

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ragvocate.git
cd ragvocate
2. Backend Setup with Poetry (Recommended)
📦 This project uses Poetry for managing dependencies and virtual environments.

Install Poetry

pip install poetry
Install Dependencies
```
```bash
poetry install
```
Activate shell
```poetry shell```
# Set Environment Variables

Create a .env file in the root directory:

dotenv
OPENAI_API_KEY=your_openai_api_key

```
# Run the Backend

uvicorn app.main:app --reload
The API will be available at: http://localhost:8000
```
# Frontend Setup (Next.js)
```bash
cd frontend
npm install
npm run dev
```
Frontend runs on: http://localhost:3000

# 📁 PROJECT STRUCTURE
```bash

ragvocate/
├── app/
│   ├── api/                 # FastAPI routes (including /ask and /langgraph endpoints)
│   ├── core/
│   │   ├── embedding_loader.py
│   │   ├── rag.py           # RAG pipeline logic
│   │   └── langraph.py      # LangGraph chat logic
│   ├── main.py              # FastAPI app entry point
│   └── utils.py
├── scripts/                 # Data preprocessing scripts
├── data/                    # Processed and chunked documents
├── frontend/                # Next.js frontend
├── pyproject.toml           # Poetry config
├── .env                     # API keys (excluded from version control)
└── README.md
```

# LANGGRAPH INTEGRATION
We support both:

#### Standard RAG-based question answering (/ask)

#### LangGraph-based stateful conversations (/langgraph/ask)

You can extend your client to hit /langgraph/ask for memory-aware chats with history logging.

``` NOTES
Frontend must communicate with backend at localhost:8000

CORS settings in FastAPI allow http://localhost:3000

Document parsing, chunking, and vector store building are handled by scripts in /scripts