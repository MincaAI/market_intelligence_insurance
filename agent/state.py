from typing import TypedDict, List, Optional

class CompareState(TypedDict):
    user_input: str
    product: str
    axa_result: str
    generali_result: str
    comparison: str
    axa_answer: str
    generali_answer: str