# core/ai/interpret.py
import datetime
from .spec import SearchSpec

def interpret_prompt_to_spec(prompt: str) -> SearchSpec:
    """
    Stub. Replace with LangChain later.
    Must return a SearchSpec.
    """
    spec = SearchSpec(query_text=prompt.strip())

    # Example defaulting behavior (adjust to taste):
    # If user says "recent" / "modern", default last 7 years
    lowered = prompt.lower()
    if "recent" in lowered or "modern" in lowered or "new" in lowered:
        year = datetime.date.today().year - 7
        spec.min_release_year = year
        spec.defaults_used.append(f"Assumed recent → release_year ≥ {year}")

    # If user says "highly rated" / "best", default baseline >= 7
    if "best" in lowered or "highly rated" in lowered or "top" in lowered:
        spec.min_baseline_score = 7.0
        spec.defaults_used.append("Assumed highly rated → baseline_score ≥ 7.0")

    # Limit default
    spec.limit = 50

    return spec
