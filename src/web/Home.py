from dotenv import load_dotenv
load_dotenv()

import streamlit as st

st.set_page_config(
    page_title="Market Intelligence for Insurance",
    page_icon="📊",
    layout="wide"
)

# Title and intro
st.title("📊 Insurance Market Intelligence Dashboard")
st.markdown("""
Welcome to the internal Market Intelligence tool developed for **Generali**.  
This app helps you monitor competitors' insurance offerings and analyze market trends through automated document analysis and web data extraction.
""")

st.divider()

# Overview cards
col1, col2, col3 = st.columns(3)
with col1:
    st.success("**T&C Scraper**\n\nExtracts and monitors competitors' General Terms & Conditions (AVBs).")
with col2:
    st.warning("**Review Analyzer**\n\nScrapes customer reviews to identify market sentiment and weaknesses.")
with col3:
    st.info("**Product Comparator**\n\nCompares competitors' coverage and pricing against Generali's offers.")

st.divider()

# Call to action
st.markdown("➡️ Use the **sidebar** to access the different analysis modules:")

st.markdown("""
- 🧾 **T&C Extraction** – scrape and track insurance documents (AVBs)  
- 💬 **Review Analysis** – monitor public feedback on competitors  
- 📊 **Insurance Comparison** – benchmark competitors' offers  
- 🧮 **Document Normalization** – align unstructured text to comparison format  
- 🔍 **Fine-Grain Comparison** – highlight clause-level differences
""")

st.caption("Built with ❤️ by MincaAI for Generali.")
