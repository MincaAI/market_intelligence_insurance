from typing import Dict, Any
from ..state import CompareState
from ..chains.rag import RAGChain

def run_axa(state: CompareState) -> CompareState:
    """
    Node for RAG search on AXA data.
    """
    try:
        # Initialize the RAG chain
        rag_chain = RAGChain()
        
        # Perform search for AXA with top 4 results
        results = rag_chain.search(
            query=state["user_input"],
            insurer="Axa",
            top_k=4
        )
        
        # Format results as text
        if results:
            axa_text = f"AXA Results:\n"
            for i, result in enumerate(results, 1):
                axa_text += f"{i}. Section: {result['section']}\n"
                axa_text += f"   Subsection: {result['subsection']}\n"
                axa_text += f"   Content: {result['content'][:200]}...\n"
                axa_text += f"   Score: {result['score']:.3f}\n\n"
        else:
            axa_text = "No results found for AXA"
        
        # Update state
        state["axa_result"] = axa_text
        
        return state
        
    except Exception as e:
        state["axa_result"] = f"Error during AXA search: {str(e)}"
        return state 