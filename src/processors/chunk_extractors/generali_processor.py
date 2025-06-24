import os
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
import json
from .pdf_processor import PDFDocumentProcessor
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import openai
import re

load_dotenv()  # charge les variables depuis .env

openai_api_key = os.getenv('OPENAI_API_KEY')
pinecone_api_key = os.getenv('PINECONE_API_KEY')

class GeneraliAVBProcessor:
    def __init__(self, document_path: str):
        self.document_path = document_path
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.pdf_processor = PDFDocumentProcessor(document_path, insurer="generali")

    def process_document(self, metadata: Dict[str, Any]) -> FAISS:
        """Traite le document complet."""
        # Extraction des chunks structurés du PDF
        pdf_chunks = self.pdf_processor.process_document()
        
        # Préparation des chunks pour la vectorisation
        chunks_for_vectorization = []
        enriched_metadata = []
        
        for chunk in pdf_chunks:
            # Création d'un texte enrichi avec les métadonnées de structure
            enriched_text = f"""
            Document: {chunk['document_name']}
            Assureur: {chunk['insurer']}
            Page: {chunk['page_number']}
            Section: {chunk['general_section']}
            Sous-section: {chunk['subsection_id']} {chunk['subsection_title']}
            Contenu: {chunk['content']}
            """
            chunks_for_vectorization.append(enriched_text)
            
            # Enrichissement des métadonnées
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "document_name": chunk['document_name'],
                "page_number": chunk['page_number'],
                "section": chunk['general_section'],
                "subsection_id": chunk['subsection_id'],
                "subsection_title": chunk['subsection_title']
            })
            enriched_metadata.append(chunk_metadata)

        # Création des embeddings
        vectorstore = FAISS.from_texts(
            chunks_for_vectorization,
            self.embeddings,
            metadatas=enriched_metadata
        )
        return vectorstore

    def save_vectorstore(self, vectorstore: FAISS, output_path: str):
        """Sauvegarde le vectorstore."""
        vectorstore.save_local(output_path)

    def display_chunks(self):
        """Affiche les chunks de manière lisible."""
        self.pdf_processor.display_chunks()

def process_generali_avb_document(document_path: str, metadata: Dict[str, Any], output_path: str):
    """Fonction utilitaire pour traiter un document AVB de Generali."""
    processor = GeneraliAVBProcessor(document_path)
    vectorstore = processor.process_document(metadata)
    processor.save_vectorstore(vectorstore, output_path)
    return processor

def process_text_with_llm(text_content):
    """
    Traite le texte avec GPT pour extraire et structurer les chunks d'information.
    """
    # Assurez-vous que la clé API est configurée
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("La clé API OpenAI n'est pas configurée. Utilisez la variable d'environnement OPENAI_API_KEY.")

    # Prompt pour le LLM
    system_prompt = """Tu es un expert en analyse de documents d'assurance. 
    Ta tâche est d'analyser le texte d'un document d'assurance et de le structurer en chunks logiques.
    Pour chaque section, tu dois extraire :
    1. Le titre de la section
    2. Le contenu complet
    3. Les métadonnées pertinentes (numéro de section, sous-section, etc.)
    4. La hiérarchie (niveau de la section)
    
    Format de sortie attendu (JSON) :
    {
        "chunks": [
            {
                "title": "Titre de la section",
                "content": "Contenu complet de la section",
                "metadata": {
                    "section_number": "X.Y",
                    "level": 1,
                    "parent_section": "X"
                }
            }
        ]
    }
    """

    # Découper le texte en morceaux plus petits si nécessaire
    max_tokens = 4000
    text_chunks = split_text_into_chunks(text_content, max_tokens)
    
    all_chunks = []
    
    for chunk in text_chunks:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": chunk}
                ],
                temperature=0.0
            )
            
            # Extraire et parser la réponse JSON
            result = json.loads(response.choices[0].message.content)
            all_chunks.extend(result.get("chunks", []))
            
        except Exception as e:
            print(f"Erreur lors du traitement d'un chunk : {str(e)}")
    
    return {"chunks": all_chunks}

def split_text_into_chunks(text, max_tokens, overlap=100):
    """
    Découpe le texte en chunks plus petits avec un certain chevauchement.
    """
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        word_length = len(word.split()) # approximation grossière des tokens
        if current_length + word_length > max_tokens:
            # Ajouter le chunk actuel à la liste
            chunks.append(" ".join(current_chunk))
            # Garder les derniers mots pour le chevauchement
            current_chunk = current_chunk[-overlap:]
            current_length = len(" ".join(current_chunk).split())
        
        current_chunk.append(word)
        current_length += word_length
    
    # Ajouter le dernier chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

def main():
    # Configuration des chemins
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent.parent
    
    # Dossiers d'entrée et de sortie
    input_dir = project_root / "data" / "processed" / "generali" / "text"
    output_dir = project_root / "data" / "processed" / "generali" / "chunks"
    
    # Créer le dossier de sortie s'il n'existe pas
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Trouver le fichier le plus récent dans le dossier d'entrée
    input_files = list(input_dir.glob("generali_text_*.txt"))
    if not input_files:
        print("Aucun fichier d'entrée trouvé.")
        return
    
    latest_file = max(input_files, key=lambda x: x.stat().st_mtime)
    
    try:
        print(f"Traitement du fichier : {latest_file}")
        
        # Lire le contenu du fichier
        with open(latest_file, 'r', encoding='utf-8') as f:
            text_content = f.read()
        
        # Traiter le texte avec le LLM
        result = process_text_with_llm(text_content)
        
        # Sauvegarder les résultats
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"generali_chunks_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\nChunks sauvegardés dans : {output_file}")
        print("\nAperçu des chunks :")
        print("=" * 80)
        print(json.dumps(result["chunks"][:2], ensure_ascii=False, indent=2))
        print("..." if len(result["chunks"]) > 2 else "")
        print("=" * 80)
        
    except Exception as e:
        print(f"Erreur lors du traitement : {str(e)}")

if __name__ == "__main__":
    main() 