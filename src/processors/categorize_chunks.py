import os
import json
import glob
from openai import OpenAI
from dotenv import load_dotenv
from tqdm import tqdm
import re
import datetime

# Charger les variables d'environnement (notamment la clé API OpenAI)
load_dotenv()

# Définir la taxonomie commune
TAXONOMY = [
    "1. Dispositions contractuelles générales",
    "2. Plaques et immatriculation",
    "3. Paiement, primes et franchises",
    "4. Résiliation et modification du contrat",
    "5. Responsabilité civile (RC)",
    "6. Assurance Casco",
    "7. Garanties corporelles (accidents)",
    "8. Services et assistance",
    "9. Garanties complémentaires",
    "10. Obligations de l'assuré",
    "11. Protection des données et droit applicable",
    "12. Dispositions spécifiques"
]

def get_latest_chunk_file(insurer: str) -> str:
    """Trouve le fichier de chunks le plus récent pour un assureur donné."""
    list_of_files = glob.glob(f'data/processed/{insurer}/chunks/*.json')
    if not list_of_files:
        raise FileNotFoundError(f"Aucun fichier de chunks trouvé pour {insurer}")
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

def load_chunks(file_path: str) -> list:
    """Charge les chunks depuis un fichier JSON."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_category_from_llm(client: OpenAI, chunk: dict, taxonomy: list) -> str:
    """
    Interroge le LLM pour obtenir la catégorie la plus pertinente pour un chunk donné,
    en utilisant les métadonnées et une logique de parsing robuste.
    """
    taxonomy_str = "\n".join(taxonomy)
    
    # Extraire les informations du chunk
    section = chunk.get('section', 'N/A')
    subsection = chunk.get('subsection', 'N/A')
    content = chunk.get('content', '')

    if not content:
        return "Contenu manquant"

    system_prompt = (
        f"Tu es un expert en assurances. Ta tâche est de classifier le texte fourni dans l'une des catégories suivantes. "
        f"Utilise les titres de la section et de la sous-section comme contexte principal, et le contenu du texte pour affiner ton choix. "
        f"Réponds uniquement avec le nom exact de la catégorie, sans aucune autre explication.\n\n"
        f"Voici les catégories disponibles :\n{taxonomy_str}"
    )
    
    user_prompt = (
        f"Section : {section}\n"
        f"Sous-section : {subsection}\n\n"
        f"Contenu :\n{content}"
    )

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,
            max_tokens=100
        )
        raw_response = completion.choices[0].message.content.strip()

        # 1. Vérification d'une correspondance exacte (cas idéal)
        if raw_response in taxonomy:
            return raw_response

        # 2. Si échec, recherche si la réponse est une sous-chaîne d'une catégorie valide
        #    (Le modèle a répondu "Assurance Casco" au lieu de "6. Assurance Casco")
        for valid_category in taxonomy:
            if raw_response in valid_category:
                return valid_category
        
        # 3. En dernier recours, si le modèle ne renvoie que le numéro (ex: "1.", "2.")
        match = re.search(r'^(\d{1,2})\.?', raw_response)
        if match:
            number = int(match.group(1))
            if 1 <= number <= len(taxonomy):
                # Retourne la catégorie correspondante depuis la liste
                return taxonomy[number - 1]

        # Si toutes les tentatives échouent, on affiche la réponse pour le débogage
        return f"Non identifiée (Réponse: '{raw_response[:60]}...')"

    except Exception as e:
        return f"Erreur API: {e}"

def save_categorized_chunks(chunks: list, insurer: str):
    """Sauvegarde les chunks enrichis avec les catégories dans un nouveau fichier JSON."""
    output_dir = f'data/processed/{insurer}/categorized_chunks'
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f'{output_dir}/categorized_{insurer}_chunks_{timestamp}.json'
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=4)
        
    print(f"\nDonnées de catégorisation sauvegardées dans : {output_filename}")

def display_categorization_summary(categorized_chunks: list, insurer_name: str):
    """Affiche un résumé structuré et clair des chunks catégorisés."""
    if not categorized_chunks:
        print(f"Aucun chunk n'a été catégorisé pour {insurer_name}.")
        return

    print(f"\n--- Résumé de la catégorisation pour {insurer_name} ({len(categorized_chunks)} chunks) ---")
    
    current_section = None
    for item in categorized_chunks:
        section = item.get("section")
        subsection = item.get("subsection")
        category = item.get("category")
        
        if section != current_section:
            # Ajoute un saut de ligne avant une nouvelle section pour aérer
            print(f"\n{section}")
            current_section = section
            
        # Aligne joliment la sortie
        print(f"  - {subsection:<70} | Catégorie -> {category}")

def process_insurer_chunks(insurer: str, client: OpenAI):
    """Traite les chunks d'un assureur spécifique."""
    try:
        print(f"\n--- Traitement de {insurer.capitalize()} ---")
        chunk_file = get_latest_chunk_file(insurer)
        print(f"Chargement des chunks depuis : {chunk_file}")
        chunks = load_chunks(chunk_file)
        
        print(f"\n{len(chunks)} chunks à catégoriser pour {insurer.capitalize()}. Début du processus...")
        
        # On itère sur les chunks pour les enrichir
        for chunk in tqdm(chunks, desc=f"Catégorisation {insurer.capitalize()}"):
            predicted_category = get_category_from_llm(client, chunk, TAXONOMY)
            chunk['category'] = predicted_category # On ajoute la nouvelle clé

        # Sauvegarder les chunks enrichis dans un nouveau fichier
        save_categorized_chunks(chunks, insurer)

        # Afficher le résumé à partir des données enrichies
        display_categorization_summary(chunks, insurer.capitalize())
        
        return chunks

    except FileNotFoundError as e:
        print(e)
        return None
    except Exception as e:
        print(f"Une erreur inattendue est survenue pour {insurer}: {e}")
        return None

def main():
    """
    Script principal pour charger les chunks, les catégoriser avec un LLM
    et afficher les résultats.
    """
    print("Initialisation du script de catégorisation...")
    
    # Initialiser le client OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Erreur: La variable d'environnement OPENAI_API_KEY n'est pas définie.")
        print("Veuillez créer un fichier .env à la racine du projet et y ajouter OPENAI_API_KEY=votre_clé")
        return
    client = OpenAI(api_key=api_key)

    # Traiter les deux assureurs
    insurers = ["generali", "axa"]
    
    for insurer in insurers:
        process_insurer_chunks(insurer, client)

if __name__ == "__main__":
    main() 