"""
RAG chains for vector search in Pinecone.
"""

import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

# Load environment variables
load_dotenv()

class RAGChain:
    """
    RAG chain for search in Pinecone vector database.
    """
    
    def __init__(self):
        """Initialize the RAG chain with necessary connections."""
        self.pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.index_name = os.getenv("PINECONE_INDEX_NAME")
        self.index = self.pinecone_client.Index(self.index_name)
        
    def search(self, query: str, insurer: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Perform vector search in Pinecone index for a given insurer.
        Args:
            query: The search query
            insurer: The insurer to search for ("Axa" or "Generali")
            top_k: Number of results to return
        Returns:
            List of results with metadata
        """
        try:
            # Create query embedding
            embedding = self.openai_client.embeddings.create(
                input=query,
                model="text-embedding-3-small"
            ).data[0].embedding
            
            # Prepare filter
            filter_dict = {"insurer": insurer}
            
            # Search in Pinecone without namespace
            results = self.index.query(
                vector=embedding,
                filter=filter_dict,
                top_k=top_k,
                include_metadata=True
            )
            
            # Format results
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
            print(f"Error during RAG search for {insurer}: {e}")
            return [] 