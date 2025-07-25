from new_langraph import build_immigration_graph,case_intake,law_retrieval
from embedding_loader import load_vectorstore   


source = "statutes"
retriever = load_vectorstore(source).as_retriever()
# Build the graph
graph = build_immigration_graph(retriever)

input_case = """
i am abudaud nawaz from pakistan, i am currently in the US on a tourist visa. 
I have been here for 6 months and my visa is valid for another 6 months. I want 
to apply for an H1B visa to work in the US. My previous visa was an F1 student 
visa which expired last year. I have a job offer from a tech company in California. i have a denied b1 visa application from 2 years ago.
"""

# Execute the graph with the input case
result = graph.invoke({
    "user_input": input_case,
    "extracted_facts": None,  # This will be filled in during the process
    "relevant_laws": None,
    "legal_options": None,
    "compliance_issues": None,
    "final_report": None
})