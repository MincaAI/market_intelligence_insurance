import streamlit as st
import os
import requests
import openai
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

st.title("📰 Market News Analysis")

st.markdown("""
Analyze recent market news and compare Generali's insurance products to the market.
""")

PRODUCTS = ["car", "travel"]
product = st.radio("Select product type:", PRODUCTS, index=0)
current_date = datetime.now().strftime('%d %B %Y')

def run_perplexity_query(query, current_date):
    api_key = os.getenv("PERPLEXITY_KEY")
    if not api_key:
        st.error("No Perplexity API key found in environment variable PERPLEXITY_KEY.")
        return None
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    body = {
        "model": "llama-3.1-sonar-small-128k-online",
        "messages": [
            {
                "role": "system",
                "content": (
                    f"Today is {current_date}. Act as a market intelligence analyst.\n\n"
                    "Provide a concise summary of the latest strategic news and business developments involving Generali Switzerland, "
                    "compared to its main competitors (AXA Switzerland, Zurich Insurance, Allianz Switzerland, and others), focusing on the past 3 months.\n\n"
                    "Highlight differences in:\n"
                    "- strategic positioning\n"
                    "- product innovation\n"
                    "- partnerships\n"
                    "- M&A activity\n"
                    "- distribution channels\n"
                    "- ESG initiatives\n"
                    "- customer experience\n\n"
                    "Summarize with clear business insights and strategic implications relevant to C-level executives.\n\n"
                    "Sources must be recent, reliable, and business-relevant. Summarize only what's meaningful for decision-making at the executive level."
                )
            },
            {
                "role": "user",
                "content": query
            }
        ]
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Perplexity API error: {response.status_code} {response.text}")
        return None

def summarize_with_llm(perplexity_response, product, current_date):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("No OpenAI API key found in environment variable OPENAI_API_KEY.")
        return None
    client = openai.OpenAI(api_key=api_key)
    prompt = (
        f"Summarize the following market news into a structured report about recent trends for Generali Switzerland "
        f"({product} insurance). Today is {current_date}. You work for Generali as the market positionning expert for Generali. Focus on key trends, competition.\n\n"
        f"Market news:\n{perplexity_response}"
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert insurance market analyst."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=600
    )
    return response.choices[0].message.content.strip()

if st.button("Run market news mapping"):
    if product == "car":
        query = "how Generali car insurance compare in switzerland to market and competitors"
    else:
        query = "how Generali travel insurance compare in switzerland to market and comeptitors"
    st.markdown(f"**Query sent to Perplexity:** {query}")
    result = run_perplexity_query(query, current_date)
    if result:
        # Try to extract the main answer from Perplexity's response
        answer = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        if answer:
            st.markdown("### Structured Market Report (LLM)")
            summary = summarize_with_llm(answer, product, current_date)
            if summary:
                st.markdown(summary)
else:
    st.write("Select a product and click the button to analyze market news.") 