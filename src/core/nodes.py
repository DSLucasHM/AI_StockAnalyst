"""
Implementation of graph nodes for the stock research agent.
"""
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage, get_buffer_string, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import Send

from .state import (
    Analyst, Perspectives, ResearchQuery, AnalystGenerationState,
    InterviewState, ResearchGraphState
)
from ..config import OPENAI_API_KEY, DEFAULT_MODEL, DEFAULT_TEMPERATURE, CURRENT_DATE
from ..retriever.search import SearchEngine
from ..utils.helpers import get_num_specialist_answers, format_sections_string, split_content_and_sources


# Initialize the language model
llm = ChatOpenAI(
    model=DEFAULT_MODEL,
    temperature=DEFAULT_TEMPERATURE
)

# Initialize the search engine
search_engine = SearchEngine()

# Instruction templates
ANALYST_INSTRUCTIONS = (
    "For the topic 'Stocks from Brazil', create one analyst for each stock in: {stocks}, for each analyst give a clear focus on one stcok, do it for each stock in the list  "
    "and one geopolitical analyst for all stocks. "
    "IMPORTANT: Create only one analyst for each stock, do not create more than one analyst for the same stock."
    "IMPORTANT: The total number of analysts must be equal to the number of stocks plus one for the geopolitical analyst."
    "Each analyst must have the following fields:\n"
    "- name: a realistic full name\n"
    "- affiliation: a plausible company, bank, or institution\n"
    "- role: a job title (e.g., Equity Analyst, Geopolitical Analyst)\n"
    "- description: a short professional background and their focus regarding the stock(s)\n"
    "Return the result as a list of analyst objects, using the exact field names above."
)

QUESTION_INSTRUCTIONS = """You are an analyst tasked with asking questions to a specialist to produce a comprehensive report about a specific Brazilian stock.

Have in mind today's date is {current_date}, and use recent information.

Your goal is to extract all relevant and important insights for a stockholder or potential buyer, including:
- Price forecasts
- Geopolitical factors
- Recent news
- Any other information that could impact the stock's value or investment decision

Here is your persona, embody this character: {goals}

Start by introducing yourself using a name that fits your persona, then ask your question.

Continue asking questions to deepen and refine your understanding of the stock.

When you are satisfied with your understanding, conclude the interview with: "Thank you very much for your help!"

Remember to stay in character throughout your response, reflecting the persona and goals provided to you.

"""

RESEARCH_QUERY_INSTRUCTIONS = """You will receive a conversation between an analyst and a specialist about a Brazilian stock.

Have in mind today's date is {current_date}, and use recent information.

Your goal is to generate a well-structured query for use in retrieval and/or web research related to the conversation.

First, analyze the complete conversation.

Pay special attention to the last question asked by the analyst.

Convert this final question into a well-structured web search query, focusing on price forecasts, geopolitical factors, news, and any other information relevant to stockholders or potential buyers."""

ANSWER_INSTRUCTIONS = """You are a specialist being interviewed by an analyst, first of all.

Here is the analyst's area of focus: {goals}. 

Your goal is to answer a question posed by the interviewer, providing a comprehensive report for a Brazilian stock, including price forecasts, geopolitical factors, news, and all information relevant to a stockholder or potential buyer.

To answer the question, use this context:

{context}

When answering the questions, follow these guidelines:

1. Use only the information provided in the context. 
2. Do not introduce external information or make assumptions beyond what is explicitly stated in the context.
3. The context contains sources at the top of each individual document.
4. Include these sources in your answer next to any relevant statements. For example, for source no. 1, use [1]. 
5. List your sources in order at the bottom of your answer. [1] Source 1, [2] Source 2, etc.
6. If the source is: <Document source="assistant/docs/llama3_1.pdf" page="7"/>', then just list: 

[1] assistant/docs/llama3_1.pdf, page 7 

And skip adding the brackets, as well as the Document source preamble in your citation.


"""

SECTION_WRITER_INSTRUCTIONS = """You are a financial technical writer specializing in Brazilian stocks.

Your task is to create a concise, actionable, and well-structured section of a stock report based on a set of source documents about a specific Brazilian stock.

**Instructions:**

1. **Analyze the source documents:**  
   - Each document begins with a <Document tag and may include a URL or file path.
   - Focus on extracting insights that matter to investors: price forecasts, recent news, geopolitical and macroeconomic factors, risks, opportunities, and anything that could impact the stock's value.

2. **Structure your report using markdown:**  
   - Use ## for the section title (make it specific and engaging, e.g., "PETR4: 2024 Outlook and Key Drivers")
   - Use ### for subsections

3. **Report content:**  
   a. **Title** (## header):  
      - Use the stock ticker and a short, informative phrase.
   b. **Summary** (### header):  
      - Briefly introduce the stock and its context in the Brazilian market.
      - Highlight the most important findings: price targets, analyst consensus, recent performance, and any major news or events.
      - Clearly state any risks or opportunities identified.
      - Use bullet points or a short numbered list for clarity if needed.
   c. **Key Insights** (### header):  
      - List and explain the most relevant insights for a stockholder or potential buyer, such as:
        - Price forecasts and valuation
        - Geopolitical or macroeconomic factors
        - Regulatory changes
        - Company-specific news or events
        - Analyst recommendations

   d. **Sources** (### header):  
      - List all sources used in your report.
      - For each source, provide the full link (URL) or document path.
      - Use a numbered list ([1], [2], etc.) and avoid duplicates.
      - Example:
        [1] https://www.b3.com.br/en_us/
        [2] https://www.valorinveste.globo.com/
      - Only include sources that were actually referenced in the summary or key insights.

4. **General guidelines:**  
   - Do not mention the names of interviewers or specialists.
   - Keep the section under 400 words.
   - Do not include a preamble before the report title.
   - Ensure the report is clear, actionable, and relevant for investors interested in the stock.
"""

REPORT_WRITER_INSTRUCTIONS = """You are a financial technical writer creating a consolidated report on the following topic:

{topic}

You have a team of analysts. Each analyst has:
1. Conducted an interview with a specialist about a specific stock or a relevant macro/geopolitical factor.
2. Written their findings in a memo.

Your task:

1. You will receive a collection of memos from your analysts.
2. Carefully analyze the insights from each memo, focusing on actionable information for stockholders or potential buyers: price forecasts, recent news, geopolitical and macroeconomic factors, risks, opportunities, and anything that could impact the stock's value.
3. Consolidate the main points from all memos into a single, cohesive, and actionable narrative.
4. Summarize the most important findings, connecting the core ideas from all memos.
5. Do not write a conclusion, nor a summary, just a report.

**Formatting:**
- Use markdown formatting.
- Do not include a preamble for the report.
- Do not use subheadings except as specified below.
- Start your report with a single title header: ## Stock Insights
- Do not mention analyst names in your report.
- Preserve any citations in the memos, which will be annotated in brackets, e.g. [1] or [2].
- Create a final consolidated list of sources and add it to a Sources section with the header ## Sources.
- List your sources in order and do not repeat them.
- Example:
[1] https://www.b3.com.br/en_us/
[2] https://www.valorinveste.globo.com/

Here are the memos from your analysts to build your report: 

{context}"""

INTRO_CONCLUSION_INSTRUCTIONS = """You are a financial technical writer finalizing a report on {topic}

You will receive all the sections of the report.

Your job is to write a concise and compelling introduction or conclusion, focused on the stock context.

The user will instruct you whether to write the introduction or the conclusion.

Do not include a preamble for any section.

Aim for about 100 words, concisely presenting (for the introduction) or recapping (for the conclusion) all sections of the report.

Use markdown formatting. 

For your introduction, create an engaging title and use the # header for the title.

For your introduction, use ## Introduction as the section header. 

For your conclusion, use ## Conclusion as the section header.

Here are the sections to reflect on when writing: {formatted_str_sections}"""

def create_analysts(state: AnalystGenerationState) -> Dict[str, Any]:
    """
    Creates one analyst per stock and one geopolitical analyst,
    using structured output from the language model (Perspectives model).
    """
    stocks = state.get('stocks', [])

    # Prepares the system prompt with topic and stocks
    system_message = ANALYST_INSTRUCTIONS.format(
        stocks=", ".join(stocks)
    )

    structured_llm = llm.with_structured_output(Perspectives)

    # Generates analysts
    analysts = structured_llm.invoke([
        SystemMessage(content=system_message),
        HumanMessage(
            content="Generate the set of analysts as structured output.")
    ])

    # Filter and validate analysts
    filtered_analysts = []
    stock_analysts = {}  # Dictionary to track analysts per stock
    geo_analyst = None   # Variable to track geopolitical analyst

    for analyst in analysts.analysts:
        # Check if it's a geopolitical analyst
        if "geopolitical" in analyst.role.lower():
            if geo_analyst is None:  # Only keep the first geopolitical analyst
                geo_analyst = analyst
                filtered_analysts.append(analyst)
        else:
            # For stock analysts, check if we already have one for this stock
            for stock in stocks:
                if stock in analyst.description.upper():
                    if stock not in stock_analysts:
                        stock_analysts[stock] = analyst
                        filtered_analysts.append(analyst)
                    break

    # Add the geopolitical analyst at the end if we have one
    if geo_analyst and geo_analyst not in filtered_analysts:
        filtered_analysts.append(geo_analyst)

    # Returns filtered analysts in the expected format
    return {"analysts": filtered_analysts}


def generate_question(state: InterviewState) -> Dict[str, Any]:
    """
    Node for the analyst to generate a question.
    """
    analyst = state["analyst"]
    messages = state["messages"]

    # Generates question using the analyst's persona
    system_message = QUESTION_INSTRUCTIONS.format(
        goals=analyst.persona, current_date=CURRENT_DATE)
    question = llm.invoke([SystemMessage(content=system_message)] + messages)

    return {"messages": [question]}


def web_search(state: InterviewState) -> Dict[str, Any]:
    """
    Retrieves documents from web search via Tavily.
    """
    messages = state['messages']

    # Generates search query
    structured_llm = llm.with_structured_output(ResearchQuery)
    research_query = structured_llm.invoke([
        SystemMessage(content=RESEARCH_QUERY_INSTRUCTIONS)
    ] + messages)

    # Executes the search
    search_result = search_engine.search(research_query.research_query)

    return {"context": [search_result]}


def generate_answer(state: InterviewState) -> Dict[str, Any]:
    """
    Node for the specialist to answer the analyst's question.
    """
    analyst = state["analyst"]
    messages = state["messages"]
    context = state["context"]

    # Responds using the context information (Tavily)
    system_message = ANSWER_INSTRUCTIONS.format(
        goals=analyst.persona,
        context=context,
        current_date=CURRENT_DATE
    )

    answer = llm.invoke([SystemMessage(content=system_message)] + messages)

    # Marks the message as coming from the specialist
    answer.name = "specialist"

    return {"messages": [answer]}


def save_interview(state: InterviewState) -> Dict[str, Any]:
    """
    Saves the interview transcript.
    """
    messages = state["messages"]

    # Converts the interview to string
    interview = get_buffer_string(messages)

    return {"interview": interview}

def route_messages(state: InterviewState, name: str = "specialist") -> str:
    """
    Routes between asking a new question or ending the interview.
    """
    messages = state["messages"]
    max_num_turns = state.get('max_num_turns', 2)

    # Count the number of specialist answers
    num_answers = get_num_specialist_answers(messages, name)
    
    # Debug logging
    print(f"Number of specialist answers: {num_answers}")
    print(f"Max turns: {max_num_turns}")

    # End if max number of turns is reached
    if num_answers >= max_num_turns:
        print("Max turns reached, ending interview")
        return 'save_interview'

    # Check if the last question signals the end
    if len(messages) >= 2:
        last_question = messages[-2]
        if "Thank you very much for your help" in last_question.content:
            print("End message detected, ending interview")
            return 'save_interview'

    print("Continuing interview")
    return "ask_question"


def write_section(state: InterviewState):
    """Node to write a report section based on the interview"""
    interview = state["interview"]
    context = state["context"]
    analyst = state["analyst"]

    # Write section based on the interview documents
    system_message = SECTION_WRITER_INSTRUCTIONS.format(
        focus=analyst.description)
    section = llm.invoke([
        SystemMessage(content=system_message),
        HumanMessage(
            content=f"Use this source to write your section: {context}")
    ])

    return {"sections": [section.content]}


def start_all_interviews(state: ResearchGraphState):
    """Start interviews in parallel for each analyst"""
    topic = state["topic"]
    return [
        Send("conduct_interview", {
            "analyst": analyst,
            "messages": [
                HumanMessage(content=f"You are preparing a report involving price forecasts, recent news, macroeconomic factors, risks, opportunities, and anything that could impact your main stock value..")
            ],
            "context": [],
            "max_num_turns": 2,
            "interview": "",
            "sections": []
        }) for analyst in state["analysts"]
    ]


def write_report(state: ResearchGraphState):
    """Generate the main report from the analysts' sections"""
    sections = state["sections"]
    topic = state["topic"]

    # Concatenate all sections
    formatted_sections_str = "\n\n".join(
        [f"{section}" for section in sections])

    # Generate the final report consolidating the sections
    system_message = REPORT_WRITER_INSTRUCTIONS.format(
        topic=topic, context=formatted_sections_str)
    report = llm.invoke([
        SystemMessage(content=system_message),
        HumanMessage(content=f"Write a report based on these memos.")
    ])

    return {"content": report.content}




def write_report(state: ResearchGraphState):
    """Generate the main report from the analysts' sections"""
    sections = state["sections"]
    topic = state["topic"]

    # Concatenate all sections
    formatted_sections_str = "\n\n".join(
        [f"{section}" for section in sections])

    # Generate the final report consolidating the sections
    system_message = REPORT_WRITER_INSTRUCTIONS.format(
        topic=topic, context=formatted_sections_str)
    report = llm.invoke([
        SystemMessage(content=system_message),
        HumanMessage(content=f"Write a report based on these memos.")
    ])

    return {"content": report.content}


def write_introduction(state: ResearchGraphState):
    """Generate introduction for the report"""
    sections = state["sections"]
    topic = state["topic"]

    # Concatenate all sections
    formatted_sections_str = "\n\n".join(
        [f"{section}" for section in sections])

    # Generate introduction
    instructions = INTRO_CONCLUSION_INSTRUCTIONS.format(
        topic=topic,
        formatted_str_sections=formatted_sections_str
    )

    intro = llm.invoke([
        SystemMessage(content=instructions),
        HumanMessage(content=f"Write the introduction of the report")
    ])

    return {"introduction": intro.content}


def write_conclusion(state: ResearchGraphState):
    """Generate conclusion for the report"""
    sections = state["sections"]
    topic = state["topic"]

    # Concatenate all sections
    formatted_sections_str = "\n\n".join(
        [f"{section}" for section in sections])

    # Generate conclusion
    instructions = INTRO_CONCLUSION_INSTRUCTIONS.format(
        topic=topic,
        formatted_str_sections=formatted_sections_str
    )

    conclusion = llm.invoke([
        SystemMessage(content=instructions),
        HumanMessage(content=f"Write the conclusion of the report")
    ])

    return {"conclusion": conclusion.content}


def finalize_report(state: ResearchGraphState):
    """Join all parts of the report (introduction, content, conclusion)"""
    content = state["content"]

    # Process the content
    if content.startswith("## Stock Insights"):
        content = content.strip("## Stock Insights")

    if "## Sources" in content:
        try:
            content, sources = content.split("\n## Sources\n")
        except:
            sources = None
    else:
        sources = None

    # Assemble the final report
    final_report = state["introduction"] + "\n\n---\n\n" + \
        content + "\n\n---\n\n" + state["conclusion"]

    # Add sources if they exist
    if sources is not None:
        final_report += "\n\n## Sources\n" + sources

    return {"final_report": final_report}
