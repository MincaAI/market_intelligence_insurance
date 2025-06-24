from typing import Dict, Any
from ..state import CompareState
from ..chains.rag import RAGChain

def run_generali(state: CompareState) -> CompareState:
    """
    Node pour la recherche RAG sur les données Generali.
    """
    try:
        # Initialiser la chaîne RAG
        rag_chain = RAGChain()
        
        # Le 'product' de l'état est utilisé comme 'namespace'
        namespace = state["product"]

        # Effectuer la recherche pour Generali avec filtre par catégorie
        results = rag_chain.search(
            query=state["user_input"],
            insurer="Generali",
            category=state.get("detected_category"),
            top_k=10
        )
        
        # Formater les résultats en texte
        if results:
            generali_text = f"Résultats Generali (Catégorie: {state.get('detected_category', 'Non spécifiée')}):\n"
            for i, result in enumerate(results, 1):
                generali_text += f"{i}. Section: {result['section']}\n"
                generali_text += f"   Sous-section: {result['subsection']}\n"
                generali_text += f"   Catégorie: {result['category']}\n"
                generali_text += f"   Contenu: {result['content'][:200]}...\n"
                generali_text += f"   Score: {result['score']:.3f}\n\n"
        else:
            generali_text = f"Aucun résultat trouvé pour Generali dans la catégorie: {state.get('detected_category', 'Non spécifiée')}"
        
        # Mettre à jour l'état
        state["generali_result"] = generali_text
        
        return state
        
    except Exception as e:
        state["generali_result"] = f"Erreur lors de la recherche Generali: {str(e)}"
        return state 