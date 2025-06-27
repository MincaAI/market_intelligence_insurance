import streamlit as st
import pandas as pd
import os
from openai import OpenAI

st.set_page_config(page_title="High Level Comparison", page_icon="🏆", initial_sidebar_state="expanded")
st.title("🏆 High Level Comparison: Generali Strengths & Weaknesses")

st.markdown("""
Once the Excel comparison tables are generated for all insurers, this section enables automated high-level analysis. 
Our AI reviews the structured data to extract actionable insights and strategic recommendations for Generali. 
You will be able to see where Generali stands out, where improvements are needed, and what competitive moves matter most. 

""")

# Add selector for insurance type
insurance_type = st.radio("Select Insurance Type:", ("Car", "Travel"))
product = insurance_type.lower()

# Determine the correct Excel report path
if product == "car":
    data_path = "data/car_comparison_report.xlsx"
else:
    data_path = "data/travel_comparison_report.xlsx"

if os.path.exists(data_path):
    if st.button("Compare"):
        df = pd.read_excel(data_path)
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        if product == "car":
            tc_prompt = (
                "You are a senior insurance product analyst working for Generali.\n\n"
                "You have received a structured comparison table between Generali's car insurance product and a competitor's product. Your task is to produce a clear, high-level comparison report designed for Generali's product managers.\n\n"
                "👉 Your output must contain:\n\n"
                "1️⃣ **Comparison Table (Markdown format)**\n"
                "- Define high-level criteria that seems relevant to position Generali vs competitor\n"
                "- For each criterion that you choose, provide:\n"
                "   • Generali's value\n"
                "   • Competitor's value\n"
                "   • A 'Comparison Insight' column: in **one impactful sentence**, state the key difference and what it means for Generali (better / weaker / similar / differentiated).\n\n"
                "2️⃣ **Executive Summary (max 5 bullet points)**\n"
                "- Highlight Generali's key strengths versus the competitor.\n"
                "- Point out clear weaknesses or competitive risks.\n"
                "- Identify any major differentiators or opportunities visible in the data.\n"
                "- Make it concise, strategic, and actionable for Generali's product team.\n\n"
                "✅ Base your analysis strictly on the provided data — no assumptions, no generic statements.\n"
                "✅ If two values are similar, clearly say so in the Comparison Insight.\n"
                "✅ Structure everything in clean English, ready for direct reuse in a business report.\n\n"
                f"Here is the provided comparison table:\n\n{df.to_markdown(index=False)}"
            )
        else:
            tc_prompt = (
                "You are a senior insurance product analyst working for Generali.  \n\n"
                "You have received as input a structured Excel file comparing two insurance products Travel (Generali's product and a competitor's).  \n\n"
                "👉 Your task is to produce the best possible output for Generali's product team:  \n\n"
                "1️⃣ **Comparison Table **  \n"
                "Create a clear, readable table comparing the two products on key criteria:  \n"
                "- Coverage elements (what is covered, limits)  \n"
                "- Exclusions  \n"
                "- Deductibles  \n"
                "- Premiums / pricing  \n"
                "- Compensation limits  \n"
                "- Special conditions  \n\n"
                "- If a criteria is not here, don't put it ! only put criteria relevant"
                "   • A 'Comparison Insight' column: in **one impactful sentence**, state the key difference and what it means for Generali (better / weaker / similar / differentiated).\n\n"
                "Put the criteria in rows, insurers in columns.  \n\n"
                "2️⃣ **Executive Summary (3-5 bullet points)**  \n"
                "Write a brief summary that highlights:  \n"
                "- Where Generali's product is stronger  \n"
                "- Where Generali is weaker or at risk  \n"
                "- Any major differentiators or innovations from the competitor  \n"
                "- Key opportunities or threats  \n"
                "- What deserves immediate attention from the product team  \n\n"
                "3️**Tone and format**  \n"
                " The output is for Generali's product managers — it must be precise, business-relevant, and immediately actionable.  \n"
                " Avoid generic statements; base your analysis strictly on the provided data.  \n"
                " If the Excel contains gaps or inconsistencies, mention them clearly.  \n\n"
                "Output everything in **English**, structured for easy reuse in a business document.  \n\n"
                "Your goal: provide an output that helps the team improve Generali's product positioning at a glance.  \n\n"
                f"{df.to_markdown(index=False)}"
            )

        tc_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert in insurance product analysis."},
                {"role": "user", "content": tc_prompt}
            ],
            temperature=0.2,
            max_tokens=1200
        )
        tc_analysis = tc_response.choices[0].message.content
        st.subheader("Comparison of Terms & Conditions (T&Cs) and Executive Summary")
        st.markdown(tc_analysis)
else:
    st.error(f"Excel report not found at {data_path}") 