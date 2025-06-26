from langgraph.graph import StateGraph, END
from .state import CompareState
from .nodes.axa_rag import run_axa
from .nodes.generali_rag import run_generali
from .nodes.compare import run_comparison

def create_agent_graph() -> StateGraph:
    """
    Create and configure the LangGraph agent workflow.
    """
    # Create the graph with our typed state
    workflow = StateGraph(CompareState)
    
    # Add the nodes
    workflow.add_node("axa_search", run_axa)
    workflow.add_node("generali_search", run_generali)
    workflow.add_node("compare", run_comparison)
    
    # Define the execution flow
    workflow.set_entry_point("axa_search")
    workflow.add_edge("axa_search", "generali_search")
    workflow.add_edge("generali_search", "compare")
    workflow.add_edge("compare", END)
    
    return workflow

def compile_agent():
    """
    Compile and return the agent ready for use.
    """
    workflow = create_agent_graph()
    return workflow.compile() 