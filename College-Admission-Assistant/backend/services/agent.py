import os
from langchain_ollama import ChatOllama
from langchain_core.tools import Tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from .college_api import search_college_scorecard
from .rag import search_college_info

# Initialize model
def get_llm():
    return ChatOllama(
        model="qwen2.5:3b",
        temperature=0.0
    )

def create_agent():
    llm = get_llm()
    
    # Define Tools
    rag_tool = Tool(
        name="Internal_College_Database",
        func=search_college_info,
        description="Useful for answering questions about college eligibility, required documents, application start/deadline, admission process, fees, placement info, and rank from our internal database. Input should be a search query like the college name."
    )
    
    api_tool = Tool(
        name="College_Scorecard_API",
        func=lambda x: str(search_college_scorecard(x)),
        description="Retrieve official, real-time data about US colleges from US Department of Education. Provides acceptance rates, cost, and enrollment. Input should be the exact school_name (e.g. 'Stanford University'). Use this for 'best' or 'top' schools as well."
    )
    
    tools = [rag_tool, api_tool]
    
    # Memory checkpointer for LangGraph
    memory = MemorySaver()
    
    system_prompt = (
        "You are a strict College Admission Assistant. "
        "You MUST use the 'Internal_College_Database' tool to answer questions about eligibility, documents, deadlines, fees, placement, and rank. "
        "You MUST use the 'College_Scorecard_API' tool for real-time university data like acceptance rates and cost. "
        "NEVER guess or make up information. If the tools do not return the specific details requested, say 'I cannot find this in my database.'"
    )
    
    # Initialize the agent using LangGraph's create_react_agent
    agent = create_react_agent(llm, tools=tools, checkpointer=memory, prompt=system_prompt)
    
    return agent

_agent_instance = None

def get_agent_instance():
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = create_agent()
    return _agent_instance

def chat_with_agent(user_message: str) -> str:
    agent = get_agent_instance()
    # Provide a thread_id to keep conversation history
    config = {"configurable": {"thread_id": "user_session_1"}}
    try:
        # The agent returns a dictionary with 'messages'
        response = agent.invoke({"messages": [("user", user_message)]}, config)
        # Extract the last message content
        return response["messages"][-1].content
    except Exception as e:
        return f"Error communicating with agent: {str(e)}"
