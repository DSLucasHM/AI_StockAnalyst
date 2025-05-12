"""
Execution graph definition for the stock research agent.
"""
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from ..state import AnalystGenerationState, InterviewState, ResearchGraphState
from ..nodes import (
    create_analysts, generate_question, web_search, generate_answer, 
    save_interview, write_section, start_all_interviews, write_report,
    write_introduction, write_conclusion, finalize_report, route_messages
)

def create_analyst_generation_graph() -> StateGraph:
    """
    Creates the analyst generation graph: one analyst per stock and one geopolitical analyst.
    
    Returns:
        StateGraph: Compiled graph for analyst generation
    """
    builder = StateGraph(AnalystGenerationState)
    builder.add_node("create_analysts", create_analysts)
    builder.add_edge(START, "create_analysts")
    builder.add_edge("create_analysts", END)
    
    return builder.compile()

def create_interview_graph() -> StateGraph:
    """
    Creates the individual interview graph: each analyst conducts a stock-focused interview and writes a section.
    
    Returns:
        StateGraph: Compiled graph for interviews
    """
    interview_builder = StateGraph(InterviewState)
    interview_builder.add_node("ask_question", generate_question)
    interview_builder.add_node("web_search", web_search)
    interview_builder.add_node("answer_question", generate_answer)
    interview_builder.add_node("save_interview", save_interview)
    interview_builder.add_node("write_section", write_section)

    interview_builder.add_edge(START, "ask_question")
    interview_builder.add_edge("ask_question", "web_search")
    interview_builder.add_edge("web_search", "answer_question")
    interview_builder.add_conditional_edges(
        "answer_question",
        route_messages,
        {
            "ask_question": "ask_question",
            "save_interview": "save_interview"
        }
    )
    interview_builder.add_edge("save_interview", "write_section")
    interview_builder.add_edge("write_section", END)
    
    return interview_builder.compile()

def create_research_graph() -> StateGraph:
    """
    Creates the main research graph: orchestrates the entire stock research and report generation.
    
    Returns:
        StateGraph: Compiled graph for research
    """
    main_builder = StateGraph(ResearchGraphState)
    main_builder.add_node("create_analysts", create_analysts)
    main_builder.add_node("conduct_interview", create_interview_graph())
    main_builder.add_node("write_report", write_report)
    main_builder.add_node("write_introduction", write_introduction)
    main_builder.add_node("write_conclusion", write_conclusion)
    main_builder.add_node("finalize_report", finalize_report)

    # Connects the nodes in the main flow
    main_builder.add_edge(START, "create_analysts")
    main_builder.add_conditional_edges("create_analysts", start_all_interviews, ["conduct_interview"])
    main_builder.add_edge("conduct_interview", "write_report")
    main_builder.add_edge("conduct_interview", "write_introduction")
    main_builder.add_edge("conduct_interview", "write_conclusion")
    main_builder.add_edge(["write_conclusion", "write_report", "write_introduction"], "finalize_report")
    main_builder.add_edge("finalize_report", END)

    # Compiles with a checkpoint to save the state
    memory = MemorySaver()
    return main_builder.compile(checkpointer=memory)


"""    interview_builder = StateGraph(InterviewState)
    interview_builder.add_node("ask_question", generate_question)
    interview_builder.add_node("web_search", web_search)
    interview_builder.add_node("answer_question", generate_answer)
    interview_builder.add_node("save_interview", save_interview)
    interview_builder.add_node("write_section", write_section)

    interview_builder.add_edge(START, "ask_question")
    interview_builder.add_edge("ask_question", "web_search")
    interview_builder.add_edge("web_search", "answer_question")
    interview_builder.add_conditional_edges("answer_question", route_messages, ['ask_question', 'save_interview'])
    interview_builder.add_edge("save_interview", "write_section")
    interview_builder.add_edge("write_section", END)
    
    return interview_builder.compile()"""