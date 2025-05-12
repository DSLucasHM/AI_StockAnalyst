"""
Centralized configurations for the application.
"""
import os
from datetime import datetime
from dotenv import load_dotenv

# Loads environment variables from the .env file
load_dotenv()

# API keys
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
LANGCHAIN_API_KEY = os.environ.get("LANGCHAIN_API_KEY")

# LangChain configurations
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Stock_Report"

# Date settings
CURRENT_DATE = datetime.now()

# Model settings
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0.5

# Search settings
MAX_SEARCH_RESULTS = 3

# Interview settings
DEFAULT_MAX_TURNS = 2


