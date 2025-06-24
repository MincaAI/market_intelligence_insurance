from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import subprocess
import re
from PyPDF2 import PdfReader
import sys

PRODUCTS = ["Car Insurance", "Travel Insurance"]
INSURERS = ["Generali", "AXA", "Allianz", "Swiss", "Baloise"]
SPIDER_MAP = {"Generali": "generali", "AXA": "axa", "Allianz": "allianz", "Swiss": "swiss", "Baloise": "baloise"}

st.title("📄 General Terms and Conditions Document Scraping")
st.write("From GTC overload to actionable insights — in one click.")

insurance_type = st.radio("Select Insurance Type:", ("Car", "Travel"))
product = insurance_type.lower()

if "show_results" not in st.session_state:
    st.session_state.show_results = False

scraping_errors = []

if st.button("Start scraping"):
    with st.spinner("Scraping in progress..."):
        for insurer in INSURERS:
            spider = SPIDER_MAP[insurer]
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "scrapy", "crawl", spider, "-a", f"product={product}"],
                    cwd=os.path.join(os.path.dirname(__file__), "..", "..", "scrapers"),
                    capture_output=True, text=True
                )
                st.text(f"{insurer} stdout:\n{result.stdout}")
                st.text(f"{insurer} stderr:\n{result.stderr}")
                if result.returncode != 0:
                    scraping_errors.append(insurer)
            except Exception as e:
                scraping_errors.append(f"{insurer} (exception: {e})")
                continue
        st.session_state.show_results = True
        if scraping_errors:
            st.info(f"No document found for: {', '.join(scraping_errors)}.")
        else:
            st.success("Scraping completed!")

if st.session_state.show_results:
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

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'documents'))
    folders = {
        "Generali": os.path.join(base_dir, "generali"), 
        "AXA": os.path.join(base_dir, "axa"), 
        "Allianz": os.path.join(base_dir, "allianz"), 
        "Swiss": os.path.join(base_dir, "swiss"),
        "Baloise": os.path.join(base_dir, "baloise")
    }

    # Mapping du dossier produit
    if 'car' in product:
        product_folder_name = 'car'
    elif 'travel' in product:
        product_folder_name = 'travel'
    else:
        product_folder_name = product.lower().replace(' ', '_')

    table_data = []
    for insurer, folder in folders.items():
        pdf_found = False
        product_folder = os.path.join(folder, product_folder_name)
        if os.path.exists(product_folder):
            for filename in sorted(os.listdir(product_folder)):
                if filename.lower().endswith('.pdf'):
                    year = extract_year_from_pdf(os.path.join(product_folder, filename))
                    table_data.append({
                        "Insurer": insurer,
                        "PDF name": filename,
                        "Year": year,
                        "File": os.path.join(product_folder, filename)
                    })
                    pdf_found = True
                    break
        if not pdf_found:
            table_data.append({
                "Insurer": insurer,
                "PDF name": "No document found",
                "Year": "-",
                "File": None
            })

    st.header("Scraping results")
    cols = st.columns([2, 5, 1, 2])
    cols[0].markdown("**Insurer**")
    cols[1].markdown("**PDF name**")
    cols[2].markdown("**Year**")
    cols[3].markdown("**Download**")

    for row in table_data:
        cols = st.columns([2, 5, 1, 2])
        cols[0].write(row["Insurer"])
        cols[1].write(row["PDF name"])
        cols[2].write(row["Year"])
        if row["File"]:
            with open(row["File"], "rb") as f:
                cols[3].download_button("Download", f, file_name=row["PDF name"])
        else:
            cols[3].write("-")
else:
    st.info("Start scraping to see the documents.") 