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
        "This is a screenshot of a travel insurance website from an insurer. Go to the customer reviews section. "
        "Give me the overall rating (on a scale of 5). Provide the total number of reviews or comments (usually over 10,000). "
        "If the information is not visible, respond with 'No rating found'. "
        "Also translate the main text of the comment or overall review into English, and include the translation in your response."
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Your are an assistant to extract visual information from a screenshot."},
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