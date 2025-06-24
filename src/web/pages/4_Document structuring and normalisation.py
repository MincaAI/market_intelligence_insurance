from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import fitz  # PyMuPDF
import concurrent.futures

st.title("Document structuring and normalisation")

insurance_type = st.radio("Select Insurance Type:", ("Car", "Travel"))

col1, col2 = st.columns(2)

with col1:
    st.header("Document 1")
    uploaded_file1 = st.file_uploader("Upload the first PDF document", type="pdf", key="struct_file1")

with col2:
    st.header("Document 2")
    uploaded_file2 = st.file_uploader("Upload the second PDF document", type="pdf", key="struct_file2")

def get_pdf_text(pdf_doc):
    pdf_bytes = pdf_doc.getvalue()
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                page_texts = list(executor.map(lambda i: doc.load_page(i).get_text(), range(len(doc))))
            return "".join(page_texts)
    except Exception as e:
        st.warning(f"Primary parser (PyMuPDF) failed: {e}.")
        return ""

if uploaded_file1:
    st.subheader("Extracted text from Document 1:")
    doc1_text = get_pdf_text(uploaded_file1)
    st.text_area("Text Document 1", doc1_text, height=300)

if uploaded_file2:
    st.subheader("Extracted text from Document 2:")
    doc2_text = get_pdf_text(uploaded_file2)
    st.text_area("Text Document 2", doc2_text, height=300) 