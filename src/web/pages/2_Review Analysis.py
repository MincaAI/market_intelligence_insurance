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

PRODUCTS = ["car", "travel"]
ASSURERS = ["generali", "axa", "allianz"]  # Baloise removed

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

st.title("⭐ Global review comparison")
st.markdown("**How does Generali's reputation compare?**  ")
st.markdown("A snapshot of customer sentiment across major competitors.")

# Product selection
product = st.radio("Select product:", PRODUCTS, index=None, key="product_radio")

# Only show the button if a product is selected
if product:
    if st.button(f"Scrape and analyze {product} reviews"):
        # Run the scraping pipeline for the selected product
        with st.spinner(f"Scraping and extracting reviews for {product}..."):
            # Run each review script for the selected product
            for script in ["allianz_reviews.py", "axa_reviews.py", "generali_reviews.py"]:
                subprocess.run(["python3", f"src/scrapers/reviews/{script}", "--product", product], check=False)
            # Then run the pipeline to aggregate results
            subprocess.run(["python3", "src/scrapers/reviews/pipeline_reviews.py", "--product", product], check=False)

        # Load the JSON if it exists
        recap_path = os.path.join("src", "data", "reviews_screenshots", "recap_reviews.json")
        if os.path.exists(recap_path):
            with open(recap_path, "r", encoding="utf-8") as f:
                reviews = json.load(f)
            st.header(f"{product.title()} reviews")
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
                    "Extracted info from websites": raw,
                    "Exact score (LLM)": score
                })
            df = pd.DataFrame(table_data)

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

            st.dataframe(df, use_container_width=True, hide_index=True)

            st.subheader("Global review comparison")
            # Altair chart
            chart = alt.Chart(chart_df).mark_bar().encode(
                x=alt.X('Insurer', sort=None, axis=alt.Axis(title=None, labelAngle=0, labelFontSize=20)),
                y=alt.Y('Score', axis=alt.Axis(title=None, grid=False, labels=False, ticks=False), scale=alt.Scale(domain=[0, 7])),
                color=alt.Color('Color:N', scale=None, legend=None),
                tooltip=['Insurer', 'Score']
            ).properties(
                width=500, height=350
            )
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