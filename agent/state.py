from typing import TypedDict, List, Optional

class CompareState(TypedDict):
    user_input: str
    detected_category: str  # Catégorie détectée pour la requête utilisateur
    axa_result: str
    generali_result: str
    comparison: str