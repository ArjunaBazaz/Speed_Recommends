# core/ai/spec.py
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class SearchSpec(BaseModel):
    query_text: str = ""

    # OR within each list; AND across lists
    genres_any: List[str] = Field(default_factory=list)
    platforms_any: List[str] = Field(default_factory=list)
    developers_any: List[str] = Field(default_factory=list)

    min_release_year: Optional[int] = None
    max_release_year: Optional[int] = None
    min_baseline_score: Optional[float] = None

    sort_by: Literal["relevance", "baseline_score", "release_year"] = "relevance"
    limit: int = 50

    # For transparency in UI
    defaults_used: List[str] = Field(default_factory=list)
