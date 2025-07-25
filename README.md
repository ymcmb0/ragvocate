# Ragvocate – AI-Powered RAG Assistant

Ragvocate is an AI-based application that uses LangChain and FastAPI to provide intelligent, context-aware answers from uploaded documents. The backend is built on FastAPI using Retrieval-Augmented Generation (RAG), and the frontend is developed in Next.js for a modern, responsive user interface.

---

TECH STACK

Backend:

* FastAPI
* LangChain
* FAISS (Vector DB)

Frontend:

* Next.js (React-based)
* TypeScript

Other Tools:

* Python 3.10+
* PyPDFLoader
* Tiktoken

---

FEATURES

* Upload PDF documents
* Automatic text chunking and embedding using LangChain
* Retrieval-Augmented Generation with OpenAI LLM
* Conversational memory with context
* Chatbot-style Q\&A interface
* Fully decoupled architecture (Next.js frontend + FastAPI backend)

---

SETUP INSTRUCTIONS

1. Clone the Repository

git clone [https://github.com/yourusername/ragvocate.git](https://github.com/yourusername/ragvocate.git)
cd ragvocate

2. Backend Setup (FastAPI)

Create virtual environment:

```
python -m venv env
source env/bin/activate       (Linux/macOS)
env\Scripts\activate          (Windows)
```

Install dependencies:

```
pip install -r requirements.txt
```

Create a `.env` file in the root directory and add:

```
OPENAI_API_KEY=your_openai_api_key
```

Run the backend:

```
uvicorn app.main:app --reload
```

The backend runs by default on [http://localhost:8000](http://localhost:8000)

3. Frontend Setup (Next.js)

   cd frontend
   npm install
   npm run dev

The frontend will be available at [http://localhost:3000](http://localhost:3000)

---

PROJECT STRUCTURE

ragvocate/
├── app/                    # FastAPI backend
│   ├── api/                # API routes
│   ├── core/               # Embedding and LangChain logic
│   ├── main.py             # Entrypoint
│   └── utils.py
├── frontend/               # Next.js frontend
├── requirements.txt
└── README.md

---

NOTES

* Ensure the frontend communicates with the backend on the correct URL (`localhost:8000`).
* CORS settings in FastAPI must allow requests from `localhost:3000`.
* PDF parsing and chunking are done automatically on upload.

---

TO-DO

* Add user authentication
* Add cloud deployment (e.g., Render, Vercel)
* Improve document metadata handling
* Add support for non-PDF file types (e.g., DOCX)
