# LegalAI Assistant - RAG Frontend

A professional Next.js frontend for a legal RAG (Retrieval Augmented Generation) assistant powered by TinyLlama and LangChain.

## Features

- **Professional Chat Interface**: Clean, lawyer-office aesthetic with real-time messaging
- **Document Management**: Upload and manage legal documents (PDF, DOC, TXT)
- **Source Citations**: Display document sources and page references for responses
- **Conversation Export**: Export chat history for record-keeping
- **Responsive Design**: Optimized for desktop and mobile use
- **Professional Theme**: Navy and gold color scheme suitable for legal professionals

## FastAPI Backend Integration

This frontend is designed to work with a FastAPI backend. Your backend should provide these endpoints:

### Required API Endpoints

```python
# FastAPI Backend Example Structure

@app.post("/api/chat")
async def chat(request: ChatRequest):
    # Process query with TinyLlama + LangChain
    # Return response with sources
    return {
        "response": "AI generated response",
        "sources": [
            {
                "document": "document_name.pdf",
                "page": 15,
                "relevance": 0.92,
                "excerpt": "Relevant text excerpt..."
            }
        ],
        "conversation_id": "session-id"
    }

@app.post("/api/upload")
async def upload_documents(files: List[UploadFile]):
    # Process and vectorize documents
    # Store in vector database
    return {
        "files": [
            {
                "filename": file.filename,
                "status": "success"
            }
        ]
    }

@app.get("/api/documents")
async def get_documents():
    # Return list of uploaded documents
    return {"documents": [...]}

@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    # Remove document from knowledge base
    return {"status": "deleted"}
```

## Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development

```bash
npm run dev
```

## Backend Setup Tips

For your FastAPI backend with TinyLlama and LangChain:

1. **Document Processing**: Use LangChain's document loaders for PDFs, DOCX
2. **Vector Store**: Consider FAISS or Chroma for document embeddings
3. **Model Integration**: Load TinyLlama with appropriate quantization
4. **CORS**: Enable CORS for your Next.js frontend

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your Next.js app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Production Considerations

- Implement proper authentication
- Add rate limiting
- Use HTTPS in production
- Consider document encryption for sensitive legal files
- Implement audit logging for legal compliance