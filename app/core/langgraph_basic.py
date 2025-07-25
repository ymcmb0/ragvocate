from typing import TypedDict, List, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_community.llms import Ollama
from langchain_core.runnables import Runnable
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
import os
from datetime import datetime

class GraphState(TypedDict):
    question: str
    context: Optional[str]
    chat_history: List[BaseMessage]
    answer: Optional[str]

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",  # or "gpt-4" if you have access
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")  # Reads from your .env
    )

def memory(state: GraphState) -> GraphState:
    """Update chat history with the latest question and answer."""
    question = state["question"]
    answer = state["answer"]
    chat_history = state.get("chat_history", [])
    
    # Append new messages
    chat_history.append(HumanMessage(content=question))
    chat_history.append(AIMessage(content=answer))
    
    return {
        **state,
        "chat_history": chat_history
    }

def generate_answer(state: GraphState) -> GraphState:
    """Generate answer using context and chat history."""
    # Format the previous conversation
    history = ""
    for message in state.get("chat_history", []):
        if isinstance(message, HumanMessage):
            history += f"\nUser: {message.content}"
        elif isinstance(message, AIMessage):
            history += f"\nAssistant: {message.content}"
    
    # Format the current prompt using memory
    prompt = f"""You are an assistant helping with U.S. immigration law.

Use the following context to answer the question.

Context:
{state['context']}

Conversation History:
{history}

Current Question:
{state['question']}
INSTRUCTIONS:
1. Answer using ONLY information from the  context
2. If unsure, say "I need more information about that"

"""

    # Invoke LLM and store answer
    answer = llm.invoke(prompt)
    state["answer"] = answer.content
    return state

def retrieve_context(state: GraphState, retriever) -> GraphState:
    """Retrieve relevant context using the retriever."""
    docs = retriever.get_relevant_documents(state["question"])
    state["context"] = "\n\n".join(doc.page_content for doc in docs)
    return state

def build_graph(retriever: Runnable) -> Runnable:
    """Build the LangGraph workflow."""
    builder = StateGraph(GraphState)
    
    # Add nodes
    builder.add_node("retriever", lambda state: retrieve_context(state, retriever))
    builder.add_node("llm", generate_answer)
    builder.add_node("memory", memory)
    
    # Define workflow
    builder.set_entry_point("retriever")
    builder.add_edge("retriever", "llm")
    builder.add_edge("llm", "memory")
    builder.add_edge("memory", END)
    
    return builder.compile()






def save_chat_history(history: list, filename: str = None,HISTORY_LOG: str = "chat_history") -> None:
    """Save conversation to a timestamped txt file."""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{HISTORY_LOG}/conversation_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        for msg in history:
            if isinstance(msg, HumanMessage):
                f.write(f"User: {msg.content}\n\n")
            elif isinstance(msg, AIMessage):
                f.write(f"Assistant: {msg.content}\n\n---\n")
