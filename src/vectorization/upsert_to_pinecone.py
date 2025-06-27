import os
import json
import glob
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from tqdm import tqdm
import argparse

# Charger les variables d'environnement dès le début du script
load_dotenv()

def get_latest_categorized_file(insurer: str) -> str:
    """Trouve le fichier de chunks le plus récent pour un assureur donné."""
    search_path = f'data/processed/{insurer}/chunks/*.json'
    list_of_files = glob.glob(search_path)
    if not list_of_files:
        raise FileNotFoundError(f"Aucun fichier de chunks trouvé pour {insurer} dans {search_path}")
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

def load_chunks(file_path: str) -> list:
    """Charge les chunks depuis un fichier JSON."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def initialize_pinecone(api_key: str):
    """Initialise et retourne le client Pinecone."""
    return Pinecone(api_key=api_key)

def process_insurer_upsert(insurer: str, pc, openai_client, index, embedding_model_name, product: str = None):
    """Traite l'upsert pour un assureur spécifique."""
    try:
        print(f"\n--- Traitement de {insurer.capitalize()} ---")
        chunk_file = get_latest_categorized_file(insurer)
        chunks = load_chunks(chunk_file)
        print(f"{len(chunks)} chunks chargés depuis {chunk_file}")

        # Déduire le produit si non fourni
        inferred_product = product
        if not inferred_product:
            if 'travel' in chunk_file.lower():
                inferred_product = 'travel'
            else:
                inferred_product = 'car'
        print(f"Produit utilisé pour l'upsert : {inferred_product}")
        
        # Préparer et envoyer les données par lots (batch)
        batch_size = 100
        print(f"Début de l'upsert par lots de {batch_size}...")
        
        for i in tqdm(range(0, len(chunks), batch_size), desc=f"Upsert {insurer.capitalize()} vers Pinecone"):
            batch = chunks[i:i + batch_size]
            
            ids = [f"{insurer}-{inferred_product}-{i+j}" for j, _ in enumerate(batch)]
            
            metadata = [
                {
                    "insurer": insurer.capitalize(),
                    "section": chunk.get("section", ""),
                    "content": chunk.get("content", ""),
                    "product": inferred_product
                } for chunk in batch
            ]

            # Créer les embeddings avec le client OpenAI
            contents = [chunk['content'] for chunk in batch]
            try:
                res = openai_client.embeddings.create(input=contents, model=embedding_model_name)
                embeddings = [record.embedding for record in res.data]
            except Exception as e:
                print(f"Erreur lors de la création des embeddings pour le lot {i//batch_size + 1}: {e}")
                continue
            
            to_upsert = list(zip(ids, embeddings, metadata))
            
            # Debug : affiche un exemple de vecteur à upserter
            if to_upsert:
                print("Exemple de vecteur à upserter :", to_upsert[0])
            
            try:
                upsert_response = index.upsert(vectors=to_upsert)
                print("Réponse Pinecone upsert:", upsert_response)
            except Exception as e:
                print(f"Erreur lors de l'upsert du lot {i//batch_size + 1}: {e}")
                continue

        print(f"✅ {insurer.capitalize()} traité avec succès")
        return True

    except FileNotFoundError as e:
        print(e)
        return False
    except Exception as e:
        print(f"Une erreur inattendue est survenue pour {insurer}: {e}")
        return False

def main():
    """
    Script principal pour vectoriser les chunks avec OpenAI et les upsert dans Pinecone.
    """
    parser = argparse.ArgumentParser(description="Upsert insurance chunks to Pinecone.")
    parser.add_argument('--insurer', type=str, default='axa', help='Insurer to process (axa, generali, etc.)')
    parser.add_argument('--product', type=str, default=None, help='Insurance product (car, travel, etc.). If not provided, will be inferred from chunk file path.')
    args = parser.parse_args()

    print("--- Début du script d'upsert vers Pinecone (avec OpenAI Embeddings) ---")
    
    # 1. Charger la configuration
    print("Vérification des variables d'environnement...")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Débogage pour voir ce qui est chargé
    print(f"PINECONE_API_KEY chargé : {'Oui' if PINECONE_API_KEY else 'Non'}")
    print(f"PINECONE_INDEX_NAME chargé : {'Oui' if PINECONE_INDEX_NAME else 'Non'}")
    print(f"OPENAI_API_KEY chargé : {'Oui' if OPENAI_API_KEY else 'Non'}")
    
    if not all([PINECONE_API_KEY, PINECONE_INDEX_NAME, OPENAI_API_KEY]):
        print("Erreur : Une ou plusieurs variables d'environnement sont manquantes. Veuillez vérifier votre fichier .env")
        return

    # 2. Initialiser les services
    try:
        pc = initialize_pinecone(PINECONE_API_KEY)
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        print("Clients Pinecone et OpenAI initialisés.")
    except Exception as e:
        print(f"Erreur lors de l'initialisation des services : {e}")
        return

    # 3. Vérifier et préparer l'index Pinecone
    embedding_model_name = "text-embedding-3-small"
    dimension = 1536  # Dimension pour le modèle text-embedding-3-small
    print(f"Utilisation du modèle d'embedding '{embedding_model_name}' (dimension : {dimension})")

    if PINECONE_INDEX_NAME not in pc.list_indexes().names():
        print(f"L'index '{PINECONE_INDEX_NAME}' n'existe pas. Création en cours...")
        try:
            pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            print(f"Index '{PINECONE_INDEX_NAME}' créé avec succès.")
        except Exception as e:
            print(f"Erreur lors de la création de l'index : {e}")
            return
    else:
        print(f"L'index '{PINECONE_INDEX_NAME}' existe déjà. Connexion...")

    index = pc.Index(PINECONE_INDEX_NAME)
    
    # 4. Traiter l'assureur choisi
    insurer_to_process = args.insurer
    product_to_use = args.product
    success = process_insurer_upsert(insurer_to_process, pc, openai_client, index, embedding_model_name, product=product_to_use)
    
    if success:
        print("\n--- Script terminé avec succès ---")
        stats = index.describe_index_stats()
        print(f"Statistiques de l'index : {stats}")
    else:
        print("\n--- Script terminé avec des erreurs ---")

if __name__ == "__main__":
    main() 