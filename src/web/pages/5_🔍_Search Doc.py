# Document Search & Comparison
import streamlit as st
import sys
import os
from pathlib import Path

# Add root directory to path for module imports
root_path = Path(__file__).parent.parent.parent.parent
sys.path.append(str(root_path))

from agent.graph import compile_agent
from agent.state import CompareState

st.set_page_config(initial_sidebar_state="expanded")

def run_agent_comparison(initial_state: CompareState):
    """
    Run the comparison agent and return results.
    """
    try:
        agent = compile_agent()
        final_state = agent.invoke(initial_state)
        return final_state
    except Exception as e:
        st.error(f"Error running the agent: {str(e)}")
        return None

def display_chunk_results(title: str, result_text: str, color: str):
    """
    Display chunk results in a formatted and robust way.
    """
    st.markdown(f"### {title}")
    if "No results found" in result_text or "Aucun résultat trouvé" in result_text:
        st.warning("No results found.")
        return
    chunks = result_text.strip().split('\n\n')[1:]
    if not chunks:
        st.info(result_text)
        return
    for chunk_str in chunks:
        if not chunk_str.strip():
            continue
        html_chunk = chunk_str.replace('\n', '<br>')
        st.markdown(
            f"<div style='background-color: {color}20; padding: 10px; border-radius: 5px; margin: 5px 0;'>{html_chunk}</div>",
            unsafe_allow_html=True
        )

def main():
    st.set_page_config(
        page_title="AXA vs Generali Document Search",
        page_icon="🔍",
        layout="wide"
    )
    st.title("🔍 Search Insurance Documents")

    st.markdown("""
    Easily find and compare specific information from two insurance documents, side by side. 

    This tool helps you quickly locate key details, clauses, or coverage points across different insurers—saving you time and making analysis effortless.
    """)

    # Section 1: Select insurance type
    st.header("1. Please select insurance type")
    insurance_type = st.radio("Select Insurance Type:", ("Car", "Travel"))
    product_type = insurance_type.lower()

    # Section 2: User input and button
    st.header(f"2. What do you want to compare?")
    user_query = st.text_area(
        "Enter your comparison topic here:",
        placeholder=f"E.g.: What are the deductibles for {insurance_type.lower()} insurance?",
        height=100,
        label_visibility="collapsed"
    )
    run_button = st.button(
        "🚀 Run Comparison",
        type="secondary"
    )

    # Section 3: Run and display results
    if run_button and user_query.strip():
        st.markdown("---")
        with st.spinner("🔄 Running comparison agent..."):
            initial_state = CompareState(
                user_input=user_query,
                product=product_type,
                axa_result="",
                generali_result="",
                comparison=""
            )
            results = run_agent_comparison(initial_state)
        if results:
            st.header("📊 Agent Results")
            col1, col2 = st.columns(2)
            with col1:
                display_chunk_results("🔵 AXA Agent", results['axa_result'], "#0066cc")
            with col2:
                display_chunk_results("🟢 Generali Agent", results['generali_result'], "#00cc66")
            st.markdown("---")
            st.subheader("📋 Comparison Table")
            if results['comparison']:
                st.markdown(results['comparison'])
            else:
                st.warning("No comparison generated.")
            st.markdown("---")
            st.header("ℹ️ Technical Information")
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Query:** {user_query}")
            with col2:
                st.info("**Status:** ✅ Completed")
    elif run_button and not user_query.strip():
        st.error("❌ Please enter a question before running the comparison.")

if __name__ == "__main__":
    main() 