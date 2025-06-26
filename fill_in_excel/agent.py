import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel
from fill_in_excel.models import (
    CarCriteria,
    TravelInsuranceProduct,
    General,
    Liability,
    PartialInsurance,
    FullyComprehensiveInsurance,
    GrossNegligence,
    Compensation,
    ParkingDamage,
    GlassPlus,
    VehicleInterior,
    TiresAndRims,
    VehicleKey,
    ChargingStationWallbox,
    Battery,
    CyberAttacksRemediationCosts,
    ItemsCarried,
    RentalReplacementVehicle,
    Assistance,
    RepairService,
    Accident,
    LegalProtection,
    GeneralPoints,
    GroupOfPeople,
    BasicCoverage,
    AdditionalCoverage,
    OtherBuildingBlocks,
    Summary,
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


def get_detailed_comparison(llm, criterion_name, value1, value2, insurer1_name="Document 1", insurer2_name="Document 2"):
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
You are a Senior Insurance Analyst. Your task is to compare two policy options based on a specific criterion.
Your goal: produce a **concise, direct comparison** that highlights the main differences in 1-2 sentences.
</ROLE>

<INSTRUCTIONS>
- Use the specific insurer names: **{insurer1}** and **{insurer2}**.
- Do NOT use generic terms like "Option 1", "Document 2", or "Product 1".
- Be straight to the point. Focus only on the most material differences.
- Avoid filler words and introductory phrases.
</INSTRUCTIONS>

<EXAMPLE>
**Criterion:** Coverage Limit
**{insurer1} Details:** 1,000 USD
**{insurer2} Details:** 2,000 USD
**Analysis:** {insurer2} offers a higher coverage limit (2,000 USD) compared to {insurer1} (1,000 USD).
</EXAMPLE>

<INPUT> 
**Criterion:** `{criterion}`
**{insurer1} Details:** ``` {option1} ```
**{insurer2} Details:** ``` {option2} ```
</INPUT>

<FINAL_OUTPUT>
Your comparison analysis here.
</FINAL_OUTPUT>
        """,
        input_variables=["criterion", "option1", "option2", "insurer1", "insurer2"],
    )

    comparison_chain = comparison_prompt | llm
    response = comparison_chain.invoke({
        "criterion": criterion_name, 
        "option1": formatted_v1, 
        "option2": formatted_v2,
        "insurer1": insurer1_name,
        "insurer2": insurer2_name
    })
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
    It now runs extractions for each sub-model in parallel and merges the results.
    """
    llm = ChatOpenAI(temperature=0, model="gpt-4.1")

    # Define all the sub-models to be extracted for CarCriteria
    models_to_extract = {
        "general": General,
        "liability": Liability,
        "partial_insurance": PartialInsurance,
        "fully_comprehensive_insurance": FullyComprehensiveInsurance,
        "gross_negligence": GrossNegligence,
        "compensation": Compensation,
        "parking_damage": ParkingDamage,
        "glass_plus": GlassPlus,
        "vehicle_interior": VehicleInterior,
        "tires_and_rims": TiresAndRims,
        "vehicle_key": VehicleKey,
        "charging_station_wallbox": ChargingStationWallbox,
        "battery": Battery,
        "cyber_attacks_remediation_costs": CyberAttacksRemediationCosts,
        "items_carried": ItemsCarried,
        "rental_replacement_vehicle": RentalReplacementVehicle,
        "assistance": Assistance,
        "repair_service": RepairService,
        "accident": Accident,
        "legal_protection": LegalProtection,
    }

    def extract_for_model(model, text):
        chain = create_extraction_chain(llm, model)
        try:
            return chain.invoke({"input_text": text})
        except Exception:
            # If a sub-model extraction fails (e.g., for optional fields), return None
            return None

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

    # Filter out None values for optional fields before creating the Pydantic object
    doc1_filtered = {k: v for k, v in doc1_results.items() if v is not None}
    doc2_filtered = {k: v for k, v in doc2_results.items() if v is not None}

    # Create Pydantic objects
    doc1_data = CarCriteria(**doc1_filtered)
    doc2_data = CarCriteria(**doc2_filtered)

    return doc1_data, doc2_data


def run_travel_comparison(doc1_text, doc2_text, status):
    """
    This function uses ChatOpenAI to compare two travel insurance documents and returns the structured Pydantic objects.
    It now runs extractions for each sub-model in parallel and merges the results.
    """
    llm = ChatOpenAI(temperature=0, model="gpt-4.1")

    # Define all the sub-models to be extracted
    models_to_extract = {
        "General Points": GeneralPoints,
        "Group of People": GroupOfPeople,
        "Basic Coverage": BasicCoverage,
        "Additional Coverage": AdditionalCoverage,
        "Other Building Blocks": OtherBuildingBlocks,
        "Summary": Summary,
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

    # Convert dictionary keys from 'Title Case' to 'snake_case' to match Pydantic model fields
    def convert_keys(d):
        return {key.lower().replace(" ", "_"): value for key, value in d.items()}

    doc1_snake_cased_results = convert_keys(doc1_results)
    doc2_snake_cased_results = convert_keys(doc2_results)

    # Merge the results into the main Pydantic model
    doc1_data = TravelInsuranceProduct(**doc1_snake_cased_results)
    doc2_data = TravelInsuranceProduct(**doc2_snake_cased_results)

    return doc1_data, doc2_data
