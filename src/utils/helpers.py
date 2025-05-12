"""
Helper functions for the agent system.
"""
from typing import List, Dict, Any
from langchain_core.messages import get_buffer_string, AIMessage, HumanMessage, SystemMessage

def get_num_specialist_answers(messages: List[Dict[str, Any]], name: str = "specialist") -> int:
    """
    Returns the number of responses from a specialist in a conversation.
    
    Args:
        messages: List of messages in the conversation
        name: Name of the specialist to count messages from
        
    Returns:
        int: Number of responses from the specialist
    """
    return len([m for m in messages if isinstance(m, AIMessage) and m.name == name])

def format_sections_string(sections: List[str]) -> str:
    """
    Concatenates a list of sections into a single string.
    
    Args:
        sections: List of strings with sections
        
    Returns:
        str: A single string with all sections concatenated
    """
    return "\n\n".join([f"{section}" for section in sections])

def split_content_and_sources(content: str) -> tuple:
    """
    Splits the content and sources from a text.
    
    Args:
        content: String containing content and sources
        
    Returns:
        tuple: (content, sources)
    """
    if "## Sources" in content:
        try:
            content_part, sources = content.split("\n## Sources\n")
            return content_part, sources
        except:
            return content, None
    else:
        return content, None

def format_search_results(search_results: List[Dict[str, Any]], query: str) -> str:
    """
    Formats search results into a string for use as context.
    
    Args:
        search_results: List of search result entries
        query: The query that was used for the search
        
    Returns:
        str: Formatted search results
    """
    formatted_documents = []
    
    if isinstance(search_results, list):
        for result in search_results:
            if isinstance(result, dict) and "url" in result and "content" in result:
                formatted_documents.append(f'<Document href="{result["url"]}"/>\n{result["content"]}\n</Document>')
    
    # Fallback if it's not possible to extract documents
    if not formatted_documents:
        return f"<Document href='https://example.com'/>\nInformation about {query} could not be retrieved. Please rely on your knowledge to answer the question.\n</Document>"
    else:
        return "\n\n---\n\n".join(formatted_documents)
