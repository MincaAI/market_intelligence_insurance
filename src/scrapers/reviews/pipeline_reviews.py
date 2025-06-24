import subprocess
import os
import json
import importlib.util
import sys

# Import dynamique de process_screenshots.py
PROCESS_SCREENSHOTS_PATH = os.path.join(os.path.dirname(__file__), 'process_screenshots.py')
spec = importlib.util.spec_from_file_location("process_screenshots", PROCESS_SCREENSHOTS_PATH)
process_screenshots = importlib.util.module_from_spec(spec)
sys.modules["process_screenshots"] = process_screenshots
spec.loader.exec_module(process_screenshots)
extract_review_info_from_image = process_screenshots.extract_review_info_from_image

# Mapping des scripts et images à générer
JOBS = [
    {
        "assureur": "generali",
        "product": "car",
        "script": "src/scrapers/reviews/generali_reviews.py",
        "img": "src/data/reviews_screenshots/generali/car_insurance_note.png"
    },
    {
        "assureur": "generali",
        "product": "travel",
        "script": "src/scrapers/reviews/generali_reviews.py",
        "img": "src/data/reviews_screenshots/generali/travel_insurance_note.png"
    },
    {
        "assureur": "axa",
        "product": "car",
        "script": "src/scrapers/reviews/axa_reviews.py",
        "img": "src/data/reviews_screenshots/axa/car_insurance_note.png"
    },
    {
        "assureur": "axa",
        "product": "travel",
        "script": "src/scrapers/reviews/axa_reviews.py",
        "img": "src/data/reviews_screenshots/axa/travel_insurance_note.png"
    },
    {
        "assureur": "allianz",
        "product": "car",
        "script": "src/scrapers/reviews/allianz_reviews.py",
        "img": "src/data/reviews_screenshots/allianz/car_insurance_note.png"
    },
    {
        "assureur": "allianz",
        "product": "travel",
        "script": "src/scrapers/reviews/allianz_reviews.py",
        "img": "src/data/reviews_screenshots/allianz/travel_insurance_note.png"
    }
]

recap = {}

for job in JOBS:
    key = f"{job['assureur']}_{job['product']}"
    print(f"\n--- Traitement {key} ---")
    # 1. Générer le screenshot
    try:
        subprocess.run(["python", job["script"], job["product"]], check=True)
    except Exception as e:
        print(f"Erreur lors du screenshot pour {key} : {e}")
        recap[key] = {"note": None, "nombre_avis": None, "erreur": str(e)}
        continue
    # 2. Extraire la note et le nombre d'avis
    try:
        result = extract_review_info_from_image(job["img"])
        # Extraction naïve de la note et du nombre d'avis depuis le texte retourné
        import re
        note = None
        nombre_avis = None
        note_match = re.search(r"([0-9][,.][0-9])\s*/\s*5", result)
        if note_match:
            note = note_match.group(1).replace(",", ".")
        avis_match = re.search(r"([0-9][0-9 .']{2,})\s*(commentaires|avis)", result)
        if avis_match:
            nombre_avis = avis_match.group(1).replace("'", "").replace(" ", "").replace(".", "")
        recap[key] = {"note": note, "nombre_avis": nombre_avis, "raw": result}
    except Exception as e:
        print(f"Erreur extraction VLM pour {key} : {e}")
        recap[key] = {"note": None, "nombre_avis": None, "erreur": str(e)}

# 3. Sauvegarde du JSON
recap_json_path = "src/data/reviews_screenshots/recap_reviews.json"
os.makedirs(os.path.dirname(recap_json_path), exist_ok=True)
with open(recap_json_path, "w", encoding="utf-8") as f:
    json.dump(recap, f, ensure_ascii=False, indent=2)
print(f"\nRécapitulatif sauvegardé dans {recap_json_path}") 