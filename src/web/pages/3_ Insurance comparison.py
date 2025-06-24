import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
import pandas as pd
from PyPDF2 import PdfReader
import io
import fitz  # PyMuPDF
import concurrent.futures
from fill_in_excel.agent import run_car_comparison, run_travel_comparison, get_detailed_comparison, format_value #type: ignore
from pydantic import BaseModel
from langchain_openai import ChatOpenAI

st.title("Detailed Insurance Comparison")
st.write("This page allows you to compare in detail the coverages, prices, exclusions, etc. between different insurers.")

# Insurance type selection
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

# Sélecteur pour Insurer 1
col1, col2 = st.columns(2)
with col1:
    st.header("Insurer 1")
    selected1 = st.selectbox(
        "Select a PDF for Insurer 1",
        [f"{assurer.capitalize()} - {filename}" for assurer, filename, _ in pdf_options],
        key="pdf1"
    )
    selected_path1 = None
    for assurer, filename, path in pdf_options:
        if f"{assurer.capitalize()} - {filename}" == selected1:
            selected_path1 = path
            break

with col2:
    st.header("Insurer 2")
    selected2 = st.selectbox(
        "Select a PDF for Insurer 2",
        [f"{assurer.capitalize()} - {filename}" for assurer, filename, _ in pdf_options],
        key="pdf2"
    )
    selected_path2 = None
    for assurer, filename, path in pdf_options:
        if f"{assurer.capitalize()} - {filename}" == selected2:
            selected_path2 = path
            break

def get_pdf_text_from_path(pdf_path):
    """
    Extracts text from a PDF file path using a two-stage parsing strategy with concurrency.
    """
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                page_texts = list(executor.map(lambda i: doc.load_page(i).get_text(), range(len(doc)))) #type: ignore
            return "".join(page_texts)
    except Exception as e1:
        st.warning(f"Primary parser (PyMuPDF) failed: {e1}. Attempting sequential fallback parser...")
        page_texts = []
        try:
            pdf_doc = io.BytesIO(pdf_bytes)
            pdf_reader = PdfReader(pdf_doc)
            for page in pdf_reader.pages:
                try:
                    page_texts.append(page.extract_text())
                except Exception:
                    page_texts.append("")
            return "".join(page_texts)
        except Exception as e2:
            st.error(f"Both PDF parsers failed. Fallback parser (PyPDF2) error: {e2}")
            return ""

def flatten_model_for_excel(model, prefix=''):
    """Recursively flattens a Pydantic model for Excel export."""
    data = {}
    if model:
        for field_name, field in model.__fields__.items():
            value = getattr(model, field_name)
            current_path = f"{prefix}.{field_name}" if prefix else field_name
            if isinstance(value, BaseModel):
                data.update(flatten_model_for_excel(value, prefix=current_path))
            else:
                data[current_path] = format_value(value)
    return data

def to_excel(doc1_data, doc2_data, llm):
    """Creates an Excel report with three sheets."""
    output = io.BytesIO()
    
    flat_doc1 = flatten_model_for_excel(doc1_data)
    flat_doc2 = flatten_model_for_excel(doc2_data)
    
    df1 = pd.DataFrame(flat_doc1.items(), columns=['Criteria', 'Value'])
    df2 = pd.DataFrame(flat_doc2.items(), columns=['Criteria', 'Value'])
    
    comparison_data = []
    all_keys = sorted(list(set(flat_doc1.keys()) | set(flat_doc2.keys())))
    for key in all_keys:
        val1 = flat_doc1.get(key, "Not Available")
        val2 = flat_doc2.get(key, "Not Available")
        comp = get_detailed_comparison(llm, key, val1, val2)
        comparison_data.append({'Criteria': key, 'Comparison': comp})
    
    df_comp = pd.DataFrame(comparison_data)

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df1.to_excel(writer, index=False, sheet_name='Insurer 1')
        df2.to_excel(writer, index=False, sheet_name='Insurer 2')
        df_comp.to_excel(writer, index=False, sheet_name='Comparison')
        
    return output.getvalue()

if selected_path1 and selected_path2:
    if st.button("Start comparison"):
        st.success("Both PDFs selected successfully!")

        doc1_text = get_pdf_text_from_path(selected_path1)
        doc2_text = get_pdf_text_from_path(selected_path2)

        doc1_data, doc2_data = None, None

        with st.status("Performing analysis and comparison...", expanded=True) as status:
            if insurance_type == "Car":
                doc1_data, doc2_data = run_car_comparison(doc1_text, doc2_text, status)
            else:
                doc1_data, doc2_data = run_travel_comparison(doc1_text, doc2_text, status)
            status.update(label="Analysis complete!", state="complete", expanded=False)

        if doc1_data and doc2_data:
            llm = ChatOpenAI(temperature=0, model="gpt-4.1")
            st.header("Comparison Summary")
            for field_name, field in doc1_data.__fields__.items():
                with st.expander(f"### {field_name.replace('_', ' ').title()}"):
                    col1, col2, col3 = st.columns(3)
                    value1 = getattr(doc1_data, field_name)
                    value2 = getattr(doc2_data, field_name)
                    with col1:
                        st.subheader("Insurer 1")
                        st.markdown(f"**{field_name.replace('_', ' ').title()}**")
                        st.markdown(format_value(value1))
                    with col2:
                        st.subheader("Insurer 2")
                        st.markdown(f"**{field_name.replace('_', ' ').title()}**")
                        st.markdown(format_value(value2))
                    with col3:
                        st.subheader("Analysis")
                        comparison_text = get_detailed_comparison(llm, field_name, value1, value2)
                        st.markdown(comparison_text)
            excel_data = to_excel(doc1_data, doc2_data, llm)
            st.download_button(
                label="Download Full Report as Excel",
                data=excel_data,
                file_name=f"{insurance_type.lower()}_comparison_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("Could not generate a comparison. Please check the documents and try again.")
