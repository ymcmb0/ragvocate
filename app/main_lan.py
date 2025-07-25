from rag import load_vectorstore
from agents import build_graph, save_chat_history
from langchain_core.messages import HumanMessage, AIMessage
import os 

HISTORY_LOG = "chat_history"  
os.makedirs(HISTORY_LOG, exist_ok=True)  

source = "statutes"
retriever = load_vectorstore(source).as_retriever()
graph = build_graph(retriever)

chat_history = []

while True:
    question = input("Your question (or type 'exit'): ")
    if question.lower() == "exit":
        break

    state = {
        "question": question,
        "chat_history": chat_history,
        "context": None,
        "answer": None
    }

    result = graph.invoke(state)
    print("Answer:", result["answer"])

    chat_history = result["chat_history"]
if chat_history:  # Only save if conversation occurred
        save_chat_history(chat_history)
        print(f"\nConversation saved to {HISTORY_LOG}/")
#      i need to apply for h1b visa, what are requirements for this visa?