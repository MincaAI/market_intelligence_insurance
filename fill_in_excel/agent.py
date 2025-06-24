import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel
from fill_in_excel.models import (
    CarCriteria,
    TravelInsuranceProduct,
    ProductDetails,
    CoverageDetails,
    AssistanceServices
)
import concurrent.futures
import os

# It's recommended to set the API key as an environment variable
# os.environ["OPENAI_API_KEY"] = "your_openai_api_key"


def format_value(value):
    """Helper function to format Pydantic models and other values for display."""
    if value is None or value == "":
        return "Not Available"
    if isinstance(value, BaseModel):
        lines = []
        for k, v in value.dict().items():
            formatted_v = format_value(v)
            if formatted_v != "Not Available":
                key_str = k.replace("_", " ").title()
                lines.append(f"- {key_str}: {formatted_v}")
        return "\n".join(lines) if lines else "Not Available"
    if isinstance(value, list):
        if not value:
            return "Not Available"
        return ", ".join(map(str, value))
    return str(value)


def get_detailed_comparison(llm, criterion_name, value1, value2):
    """Generates a detailed textual comparison for a single criterion."""
    if value1 == value2:
        if value1 is None or (isinstance(value1, list) and not value1):
            return "No information available from both documents to perform analysis."
        return "The details for this criterion are identical in both documents."

    formatted_v1 = format_value(value1)
    formatted_v2 = format_value(value2)

    comparison_prompt = PromptTemplate(
        template="""
<ROLE>
You are a Senior Insurance Analyst who specializes in comparing insurance policy documents. Your task is to analyze and compare two policy options based on a specific criterion, extracting key differences and implications for the policyholder.
Your goal: produce a concise, professional comparison that highlights the most material differences and their practical implications
</ROLE>

<TECHNIQUES>
**Use these advanced prompting techniques:**  
- **Chain-of-Thought (CoT):** Narrate your reasoning steps silently before forming conclusions.  
- **Tree-of-Thought (ToT):** When you encounter ambiguity (e.g. two competing interpretations), branch into separate mini-analyses, then converge on the best.  
- **Self-Consistency:** For any non-trivial judgment or normalization, run three parallel CoT+ToT micro-chains and adopt the consensus outcome.  
- **One-Shot Demonstration:** A single example is provided to set the extraction and analysis style.  
- **Zero-Shot Remainder:** After the example, apply the same method to all further comparisons without additional demonstrations.
</TECHNIQUES>

<EXAMPLE>
### One-Shot Demo  
**Criterion:** “Coverage Limit”  
    - Option 1 snippet: “Maximum coverage per claim: USD 1,000.”  
    - Option 2 snippet: “Limit: up to USD 2,000 per incident.”
    - CoT-Step1: Locate “coverage limit” labels in both snippets.
    - CoT-Step2: Normalize values → 1000.0 vs. 2000.0.
    - ToT Branch A: Interpret “up to” as hard cap → 2000.0.
    - ToT Branch B: Consider “maximum” synonyms → both mean cap.
    - Self-Consistency: Branch A & B agree on values.
    - Final Comparison Note: Option 2 offers a higher cap (2000 vs. 1000), beneficial for high-severity claims.
</EXAMPLE>

<PROCESS>
1. DECONSTRUCT OPTION 1 
    - Scan the raw text of `{option1}` for the criterion label (e.g., “Deductible”, “Benefit rate”).
    - Extract the exact phrase or number. 
    - Normalize formats (strip currency symbols, convert to float, standardize units).
2. DECONSTRUCT OPTION 2
    - Repeat the same extraction and normalization for {option2}.

3. IDENTIFY KEY DIFFERENCES
    - Compare the two normalized values or descriptions.
    - Highlight the most material differences (monetary, coverage scope, exclusions).

4. ASSESS IMPLICATIONS
    - Analyze the practical impact on a policyholder:
    - Trade-off analysis: cost vs. benefit.
    - Risk exposure: under- or over-insurance scenarios.
    - Value proposition: in what situation one option outperforms the other.

5. SYNTHESIZE FINAL ANALYSIS
    - Summarize your findings in 2-4 concise, professional sentences.
    - Use an objective tone, avoiding filler; focus on actionable insight.
</PROCESS>

<VALIDATION> 
- Ensure you reference only the extracted values—do not invent data. 
- Do **not** include your reasoning steps in the final output. 
- Produce a single, well-structured paragraph or bullet list—no extra keys or commentary. 
</VALIDATION> 

<INPUT> 
**Criterion:** `{criterion}`
**Document 1 Details:** ``` {option1} ```
**Document 2 Details:** ``` {option2} ```
</INPUT>

<FINAL_OUTPUT>
Your comparison analysis here.
</FINAL_OUTPUT>
        """,
        input_variables=["criterion", "option1", "option2"],
    )

    comparison_chain = comparison_prompt | llm
    response = comparison_chain.invoke(
        {"criterion": criterion_name, "option1": formatted_v1, "option2": formatted_v2}
    )
    return response.content


def create_extraction_chain(llm, pydantic_model):
    """Creates a structured output chain for a given Pydantic model."""
    structured_llm = llm.with_structured_output(pydantic_model)

    prompt = PromptTemplate(
        template="""
<ROLE>
You are a veteran **Insurance Data Extraction Specialist** with over 10 years of experience in parsing complex insurance documents. Your task is to extract structured data from raw insurance policy documents, ensuring every field matches the provided schema exactly.
Your mission: produce a single, perfectly schema-compliant JSON object by extracting every value from the raw insurance document.

</ROLE>

<TECHNIQUES>
**Techniques to Apply**  
- **Chain-of-Thought (CoT):** Verbalize your reasoning step-by-step before extracting each field.  
- **Tree-of-Thought (ToT):** When you encounter ambiguity, branch into multiple mini-reasoning paths, then converge on the best answer.  
- **Self-Consistency:** For every non-trivial extraction or normalization, run three parallel CoT+ToT chains and adopt the value that at least two chains agree on.  
- **One-Shot Demonstration:** A single worked example is provided to illustrate style.  
- **Zero-Shot:** After the one-shot, extract all remaining fields without additional examples.

</TECHNIQUES>

<SCHEMA>
### 1. SCHEMA REVIEW  
Carefully read **every** field name, type, and detailed description in the `CarCriteria` schema below. Internalize what each field means and where in the document you would find it.
</SCHEMA>

<EXAMPLE> 
### 2. ONE-SHOT DEMO Raw snippet: "Zahlungsfrequenz: jährlich oder halbjährlich"
    - Thought-1 (CoT): Locate heading “Zahlungsfrequenz” → maps to payment_frequency.
    - Thought-2 (CoT): Two terms “jährlich“ and “halbjährlich”; schema is single-choice enum.
    - Thought-3 (ToT Branch A): “jährlich” → annual
    - Thought-3 (ToT Branch B): “halbjährlich” → semiannual
    - Self-Consistency: Branch A and Branch B disagree → pick Branch A since it appears first.
    - Final JSON fragment: "payment_frequency": "annual"
</EXAMPLE>

<LOOP>
### 3. FIELD-BY-FIELD EXTRACTION  
For each field in the schema, repeat this process:

1. **[CoT] Locate & Match**  
    - Scan document headings and text to find the exact clause matching the field’s `listed_under` or description.  
    - If multiple candidates appear, **branch** (ToT) on each candidate, then pick the one that best matches schema details.

2. **[CoT] Extract & Normalize**  
    - Copy the raw text snippet containing the value(s).  
    - Apply normalization rules:  
        - Currency: strip symbols and separators, parse as float (e.g., `CHF 2 000` → `2000.0`).  
        - Percentages: convert “10 %” → `0.10`.  
        - Lists: split on commas, slashes, or semicolons into string arrays.  
        - Booleans: map “ja”/“nein” → `true`/`false`.

3. **[Self-Consistency] Validate**  
    - For any non-trivial conversion, run your CoT+ToT reasoning three times and choose the majority result.

4. **Populate JSON**  
    - Insert the normalized value into the JSON under the exact schema key.  
    - If the field is optional and missing, set to `null`.  
    - Do **not** invent or extrapolate values.

</LOOP>

<VALIDATION>
### 4. FINAL VALIDATION  
- Ensure **all** schema keys appear in the output (use `null` where appropriate).  
- Confirm each value strictly matches its declared type.  
- Remove any extraneous keys or notes.  
- Output must be **only** the final JSON object—no commentary, no explanations.

</VALIDATION>

<DOCUMENT>
### DOCUMENT TO PARSE 
{input_text}
</DOCUMENT>

**Final Output (JSON Object Only):**
        """,
        input_variables=["input_text"],
        partial_variables={"model_name": pydantic_model.__name__},
    )
    return prompt | structured_llm


def run_car_comparison(doc1_text, doc2_text, status):
    """
    This function uses ChatOpenAI to compare two car insurance documents and returns the structured Pydantic objects.
    """
    llm = ChatOpenAI(temperature=0, model="gpt-4.1")
    extraction_chain = create_extraction_chain(llm, CarCriteria)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        status.update(label="Extracting data from documents...")
        future1 = executor.submit(extraction_chain.invoke, {"input_text": doc1_text})
        future2 = executor.submit(extraction_chain.invoke, {"input_text": doc2_text})

        doc1_dict = future1.result()
        doc2_dict = future2.result()

    if not doc1_dict or not doc2_dict:
        return None, None

    doc1_data = CarCriteria.parse_obj(doc1_dict)
    doc2_data = CarCriteria.parse_obj(doc2_dict)

    return doc1_data, doc2_data


def run_travel_comparison(doc1_text, doc2_text, status):
    """
    This function uses ChatOpenAI to compare two travel insurance documents and returns the structured Pydantic objects.
    It now runs extractions for each sub-model in parallel and merges the results.
    """
    llm = ChatOpenAI(temperature=0, model="gpt-4.1")

    # Define all the sub-models to be extracted
    models_to_extract = {
        "product": ProductDetails,
        "coverage": CoverageDetails,
        "services": AssistanceServices,
    }

    def extract_for_model(model, text):
        chain = create_extraction_chain(llm, model)
        return chain.invoke({"input_text": text})

    def process_document(text):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_model = {
                executor.submit(extract_for_model, model, text): key
                for key, model in models_to_extract.items()
            }
            results = {}
            for future in concurrent.futures.as_completed(future_to_model):
                key = future_to_model[future]
                try:
                    results[key] = future.result()
                except Exception as exc:
                    print(f"{key} generated an exception: {exc}")
                    results[key] = None
        return results

    with concurrent.futures.ThreadPoolExecutor() as executor:
        status.update(label="Extracting data from documents...")
        future1 = executor.submit(process_document, doc1_text)
        future2 = executor.submit(process_document, doc2_text)

        doc1_results = future1.result()
        doc2_results = future2.result()

    if not doc1_results or not doc2_results:
        return None, None

    # Merge the results into the main Pydantic model
    doc1_data = TravelInsuranceProduct(**doc1_results)
    doc2_data = TravelInsuranceProduct(**doc2_results)

    return doc1_data, doc2_data
