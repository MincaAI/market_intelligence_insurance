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
You are an expert in car insurance. You are comparing two contracts on the same topic (e.g., liability) for a professional use case.

Here are the search results from your two insurer agents:

AXA:
{state['axa_result']}

Generali:
{state['generali_result']}

Your mission:

1. Analyze the coverages, exclusions, limitations, and conditions of each insurer.
2. Compare each element rigorously.
3. For **each row**, determine which contract is more advantageous or protective for the insured.
4. If neither option is clearly better, write: "Equivalent".
5. Make the comparison as detailed as possible, and provide as many comparison points as possible in the table.

### Constraints:
- Do not make any assumptions: base your analysis only on the provided texts.
- Use a clear, professional, and factual tone.
- Do not recommend an insurer overall: analyze **element by element**.
- **Always answer in English.**

### Output format (mandatory):

1. **Comparison table**:

| Element analyzed        | AXA                                      | Generali                                 | Best choice                             |
|------------------------|-------------------------------------------|-------------------------------------------|------------------------------------------|
| Element A   | ...                                       | ...                                       | AXA / Generali / Equivalent              |
| Element B   | ...                                       | ...                                       | ...                                      |
| Element C   | ...                                       | ...                                       | ...                                      |
| Element D   | ...                                       | ...                                       | ...                                      |
| Element E   | ...                                       | ...                                       | ...                                      |
| Element F   | ...                                       | ...                                       | ...                                      |
| Element G   | ...                                       | ...                                       | ...                                      |
| Element H   | ...                                       | ...                                       | ...                                      |
| Element I   | ...                                       | ...                                       | ...                                      |
| Element J   | ...                                       | ...                                       | ...                                      |

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