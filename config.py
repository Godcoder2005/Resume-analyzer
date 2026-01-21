"""
Configuration file for Resume Analyzer
Contains all LLM models and memory store initialization
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.store.memory import InMemoryStore
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize memory store
store = InMemoryStore()

# LLM model for formatting evaluation
llm_formatting = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7
)

# LLM model for evaluation and scoring
llm_eval = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7
)

# LLM model for clarity evaluation
llm_clarity = ChatGoogleGenerativeAI(
    model='gemini-2.5-flash',
    temperature=0.7
)

# LLM for long term memory reading
llm_memory_read = ChatGoogleGenerativeAI(
    model='gemini-2.5-flash'
)

# LLM for longterm memory writing
llm_memory_write = ChatGoogleGenerativeAI(
    model='gemini-2.5-flash'
)