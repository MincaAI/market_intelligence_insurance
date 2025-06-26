import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
import io
import fitz  # PyMuPDF
import concurrent.futures
from .agent import run_car_comparison, run_travel_comparison, get_detailed_comparison, format_value
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from .models import TravelInsuranceProduct, CarCriteria
from typing import get_args

st.set_page_config(layout="wide")

st.title("Insurance Comparison")

insurance_type = st.radio("Select Insurance Type:", ("Car", "Travel"))

# Create two columns for file uploads
col1, col2 = st.columns(2)

with col1:
    st.header("Document 1")
    uploaded_file1 = st.file_uploader("Upload the first PDF document", type="pdf", key="file1")

with col2:
    st.header("Document 2")
    uploaded_file2 = st.file_uploader("Upload the second PDF document", type="pdf", key="file2")

def get_pdf_text(pdf_doc):
    """
    Extracts text from a PDF using a two-stage parsing strategy with concurrency.
    """
    pdf_bytes = pdf_doc.getvalue()
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                page_texts = list(executor.map(lambda i: doc.load_page(i).get_text(), range(len(doc)))) #type: ignore
            # st.info("PDF text extracted successfully using the primary parser (PyMuPDF).")
            return "".join(page_texts)
    except Exception as e1:
        st.warning(f"Primary parser (PyMuPDF) failed: {e1}. Attempting sequential fallback parser...")
        page_texts = []
        try:
            pdf_doc.seek(0)
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
        comp = get_detailed_comparison(llm, key, val1, val2, insurer1_name=insurer1_name, insurer2_name=insurer2_name)
        
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


if uploaded_file1 and uploaded_file2:
    st.success("Both files uploaded successfully!")

    doc1_text = get_pdf_text(uploaded_file1)
    doc2_text = get_pdf_text(uploaded_file2)

    doc1_data, doc2_data = None, None

    with st.status("Performing analysis and comparison...", expanded=True) as status:
        if insurance_type == "Car":
            doc1_data, doc2_data = run_car_comparison(doc1_text, doc2_text, status)
        else:
            doc1_data, doc2_data = run_travel_comparison(doc1_text, doc2_text, status)
        status.update(label="Analysis complete!", state="complete", expanded=False)

    if doc1_data and doc2_data:
        llm = ChatOpenAI(temperature=0, model="gpt-4")
        
        st.header("Comparison Summary")
        
        for field_name, field in doc1_data.__class__.model_fields.items():
            with st.expander(f"### {field_name.replace('_', ' ').title()}"):
                col1, col2, col3 = st.columns(3)
                
                value1 = getattr(doc1_data, field_name)
                value2 = getattr(doc2_data, field_name)

                with col1:
                    st.subheader("Document 1")
                    st.markdown(f"**{field_name.replace('_', ' ').title()}**")
                    st.markdown(format_value(value1))

                with col2:
                    st.subheader("Document 2")
                    st.markdown(f"**{field_name.replace('_', ' ').title()}**")
                    st.markdown(format_value(value2))
                
                with col3:
                    st.subheader("Analysis")
                    insurer1_name = "Generali" if "generali" in uploaded_file1.name.lower() else "AXA" if "axa" in uploaded_file1.name.lower() else "Document 1"
                    insurer2_name = "Generali" if "generali" in uploaded_file2.name.lower() else "AXA" if "axa" in uploaded_file2.name.lower() else "Document 2"
                    comparison_text = get_detailed_comparison(llm, field_name, value1, value2, insurer1_name=insurer1_name, insurer2_name=insurer2_name)
                    st.markdown(comparison_text)

        excel_data = to_excel(doc1_data, doc2_data, llm, uploaded_file1.name, uploaded_file2.name)
        st.download_button(
            label="Download Full Report as Excel",
            data=excel_data,
            file_name=f"{insurance_type.lower()}_comparison_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("Could not generate a comparison. Please check the documents and try again.")
