from langgraph.graph import StateGraph, END
from .state import CompareState
from .nodes.classify_query import classify_query
from .nodes.axa_rag import run_axa
from .nodes.generali_rag import run_generali
from .nodes.compare import run_comparison

def create_agent_graph() -> StateGraph:
    """
    Crée et configure le graphe de l'agent LangGraph.
    """
    # Créer le graphe avec notre état typé
    workflow = StateGraph(CompareState)
    
    # Ajouter les nodes
    workflow.add_node("classify", classify_query)
    workflow.add_node("axa_search", run_axa)
    workflow.add_node("generali_search", run_generali)
    workflow.add_node("compare", run_comparison)
    
    # Définir le flux d'exécution
    workflow.set_entry_point("classify")
    workflow.add_edge("classify", "axa_search")
    workflow.add_edge("axa_search", "generali_search")
    workflow.add_edge("generali_search", "compare")
    workflow.add_edge("compare", END)
    
    return workflow

def compile_agent():
    """
    Compile et retourne l'agent prêt à l'utilisation.
    """
    workflow = create_agent_graph()
    return workflow.compile() 