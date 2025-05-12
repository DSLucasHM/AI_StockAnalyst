"""
Implementation of search using the Tavily API.
"""
from typing import Dict, Any, List
from langchain_community.tools.tavily_search import TavilySearchResults
from src.config import TAVILY_API_KEY, MAX_SEARCH_RESULTS
from src.utils.helpers import format_search_results

class SearchEngine:
    """
    Class for performing searches using the Tavily API.
    """
    
    def __init__(self, max_results: int = MAX_SEARCH_RESULTS):
        """
        Initializes the search engine.
        
        Args:
            max_results: Maximum number of results to return
        """
        self.search_tool = TavilySearchResults(max_results=max_results)
    
    def search(self, query: str) -> str:
        """
        Performs a web search using the Tavily API.
        
        Args:
            query: Search query
            
        Returns:
            str: Formatted search results for use as context
        """
        try:
            # Search via Tavily
            search_results = self.search_tool.invoke(query)
            print(f"Search query: {query}")
            
            # Format the results
            return format_search_results(search_results, query)
            
        except Exception as e:
            print(f"Error in web_search: {e}")
            return f"<Document href='https://example.com'/>\nError retrieving information about {query}. Please rely on your knowledge to answer the question.\n</Document>"
