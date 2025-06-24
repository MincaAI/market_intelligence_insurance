"""
Chains RAG pour la recherche vectorielle dans Pinecone.
"""

import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

# Charger les variables d'environnement
load_dotenv()

class RAGChain:
    """
    Chaîne RAG pour la recherche dans la base vectorielle Pinecone.
    """
    
    def __init__(self):
        """Initialise la chaîne RAG avec les connexions nécessaires."""
        self.pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.index_name = os.getenv("PINECONE_INDEX_NAME")
        self.index = self.pinecone_client.Index(self.index_name)
        
    def search(self, query: str, insurer: str, namespace: str, category: Optional[str] = None, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Effectue une recherche vectorielle dans un namespace spécifique pour un assureur donné.
        
        Args:
            query: La requête de recherche
            insurer: L'assureur à rechercher ("Axa" ou "Generali")
            namespace: Le namespace à interroger (ex: "car" ou "travel")
            category: Catégorie optionnelle pour filtrer les résultats
            top_k: Nombre de résultats à retourner
            
        Returns:
            Liste des résultats avec métadonnées
        """
        try:
            # Créer l'embedding de la requête
            embedding = self.openai_client.embeddings.create(
                input=query,
                model="text-embedding-3-small"
            ).data[0].embedding
            
            # Préparer le filtre (le produit est maintenant géré par le namespace)
            filter_dict = {"insurer": insurer}
            if category and category != "Catégorie non identifiée":
                filter_dict["category"] = category
            
            # Recherche dans Pinecone avec le bon namespace et les filtres
            results = self.index.query(
                namespace=namespace,
                vector=embedding,
                filter=filter_dict,
                top_k=top_k,
                include_metadata=True
            )
            
            # Formater les résultats
            formatted_results = []
            for match in results.matches:
                formatted_results.append({
                    "score": match.score,
                    "content": match.metadata.get("content", ""),
                    "section": match.metadata.get("section", ""),
                    "subsection": match.metadata.get("subsection", ""),
                    "category": match.metadata.get("category", ""),
                    "insurer": match.metadata.get("insurer", ""),
                    "product": match.metadata.get("product", "")
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"Erreur lors de la recherche RAG pour {insurer}: {e}")
            return [] 