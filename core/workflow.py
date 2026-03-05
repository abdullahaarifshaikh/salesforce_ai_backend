from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from core.state import AgentState
from core.model import model_with_tools
from tools import tools
from langgraph.checkpoint.memory import MemorySaver

SYSTEM_PROMPT = """
You are AnyConnect — an AI-powered business assistant designed to help businesses manage their daily operations using Salesforce CRM. 
You operate through natural language instructions that feel conversational, like a WhatsApp chat.

Your role:
- Interpret user queries in plain English or Hindi and map them to the correct Salesforce CRM operation.
- Use available tools to manage Leads (add, update, remove, list, export).
- If the user sends an image (like a business card) or a voice note, the system will automatically extract the text for you and pass it along in brackets. Use that extracted text to fulfill the user's implicit or explicit request (e.g., adding a lead from a business card).
- Always explain actions clearly, concisely, and professionally.
- Be user-friendly, proactive, and never display raw technical data unless asked.
"""

def call_model(state: AgentState):
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}

def build_workflow():
    wf = StateGraph(AgentState)
    tool_node = ToolNode(tools)
    wf.add_node("agent", call_model)
    wf.add_node("tools", tool_node)
    wf.add_edge(START, "agent")
    wf.add_conditional_edges("agent", tools_condition)
    wf.add_edge("tools", "agent")
    wf.add_edge("agent", END)
    return wf.compile(checkpointer=MemorySaver())

