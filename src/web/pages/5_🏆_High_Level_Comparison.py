import streamlit as st
import pandas as pd
import os
from openai import OpenAI

st.set_page_config(page_title="High Level Comparison", page_icon="🏆", initial_sidebar_state="expanded")
st.title("🏆 High Level Comparison: Generali Strengths & Weaknesses")

# Load the Excel report
data_path = "data/travel_comparison_report.xlsx"
if os.path.exists(data_path):
    df = pd.read_excel(data_path)
    st.subheader("Comparison Report (Excel)")
    st.dataframe(df)

    # Improved prompt for a visually structured answer
    prompt = (
        "You are an insurance market analyst. Based on the following comparison report, "
        "identify the main strengths and weaknesses of Generali compared to its competitors. "
        "Return your answer in two sections, each with a clear emoji and title:\n"
        "🟢 Strengths\n🔴 Weaknesses\n\n"
        "Be concise and focus on actionable insights for Generali's management.\n\n"
        f"{df.to_markdown(index=False)}"
    )

    # Call the agent (OpenAI)
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert insurance analyst."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=600
    )
    summary = response.choices[0].message.content

    st.subheader("Summary of Generali's Strengths & Weaknesses")
    st.markdown(summary)
else:
    st.error(f"Excel report not found at {data_path}") 