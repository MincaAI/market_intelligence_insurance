import streamlit as st
import os
import requests
import openai
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

st.title("📰 Market News Analysis")

st.markdown("""
Analyze recent competitor market news and compare Generali's insurance positioning. Focused, high-level insights for decision makers.
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
                    f"Today is {current_date}. You are a senior market intelligence analyst for Generali.\n\n"
                    "Your job is to track recent, business-critical developments from Generali’s main competitors in Switzerland "
                    "(AXA Switzerland, Zurich Insurance, Allianz Switzerland).\n\n"
                    "Focus only on the last 30 days and only include facts about:\n"
                    "- product launches or product changes\n"
                    "- pricing updates\n"
                    "- partnerships or M&A\n"
                    "- regulatory changes\n"
                    "- major claims or incidents\n\n"
                    "Exclude generic statements. Provide a short bullet list (max 5 points) of news items that matter to Generali’s business and could impact strategic decisions."
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
        f"Today is {current_date}. You are an expert in insurance market positioning working for Generali.\n\n"
        f"Based on the news below, write a concise market news summary for Generali Switzerland ({product} insurance). "
        f"Highlight competitive moves, threats, or opportunities. Structure it as:\n"
        f"- Key competitor moves (AXA, Zurich, Allianz)\n"
        f"- Implications for Generali’s strategy\n\n"
        f"Keep it under 5 bullet points. Prioritize clarity and relevance for C-level executives.\n\n"
        f"Market news:\n{perplexity_response}"
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an insurance market analyst specialized in competitive strategy."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=600
    )
    return response.choices[0].message.content.strip()

if st.button("Run market news mapping"):
    if product == "car":
        query = "recent car insurance news Switzerland AXA Zurich Allianz last 30 days"
    else:
        query = "recent travel insurance news Switzerland AXA Zurich Allianz last 30 days"
    result = run_perplexity_query(query, current_date)
    if result:
        answer = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        if answer:
            st.markdown("### Structured Market Report (LLM)")
            summary = summarize_with_llm(answer, product, current_date)
            if summary:
                st.markdown(summary)
else:
    st.write("Select a product and click the button to analyze market news.") 