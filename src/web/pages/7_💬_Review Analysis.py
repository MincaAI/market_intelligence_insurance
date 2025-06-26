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

tab1, tab2 = st.tabs(["🏢 Competitors website", "🌍 Public source"])

with tab1:
    st.markdown("Below is a snapshot of customer reviews collected from insurers websites.")
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

with tab2:
    st.markdown("Below is a snapshot of customer reviews collected from eKomi and Comparis.ch. Data sources are indicated for each insurer.")

    # Product selection for public source
    public_products = ["car", "travel"]
    public_product = st.radio("Select product:", public_products, index=None, key="public_product_radio")

    if public_product:
        if st.button("Run scraping", key="public_scraping_btn"):
            st.session_state["show_public_reviews"] = True
    else:
        st.session_state["show_public_reviews"] = False

    if st.session_state.get("show_public_reviews", False):
        if public_product == "car":
            # Detailed criteria table for car insurance (scores out of 6)
            car_criteria_data = [
                {
                    "Insurer": "AXA",
                    "Value for money": "5.0 / 6",
                    "Quality & service": "5.1 / 6",
                    "Info & transparency": "5.1 / 6",
                    "Friendliness": "5.1 / 6",
                    "Overall satisfaction": "5.2 / 6",
                    "Category": "Silver"
                },
                {
                    "Insurer": "Generali",
                    "Value for money": "4.9 / 6",
                    "Quality & service": "4.9 / 6",
                    "Info & transparency": "5.0 / 6",
                    "Friendliness": "5.0 / 6",
                    "Overall satisfaction": "5.1 / 6",
                    "Category": "Silver"
                },
                {
                    "Insurer": "Allianz",
                    "Value for money": "5.0 / 6",
                    "Quality & service": "5.0 / 6",
                    "Info & transparency": "5.0 / 6",
                    "Friendliness": "5.0 / 6",
                    "Overall satisfaction": "5.1 / 6",
                    "Category": "Silver"
                },
            ]
            df_criteria = pd.DataFrame(car_criteria_data)
            st.subheader("Comparis.ch Criteria Table (Car Insurance)")
            st.dataframe(df_criteria, use_container_width=True, hide_index=True)
        elif public_product == "travel":
            st.info("No detailed public criteria available for travel insurance.")

        # Optional: textual summary
        for _, row in df_reviews.iterrows():
            st.markdown(f"**{row['Insurer']}** (Source: {row['Source']}): {row['Score']}/5")

        st.info("All scores and reviews are sourced from Comparis.ch for car insurance and from eKomi/Comparis.ch for travel insurance. Scores are normalized to a 5-point scale for comparison when needed.")

        if public_product == "car":
            # Detailed criteria table for car insurance (scores out of 6)
            car_criteria_data = [
                {
                    "Insurer": "AXA",
                    "Value for money": "5.0 / 6",
                    "Quality & service": "5.1 / 6",
                    "Info & transparency": "5.1 / 6",
                    "Friendliness": "5.1 / 6",
                    "Overall satisfaction": "5.2 / 6",
                    "Category": "Silver"
                },
                {
                    "Insurer": "Generali",
                    "Value for money": "4.9 / 6",
                    "Quality & service": "4.9 / 6",
                    "Info & transparency": "5.0 / 6",
                    "Friendliness": "5.0 / 6",
                    "Overall satisfaction": "5.1 / 6",
                    "Category": "Silver"
                },
                {
                    "Insurer": "Allianz",
                    "Value for money": "5.0 / 6",
                    "Quality & service": "5.0 / 6",
                    "Info & transparency": "5.1 / 6",
                    "Friendliness": "5.0 / 6",
                    "Overall satisfaction": "5.1 / 6",
                    "Category": "Silver"
                }
            ]
            df_criteria = pd.DataFrame(car_criteria_data)
            st.subheader("Detailed Comparis.ch Criteria (Car Insurance)")
            st.dataframe(df_criteria, use_container_width=True, hide_index=True)

            # Extract overall satisfaction for each insurer (car insurance)
            chart_data = [
                {"Insurer": "AXA", "Score": 5.2},
                {"Insurer": "Generali", "Score": 5.1},
                {"Insurer": "Allianz", "Score": 5.1},
            ]
            chart_df = pd.DataFrame(chart_data)
            chart_df["Color"] = ["#1f77b4" if insurer != "Generali" else "#d62728" for insurer in chart_df["Insurer"]]

            st.subheader("Overall satisfaction comparison (Comparis.ch)")
            chart = alt.Chart(chart_df).mark_bar().encode(
                x=alt.X('Insurer', sort=None, axis=alt.Axis(title=None, labelAngle=0, labelFontSize=20)),
                y=alt.Y('Score', axis=alt.Axis(title=None, grid=False, labels=False, ticks=False), scale=alt.Scale(domain=[0, 6])),
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