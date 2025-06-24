# Script pour le post-traitement des screenshots d'avis clients (VLM, OCR, etc.) 

import os
from dotenv import load_dotenv
import openai
import base64

# Charge le .env à la racine du projet
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../../.env'))

def extract_review_info_from_image(image_path):
    """
    Envoie le screenshot à l'API OpenAI (GPT-4V) et retourne la note et le nombre d'avis.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY n'est pas défini dans les variables d'environnement.")

    client = openai.OpenAI(api_key=api_key)

    with open(image_path, "rb") as img_file:
        image_b64 = base64.b64encode(img_file.read()).decode("utf-8")

    prompt = (
        "Voici un screenshot du site d'assurance voyage d'un assureur. Vas dans la section avis de la clientele. "
        "Donne-moi l'évaluation globale, qui correpond a une note sur 5. Donne le nombre total de commentaires ou avis (en général plus de 10,000). "
        "Si l'information n'est pas visible, réponds 'Aucune note trouvée'. "
        "Traduits aussi en anglais le texte principal du commentaire ou de l'évaluation globale, et fournis la traduction dans la réponse. "
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Tu es un assistant d'extraction d'information visuelle."},
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
            ]}
        ],
        max_tokens=100
    )
    result = response.choices[0].message.content
    print(f"Résultat VLM : {result}")
    return result

# Exemple d'utilisation
if __name__ == "__main__":
    image_path = os.path.join(os.path.dirname(__file__), '../../data/reviews_screenshots/generali/travel_insurance_note.png')
    extract_review_info_from_image(image_path) 