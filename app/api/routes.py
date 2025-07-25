# app/api/endpoints.py
from dotenv import load_dotenv
from fastapi import APIRouter
from langchain.callbacks import LangChainTracer
from langsmith import traceable
from pydantic import BaseModel
from app.core.langgraph_basic import save_chat_history
from app.core.rag import setup_qa_chain, setup_langgraph, setup_report_graph

load_dotenv()
tracer = LangChainTracer()
router = APIRouter()
qa_chains = setup_qa_chain()
graph = setup_langgraph()

class QueryRequest(BaseModel):
    query: str
    source: str  # 'statutes', 'precedents', or 'both'

@router.post("/ask")
def ask_question(request: QueryRequest):
    query = request.query
    source = request.source.lower()
    if source == "statutes":
        result = qa_chains["statutes"].invoke(
            {"query": query}, config={"callbacks": [tracer]}
        )
        return {"answer": result["result"]}
    elif source == "precedents":
        result = qa_chains["precedents"].invoke(
            {"query": query}, config={"callbacks": [tracer]}
        )
        return {"answer": result["result"]}
    elif source == "both":
        result1 = qa_chains["statutes"].invoke(
            {"query": query}, config={"callbacks": [tracer]}
        )
        result2 = qa_chains["precedents"].invoke(
            {"query": query}, config={"callbacks": [tracer]}
        )
        combined = (
            f"[Statutes]\n{result1['result']}\n\n[Precedents]\n{result2['result']}"
        )
        return {"answer": combined}
    else:
        return {
            "error": "Invalid source. Choose from 'statutes', 'precedents', or 'both'."
        }
class LangGraphQuery(BaseModel):
    query: str

chat_history = []
@router.post("/ask/langgraph")
def ask_with_langgraph(request: LangGraphQuery):
    query = request.query

    state = {
        "question": query,
        "chat_history": chat_history,
        "context": None,
        "answer": None
    }

    result = graph.invoke(state)

    # Update history for future queries
    chat_history.clear()
    chat_history.extend(result["chat_history"])

    # Save to disk
    if chat_history:
        save_chat_history(chat_history)

    return {"answer": result["answer"]}

class ReportRequest(BaseModel):
    user_input: str
report_graph = setup_report_graph()

@router.post("/generate-report")
def generate_immigration_report(request: ReportRequest):
    try:
        input_state = {
            "user_input": request.user_input,
            "extracted_facts": None,
            "relevant_laws": None,
            "legal_options": None,
            "compliance_issues": None,
            "final_report": None
        }

        result = report_graph.invoke(input_state)

        return {
            "report_text": result.get("final_report"),
            "facts": result.get("extracted_facts"),
            "legal_options": result.get("legal_options"),
            "compliance_issues": result.get("compliance_issues"),
        }

    except Exception as e:
        return {"error": str(e)}