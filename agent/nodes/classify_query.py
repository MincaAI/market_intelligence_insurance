import os
import re
from typing import Dict, Any
from ..state import CompareState
from openai import OpenAI
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Taxonomie commune (la même que celle utilisée pour la catégorisation des chunks)
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

def classify_query(state: CompareState) -> CompareState:
    """
    Node pour classifier la requête utilisateur dans une catégorie de la taxonomie.
    """
    try:
        # Initialiser le client OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Préparer le prompt de classification (même logique que categorize_chunks.py)
        taxonomy_str = "\n".join(TAXONOMY)
        
        system_prompt = (
            f"Tu es un expert en assurances automobiles. Ta tâche est de classifier la requête de l'utilisateur "
            f"dans l'une des catégories suivantes. Réponds uniquement avec le nom exact de la catégorie, "
            f"sans aucune autre explication.\n\n"
            f"Voici les catégories disponibles :\n{taxonomy_str}"
        )
        
        # Effectuer la classification
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": state["user_input"]}
            ],
            temperature=0.0,
            max_tokens=100
        )
        
        # Extraire et valider la réponse (même logique robuste que categorize_chunks.py)
        raw_response = completion.choices[0].message.content.strip()
        
        # 1. Vérification d'une correspondance exacte (cas idéal)
        if raw_response in TAXONOMY:
            detected_category = raw_response
        else:
            # 2. Si échec, recherche si la réponse est une sous-chaîne d'une catégorie valide
            #    (Le modèle a répondu "Assurance Casco" au lieu de "6. Assurance Casco")
            for valid_category in TAXONOMY:
                if raw_response in valid_category:
                    detected_category = valid_category
                    break
            else:
                # 3. En dernier recours, si le modèle ne renvoie que le numéro (ex: "1.", "2.")
                match = re.search(r'^(\d{1,2})\.?', raw_response)
                if match:
                    number = int(match.group(1))
                    if 1 <= number <= len(TAXONOMY):
                        # Retourne la catégorie correspondante depuis la liste
                        detected_category = TAXONOMY[number - 1]
                    else:
                        detected_category = "Catégorie non identifiée"
                else:
                    # Si toutes les tentatives échouent, on affiche la réponse pour le débogage
                    detected_category = f"Non identifiée (Réponse: '{raw_response[:60]}...')"
        
        # Mettre à jour l'état
        state["detected_category"] = detected_category
        
        return state
        
    except Exception as e:
        state["detected_category"] = f"Erreur de classification: {str(e)}"
        return state 