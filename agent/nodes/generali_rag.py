from typing import Dict, Any
from ..state import CompareState
from ..chains.rag import RAGChain

def run_generali(state: CompareState) -> CompareState:
    """
    Node for RAG search on Generali data.
    """
    try:
        # Initialize the RAG chain
        rag_chain = RAGChain()
        
        # Perform search for Generali with top 4 results
        results = rag_chain.search(
            query=state["user_input"],
            insurer="Generali",
            product=state["product"],
            top_k=4
        )
        
        # Format results as text
        if results:
            generali_text = f"Generali Results:\n"
            for i, result in enumerate(results, 1):
                generali_text += f"{i}. Section: {result['section']}\n"
                generali_text += f"   Subsection: {result['subsection']}\n"
                generali_text += f"   Content: {result['content'][:200]}...\n"
                generali_text += f"   Score: {result['score']:.3f}\n\n"
        else:
            generali_text = "No results found for Generali"
        
        # Update state
        state["generali_result"] = generali_text
        
        return state
        
    except Exception as e:
        state["generali_result"] = f"Error during Generali search: {str(e)}"
        return state 