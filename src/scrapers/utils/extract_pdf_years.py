import streamlit as st
import os
import re
from PyPDF2 import PdfReader

PRODUCTS = ["Car Insurance", "Travel Insurance"]
INSURERS = ["Generali", "AXA"]

st.title("Insurance AVB PDF Scraper")

product = st.selectbox("Sélectionnez le produit d'assurance", PRODUCTS)

documents_dir = os.path.join(os.path.dirname(__file__), '..', 'documents')

def extract_year_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        first_page = reader.pages[0]
        text = first_page.extract_text() or ''
        match = re.search(r'\b(20\d{2}|19\d{2})\b', text)
        if match:
            return match.group(0)
    except Exception:
        pass
    return "-"

st.header("Résultats du scraping")

data = []
for filename in os.listdir(documents_dir):
    if filename.lower().endswith('.pdf'):
        # Détection de l'assureur par le nom du fichier
        if "axa" in filename.lower():
            insurer = "AXA"
        elif "generali" in filename.lower():
            insurer = "Generali"
        else:
            insurer = "Inconnu"
        year = extract_year_from_pdf(os.path.join(documents_dir, filename))
        data.append({
            "Assureur": insurer,
            "Nom du PDF": filename,
            "Année": year,
            "Fichier": os.path.join(documents_dir, filename)
        })

if not data:
    st.warning("Aucun PDF trouvé dans le dossier documents.")
else:
    st.table([{k: v for k, v in row.items() if k != "Fichier"} for row in data])
    for row in data:
        with open(row["Fichier"], "rb") as f:
            st.download_button(f"Télécharger {row['Assureur']} - {row['Nom du PDF']}", f, file_name=row["Nom du PDF"]) 