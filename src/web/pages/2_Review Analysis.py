# Review Analysis
import streamlit as st
import os
import json
import subprocess
import pandas as pd
import openai
from dotenv import load_dotenv
import re
import altair as alt

load_dotenv()

PRODUCTS = ["Car Insurance", "Travel Insurance"]
ASSURERS = ["generali", "axa", "allianz", "baloise"]  # Adapt if you add more in the pipeline

# Fonction pour extraire la note exacte via GPT-4o
@st.cache_data(show_spinner=False)
def extract_score_with_llm(raw_text):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "No API key found."
    client = openai.OpenAI(api_key=api_key)
    prompt = (
        "Extract the global review score (out of 5) from the following text. "
        "The text may be in French. Return only the number (with a dot or comma) or 'N/A'.\n\n"
        f"Text: {raw_text}"
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for extracting review scores."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=20
    )
    return response.choices[0].message.content.strip()

st.title("Customer Reviews Analysis")
st.write("")

insurance_type = st.radio("Select Insurance Type:", ("Car", "Travel"))
product = insurance_type.lower()

# Load the JSON if it exists
recap_path = os.path.join("src", "data", "reviews_screenshots", "recap_reviews.json")
if os.path.exists(recap_path):
    with open(recap_path, "r", encoding="utf-8") as f:
        reviews = json.load(f)
    st.header(f"{product.title()} insurance reviews")
    table_data = []
    for assurer in ASSURERS:
        key = f"{assurer}_{product}"
        info = reviews.get(key, {})
        raw = info.get("raw", "")
        if raw and raw != "-":
            score = extract_score_with_llm(raw)
        else:
            score = "N/A"
        table_data.append({
            "Insurer": assurer.capitalize(),
            "Raw JSON": raw,
            "Exact score (LLM)": score
        })
    df = pd.DataFrame(table_data)

    if "llm_scores" not in st.session_state:
        st.session_state.llm_scores = {}

    def extract_all_scores():
        for idx, row in df.iterrows():
            raw = row["Raw JSON"]
            if raw and raw != "-":
                score = extract_score_with_llm(raw)
            else:
                score = "N/A"
            st.session_state.llm_scores[row["Insurer"]] = score

    if st.button("Extract all scores (LLM)"):
        with st.spinner("Extracting all scores with GPT-4o..."):
            extract_all_scores()

    # Update DataFrame with extracted scores if available
    for idx, row in df.iterrows():
        insurer = row["Insurer"]
        score = st.session_state.llm_scores.get(insurer, "")
        df.at[idx, "Exact score (LLM)"] = score

    # Uniformiser le format des scores extraits (toujours float avec point)
    for idx, row in df.iterrows():
        score_str = str(row["Exact score (LLM)"]).replace(",", ".")
        match = re.search(r"(\d+(?:\.\d+)?)", score_str)
        if match:
            df.at[idx, "Exact score (LLM)"] = str(float(match.group(1)))
        else:
            df.at[idx, "Exact score (LLM)"] = "N/A"

    # Ajouter une colonne couleur : rouge pour Generali, bleu sinon (pour le graphique uniquement)
    chart_df = df[["Insurer", "Exact score (LLM)"]].copy()
    chart_df["Score"] = [float(x) if x != "N/A" else 0 for x in chart_df["Exact score (LLM)"]]
    chart_df["Color"] = ["#d62728" if insurer == "Generali" else "#1f77b4" for insurer in chart_df["Insurer"]]

    # Affichage du tableau sans la colonne 'Color'
    df_display = df.drop(columns=["Color"], errors="ignore").rename(columns={"Raw JSON": "Extracted info from websites"})
    st.dataframe(df_display, use_container_width=True, hide_index=True)

    st.subheader("Global car review comparison")
    # Altair chart
    chart = alt.Chart(chart_df).mark_bar().encode(
        x=alt.X('Insurer', sort=None, axis=alt.Axis(title=None, labelAngle=0, labelFontSize=20)),
        y=alt.Y('Score', axis=alt.Axis(title=None, grid=False, labels=False, ticks=False), scale=alt.Scale(domain=[0, 7])),
        color=alt.Color('Color:N', scale=None, legend=None),
        tooltip=['Insurer', 'Score']
    ).properties(
        width=500, height=350
    )
    # Add text above bars (taille réduite)
    text = alt.Chart(chart_df).mark_text(
        align='center',
        baseline='bottom',
        dy=-10,
        fontSize=24,
        fontWeight='bold'
    ).encode(
        x=alt.X('Insurer', sort=None),
        y=alt.Y('Score'),
        text=alt.Text('Score', format='.1f')
    )
    # Remove background and grid
    final_chart = (chart + text).configure_view(
        strokeWidth=0,
        fill=None
    ).configure_axis(
        grid=False
    )
    st.altair_chart(final_chart, use_container_width=True)

    # Affichage des screenshots pour chaque assureur
    st.subheader("Screenshots of review pages")
    for assurer in ASSURERS:
        img_path = f"src/data/reviews_screenshots/{assurer}/{product}_insurance_note.png"
        if os.path.exists(img_path):
            st.markdown(f"**{assurer.capitalize()}**")
            st.image(img_path, use_column_width=True)
        else:
            st.markdown(f"**{assurer.capitalize()}**: No screenshot found.")
else:
    st.info("No review results found. Please run the pipeline.") 