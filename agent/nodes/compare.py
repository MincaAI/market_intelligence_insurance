import os
from typing import Dict, Any
from ..state import CompareState
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_comparison(state: CompareState) -> CompareState:
    """
    Node for the final comparison between AXA and Generali.
    """
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Create the comparison prompt in English
        comparison_prompt = f"""
You are an expert in TC insurance. You are comparing two contracts on the same topic (e.g., liability) for a professional use case.

Here are the search results from your two insurer agents:

AXA:
{state['axa_result']}

Generali:
{state['generali_result']}

Your mission:
Anlayze what seems to be the best options.

### Constraints:
- Do not make any assumptions: base your analysis only on the provided texts.
- Use a clear, professional, and factual tone.
- Do not recommend an insurer overall: analyze **element by element**.
- **Always answer in English.**

2. **Summary (max 5 lines)**:
Present the main differences and contractual advantages identified, without recommending an insurer overall.
"""
        
        # Generate the comparison with OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert in car insurance. Create clear and structured tables to compare insurance products. Always answer in English."},
                {"role": "user", "content": comparison_prompt}
            ],
            temperature=0.1,
            max_tokens=2000
        )
        
        # Extract the response
        comparison_result = response.choices[0].message.content
        
        # Update state
        state["comparison"] = comparison_result
        
        return state
        
    except Exception as e:
        state["comparison"] = f"Error during comparison: {str(e)}"
        return state