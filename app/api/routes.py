# app/api/endpoints.py

from fastapi import APIRouter
from pydantic import BaseModel
from app.core.rag import setup_qa_chain

router = APIRouter()
qa_chains = setup_qa_chain()

class QueryRequest(BaseModel):
    query: str
    source: str  # 'statutes', 'precedents', or 'both'

@router.post("/ask")
def ask_question(request: QueryRequest):
    query = request.query
    source = request.source.lower()

    if source == "statutes":
        result = qa_chains["statutes"].invoke({"query": query})
        return {"answer": result["result"]}
    elif source == "precedents":
        result = qa_chains["precedents"].invoke({"query": query})
        return {"answer": result["result"]}
    elif source == "both":
        result1 = qa_chains["statutes"].invoke({"query": query})
        result2 = qa_chains["precedents"].invoke({"query": query})
        combined = f"[Statutes]\n{result1['result']}\n\n[Precedents]\n{result2['result']}"
        return {"answer": combined}
    else:
        return {"error": "Invalid source. Choose from 'statutes', 'precedents', or 'both'."}
