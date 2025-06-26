from enum import Enum
from typing import List, Optional, Union, Dict
from pydantic import BaseModel, Field

class General(BaseModel):
    payment_frequency: List[str] = Field(
        ...,
        description="Payment frequency. Example: ['Annual', 'Semi-annual', 'Monthly']"
    )
    online_discount: List[str] = Field(
        ...,
        description="Online discount. Example: ['10% off for online purchase']"
    )
    risk_questions_new: List[str] = Field(
        ...,
        description="Risk questions. Example: ['Have you had any accidents in the past 5 years?']"
    )

class Liability(BaseModel):
    deductible_for_young_drivers_selection: str = Field(
        ...,
        description="Deductible for young drivers (Selection). Example: 'CHF 1,000'"
    )
    standard_deductible_selection: str = Field(
        ...,
        description="Standard deductible (Selection). Example: 'CHF 500'"
    )
    bonus_protection: List[str] = Field(
        ...,
        description="Bonus protection. Example: ['No-claim bonus protection']"
    )
    bonus_protection_listed_under: List[str] = Field(
        ...,
        description="Bonus protection listed under. Example: ['Collision coverage']"
    )
    scope_of_coverage_selection: str = Field(
        ...,
        description="Scope of coverage (Selection). Example: 'Switzerland & EU'"
    )
    own_damage: List[str] = Field(
        ...,
        description="Own damage coverage. Example: ['Fire', 'Theft']"
    )
    own_damage_listed_under: List[str] = Field(
        ...,
        description="Own damage listed under. Example: ['Comprehensive coverage']"
    )
    own_damage_sum_insured: str = Field(
        ...,
        description="Own damage sum insured. Example: 'CHF 25,000'"
    )

class PartialInsurance(BaseModel):
    deductible_selection: str = Field(
        ...,
        description="Partial insurance deductible (Selection). Example: 'CHF 300'"
    )
    scope_of_coverage: str = Field(
        ...,
        description="Partial insurance scope of coverage. Example: 'Collision only'"
    )

class FullyComprehensiveInsurance(BaseModel):
    deductible_for_young_drivers_selection: str = Field(
        ...,
        description="Deductible for young drivers (Selection). Example: 'CHF 1,500'"
    )
    standard_deductible_selection: str = Field(
        ...,
        description="Standard deductible (Selection). Example: 'CHF 700'"
    )
    bonus_protection: List[str] = Field(
        ...,
        description="Bonus protection. Example: ['Protected no-claim bonus']"
    )
    bonus_protection_listed_under: List[str] = Field(
        ...,
        description="Bonus protection listed under. Example: ['Fully comprehensive']"
    )
    scope_of_coverage_selection: str = Field(
        ...,
        description="Scope of coverage (Selection). Example: 'Worldwide'"
    )

class GrossNegligence(BaseModel):
    coverage_module: List[str] = Field(
        ...,
        description="Gross negligence coverage module. Example: ['Up to CHF 10,000']"
    )
    listed_under: List[str] = Field(
        ...,
        description="Gross negligence listed under. Example: ['Legal protection']"
    )

class Compensation(BaseModel):
    coverage_module: List[str] = Field(
        ...,
        description="Compensation coverage module. Example: ['Vehicle value compensation']"
    )
    listed_under: List[str] = Field(
        ...,
        description="Compensation listed under. Example: ['Accident benefits']"
    )
    selection: str = Field(
        ...,
        description="Compensation option (Selection). Example: 'Market value at loss date'"
    )

class ParkingDamage(BaseModel):
    coverage_module: List[str] = Field(
        ...,
        description="Parking damage coverage module. Example: ['Parking bumpers']"
    )
    listed_under: List[str] = Field(
        ...,
        description="Parking damage listed under. Example: ['Partial insurance']"
    )
    sum_insured: str = Field(
        ...,
        description="Parking damage sum insured. Example: 'CHF 2,000'"
    )
    sum_insured_selection: str = Field(
        ...,
        description="Parking damage sum insured (Selection). Example: 'Up to CHF 2,000'"
    )
    deductible: str = Field(
        ...,
        description="Parking damage deductible. Example: 'CHF 300'"
    )
    deductible_selection: str = Field(
        ...,
        description="Parking damage deductible (Selection). Example: 'CHF 300 per event'"
    )
    scope_of_coverage: str = Field(
        ...,
        description="Parking damage scope of coverage. Example: 'Public parking only'"
    )

class GlassPlus(BaseModel):
    coverage_module: List[str] = Field(
        ...,
        description="Glass Plus coverage module. Example: ['Windshield repair']"
    )
    listed_under: List[str] = Field(
        ...,
        description="Glass Plus listed under. Example: ['Additional coverage']"
    )
    deductible: str = Field(
        ...,
        description="Glass Plus deductible. Example: 'No deductible'"
    )

class VehicleInterior(BaseModel):
    coverage_module: List[str] = Field(
        ...,
        description="Vehicle interior coverage module. Example: ['Seat upholstery']"
    )
    listed_under: List[str] = Field(
        ...,
        description="Vehicle interior listed under. Example: ['Comprehensive add-on']"
    )
    sum_insured: str = Field(
        ...,
        description="Vehicle interior sum insured. Example: 'CHF 1,000'"
    )
    sum_insured_selection: str = Field(
        ...,
        description="Vehicle interior sum insured (Selection). Example: 'Up to CHF 1,000'"
    )

class TiresAndRims(BaseModel):
    coverage_module: List[str] = Field(
        ...,
        description="Tires & rims coverage module. Example: ['Puncture protection']"
    )
    listed_under: List[str] = Field(
        ...,
        description="Tires & rims listed under. Example: ['Additional cover']"
    )
    sum_insured: str = Field(
        ...,
        description="Tires & rims sum insured. Example: 'CHF 2,500'"
    )
    sum_insured_selection: str = Field(
        ...,
        description="Tires & rims sum insured (Selection). Example: 'Up to CHF 2,500'"
    )

class VehicleKey(BaseModel):
    coverage_module: List[str] = Field(
        ...,
        description="Vehicle key coverage module. Example: ['Key replacement']"
    )
    listed_under: List[str] = Field(
        ...,
        description="Vehicle key listed under. Example: ['Comprehensive add-on']"
    )
    sum_insured: str = Field(
        ...,
        description="Vehicle key sum insured. Example: 'CHF 1,200'"
    )

class ChargingStationWallbox(BaseModel):
    coverage_module: List[str] = Field(
        ...,
        description="Charging station (wallbox) coverage module. Example: ['Wallbox repair']"
    )
    listed_under: List[str] = Field(
        ...,
        description="Charging station listed under. Example: ['Home assistance']"
    )
    sum_insured: str = Field(
        ...,
        description="Charging station sum insured. Example: 'CHF 3,000'"
    )
    deductible: str = Field(
        ...,
        description="Charging station deductible. Example: 'CHF 500'"
    )

class Battery(BaseModel):
    coverage_module: List[str] = Field(
        ...,
        description="Battery coverage module. Example: ['Battery replacement']"
    )
    listed_under: List[str] = Field(
        ...,
        description="Battery listed under. Example: ['Additional coverage']"
    )
    sum_insured: str = Field(
        ...,
        description="Battery sum insured. Example: 'CHF 4,000'"
    )
    deductible: str = Field(
        ...,
        description="Battery deductible. Example: 'CHF 800'"
    )

class CyberAttacksRemediationCosts(BaseModel):
    coverage_module: List[str] = Field(
        ...,
        description="Cyber-attack remediation coverage module. Example: ['Data recovery']"
    )
    listed_under: List[str] = Field(
        ...,
        description="Cyber-attack listed under. Example: ['Special risks']"
    )
    sum_insured: str = Field(
        ...,
        description="Cyber-attack sum insured. Example: 'CHF 50,000'"
    )
    sum_insured_selection: str = Field(
        ...,
        description="Cyber-attack sum insured (Selection). Example: 'Up to CHF 50,000'"
    )

class ItemsCarried(BaseModel):
    coverage_module: List[str] = Field(
        ...,
        description="Items carried coverage module. Example: ['Luggage contents']"
    )
    listed_under: List[str] = Field(
        ...,
        description="Items carried listed under. Example: ['Luggage extension']"
    )
    sum_insured: str = Field(
        ...,
        description="Items carried sum insured. Example: 'CHF 2,000'"
    )
    sum_insured_selection: str = Field(
        ...,
        description="Items carried sum insured (Selection). Example: 'Up to CHF 2,000'"
    )

class RentalReplacementVehicle(BaseModel):
    coverage_module: List[str] = Field(
        ...,
        description="Rental/replacement vehicle coverage module. Example: ['Car hire cover']"
    )
    listed_under: List[str] = Field(
        ...,
        description="Rental/replacement listed under. Example: ['Roadside assistance']"
    )
    sum_insured: str = Field(
        ...,
        description="Rental/replacement sum insured. Example: 'CHF 150/day'"
    )
    sum_insured_selection: str = Field(
        ...,
        description="Rental/replacement sum insured (Selection). Example: 'Up to CHF 150/day'"
    )

class Assistance(BaseModel):
    coverage_module: List[str] = Field(
        ...,
        description="Assistance coverage module. Example: ['Roadside assistance']"
    )
    listed_under: List[str] = Field(
        ...,
        description="Assistance listed under. Example: ['Basic cover']"
    )
    scope: str = Field(
        ...,
        description="Assistance scope. Example: '24/7 in Europe'"
    )
    scope_selection: str = Field(
        ...,
        description="Assistance scope (Selection). Example: 'Europe only'"
    )

class RepairService(BaseModel):
    coverage_module: List[str] = Field(
        ...,
        description="Repair service coverage module. Example: ['On-site repairs']"
    )
    listed_under: List[str] = Field(
        ...,
        description="Repair service listed under. Example: ['Additional services']"
    )
    option: List[str] = Field(
        ...,
        description="Repair options. Example: ['Mobile workshop']"
    )
    option_selection: str = Field(
        ...,
        description="Repair option (Selection). Example: 'Mobile workshop'"
    )

class Accident(BaseModel):
    coverage_module: List[str] = Field(
        ...,
        description="Accident coverage module. Example: ['Personal accident cover']"
    )
    listed_under: List[str] = Field(
        ...,
        description="Accident listed under. Example: ['Basic coverage']"
    )
    death_benefit_selection: str = Field(
        ...,
        description="Death benefit (Selection). Example: 'CHF 50,000'"
    )
    disability_capital_selection: str = Field(
        ...,
        description="Disability capital (Selection). Example: 'CHF 30,000'"
    )
    daily_allowance_selection: str = Field(
        ...,
        description="Daily allowance (Selection). Example: 'CHF 100/day'"
    )
    hospital_daily_allowance_selection: str = Field(
        ...,
        description="Hospital daily allowance (Selection). Example: 'CHF 200/day'"
    )
    healing_costs: str = Field(
        ...,
        description="Healing costs. Example: 'Covered up to CHF 5,000'"
    )

class LegalProtection(BaseModel):
    coverage_module: List[str] = Field(
        ...,
        description="Legal protection coverage module. Example: ['Traffic legal cover']"
    )
    listed_under: List[str] = Field(
        ...,
        description="Legal protection listed under. Example: ['Additional coverage']"
    )
    option: List[str] = Field(
        ...,
        description="Legal protection options. Example: ['Civil disputes']"
    )
    option_selection: str = Field(
        ...,
        description="Legal protection option (Selection). Example: 'Civil disputes'"
    )
    
class CarCriteria(BaseModel):
    general: Optional[General] = Field(
        None,
        description="General criteria for the car insurance product."
    )
    liability: Optional[Liability] = Field(
        None,
        description="Liability coverage details."
    )
    partial_insurance: Optional[PartialInsurance] = Field(
        None,
        description="Partial insurance coverage details."
    )
    fully_comprehensive_insurance: Optional[FullyComprehensiveInsurance] = Field(
        None,
        description="Fully comprehensive insurance coverage details."
    )
    gross_negligence: Optional[GrossNegligence] = Field(
        None,
        description="Gross negligence coverage details."
    )
    compensation: Optional[Compensation] = Field(
        None,
        description="Compensation coverage details."
    )
    parking_damage: Optional[ParkingDamage] = Field(
        None,
        description="Parking damage coverage details."
    )
    glass_plus: Optional[GlassPlus] = Field(
        None,
        description="Glass Plus coverage details."
    )
    vehicle_interior: Optional[VehicleInterior] = Field(
        None,
        description="Vehicle interior coverage details."
    )
    tires_and_rims: Optional[TiresAndRims] = Field(
        None,
        description="Tires and rims coverage details."
    )
    vehicle_key: Optional[VehicleKey] = Field(
        None,
        description="Vehicle key coverage details."
    )
    charging_station_wallbox: Optional[ChargingStationWallbox] = Field(
        None,
        description="Charging station (wallbox) coverage details."
    )
    battery: Optional[Battery] = Field(
        None,
        description="Battery coverage details."
    )
    cyber_attacks_remediation_costs: Optional[CyberAttacksRemediationCosts] = Field(
        None,
        description="Cyber-attack remediation costs coverage details."
    )
    items_carried: Optional[ItemsCarried] = Field(
        None,
        description="Items carried coverage details."
    )
    rental_replacement_vehicle: Optional[RentalReplacementVehicle] = Field(
        None,
        description="Rental/replacement vehicle coverage details."
    )
    assistance: Optional[Assistance] = Field(
        None,
        description="Assistance services provided with the insurance."
    )
    repair_service: Optional[RepairService] = Field(
        None,
        description="Repair service options available with the insurance."
    )
    accident: Optional[Accident] = Field(
        None,
        description="Accident coverage options."
    )
    legal_protection: Optional[LegalProtection] = Field(
        None,
        description="Legal protection coverage options."
    )
    

class GeneralPoints(BaseModel):
    product_variants_available: List[str] = Field(
        ..., 
        description="List all product variants available (e.g., 'Single Trip', 'Annual', 'Family', 'Business')."
    )
    contract_duration_options: List[str] = Field(
        ..., 
        description="Contract duration options (e.g., 'Single trip: 7 days', 'Annual: 12 months', 'Other')."
    )
    special_discounts_available: List[str] = Field(
        ..., 
        description="Special discounts available (e.g., 'Family', 'Senior', 'Online booking')."
    )
    territorial_validity: List[str] = Field(
        ..., 
        description="Territorial validity regions (e.g., 'Europe', 'Worldwide', 'Worldwide excl. USA-Canada')."
    )
    cancellation_rights: List[str] = Field(
        ..., 
        description="Cancellation rights (e.g., 'Automatic renewal: No', 'Special termination rights apply')."
    )
    notice_period: str = Field(
        ..., 
        description="Notice period (e.g., '1 month', '30 days' or 'Automatic expiry')."
    )
    service_features: List[str] = Field(
        ..., 
        description="Service features included (e.g., '24/7 hotline', 'Online claims', 'App-based support')."
    )
    online_purchase_available: List[str] = Field(
        ..., 
        description="Online purchase availability (e.g., 'Yes', 'No', 'Restrictions apply')."
    )
    annual_premium_basic_coverage: str = Field(
        ..., 
        description="Annual premium for basic coverage (e.g., 'From CHF 100')."
    )
    annual_premium_additional_coverage: str = Field(
        ..., 
        description="Annual premium for additional coverage options (e.g., 'CHF 20 for sports coverage')."
    )
    payment_methods: List[str] = Field(
        ..., 
        description="Payment methods supported (e.g., 'Monthly', 'Annual', 'Per trip')."
    )
    leisure_protection: List[str] = Field(
        ..., 
        description="Leisure protection coverage (e.g., 'Covered up to CHF 200', 'Not covered')."
    )
    pet_coverage: List[str] = Field(
        ..., 
        description="Pet coverage options (e.g., 'Optional: up to CHF 100', 'Excluded')."
    )
    epidemic_pandemic_coverage: List[str] = Field(
        ..., 
        description="Epidemic/pandemic coverage (e.g., 'Covered', 'Excluded', 'Limited coverage')."
    )
    min_max_trip_duration: str = Field(
        ..., 
        description="Minimum/maximum trip duration (e.g., '3 days min / 180 days max')."
    )
    age_limits: str = Field(
        ..., 
        description="Age limits for travel (e.g., 'Min age 18 / Max age 75')."
    )
    waiting_periods: str = Field(
        ..., 
        description="Waiting periods before coverage applies (e.g., 'None', 'X days by coverage type')."
    )

class GroupOfPeople(BaseModel):
    individual_insurance: str = Field(
        ..., 
        description="Individual insurance criteria (e.g., 'Age 18–65; health screening required')."
    )
    family_insurance: str = Field(
        ..., 
        description="Family insurance definition (e.g., 'Spouse + up to 3 children under 18')."
    )
    additional_insured_persons: str = Field(
        ..., 
        description="Additional insured persons allowed (e.g., 'Up to 2 additional adults')."
    )
    family_definition: List[str] = Field(
        ..., 
        description="Definition of family members (e.g., 'Spouse', 'Children until age 18')."
    )

class BasicCoverage(BaseModel):
    insured_events_overview: List[str] = Field(
        ..., 
        description="Covered events overview (e.g., ['Cancellation', 'Delay', 'Medical'])."
    )
    cancellation_maximum_coverage: str = Field(
        ..., 
        description="Maximum cancellation coverage (e.g., 'CHF 2,000 per person')."
    )
    cancellation_covered_reasons: List[str] = Field(
        ..., 
        description="Covered cancellation reasons (e.g., 'Illness', 'Accident')."
    )
    cancellation_deductible: str = Field(
        ..., 
        description="Cancellation deductible (e.g., 'CHF 50')."
    )
    cancellation_time_limits: str = Field(
        ..., 
        description="Cancellation time limits (e.g., 'Within 48 hours of booking')."
    )
    cancellation_covered_costs: List[str] = Field(
        ..., 
        description="Covered cancellation costs (e.g., 'Flights', 'Hotels')."
    )
    cancellation_exclusions: List[str] = Field(
        ..., 
        description="Cancellation exclusions (e.g., 'Pre-existing conditions')."
    )
    cancellation_additional_benefits: List[str] = Field(
        ..., 
        description="Additional cancellation benefits (e.g., 'Waiver of deductible for medical staff')."
    )
    trip_interruption: str = Field(
        ..., 
        description="Trip interruption coverage (e.g., 'Covered up to CHF 1,000')."
    )
    trip_delay: str = Field(
        ..., 
        description="Trip delay compensation (e.g., 'CHF 50/day after 12h delay')."
    )
    missed_departure: str = Field(
        ..., 
        description="Missed departure coverage (e.g., 'Covered up to CHF 200')."
    )
    personal_assistance_available: bool = Field(
        ..., 
        description="Is personal assistance available? (e.g., True for 24/7 service)."
    )
    medical_evacuation: str = Field(
        ..., 
        description="Medical evacuation coverage (e.g., 'Unlimited')."
    )
    repatriation: str = Field(
        ..., 
        description="Repatriation coverage (e.g., 'Unlimited for medical necessity')."
    )
    hospital_visit_organization: str = Field(
        ..., 
        description="Hospital visit organization coverage (e.g., 'Up to CHF 500 per visitor')."
    )
    return_of_children: str = Field(
        ..., 
        description="Return of children coverage (e.g., 'Covered up to age 15')."
    )
    search_and_rescue_costs: str = Field(
        ..., 
        description="Search and rescue coverage (e.g., 'Up to CHF 5,000')."
    )
    medical_referral_service: str = Field(
        ..., 
        description="Medical referral service availability (e.g., '24/7 in EN/DE/FR')."
    )
    other_personal_assistance: List[str] = Field(
        ..., 
        description="Other personal assistance services (e.g., ['Interpreter service'])."
    )
    vehicle_assistance_available: bool = Field(
        ..., 
        description="Is vehicle assistance available? (e.g., True)."
    )
    breakdown_assistance: str = Field(
        ..., 
        description="Breakdown assistance coverage (e.g., 'CHF 300 for car')."
    )
    towing_service: str = Field(
        ..., 
        description="Towing service details (e.g., 'Up to 50 km')."
    )
    replacement_vehicle: str = Field(
        ..., 
        description="Replacement vehicle provision (e.g., '3 days, compact car')."
    )
    onwards_return_journey: str = Field(
        ..., 
        description="Onward/return journey coverage (e.g., 'Up to CHF 1,000')."
    )
    vehicle_return: str = Field(
        ..., 
        description="Vehicle return conditions (e.g., 'Covered; licensed driver required')."
    )
    other_vehicle_assistance: List[str] = Field(
        ..., 
        description="Other vehicle assistance services (e.g., ['Fuel delivery'])."
    )
    additional_accommodation: str = Field(
        ..., 
        description="Additional accommodation coverage (e.g., 'CHF 150/day up to CHF 600')."
    )
    phone_costs: str = Field(
        ..., 
        description="Phone costs coverage (e.g., 'Up to CHF 100 for local calls')."
    )
    translation_services: str = Field(
        ..., 
        description="Translation services coverage (e.g., 'Up to CHF 200 in emergencies')."
    )
    legal_advance_payment: str = Field(
        ..., 
        description="Legal advance payment details (e.g., 'Up to CHF 5,000; repay within 30 days')."
    )
    bail_bond_advance: str = Field(
        ..., 
        description="Bail bond advance coverage (e.g., 'Up to CHF 10,000')."
    )
    other_cost_coverage: List[str] = Field(
        ..., 
        description="Other cost coverages (e.g., ['Visa fees'])."
    )
    business_travel_basic_coverage: List[str] = Field(
        ..., 
        description="Basic business travel coverage (e.g., ['Included'])."
    )
    business_travel_additional_premium: str = Field(
        ..., 
        description="Additional premium for business travel (e.g., '+10%')."
    )
    business_equipment: str = Field(
        ..., 
        description="Business equipment coverage (e.g., 'Up to CHF 2,000 for laptop')."
    )
    replacement_person: str = Field(
        ..., 
        description="Replacement person coverage (e.g., 'Up to CHF 1,500')."
    )
    business_interruption: str = Field(
        ..., 
        description="Business interruption coverage (e.g., 'Up to CHF 3,000/day')."
    )

class AdditionalCoverage(BaseModel):
    travel_legal_protection_available: bool = Field(
        ..., 
        description="Is travel legal protection available? (e.g., True)."
    )
    legal_protection_coverage_limit: str = Field(
        ..., 
        description="Legal protection coverage limit (e.g., 'CHF 2,000 per case')."
    )
    legal_protection_deductible: str = Field(
        ..., 
        description="Legal protection deductible (e.g., 'CHF 200')."
    )
    legal_protection_covered_disputes: List[str] = Field(
        ..., 
        description="Types of disputes covered (e.g., ['Contract disputes', 'Traffic fines'])."
    )
    legal_protection_geographic_scope: List[str] = Field(
        ..., 
        description="Geographic scope for legal protection (e.g., ['Switzerland', 'EU'])."
    )
    legal_protection_waiting_period: str = Field(
        ..., 
        description="Legal protection waiting period (e.g., '30 days')."
    )
    travel_luggage_available: bool = Field(
        ..., 
        description="Is luggage coverage available? (e.g., True)."
    )
    luggage_sum_insured: str = Field(
        ..., 
        description="Luggage insured sum (e.g., 'CHF 1,500')."
    )
    luggage_per_item_limit: str = Field(
        ..., 
        description="Per item limit for luggage (e.g., 'CHF 500')."
    )
    valuables_limit: str = Field(
        ..., 
        description="Valuables coverage limit (e.g., 'CHF 300 for jewelry')."
    )
    luggage_deductible: str = Field(
        ..., 
        description="Luggage deductible amount (e.g., 'CHF 50')."
    )
    luggage_covered_perils: List[str] = Field(
        ..., 
        description="Covered luggage perils (e.g., ['Theft', 'Damage'])."
    )
    luggage_delay_compensation: str = Field(
        ..., 
        description="Luggage delay compensation (e.g., 'After 12h: CHF 100')."
    )
    luggage_exclusions: List[str] = Field(
        ..., 
        description="Luggage exclusions (e.g., ['Bicycles'])."
    )
    cdw_coverage_available: bool = Field(
        ..., 
        description="Is CDW coverage available? (e.g., True)."
    )
    cdw_coverage_limit: str = Field(
        ..., 
        description="CDW coverage limit (e.g., 'CHF 2,000 per event')."
    )
    cdw_vehicle_types: List[str] = Field(
        ..., 
        description="Vehicle types covered under CDW (e.g., ['Cars'])."
    )
    cdw_geographic_validity: List[str] = Field(
        ..., 
        description="Geographic validity for CDW (e.g., ['Europe'])."
    )
    cdw_rental_duration_limit: str = Field(
        ..., 
        description="Max rental duration for CDW (e.g., 'Max 30 days')."
    )
    cdw_premium: str = Field(
        ..., 
        description="Premium for CDW (e.g., 'CHF 25')."
    )

class OtherBuildingBlocks(BaseModel):
    ebike_assistance_available: bool = Field(
        ..., 
        description="Is e-bike assistance available? (e.g., True)."
    )
    ebike_breakdown_service: str = Field(
        ..., 
        description="E-bike breakdown service (e.g., 'CHF 100 within 20 km')."
    )
    ebike_transport: str = Field(
        ..., 
        description="E-bike transport details (e.g., 'To nearest repair shop within 50 km')."
    )
    ebike_replacement_vehicle: str = Field(
        ..., 
        description="E-bike replacement vehicle provision (e.g., 'Loaner e-bike for 2 days')."
    )
    ebike_onward_journey: str = Field(
        ..., 
        description="E-bike onward journey support (e.g., 'CHF 80 taxi voucher')."
    )
    ebike_theft_assistance: str = Field(
        ..., 
        description="E-bike theft assistance details (e.g., 'Covers lock replacement')."
    )
    home_assistance_available: bool = Field(
        ..., 
        description="Is home assistance available? (e.g., True)."
    )
    emergency_home_repairs: str = Field(
        ..., 
        description="Emergency home repair services (e.g., 'Up to CHF 500 for plumbing')."
    )
    security_services: str = Field(
        ..., 
        description="Security services provided (e.g., '2-hour patrol after break-in')."
    )
    key_service: str = Field(
        ..., 
        description="Key service details (e.g., 'CHF 100 for lockout')."
    )
    property_monitoring: str = Field(
        ..., 
        description="Property monitoring services (e.g., '24/7 alarm forwarding')."
    )
    medical_costs_available: bool = Field(
        ..., 
        description="Are medical costs covered? (e.g., True)."
    )
    medical_costs_coverage_limit: str = Field(
        ..., 
        description="Medical costs coverage limit (e.g., 'CHF 10,000 per event')."
    )
    medical_costs_deductible: str = Field(
        ..., 
        description="Medical costs deductible (e.g., 'CHF 100')."
    )
    covered_treatments: List[str] = Field(
        ..., 
        description="Covered medical treatments (e.g., ['Emergency', 'Dental'])."
    )
    direct_billing: str = Field(
        ..., 
        description="Direct billing arrangements (e.g., 'Yes with network hospitals')."
    )
    pre_authorization_required: bool = Field(
        ..., 
        description="Is pre-authorization required? (e.g., True)."
    )
    medical_costs_exclusions: List[str] = Field(
        ..., 
        description="Medical cost exclusions (e.g., ['Pre-existing conditions'])."
    )
    insolvency_protection_available: bool = Field(
        ..., 
        description="Is insolvency protection available? (e.g., True)."
    )
    insolvency_coverage_limit: str = Field(
        ..., 
        description="Insolvency protection limit (e.g., 'CHF 2,000 per booking')."
    )
    insolvency_covered_providers: List[str] = Field(
        ..., 
        description="Providers covered under insolvency protection (e.g., ['Airlines'])."
    )
    insolvency_covered_costs: List[str] = Field(
        ..., 
        description="Costs covered by insolvency protection (e.g., ['Rebooking fees'])."
    )
    insolvency_time_limits: str = Field(
        ..., 
        description="Insolvency protection booking time limits (e.g., 'Booked at least 7 days prior')."
    )
    insolvency_exclusions: List[str] = Field(
        ..., 
        description="Insolvency protection exclusions (e.g., ['Low-cost carriers'])."
    )

class Summary(BaseModel):
    product_name: str = Field(
        ..., 
        description="Product name as written (e.g., 'General Policy Conditions (GPC) Travel Insurance 2025')."
    )
    product_type: List[str] = Field(
        ..., 
        description="Product type(s) available (e.g., ['Single Trip', 'Annual'])."
    )
    target_market: List[str] = Field(
        ..., 
        description="Intended target markets (e.g., ['Leisure', 'Business'])."
    )
    single_trip_price_from: str = Field(
        ..., 
        description="Single trip starting price (e.g., 'CHF 50')."
    )
    annual_individual_from: str = Field(
        ..., 
        description="Annual individual policy starting price (e.g., 'CHF 200')."
    )
    annual_family_from: str = Field(
        ..., 
        description="Annual family policy starting price (e.g., 'CHF 350')."
    )
    unique_selling_points: List[str] = Field(
        ..., 
        description="Unique selling points (e.g., ['No deductible for children'])."
    )
    major_exclusions: List[str] = Field(
        ..., 
        description="Major exclusions (e.g., ['Adventure sports'])."
    )
    special_features: List[str] = Field(
        ..., 
        description="Special features beyond standard coverage (e.g., ['Carbon offset contribution'])."
    )

class TravelInsuranceProduct(BaseModel):
    general_points: GeneralPoints
    group_of_people: GroupOfPeople
    basic_coverage: BasicCoverage
    additional_coverage: AdditionalCoverage
    other_building_blocks: OtherBuildingBlocks
    summary: Summary
