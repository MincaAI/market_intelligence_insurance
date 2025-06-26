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
from fill_in_excel.models import TravelInsuranceProduct, CarCriteria
from typing import get_args

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

def get_ordered_keys_from_model(model_class, prefix=''):
    """Recursively generates ordered, flattened keys from a Pydantic model class."""
    keys = []
    for name, field in model_class.model_fields.items():
        current_key = f"{prefix}.{name}" if prefix else name
        
        field_type = field.annotation
        
        # Handle Optional[Model] and Union[Model, None]
        type_args = get_args(field_type)
        
        model_in_union = next((arg for arg in type_args if isinstance(arg, type) and issubclass(arg, BaseModel)), None)

        if model_in_union:
            keys.extend(get_ordered_keys_from_model(model_in_union, prefix=current_key))
        elif isinstance(field_type, type) and issubclass(field_type, BaseModel):
            keys.extend(get_ordered_keys_from_model(field_type, prefix=current_key))
        else:
            keys.append(current_key)
    return keys

def flatten_model_for_excel(model, prefix=''):
    """Recursively flattens a Pydantic model for Excel export."""
    data = {}
    if model:
        for field_name, field in model.model_fields.items():
            value = getattr(model, field_name)
            current_path = f"{prefix}.{field_name}" if prefix else field_name
            if isinstance(value, BaseModel):
                data.update(flatten_model_for_excel(value, prefix=current_path))
            else:
                data[current_path] = format_value(value)
    return data

def to_excel(doc1_data, doc2_data, llm, doc1_name, doc2_name):
    """Creates an Excel report with one sheet."""
    output = io.BytesIO()

    def get_insurer_name(filename):
        if "generali" in filename.lower():
            return "Generali"
        if "axa" in filename.lower():
            return "AXA"
        return "Insurer"

    insurer1_name = get_insurer_name(doc1_name)
    insurer2_name = get_insurer_name(doc2_name)

    flat_doc1 = flatten_model_for_excel(doc1_data)
    flat_doc2 = flatten_model_for_excel(doc2_data)

    # Get keys in the order defined by the model
    if isinstance(doc1_data, TravelInsuranceProduct):
        all_keys = get_ordered_keys_from_model(TravelInsuranceProduct)
    elif isinstance(doc1_data, CarCriteria):
        all_keys = get_ordered_keys_from_model(CarCriteria)
    else:
        # Fallback to the old method if the type is unknown
        all_keys = sorted(list(set(flat_doc1.keys()) | set(flat_doc2.keys())))
    
    comparison_data = []
    for key in all_keys:
        val1 = flat_doc1.get(key, "Not Available")
        val2 = flat_doc2.get(key, "Not Available")
        comp = get_detailed_comparison(llm, key, val1, val2, insurer1_name, insurer2_name)
        
        row = {
            'Criteria': key,
            insurer1_name: val1,
            insurer2_name: val2,
            'Comparison': comp
        }
        comparison_data.append(row)

    df_comp = pd.DataFrame(comparison_data)

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_comp.to_excel(writer, index=False, sheet_name='Comparison')
        
    return output.getvalue()


def get_comparison_table(section_title, doc1_section, doc2_section, llm, insurer1_name, insurer2_name):
    """Generates a comparison table for a section of the insurance product."""
    st.header(section_title)
    
    table_data = []
    
    if doc1_section is None and doc2_section is None:
        st.write("Not available in either document.")
        return

    # Use the model class to iterate over fields, not the instance
    model_class = type(doc1_section) if doc1_section is not None else type(doc2_section)

    if issubclass(model_class, BaseModel):
        for field_name, field in model_class.model_fields.items():
            value1 = getattr(doc1_section, field_name, None) if doc1_section else None
            value2 = getattr(doc2_section, field_name, None) if doc2_section else None
            
            # Format values for display
            formatted_value1 = format_value(value1)
            formatted_value2 = format_value(value2)
            
            # Get detailed comparison
            analysis = get_detailed_comparison(llm, field_name, value1, value2, insurer1_name, insurer2_name)
            
            table_data.append([
                field_name.replace('_', ' ').title(),
                formatted_value1,
                formatted_value2,
                analysis
            ])
    else:
        # Handle simple fields
        formatted_value1 = format_value(doc1_section)
        formatted_value2 = format_value(doc2_section)
        analysis = get_detailed_comparison(llm, section_title, doc1_section, doc2_section, insurer1_name, insurer2_name)
        table_data.append([
            section_title,
            formatted_value1,
            formatted_value2,
            analysis
        ])

        
    df = pd.DataFrame(table_data, columns=["Criterion", insurer1_name, insurer2_name, "Analysis"])
    
    st.dataframe(df)

if st.button("Compare"):
    if selected_path1 and selected_path2:
        st.success("Both files uploaded successfully!")

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

            # Use the model class for iteration
            for field_name, field in doc1_data.__class__.model_fields.items():
                doc1_section = getattr(doc1_data, field_name, None)
                doc2_section = getattr(doc2_data, field_name, None)
                insurer1_name = "Generali" if "generali" in selected_path1.lower() else "AXA" if "axa" in selected_path1.lower() else "Insurer 1"
                insurer2_name = "Generali" if "generali" in selected_path2.lower() else "AXA" if "axa" in selected_path2.lower() else "Insurer 2"
                get_comparison_table(field_name.replace('_', ' ').title(), doc1_section, doc2_section, llm, insurer1_name, insurer2_name)

            excel_data = to_excel(doc1_data, doc2_data, llm, selected_path1, selected_path2)
            st.download_button(
                label="Download Full Report as Excel",
                data=excel_data,
                file_name=f"{insurance_type.lower()}_comparison_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("Could not generate a comparison. Please check the documents and try again.")
    else:
        st.error("Please select two PDF files to compare.")
