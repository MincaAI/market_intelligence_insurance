import streamlit as st
import os
import pandas as pd
import re
from pypdf import PdfReader
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0

def extract_year_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        first_page = reader.pages[0]
        text = first_page.extract_text() or ''
        match = re.search(r'\b(20\d{2}|19\d{2})\b', text)
        if match:
            return match.group(0)
    except Exception:
        return "-"
    return "-"

def extract_version_or_month_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        first_page = reader.pages[0]
        text = first_page.extract_text() or ''
        match = re.search(r'(Version[\s:]*[\w\-.]+|V\.[\w\-.]+)', text, re.IGNORECASE)
        if match:
            return match.group(0)
        match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)[\s-]+\d{4}', text, re.IGNORECASE)
        if match:
            return match.group(0)
        match = re.search(r'\b(0[1-9]|1[0-2])[\/-](19|20)\d{2}\b', text)
        if match:
            return match.group(0)
    except Exception:
        return "-"
    return "-"

def detect_language_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        first_page = reader.pages[0]
        text = first_page.extract_text() or ''
        lang = detect(text)
        lang_map = {'de': 'DE', 'fr': 'FR', 'it': 'IT', 'en': 'EN'}
        return lang_map.get(lang, lang.upper())
    except Exception:
        return "-"

st.title("📈 Simulated monitoring")

st.markdown("""
This page displays a simulated monitoring table of all insurance documents available in the repository.
""")

# Define the root directory for documents
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'documents'))
insurers = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
products_map = {'car': 'car', 'travel': 'travel'}
rows = []
for insurer in insurers:
    insurer_dir = os.path.join(base_dir, insurer)
    for product in os.listdir(insurer_dir):
        product_dir = os.path.join(insurer_dir, product)
        if not os.path.isdir(product_dir):
            continue
        for filename in os.listdir(product_dir):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(product_dir, filename)
                year = extract_year_from_pdf(pdf_path)
                version_or_month = extract_version_or_month_from_pdf(pdf_path)
                lang = detect_language_from_pdf(pdf_path)
                version_str = f"{version_or_month} - {year}" if version_or_month != '-' else year
                rows.append({
                    'Insurer': insurer.capitalize(),
                    'Product': products_map.get(product, product),
                    'Version': version_str,
                    'Fetching date': '2025-06-25',
                    'Status': 'active',
                    'Language': lang,
                    'Previous version': 'Placeholder',
                    'Comparison with previous version': 'Placeholder'
                })

if rows:
    rows[0]['Status'] = 'new'
    for row in rows:
        if row['Insurer'].lower() == 'axa':
            row['Previous version'] = 'June 2022'
            row['Comparison with previous version'] = 'available'
        else:
            row['Previous version'] = 'NA'
            row['Comparison with previous version'] = 'NA'
        if row['Insurer'].lower() == 'generali':
            row['Status'] = 'active'
    df = pd.DataFrame(rows)
    df = df[['Insurer', 'Product', 'Version', 'Fetching date', 'Status', 'Language', 'Previous version', 'Comparison with previous version']]
    df = df.sort_values(by=['Product'], ascending=[True])
    st.table(df)
else:
    st.info("No documents found in the repository.")

st.markdown("---")

st.subheader("🔍 Version Monitoring")
st.markdown("Automatic detection of document changes and version differences.")
st.markdown("""
<div style='background-color:#e6eecf; padding: 12px; border-radius: 8px; font-weight:bold;'>
    🟩 <b>New Version Detected!</b> AXA Travel Insurance June 2022 → AXA Travel Insurance 2023 (Updated 2 hours ago)
</div>
""", unsafe_allow_html=True)

col_prev, col_curr = st.columns(2)
with col_prev:
    st.markdown("""
    ### 📄 Previous Version (AXA June 2022)
    **Key Sections:**
    - Coverage amount: CHF 5,000
    - Deductible: CHF 200
    - Medical coverage: CHF 50,000
    - Luggage: CHF 2,000
    - Trip cancellation: Up to 100% of trip cost
    """)
with col_curr:
    st.markdown("""
    ### 📄 Current Version (AXA 2023)
    **Key Sections:**
    - Coverage amount: CHF 5,000
    - Deductible: CHF 150 ⬇️ <span style='color:#e67e22'><b>CHANGED</b></span>
    - Medical coverage: CHF 75,000 ⬆️ <span style='color:#27ae60'><b>IMPROVED</b></span>
    - Luggage: CHF 2,500 ⬆️ <span style='color:#27ae60'><b>IMPROVED</b></span>
    - Trip cancellation: Up to 100% of trip cost
    """, unsafe_allow_html=True)

st.markdown("### 🔄 Change Summary")
sum_data = [
    {"Section": "Deductible", "Previous": "CHF 200", "Current": "CHF 150", "Impact": "Positive", "Importance": "Medium"},
    {"Section": "Medical coverage", "Previous": "CHF 50,000", "Current": "CHF 75,000", "Impact": "Positive", "Importance": "High"},
    {"Section": "Luggage coverage", "Previous": "CHF 2,000", "Current": "CHF 2,500", "Impact": "Positive", "Importance": "Medium"},
]
sum_df = pd.DataFrame(sum_data)
st.table(sum_df) 