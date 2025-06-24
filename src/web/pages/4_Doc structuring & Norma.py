from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import fitz  # PyMuPDF
import concurrent.futures
import os
import importlib.util
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0

st.title("🧠 Doc structuring & normalisation")
st.markdown("Turn messy insurance PDFs into structured, comparable data — instantly.")

insurance_type = st.radio("Select Insurance Type:", ("Car", "Travel"))
product = insurance_type.lower()

# Lister tous les PDF disponibles pour chaque assureur
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'documents'))
assureurs = ["generali", "axa", "allianz", "swiss", "baloise"]
pdf_options = []
for assurer in assureurs:
    folder = os.path.join(base_dir, assurer, product)
    if os.path.exists(folder):
        for filename in sorted(os.listdir(folder)):
            if filename.lower().endswith('.pdf'):
                pdf_options.append((assurer, filename, os.path.join(folder, filename)))

col1, col2 = st.columns(2)

with col1:
    st.header("Document 1")
    selected1 = st.selectbox(
        "Select a PDF for Document 1",
        [f"{assurer.capitalize()} - {filename}" for assurer, filename, _ in pdf_options],
        key="struct_pdf1"
    )
    selected_path1 = None
    for assurer, filename, path in pdf_options:
        if f"{assurer.capitalize()} - {filename}" == selected1:
            selected_path1 = path
            break

with col2:
    st.header("Document 2")
    selected2 = st.selectbox(
        "Select a PDF for Document 2",
        [f"{assurer.capitalize()} - {filename}" for assurer, filename, _ in pdf_options],
        key="struct_pdf2"
    )
    selected_path2 = None
    for assurer, filename, path in pdf_options:
        if f"{assurer.capitalize()} - {filename}" == selected2:
            selected_path2 = path
            break

def get_pdf_text_from_path(pdf_path):
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                page_texts = list(executor.map(lambda i: doc.load_page(i).get_text(), range(len(doc))))
            return "".join(page_texts)
    except Exception as e:
        st.warning(f"Primary parser (PyMuPDF) failed: {e}.")
        return ""

run_chunking = st.button("Run chunking")

if run_chunking and (selected_path1 or selected_path2):
    if selected_path1:
        st.subheader("Extracted text from Document 1:")
        doc1_text = get_pdf_text_from_path(selected_path1)
        st.text_area("Text Document 1", doc1_text, height=300)

        # Détection de la langue
        try:
            lang1 = detect(doc1_text)
        except Exception:
            lang1 = "fr"
        lang1 = "en" if lang1 == "en" else "fr"

        # --- LOGIQUE DE CHUNKING ---
        if "generali" in selected_path1.lower():
            spec = importlib.util.spec_from_file_location("generali_chunk_generator", os.path.abspath(os.path.join(os.path.dirname(__file__), '../../processors/chunk_extractors/generali_chunk_generator.py')))
            generali_chunk_generator = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(generali_chunk_generator)
            chunks = generali_chunk_generator.extract_chunks_from_text(doc1_text, os.path.basename(selected_path1), lang=lang1)
            st.markdown(f"**Sections & Subsections (Generali, mapping: {'English' if lang1 == 'en' else 'French'}):**")
            for chunk in chunks:
                st.markdown(f"- **{chunk.get('section', 'Section ?')}**<br/> &nbsp;&nbsp;&nbsp;{chunk.get('subsection', 'Sous-section ?')}", unsafe_allow_html=True)
        elif "axa" in selected_path1.lower():
            spec = importlib.util.spec_from_file_location("axa_chunk_generator", os.path.abspath(os.path.join(os.path.dirname(__file__), '../../processors/chunk_extractors/axa_chunk_generator.py')))
            axa_chunk_generator = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(axa_chunk_generator)
            chunks = axa_chunk_generator.extract_chunks_from_text(doc1_text, os.path.basename(selected_path1))
            st.markdown("**Sections & Subsections (AXA):**")
            for chunk in chunks:
                st.markdown(f"- **{chunk.get('section', 'Section ?')}**<br/> &nbsp;&nbsp;&nbsp;{chunk.get('subsection', 'Sous-section ?')}", unsafe_allow_html=True)
        else:
            st.info("No chunking logic implemented for this insurer.")

    if selected_path2:
        st.subheader("Extracted text from Document 2:")
        doc2_text = get_pdf_text_from_path(selected_path2)
        st.text_area("Text Document 2", doc2_text, height=300)

        try:
            lang2 = detect(doc2_text)
        except Exception:
            lang2 = "fr"
        lang2 = "en" if lang2 == "en" else "fr"

        # --- LOGIQUE DE CHUNKING ---
        if "generali" in selected_path2.lower():
            spec = importlib.util.spec_from_file_location("generali_chunk_generator", os.path.abspath(os.path.join(os.path.dirname(__file__), '../../processors/chunk_extractors/generali_chunk_generator.py')))
            generali_chunk_generator = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(generali_chunk_generator)
            chunks = generali_chunk_generator.extract_chunks_from_text(doc2_text, os.path.basename(selected_path2), lang=lang2)
            st.markdown(f"**Sections & Subsections (Generali, mapping: {'English' if lang2 == 'en' else 'French'}):**")
            for chunk in chunks:
                st.markdown(f"- **{chunk.get('section', 'Section ?')}**<br/> &nbsp;&nbsp;&nbsp;{chunk.get('subsection', 'Sous-section ?')}", unsafe_allow_html=True)
        elif "axa" in selected_path2.lower():
            spec = importlib.util.spec_from_file_location("axa_chunk_generator", os.path.abspath(os.path.join(os.path.dirname(__file__), '../../processors/chunk_extractors/axa_chunk_generator.py')))
            axa_chunk_generator = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(axa_chunk_generator)
            chunks = axa_chunk_generator.extract_chunks_from_text(doc2_text, os.path.basename(selected_path2))
            st.markdown("**Sections & Subsections (AXA):**")
            for chunk in chunks:
                st.markdown(f"- **{chunk.get('section', 'Section ?')}**<br/> &nbsp;&nbsp;&nbsp;{chunk.get('subsection', 'Sous-section ?')}", unsafe_allow_html=True)
        else:
            st.info("No chunking logic implemented for this insurer.") 