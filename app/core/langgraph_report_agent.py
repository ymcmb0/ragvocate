from typing import TypedDict, List, Optional
from langchain_core.runnables import Runnable, chain
from langgraph.graph import StateGraph
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
# from langchain.llms import LlamaCpp  # Assuming you're using LlamaCpp
from embedding_loader import load_vectorstore   
# from langchain_community.llms import Ollama
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
import json
from fpdf import FPDF
from datetime import datetime
import re

# Load .env variables
load_dotenv()

# Create the LLM using OpenAI
llm = ChatOpenAI(
    model="gpt-3.5-turbo",  # or "gpt-4" if you have access
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")  # Reads from your .env
)

# llm = Ollama(model="tinyllama")
source = "statutes"
retriever = load_vectorstore(source).as_retriever()

# Shared State
class CaseState(TypedDict):
    user_input: str
    extracted_facts: Optional[dict]  # From Case Intake
    relevant_laws: Optional[List[str]]  # From Law Retrieval
    legal_options: Optional[List[str]]  # From Legal Reasoning
    compliance_issues: Optional[List[str]]  # From Compliance
    final_report: Optional[str]  # From Report Generator

# Models for structured data
class VisaHistory(BaseModel):
    visa_type: str
    years_held: int
    status: str  # "current", "expired", "denied"

class CaseFacts(BaseModel):
    name: str
    country_of_origin: str
    current_status: str
    visa_history: List[VisaHistory]



def case_intake(state: CaseState) -> CaseState:
    """Extract structured facts from user input"""
    parser = JsonOutputParser(pydantic_object=CaseFacts)

    prompt = ChatPromptTemplate.from_template("""
    Extract these exact fields from the input:
    - name
    - country_of_origin  
    - current_status
    - visa_history (list of visa_type, years_held, status)
    Format the output as a JSON object with these keys.
    
    Input:
    {input}
    
 
    """)

    chain = prompt | llm | parser

    try:
        result = chain.invoke({
            "input": state["user_input"],
            "format_instructions": parser.get_format_instructions()
        })
        
        # Handle both Pydantic model and dict cases
        if hasattr(result, 'model_dump'):  # Pydantic v2
            state["extracted_facts"] = result.model_dump()
        elif hasattr(result, 'dict'):  # Pydantic v1
            state["extracted_facts"] = result.dict()
        elif isinstance(result, dict):  # Raw dictionary
            state["extracted_facts"] = result
        else:
            raise ValueError(f"Unexpected parser output type: {type(result)}")
            
    except Exception as e:
        print(f"Case intake failed: {e}")
        print(f"Input was: {state['user_input']}")
        state["extracted_facts"] = None
    
    return state



def law_retrieval(state: CaseState) -> CaseState:
    """Retrieve relevant laws based on extracted facts"""
    query = f"""
    Country: {state['extracted_facts']['country_of_origin']}
    Visa History: {[v['visa_type'] for v in state['extracted_facts']['visa_history']]}
    Current Status: {state['extracted_facts']['current_status']}
    """
    
    docs = retriever.get_relevant_documents(query)
    state["relevant_laws"] = [doc.page_content for doc in docs]
    return state



def legal_reasoning(state: CaseState) -> CaseState:
    """Determine eligibility and options"""
    prompt = f"""
    Analyze this immigration case:
    
    Facts:
    {state['extracted_facts']}
    
    Relevant Laws:
    {state['relevant_laws']}
    
    Step-by-step determine:
    1. Possible visa pathways
    2. Eligibility for each
    3. Recommended action plan
    
    Output as JSON with these exact keys:
    - recommended_visa (string)
    - options (list of visa types)
    - eligibility (list of notes)
    - recommendations (list of next steps)"""
    
    # result = llm.invoke(prompt)
    # state["legal_options"] = result
    result = llm.invoke(prompt)
    content = result.content if hasattr(result, "content") else result
    parsed = json.loads(content)
    state["legal_options"] = [parsed]

    return state


def compliance_check(state: CaseState) -> CaseState:
    """Check for any compliance issues based on the case facts"""
    compliance_issues = []

    facts = state["extracted_facts"]

    # Check current status
    if facts.get("current_status", "").lower() == "denied":
        compliance_issues.append("Current status is denied")

    # Check visa history for past denials
    for visa in facts.get("visa_history", []):
        if visa.get("status", "").lower() == "denied":
            compliance_issues.append(f"Past visa denial: {visa.get('visa_type', 'Unknown')}")

    state["compliance_issues"] = compliance_issues
    return state

def get_required_documents(visa_type: str, case_facts: dict) -> List[str]:
    """Ask the LLM to determine required documents based on visa type and applicant details."""
    
    prompt = f"""
    Given the visa type "{visa_type}" and the following applicant information:
    
    Name: {case_facts.get('name')}
    Country of Origin: {case_facts.get('country_of_origin')}
    Current Status: {case_facts.get('current_status')}
    Visa History: {case_facts.get('visa_history')}
    
    What documents are typically required for this type of visa application?
    Provide the list as bullet points in JSON format: ["document1", "document2", ...]
    """
    
    try:
        result = llm.invoke(prompt)
        # Attempt to parse result as JSON
        docs = json.loads(result.content.strip()) if hasattr(result, "content") else json.loads(result.strip())
        if isinstance(docs, list):
            return docs
    except Exception as e:
        print("⚠️ Error getting required documents:", e)

    # Fallback if LLM fails or returns invalid output
    return ["passport", "visa application form", "supporting documents"]
def calculate_deadline_llm(visa_type: str, case_facts: dict) -> str:
    """Ask the LLM to determine a deadline for visa filing based on case facts and urgency."""
    prompt = f"""
You are an immigration advisor AI. Estimate a realistic filing deadline based on the following:

Visa Type: {visa_type}

Applicant Case:
{json.dumps(case_facts, indent=2)}

Instructions:
- If the applicant has a denied or expired status, consider urgency.
- If there's a common statutory deadline (e.g., 30 or 90 days after denial or expiration), use that.
- If no official deadline is known, estimate a recommended deadline within 2–6 months from today.
- Always return a **single date only** in the format YYYY-MM-DD.
- Do not return "N/A" unless absolutely no information is available.

Today's date is: {datetime.now().strftime("%Y-%m-%d")}
Respond only with the date.
"""

    try:
        result = llm.invoke(prompt)
        content = result.content.strip() if hasattr(result, "content") else result.strip()

        # Optional strict format check
        if re.match(r"\d{4}-\d{2}-\d{2}", content):
            return content
        else:
            print("⚠️ Unexpected deadline format:", content)
            return "N/A"
    except Exception as e:
        print("⚠️ Deadline generation failed:", e)
        return "N/A"

def generate_report(state: CaseState) -> CaseState:
    """Create client-ready summary and save it as a PDF"""

    required_docs = get_required_documents(
        state["legal_options"][0]["recommended_visa"],
        state["extracted_facts"]
    )

    template = """
    IMMIGRATION CASE PLAN

    Client: {name}
    Origin: {country}

    Legal Pathways:
    - {options}

    Identified Risks:
    - {risks}

    Next Steps:
    1. Gather: {documents}
    2. File by: {deadline}
    """

    # Format the text for display
    report_text = template.format(
        name=state["extracted_facts"]["name"],
        country=state["extracted_facts"]["country_of_origin"],
        options="\n- ".join(str(option) for option in state["legal_options"]),
        risks="\n- ".join(state["compliance_issues"] or ["None"]),
        documents=", ".join(required_docs),
        deadline=calculate_deadline_llm(
            state["legal_options"][0]["recommended_visa"],
            state["extracted_facts"]
        )
    )

    # Save the formatted text in state
    state["final_report"] = report_text

    # ✅ Generate the PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for line in report_text.strip().split('\n'):
        pdf.multi_cell(0, 10, line)

    # Save to file
    filename = f"immigration_report_{state['extracted_facts']['name'].replace(' ', '_')}.pdf"
    pdf.output(filename)

    return state

def build_immigration_graph(retriever: Runnable) -> Runnable:
    builder = StateGraph(CaseState)
    
    # Add nodes for each stage of the process
    builder.add_node("intake", case_intake)
    builder.add_node("retrieve_laws", law_retrieval)
    builder.add_node("analyze", legal_reasoning)
    builder.add_node("compliance", compliance_check)
    builder.add_node("report", generate_report)
    
    # Set entry point and define edges (workflow)
    builder.set_entry_point("intake")
    builder.add_edge("intake", "retrieve_laws")
    builder.add_edge("retrieve_laws", "analyze")
    builder.add_edge("analyze", "compliance")
    builder.add_edge("compliance", "report")
    builder.add_edge("report", END)  # End the graph here
    
    return builder.compile()

