import os
from dotenv import load_dotenv

# Load environment variables from .env file
# (LANGSMITH_TRACING, LANGSMITH_API_KEY, LANGSMITH_PROJECT should be in your .env)
load_dotenv(override=True) # Use override=True to ensure .env values take precedence ....env file will take precedence and overwrite them for the duration of this script's execution.
# This prevents accidental conflicts and ensures your .env is the single source of truth for this specific project's configuration.

# Import necessary LangChain components for Ollama, prompts, and output parsing
from langchain_ollama import OllamaLLM  # Recommended: pip install -U langchain-ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Initialize Ollama LLM (ensure Ollama server is running and model is pulled)
llm = OllamaLLM(model="tinyllama")

# Define prompt template 
prompt = PromptTemplate.from_template(
    "You are a helpful AI assistant. Answer the following questions:\n{question}"
)

# Create the LangChain pipeline (prompt -> LLM -> output parser)
chain = prompt | llm | StrOutputParser()

print("Invoking the LLM...")

try:
    # First question
    question1 = "What is the capital of France?"
    response1 = chain.invoke({"question": question1})
    print(f"\nQuestion 1: {question1}")
    print(f"Response 1: {response1}")

    # Second question
    question2 = "Tell me a short story about a robot."
    response2 = chain.invoke({"question": question2})
    print(f"\nQuestion 2: {question2}")
    print(f"Response 2: {response2}")

except Exception as e:
    print(f"\nAn error occurred: {e}")
    print("Please ensure your Ollama server is running and the 'tinyllama' model is downloaded (`ollama pull tinyllama`).")

print("\nCheck your LangSmith UI for traces under the 'ravogate' project!")





# import os
# from dotenv import load_dotenv

# load_dotenv()

# # verify langsmith tracking is enabaled
# print(f"LangSmith Tracking: {os.getenv('LANGSMITH_TRACKING')}")
# print(f"LangSmith PROJECT: {os.getenv('LANGSMITH_PROJECT')}")

# from langchain_community.llms import Ollama
# from langchain_core.prompts import PromptTemplate
# from langchain_core.output_parsers import StrOutputParser

# llm=Ollama(model="tinyllama")

# prompt=PromptTemplate.from_template(
#     "you are a helpful AI assistant. Answer the following questions:\n{question}"
# )

# chain=prompt|llm|StrOutputParser()

# print("\nInvoking the LLM....")

# try:
#     question="what is the capital of france?"
#     response=chain.invoke({"question":question})
#     print(f"Question:{question}")
#     print(f"Response:{response}")
    
#     print("\nInvoking the LLM with another question...")
#     question2="tell me a short story about a robot."
#     response2=chain.invoke({"question":question2})
#     print(f"Question:{question2}")
#     print(f"response:{response2}")
    
# except Exception as e:
#     print(f"an error occured:{e}")
#     print("please ensure the requirements are clear.")

# print("\nCheck your langsmith ui for traces under the reavogate project")

