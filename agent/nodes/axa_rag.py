from typing import Dict, Any
from ..state import CompareState
from ..chains.rag import RAGChain

def run_axa(state: CompareState) -> CompareState:
    """
    Node pour la recherche RAG sur les données AXA.
    """
    try:
        # Initialiser la chaîne RAG
        rag_chain = RAGChain()
        
        # Le 'product' de l'état est utilisé comme 'namespace'
        namespace = state["product"] 
        
        # Effectuer la recherche pour AXA avec filtre par catégorie
        results = rag_chain.search(
            query=state["user_input"],
            insurer="Axa",
            category=state.get("detected_category"),
            top_k=10
        )
        
        # Formater les résultats en texte
        if results:
            axa_text = f"Résultats AXA (Catégorie: {state.get('detected_category', 'Non spécifiée')}):\n"
            for i, result in enumerate(results, 1):
                axa_text += f"{i}. Section: {result['section']}\n"
                axa_text += f"   Sous-section: {result['subsection']}\n"
                axa_text += f"   Catégorie: {result['category']}\n"
                axa_text += f"   Contenu: {result['content'][:200]}...\n"
                axa_text += f"   Score: {result['score']:.3f}\n\n"
        else:
            axa_text = f"Aucun résultat trouvé pour AXA dans la catégorie: {state.get('detected_category', 'Non spécifiée')}"
        
        # Mettre à jour l'état
        state["axa_result"] = axa_text
        
        return state
        
    except Exception as e:
        state["axa_result"] = f"Erreur lors de la recherche AXA: {str(e)}"
        return state 