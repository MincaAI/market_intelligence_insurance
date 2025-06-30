from dotenv import load_dotenv
load_dotenv()

import streamlit as st

st.set_page_config(
    page_title="Market Intelligence for Insurance",
    page_icon="📊",
    layout="wide"
)

# Title and intro
st.title("📊 Insurance Market Intelligence Solution")
st.write("")  # Add vertical space after the title
st.markdown("""
Welcome to the Market Intelligence Dashboard!

This demo introduces the foundations of MincaAI's approach to help any insurer monitor competitors, automate product positioning vs competition and deliver key insights.

The MVP lays the groundwork for:
• Automated retrieval of T&Cs.  
• Structuring and normalising insurance documents.  
• Comparative product analysis.  
• Tailored reporting for different stakeholders.
""")

st.divider()

# Overview cards
col1, col2, col3 = st.columns(3)
with col1:
    st.success("**T&Cs Scraper**\n\nExtracts and monitors competitors' T&Cs.")
with col2:
    st.warning("**Doc normalisationr**\n\nPrepare the ground for T&Cs comparison")
with col3:
    st.info("**Product Comparator**\n\nCompares competitors' offer against others's offers.")

st.divider()

# Call to action
st.markdown("➡️ Use the **sidebar** to access the different modules:")

st.markdown("""
- **T&C Extraction** – scrape and track AVBs 
- **Document Normalization** – align unstructured text to comparison format 
- **Insurance Comparison** – benchmark competitors' products 
- **Fine-Grain Comparison** – highlight clause-level differences
- **Review Analysis** – monitor public feedback on competitors  

""")

st.write("")  # Add vertical space before the caption
st.caption("Built with ❤️ by MincaAI")
