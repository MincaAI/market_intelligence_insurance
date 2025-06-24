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

class ProductDetails(BaseModel):
    # ── Identity & Pricing ──────────────────────────────────────────────────────
    product_name: str = Field(
        ...,
        description="Full product name as it appears on documentation, preserving edition, trademarks, version."
    )
    product_type: List[str] = Field(
        ...,
        description="List product types offered: 'Single Trip', 'Annual', 'Modular', etc."
    )
    target_market: List[str] = Field(
        ...,
        description="List intended audience segments: 'Leisure', 'Business', 'Both'."
    )
    single_trip_price_from: str = Field(
        ...,
        description="Specify price for single-trip policies, e.g. 'From CHF X'."
    )
    annual_individual_from: str = Field(
        ...,
        description="Specify starting price for annual individual policies, e.g. 'From CHF X'."
    )
    annual_family_from: str = Field(
        ...,
        description="Specify starting price for annual family policies, e.g. 'From CHF X'."
    )
    unique_selling_points: List[str] = Field(
        ...,
        description="List main advantages or selling points of this product."
    )
    major_exclusions: List[str] = Field(
        ...,
        description="List the principal exclusions or limitations."
    )
    special_features: List[str] = Field(
        ...,
        description="List any additional benefits not covered elsewhere."
    )

    # ── Payment & Premium ───────────────────────────────────────────────────────
    annual_premium_basic_coverage: str = Field(
        ...,
        description="Specify the annual premium for basic coverage as a CHF amount or range, e.g. 'CHF X–Y' or 'From CHF X'."
    )
    annual_premium_additional_coverage: str = Field(
        ...,
        description="Specify the annual premium for any additional coverage options (CHF per option)."
    )
    payment_methods: List[str] = Field(
        ...,
        description="List accepted payment frequencies or methods, e.g. 'Annual', 'Semi-annual', 'Monthly', 'Per trip'."
    )
    online_purchase_available: List[str] = Field(
        ...,
        description="Indicate whether online purchase is available and any restrictions, e.g. 'Yes', 'No', 'Restrictions (describe)'."
    )

class CoverageDetails(BaseModel):
    # ── Core Policy Terms ───────────────────────────────────────────────────────
    product_variants_available: List[str] = Field(
        ...,
        description="List all distinct policy types or plans available under this product, e.g. 'Single Trip', 'Annual', 'Family', 'Business'."
    )
    contract_duration_options: List[str] = Field(
        ...,
        description="List the contract duration options with their time frames, e.g. 'Single trip: X days', 'Annual: 12 months', 'Other'."
    )
    special_discounts_available: List[str] = Field(
        ...,
        description="List any special discounts such as 'Family', 'Senior', 'Youth', 'Group', 'Online booking'."
    )
    territorial_validity: List[str] = Field(
        ...,
        description="List geographic regions where coverage applies, e.g. 'Europe', 'Worldwide', 'Worldwide excl. USA-Canada', 'Zones'."
    )
    cancellation_rights: List[str] = Field(
        ...,
        description="List cancellation rights and values, e.g. 'Automatic renewal: Yes/No', 'Special termination rights'."
    )
    notice_period: List[str] = Field(
        ...,
        description="List any notice period requirements, e.g. 'X months/days', 'Automatic expiry'."
    )
    service_features: List[str] = Field(
        ...,
        description="List service features such as '24/7 hotline', 'App', 'Online claims'."
    )
    leisure_protection: List[str] = Field(
        ...,
        description="Detail leisure protection coverage, e.g. 'Covered up to CHF X', 'Not covered', conditions."
    )
    pet_coverage: List[str] = Field(
        ...,
        description="Specify pet coverage: 'Included', 'Optional', 'Excluded', plus any limits."
    )
    epidemic_pandemic_coverage: List[str] = Field(
        ...,
        description="List if epidemic/pandemic events are 'Covered', 'Excluded', or 'Limited' with conditions."
    )
    min_max_trip_duration: str = Field(
        ...,
        description="Specify minimum/maximum trip durations, e.g. 'X days minimum / Y days maximum'."
    )
    age_limits: str = Field(
        ...,
        description="Detail age restrictions, e.g. 'Min age X', 'Max age Y', 'Senior conditions'."
    )
    waiting_periods: List[str] = Field(
        ...,
        description="List waiting periods, e.g. 'X days', 'None', 'By coverage type'."
    )
    individual_insurance: List[str] = Field(
        ...,
        description="List specifics for individual insurance: 'Age limits', 'Conditions', 'Premium factors'."
    )
    family_insurance: List[str] = Field(
        ...,
        description="List specifics for family insurance: 'Definition of family', 'Age limits for children', 'Max persons'."
    )
    additional_insured_persons: List[str] = Field(
        ...,
        description="List any additional insured persons (e.g. travel companions) and conditions."
    )
    family_definition: List[str] = Field(
        ...,
        description="Define 'family' per policy, e.g. 'Spouse/Partner', 'Children until age X', living arrangement."
    )

    # ── Cancellation & Trip ─────────────────────────────────────────────────────
    cancellation_costs_maximum_coverage: str = Field(
        ...,
        description="State maximum cancellation coverage, e.g. 'CHF X per person', 'CHF Y per trip'."
    )
    cancellation_covered_reasons: List[str] = Field(
        ...,
        description="List reasons covered for cancellation: 'Illness', 'Accident', 'Death', 'Job loss', etc."
    )
    cancellation_deductible: str = Field(
        ...,
        description="Specify the deductible, e.g. a CHF amount or X% of claim."
    )
    cancellation_time_limits: str = Field(
        ...,
        description="State the cancellation time limit, e.g. 'Must cancel within X hours/days'."
    )
    cancellation_covered_costs: List[str] = Field(
        ...,
        description="List covered costs: 'Flights', 'Hotels', 'Tours', 'Other'."
    )
    cancellation_exclusions: List[str] = Field(
        ...,
        description="List any exclusions specific to cancellation coverage."
    )
    cancellation_additional_benefits: List[str] = Field(
        ...,
        description="List any special features or additional benefits for cancellation."
    )
    trip_interruption: str = Field(
        ...,
        description="Detail trip interruption coverage, e.g. 'Covered up to CHF X', conditions."
    )
    trip_delay: str = Field(
        ...,
        description="Detail trip delay compensation, e.g. 'CHF X per hour/day after Y hours delay'."
    )
    missed_departure: str = Field(
        ...,
        description="Specify missed departure coverage, e.g. 'Covered up to CHF X', conditions."
    )

    # ── Business, Legal & Luggage ────────────────────────────────────────────────
    business_travel_basic_coverage: bool = Field(
        ...,
        description="Indicate if basic business travel coverage is included (True/False)."
    )
    business_travel_additional_premium: str = Field(
        ...,
        description="Specify additional premium for business travel, CHF amount or percentage."
    )
    business_equipment: str = Field(
        ...,
        description="Detail business equipment coverage, limit and item types."
    )
    replacement_person: str = Field(
        ...,
        description="Specify coverage for replacement person costs, including limits."
    )
    business_interruption: str = Field(
        ...,
        description="Detail business interruption coverage scope and limits."
    )
    travel_legal_protection_available: bool = Field(
        ...,
        description="Indicate if travel/legal protection is available (True/False)."
    )
    legal_protection_coverage_limit: str = Field(
        ...,
        description="Specify coverage limit e.g. 'CHF X per case', 'CHF Y per year'."
    )
    legal_protection_deductible: str = Field(
        ...,
        description="Specify deductible for legal protection, CHF amount."
    )
    legal_protection_covered_disputes: List[str] = Field(
        ...,
        description="List types of disputes covered under legal protection."
    )
    legal_protection_geographic_scope: List[str] = Field(
        ...,
        description="List geographic scope for legal protection coverage."
    )
    legal_protection_waiting_period: str = Field(
        ...,
        description="Specify waiting period for legal protection, e.g. 'X days', 'None'."
    )
    travel_luggage_available: bool = Field(
        ...,
        description="Indicate if luggage coverage is available (True/False)."
    )
    luggage_sum_insured: str = Field(
        ...,
        description="Specify sum insured for luggage, e.g. 'CHF X per person/trip'."
    )
    luggage_per_item_limit: str = Field(
        ...,
        description="Specify per-item limit for luggage coverage."
    )
    luggage_valuables_limit: str = Field(
        ...,
        description="Specify valuables limit under luggage coverage."
    )
    luggage_deductible: str = Field(
        ...,
        description="Specify deductible for luggage coverage, as CHF amount or percentage."
    )
    luggage_covered_perils: List[str] = Field(
        ...,
        description="List perils covered under luggage, e.g. 'Theft', 'Damage', 'Loss', 'Delay'."
    )
    luggage_delay_compensation: str = Field(
        ...,
        description="Detail compensation for luggage delay, e.g. 'After X hours: CHF Y'."
    )
    luggage_exclusions: List[str] = Field(
        ...,
        description="List exclusions specific to luggage coverage."
    )
    cdw_coverage_available: bool = Field(
        ...,
        description="Indicate if CDW coverage is available (True/False)."
    )
    cdw_coverage_limit: str = Field(
        ...,
        description="Specify CDW coverage limit, e.g. 'CHF X per event', 'per year'."
    )
    cdw_vehicle_types: List[str] = Field(
        ...,
        description="List vehicle types covered under CDW, e.g. 'Cars', 'Motorhomes', 'Motorcycles'."
    )
    cdw_geographic_validity: List[str] = Field(
        ...,
        description="List geographic validity for CDW coverage."
    )
    cdw_rental_duration_limit: str = Field(
        ...,
        description="Specify rental duration limit under CDW, e.g. 'Max X days'."
    )
    cdw_premium: str = Field(
        ...,
        description="Specify premium for CDW coverage, as a CHF amount."
    )

class AssistanceServices(BaseModel):
    # ── Personal & Medical ───────────────────────────────────────────────────────
    personal_assistance_available: bool = Field(
        ...,
        description="Indicate if personal assistance is available (True/False)."
    )
    medical_evacuation: str = Field(
        ...,
        description="Detail medical evacuation coverage, e.g. 'Covered up to CHF X', conditions."
    )
    repatriation: str = Field(
        ...,
        description="Detail repatriation coverage, e.g. 'Covered up to CHF X', medical necessity."
    )
    hospital_visit_organization: str = Field(
        ...,
        description="Detail hospital visit organization coverage, including travel cost limits and beneficiaries."
    )
    return_of_children: str = Field(
        ...,
        description="Specify child return coverage, e.g. 'Covered', age limits, accompaniment."
    )
    search_and_rescue_costs: str = Field(
        ...,
        description="Detail search and rescue costs coverage, max amount and limits."
    )
    medical_referral_service: List[str] = Field(
        ...,
        description="List medical referral service details, e.g. '24/7', languages."
    )
    other_personal_assistance: List[str] = Field(
        ...,
        description="List additional personal assistance services."
    )

    # ── Vehicle & Travel ────────────────────────────────────────────────────────
    vehicle_assistance_available: bool = Field(
        ...,
        description="Indicate if vehicle assistance is available (True/False)."
    )
    breakdown_assistance: str = Field(
        ...,
        description="Detail breakdown assistance coverage, e.g. 'Covered up to CHF X'."
    )
    towing_service: str = Field(
        ...,
        description="Detail towing service limits, e.g. 'Distance/Amount CHF X', destination."
    )
    replacement_vehicle: str = Field(
        ...,
        description="Specify replacement vehicle coverage: days, category, conditions."
    )
    onwards_return_journey: str = Field(
        ...,
        description="Detail onward or return journey coverage, limits."
    )
    vehicle_return: str = Field(
        ...,
        description="Detail vehicle return coverage, including driver conditions."
    )
    other_vehicle_assistance: List[str] = Field(
        ...,
        description="List additional vehicle assistance services."
    )
    additional_accommodation: str = Field(
        ...,
        description="Specify additional accommodation coverage, e.g. 'CHF X per day', max total."
    )
    phone_costs: str = Field(
        ...,
        description="Detail phone cost coverage, limits and call types."
    )
    translation_services: str = Field(
        ...,
        description="Detail translation service coverage, limits and availability."
    )
    legal_advance_payment: str = Field(
        ...,
        description="Specify legal advance payment coverage, e.g. 'Up to CHF X', repayment terms."
    )
    bail_bond_advance: str = Field(
        ...,
        description="Specify bail bond advance coverage and conditions."
    )
    other_cost_coverage: List[str] = Field(
        ...,
        description="List any other costs covered by the policy."
    )

    # ── E-Bike, Home & Insolvency ───────────────────────────────────────────────
    e_bike_moped_assistance_available: bool = Field(
        ...,
        description="Indicate if E-Bike/Moped assistance is available (True/False)."
    )
    e_bike_breakdown_service: str = Field(
        ...,
        description="Detail E-Bike breakdown service, e.g. 'CHF X per event', distance limits."
    )
    e_bike_transport: str = Field(
        ...,
        description="Specify E-Bike transport coverage, e.g. 'To where', 'Max distance'."
    )
    e_bike_replacement_vehicle: str = Field(
        ...,
        description="Detail E-Bike replacement vehicle coverage: type, duration, availability."
    )
    e_bike_onwards_journey: str = Field(
        ...,
        description="Detail onward journey coverage for E-Bike, limits."
    )
    e_bike_theft_assistance: str = Field(
        ...,
        description="Describe E-Bike theft assistance services and conditions."
    )
    home_assistance_available: bool = Field(
        ...,
        description="Indicate if home assistance is available (True/False)."
    )
    emergency_home_repairs: str = Field(
        ...,
        description="Detail emergency home repairs coverage, e.g. 'CHF X per event', emergencies."
    )
    security_services: str = Field(
        ...,
        description="Describe security services coverage, triggers, duration."
    )
    key_service: str = Field(
        ...,
        description="Specify key service coverage, e.g. 'CHF X', circumstances."
    )
    property_monitoring: str = Field(
        ...,
        description="Detail property monitoring coverage, how arranged."
    )
    medical_costs_available: bool = Field(
        ...,
        description="Indicate if medical costs coverage is available (True/False)."
    )
    medical_costs_coverage_limit: str = Field(
        ...,
        description="Specify medical cost coverage limit, e.g. 'CHF X per person/event'."
    )
    medical_costs_deductible: str = Field(
        ...,
        description="Specify deductible for medical costs, as a CHF amount."
    )
    covered_treatments: List[str] = Field(
        ...,
        description="List treatments covered, e.g. 'Emergency', 'Dental', 'Medication', 'Other'."
    )
    direct_billing: bool = Field(
        ...,
        description="Indicate if direct billing is supported (True/False) and providers."
    )
    pre_authorization: bool = Field(
        ...,
        description="Indicate if pre-authorization is required for treatment (True/False)."
    )
    medical_costs_exclusions: List[str] = Field(
        ...,
        description="List any exclusions for medical costs coverage."
    )
    insolvency_protection_available: bool = Field(
        ...,
        description="Indicate if insolvency protection is available (True/False)."
    )
    insolvency_coverage_limit: str = Field(
        ...,
        description="Specify insolvency coverage limit, e.g. 'CHF X per person/booking'."
    )
    insolvency_covered_providers: List[str] = Field(
        ...,
        description="List providers covered under insolvency protection, e.g. 'Airlines', 'Tour operators'."
    )
    insolvency_covered_costs: List[str] = Field(
        ...,
        description="List costs covered upon insolvency, e.g. 'Unused services', 'Return journey'."
    )
    insolvency_time_limits: str = Field(
        ...,
        description="Specify booking time limits for insolvency coverage, e.g. 'Booked X days before'."
    )
    insolvency_exclusions: List[str] = Field(
        ...,
        description="List any exclusions for insolvency protection."
    )

class TravelInsuranceProduct(BaseModel):
    product: ProductDetails
    coverage: CoverageDetails
    services: AssistanceServices