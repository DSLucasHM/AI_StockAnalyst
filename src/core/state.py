"""
State definitions for the agent system.
"""
from typing import List, Annotated
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
import operator
from langgraph.graph import MessagesState 

class Analyst(BaseModel):
    """
    Model to represent an analyst with information about their affiliation and focus.
    """
    affiliation: str = Field(
        description="Main affiliation of the analyst.",
    )
    name: str = Field(
        description="Name of the analyst."
    )
    role: str = Field(
        description="Role of the analyst in the context of the topic.",
    )
    description: str = Field(
        description="Description of the analyst's focus, concerns, and motivations.",
    )
    
    @property
    def persona(self) -> str:
        """
        Returns a textual representation of the analyst's persona.
        """
        return f"Name: {self.name}\nRole: {self.role}\nAffiliation: {self.affiliation}\nDescription: {self.description}\n"

class Perspectives(BaseModel):
    """
    Model to represent a list of analysts with their roles and affiliations.
    """
    analysts: List[Analyst] = Field(
        description="Comprehensive list of analysts with their roles and affiliations.",
    )

class ResearchQuery(BaseModel):
    """
    Model for research query.
    """
    research_query: str = Field(None, description="Research query for retrieval.")

class AnalystGenerationState(TypedDict):
    """
    State for analyst generation.
    """
    topic: str  # Research topic
    max_analysts: int  # Number of analysts
    analysts: List[Analyst]  # Analysts' questions
    stocks: List[str]  # List of stocks for analysis

class InterviewState(MessagesState):
    """
    State for individual interview.
    """
    max_num_turns: int  # Number of conversation turns
    context: Annotated[list, operator.add]  # Source documents
    analyst: Analyst  # Analyst asking questions
    interview: str  # Interview transcript
    sections: list  # Final key duplicated in the outer state for the Send() API

class ResearchGraphState(TypedDict):
    """
    State for the main research graph.
    """
    topic: str  # Research topic
    max_analysts: int  # Number of analysts
    analysts: List[Analyst]  # Analyst asking questions
    sections: Annotated[list, operator.add]  # Key for the Send() API
    introduction: str  # Introduction for the final report
    content: str  # Content for the final report
    conclusion: str  # Conclusion for the final report
    final_report: str  # Final report
    stocks: List[str]  # List of stocks for analysis
