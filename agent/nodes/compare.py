import os
from typing import Dict, Any
from ..state import CompareState
from openai import OpenAI
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def run_comparison(state: CompareState) -> CompareState:
    """
    Node pour la comparaison finale entre AXA et Generali.
    """
    try:
        # Initialiser le client OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Créer le prompt de comparaison simplifié
        comparison_prompt = f"""
Tu es un expert en assurance auto. Tu compares deux contrats concernant un même thème (ex : responsabilité civile) pour un usage professionnel.

Voici le résultat de recherche de tes 2 agents assureurs :

AXA :
{state['axa_result']}

Generali :
{state['generali_result']}

Ta mission :

1. Analyse les garanties, exclusions, limitations et conditions de chaque assureur.
2. Compare chaque élément de manière rigoureuse.
3. Détermine, **pour chaque ligne**, lequel des deux contrats est plus avantageux ou protecteur pour l’assuré.
4. Si aucune des deux options n’est clairement meilleure, écris : “Équivalent”.
5. Tu dois faire la comparaison la plus fine possible, et donner le plus d'éléments de comparaison dans le tableau.

### Contraintes :
- Ne fais aucune supposition : base-toi uniquement sur les textes fournis.
- Utilise un ton clair, professionnel et factuel.
- Ne recommande pas un assureur globalement : analyse **élément par élément**.

### Format de sortie (obligatoire) :

1. **Tableau comparatif** :

| Élément analysé        | AXA                                      | Generali                                 | Meilleur choix                           |
|------------------------|-------------------------------------------|-------------------------------------------|------------------------------------------|
| Element A   | ...                                       | ...                                       | AXA / Generali / Équivalent              |
| Elements B            | ...                                       | ...                                       | ...                                      |
| Element C    | ...                                       | ...                                       | ...                                      |
| Element D    | ...                                       | ...                                       | ...                                      |
| Element E    | ...                                       | ...                                       | ...                                      |
| Element F    | ...                                       | ...                                       | ...                                      |
| Element G    | ...                                       | ...                                       | ...                                      |
| Element H    | ...                                       | ...                                       | ...                                      |
| Element I    | ...                                       | ...                                       | ...                                      |
| Element J    | ...                                       | ...                                       | ...                                      |

2. **Résumé synthétique (5 lignes max)** :
Présente les différences principales et les avantages contractuels identifiés, sans recommander un assureur globalement.
"""
        
        # Générer la comparaison avec OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Tu es un expert en assurances automobiles. Crée des tableaux clairs et structurés pour comparer les produits d'assurance."},
                {"role": "user", "content": comparison_prompt}
            ],
            temperature=0.1,
            max_tokens=2000
        )
        
        # Extraire la réponse
        comparison_result = response.choices[0].message.content
        
        # Mettre à jour l'état
        state["comparison"] = comparison_result
        
        return state
        
    except Exception as e:
        state["comparison"] = f"Erreur lors de la comparaison: {str(e)}"
        return state