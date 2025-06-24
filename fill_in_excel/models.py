from enum import Enum
from typing import List, Optional, Union, Dict
from pydantic import BaseModel, Field

class PaymentFrequency(str, Enum):
    """
    Enumeration of supported intervals for premium payments within an insurance policy.
    Useful for identifying and validating the billing cycle specified in the raw document.

    Possible values:
    - monthly: Premium is due every calendar month.
    - quarterly: Premium is due every three months.
    - semiannual: Premium is due every six months.
    - annual: Premium is paid once per policy year.
    """
    monthly = "monthly"
    quarterly = "quarterly"
    semiannual = "semiannual"
    annual = "annual"


class CoverageDetailOptions(BaseModel):
    """
    Describes configuration options for a particular coverage component.
    When extracting from text, locate the section heading that introduces this coverage,
    then capture all listed monetary limits, deductible tiers, and scope descriptions.

    Attributes:
    - listed_under: Document section title where this coverage is defined.
    - coverage_sum_options: Valid coverage limit values or ranges as stated.
    - deductible_options: Available deductible tiers for this coverage.
    - scope_options: Textual descriptions of included perils and conditions.
    """
    listed_under: Optional[str] = Field(
        None,
        description=(
            "Document heading or clause under which this coverage’s details appear. "
            "Used by the extractor to navigate to the correct section of the policy text."
        )
    )
    coverage_sum_options: Optional[List[str]] = Field(
        None,
        description=(
            "List of coverage limit values or labeled ranges as shown in the policy, e.g., '1000 USD', 'No limit'. "
            "Enables validation of selected sums against permitted options."
        )
    )
    deductible_options: Optional[List[str]] = Field(
        None,
        description=(
            "List of deductible choices defined for this coverage, such as 'Standard', 'Premium'. "
            "Each choice represents a defined out-of-pocket responsibility tier."
        )
    )
    scope_options: Optional[List[str]] = Field(
        None,
        description=(
            "Descriptions of covered events or perils associated with each option, "
            "for example ['Fire', 'Theft', 'Glass breakage'], to clarify policy scope."
        )
    )


class DeductibleSelection(BaseModel):
    """
    Captures deductible configuration for specific driver categories or coverage types.

    Attributes:
    - listed_under: Section label indicating where deductible options are presented.
    - options: List of deductible labels or numeric values extracted.
    """
    listed_under: Optional[str] = Field(
        None,
        description=(
            "Label or clause title in the policy text where deductible information is provided. "
            "Guides the extractor to the relevant deductible section."
        )
    )
    options: Optional[List[str]] = Field(
        None,
        description=(
            "List of named deductible levels or amounts offered, e.g., '250', '500', '1000'. "
            "Allows downstream systems to present and validate user selections."
        )
    )


class OptionCoverage(BaseModel):
    """
    Represents optional add-on features or service tiers without explicit monetary limits.

    Attributes:
    - listed_under: Policy text heading under which the add-on is described.
    - choices: Available option names or variants as presented in the document.
    """
    listed_under: Optional[str] = Field(
        None,
        description=(
            "Heading in the policy document where this optional coverage is detailed. "
            "Essential for locating the descriptive rules associated with the add-on."
        )
    )
    choices: Optional[List[str]] = Field(
        None,
        description=(
            "List of available add-on tiers or feature names, such as 'Basic', 'Premium'. "
            "Used to map user selections to policy-defined options."
        )
    )


class AccidentOptions(BaseModel):
    """
    Structured representation of benefits and allowances under accident protection.

    Attributes:
    - listed_under: Section heading grouping all accident protection details.
    - death_benefit: Available death capital amounts.
    - disability_benefit: Disability compensation sums.
    - daily_allowance: Daily recovery allowances.
    - hospital_daily_allowance: Inpatient daily rates.
    - medical_costs: Maximum medical expense coverage options.
    """
    listed_under: Optional[str] = Field(
        None,
        description=(
            "Section or clause in the policy where accident benefits are introduced. "
            "Used to anchor extraction of all related fields."
        )
    )
    death_benefit: Optional[List[str]] = Field(
        None,
        description=(
            "List of death benefit amounts specified, such as '10000 USD', '20000 USD'. "
            "Ensures extracted values align with policy-defined benefit levels."
        )
    )
    disability_benefit: Optional[List[str]] = Field(
        None,
        description=(
            "List of compensation amounts payable for permanent disability events."
        )
    )
    daily_allowance: Optional[List[str]] = Field(
        None,
        description=(
            "Available daily allowance rates for recovery days, e.g., '100 USD/day'. "
            "Helps determine per-day compensation levels."
        )
    )
    hospital_daily_allowance: Optional[List[str]] = Field(
        None,
        description=(
            "Daily reimbursement rates for hospital stays, distinct from general allowances."
        )
    )
    medical_costs: Optional[List[str]] = Field(
        None,
        description=(
            "Maximum medical cost coverage options as listed, defining treatment ceilings."
        )
    )


class AssistanceDetail(BaseModel):
    """
    Extracts roadside assistance service details, including geographic applicability.

    Attributes:
    - listed_under: Heading where assistance services are documented.
    - region_options: Geographic areas covered by assistance.
    """
    listed_under: Optional[str] = Field(
        None,
        description=(
            "Heading or label in the policy text that introduces assistance coverage details."
        )
    )
    region_options: Optional[List[str]] = Field(
        None,
        description=(
            "List of regions or territories where assistance applies, as specified in the coverage section."
        )
    )


class CarCriteria(BaseModel):
    """
    Defines the full extraction schema for a motor insurance policy.
    Each field maps to a specific piece of information in the raw policy text.

    General Settings:
    - general_info: High-level title or summary text.
    - payment_frequency: Premium billing interval.
    - online_discount: Discount rate for online purchases.
    - new_risk_questions: Additional underwriting questions text.

    Liability & Deductibles:
    - liability, young_driver_deductible, standard_deductible, bonus_protection, own_damage

    Optional Coverage Modules:
    - partial_comprehensive, full_comprehensive, gross_negligence, compensation,
      parking_damage, glass_plus, interior, tires_and_rims, keys, wallbox, battery,
      cyber_attack, personal_effects, rental_vehicle, repair_service, legal_protection

    Assistance & Accident:
    - assistance, accident_protection
    """
    # — General Settings —
    general_info: Optional[str] = Field(
        None,
        description=(
            "Free-text title, header, or summary that provides context for the entire policy. "
            "Typically a document title or key introductory phrase."
        )
    )
    payment_frequency: Optional[PaymentFrequency] = Field(
        None,
        description=(
            "Specifies how often the policy premium must be paid, as described in the text. "
            "E.g., 'monthly', 'annual'."
        )
    )
    online_discount: Optional[float] = Field(
        None,
        description=(
            "Decimal representation of any discount applied to online policy purchases, "
            "for example '0.10' indicates a 10% reduction in premium."
        )
    )
    new_risk_questions: Optional[str] = Field(
        None,
        description=(
            "Text of any new or updated risk assessment questions required by the insurer, "
            "often referencing prior claims or driving history."
        )
    )

    # — Liability & Deductibles —
    liability: CoverageDetailOptions
    young_driver_deductible: DeductibleSelection
    standard_deductible: DeductibleSelection
    bonus_protection: OptionCoverage
    own_damage: CoverageDetailOptions

    # — Optional Coverage Modules —
    partial_comprehensive: CoverageDetailOptions
    full_comprehensive: CoverageDetailOptions
    gross_negligence: CoverageDetailOptions
    compensation: CoverageDetailOptions
    parking_damage: CoverageDetailOptions
    glass_plus: CoverageDetailOptions
    interior: CoverageDetailOptions
    tires_and_rims: CoverageDetailOptions
    keys: CoverageDetailOptions
    wallbox: CoverageDetailOptions
    battery: CoverageDetailOptions
    cyber_attack: CoverageDetailOptions
    personal_effects: CoverageDetailOptions
    rental_vehicle: CoverageDetailOptions
    repair_service: OptionCoverage
    legal_protection: OptionCoverage

    # — Assistance & Accident —
    assistance: AssistanceDetail
    accident_protection: AccidentOptions


class TravelInsuranceProduct(BaseModel):
    # ── Product Metadata ──────────────────────────────────────────────────────
    product_name: str = Field(
        ...,  
        description=(
            "Exact, full product title as it appears in policy documents or marketing materials. "
            "Example: 'General Policy Conditions (GPC) Travel Insurance Edition 2025'. "
            "This field helps the LLM identify the authoritative name used throughout the document, "
            "preserving any edition numbers, trademarks, or version details."
        )
    )
    product_variants: List[str] = Field(
        ...,  
        description=(
            "List of all distinct policy types or plans available under this product. "
            "Expected values include 'Single Trip', 'Annual', 'Family', 'Business'. "
            "LLM should locate the section or dropdown listing variants, extract each option as a separate string, "
            "and maintain their exact naming."
        )
    )
    target_market: List[str] = Field(
        ...,  
        description=(
            "Intended audience segments for this insurance product. "
            "Typical values: 'Leisure' for recreational travel, 'Business' for corporate trips, or 'Both'. "
            "Extraction should capture every segment explicitly mentioned under 'Target Market' or similar heading."
        )
    )
    territorial_validity: List[str] = Field(
        ...,  
        description=(
            "Geographical regions where the policy provides coverage. "
            "Common entries: 'Europe', 'Worldwide', 'Worldwide excl. USA-Canada', or specifically defined zones. "
            "The LLM should parse tables or bullet lists under 'Territorial Validity' and return each region as a string."
        )
    )
    min_trip_duration: int = Field(
        ...,  
        description=(
            "Minimum number of days a trip must span to qualify for coverage. "
            "Extract the numeric value from phrasing like 'Minimum trip duration: X days'."
        )
    )
    max_trip_duration: int = Field(
        ...,  
        description=(
            "Maximum allowable trip length in days. "
            "Derived from statements such as 'Maximum trip duration: Y days' or document logic. "
            "LLM should strip units and return the integer number of days."
        )
    )
    age_minimum: int = Field(
        ...,  
        description=(
            "Youngest age at which an individual is eligible for this policy. "
            "Found under 'Age Limits' sections; extract integer value before 'years'."
        )
    )
    age_maximum: int = Field(
        ...,  
        description=(
            "Oldest age covered without special senior terms. "
            "If document specifies senior conditions above this age, capture the cutoff. "
            "LLM should convert to integer."
        )
    )
    online_purchase: bool = Field(
        ...,  
        description=(
            "Indicates whether the policy can be purchased directly online. "
            "Extract 'Yes'/'No' or equivalent phrasing and map to boolean True/False."
        )
    )
    online_discount_rate: Optional[float] = Field(
        None,  
        description=(
            "Percentage discount for online purchase, expressed as a decimal. "
            "For example, '10% online discount' becomes 0.10. "
            "If multiple tiers exist, return the primary or highest rate."
        )
    )

    # ── Pricing & Payment ──────────────────────────────────────────────────────
    annual_premium_basic: Optional[str] = Field(
        None,  
        description=(
            "Base annual premium for the entry-level plan. "
            "Format examples: 'CHF 100–200' or 'from CHF 150'. "
            "LLM should preserve currency and range syntax exactly as shown."
        )
    )
    trip_premium_from: Optional[float] = Field(
        None,  
        description=(
            "Starting price for a single-trip variant in Swiss Francs. "
            "Extract the numeric value after 'from CHF'."
        )
    )
    payment_frequencies: List[str] = Field(
        ...,  
        description=(
            "Allowed intervals for premium billing. "
            "Examples: 'Annual', 'Semi-annual', 'Monthly', 'Per trip'. "
            "LLM should read from 'Payment Frequency' tables or lists and return each as a clean string."
        )
    )
    payment_methods: List[str] = Field(
        ...,  
        description=(
            "Accepted payment options. Examples include 'Credit Card', 'Bank Transfer', 'PayPal'. "
            "LLM should enumerate each method exactly as described in the 'Payment Methods' section."
        )
    )
    cancellation_refund_limit: Optional[str] = Field(
        None,  
        description=(
            "Maximum refundable amount upon policy cancellation. "
            "Format: 'CHF X per person' or 'CHF Y per trip'. "
            "LLM should match currency and per-unit wording exactly."
        )
    )

    # ── Cancellation Cover ────────────────────────────────────────────────────
    cancellation_covered_reasons: List[str] = Field(
        ...,  
        description=(
            "Enumerates all valid reasons policyholders can cancel and claim a refund. "
            "Typical values: 'Illness', 'Accident', 'Death', 'Job loss', 'Other'. "
            "LLM should parse bullet lists or tables under 'Cancellation Covered Reasons'."
        )
    )
    cancellation_timeframe: str = Field(
        ...,  
        description=(
            "Deadline for submitting a cancellation notice before trip start. "
            "Extract phrasing like 'Must cancel within X days/hours before departure'. "
            "Return the full phrase."
        )
    )
    cancellation_deductible: Optional[str] = Field(
        None,  
        description=(
            "Fixed fee or percentage deducted from the cancellation reimbursement. "
            "Example formats: 'CHF 50' or '10% of claim'. "
            "LLM should preserve unit and symbol."
        )
    )
    cancellation_exclusions: List[str] = Field(
        ...,  
        description=(
            "Specific scenarios where cancellation cover does not apply. "
            "Examples: 'Change of mind', 'Pre-existing medical conditions'. "
            "LLM to extract each exclusion as listed under 'Cancellation Exclusions'."
        )
    )

    # ── Medical & Assistance ──────────────────────────────────────────────────
    medical_evacuation_limit: str = Field(
        ...,  
        description=(
            "Maximum sum insured for emergency medical evacuation by air or ground. "
            "Format: 'CHF X' or 'Unlimited'. "
            "LLM should read from the 'Medical Evacuation' clause."
        )
    )
    repatriation_limit: str = Field(
        ...,  
        description=(
            "Coverage limit for repatriation of remains to home country. "
            "Example: 'CHF 20,000' or 'Unlimited'. "
            "Ensure currency and amount match policy text."
        )
    )
    emergency_medical_limit: str = Field(
        ...,  
        description=(
            "Maximum cover for emergency medical treatment abroad. "
            "Format: 'Up to CHF X'. "
            "LLM to capture exact phrasing from 'Emergency Medical Treatment' section."
        )
    )
    hospital_daily_allowance: Optional[str] = Field(
        None,  
        description=(
            "Daily cash benefit paid while hospitalized. "
            "Example: 'CHF 150 per day'. "
            "LLM should extract amount and unit phrase accurately."
        )
    )
    search_and_rescue_limit: str = Field(
        ...,  
        description=(
            "Maximum insured amount for search and rescue operations. "
            "Format: 'Up to CHF X per incident'. "
            "LLM should pull from 'Search & Rescue' limit table."
        )
    )
    personal_assistance: bool = Field(
        ...,  
        description=(
            "Whether a dedicated 24/7 personal assistance hotline or concierge service is included. "
            "Map 'Yes'/'No' from the document to True/False."
        )
    )

    # ── Luggage & Personal Effects ─────────────────────────────────────────────
    luggage_sum_insured: str = Field(
        ...,  
        description=(
            "Maximum cover for loss or damage of all luggage per person. "
            "Format: 'CHF X per person/event'. "
            "LLM should preserve event context and currency."
        )
    )
    luggage_per_item_limit: Optional[str] = Field(
        None,  
        description=(
            "Maximum sum insured for any single item, such as valuables. "
            "Example: 'CHF 1,000'. "
            "LLM to extract numeric limit and currency precisely."
        )
    )
    luggage_delay_compensation: Optional[str] = Field(
        None,  
        description=(
            "Reimbursement paid when luggage is delayed beyond a specified threshold. "
            "Example: 'After 4 hours delay: CHF 200'. "
            "LLM should capture both delay trigger and compensation amount."
        )
    )
    luggage_exclusions: List[str] = Field(
        ...,  
        description=(
            "List of items or situations excluded from luggage cover. "
            "Examples: 'Jewelry', 'Sports equipment', 'Bicycles'. "
            "LLM to enumerate each exclusion exactly."
        )
    )

    # ── Vehicle Assistance ────────────────────────────────────────────────────
    vehicle_assistance: bool = Field(
        ...,  
        description=(
            "Indicates whether roadside or rental vehicle assistance is part of the policy. "
            "Map 'Yes'/'No' to True/False."
        )
    )
    towing_service_limit: Optional[str] = Field(
        None,  
        description=(
            "Coverage limit for towing service after vehicle breakdown. "
            "Example: 'Up to CHF 300 per event' or 'Distance limit 100 km'. "
            "LLM should extract both currency/amount and any distance restrictions."
        )
    )
    replacement_vehicle_days: Optional[int] = Field(
        None,  
        description=(
            "Number of days a replacement vehicle will be provided following a covered breakdown. "
            "LLM should parse numeric days from phrases like 'Up to 5 days replacement vehicle'."
        )
    )

    # ── Legal Protection ──────────────────────────────────────────────────────
    legal_protection: bool = Field(
        ...,  
        description=(
            "Specifies if a travel-related legal protection module is offered. "
            "Translate 'Yes'/'No' to True/False."
        )
    )
    legal_protection_limit: Optional[str] = Field(
        None,  
        description=(
            "Maximum coverage amount for legal expenses. "
            "Format: 'CHF X per case' or 'CHF Y per year'. "
            "LLM should retain currency and per-unit detail."
        )
    )
    legal_waiting_period: Optional[int] = Field(
        None,  
        description=(
            "Number of days the legal protection cover must wait before activation. "
            "Extract integer from 'Waiting period: X days'."
        )
    )

    # ── Extras & Add-Ons ──────────────────────────────────────────────────────
    ski_snowboard_cover: Optional[bool] = Field(
        None,  
        description=(
            "Indicates if winter sports coverage for skiing/snowboarding is available. "
            "Map policy text under 'Winter Sports' to True/False."
        )
    )
    extreme_sports_cover: Optional[bool] = Field(
        None,  
        description=(
            "Indicates coverage availability for high-risk or extreme activities (e.g., bungee jumping, scuba diving). "
            "LLM to read from 'Extreme Sports' clause."
        )
    )
    pet_cover: Optional[bool] = Field(
        None,  
        description=(
            "Specifies whether pets (typically cats/dogs) are included in the coverage. "
            "Translate 'Included'/'Optional'/'Excluded' into boolean or None as appropriate."
        )
    )
    epidemic_cover: Optional[str] = Field(
        None,  
        description=(
            "Status of epidemic/pandemic coverage under communicable disease exclusions. "
            "Possible values: 'Covered', 'Excluded', 'Limited coverage – see conditions'. "
            "LLM should extract the full policy phrase."
        )
    )
