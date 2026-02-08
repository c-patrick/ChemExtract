from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict
from datetime import datetime


class ReactionResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True  # Allows SQLAlchemy model instances to be converted to Pydantic models
    )

    id: int
    document_id: int
    summary: str
    confidence_score: float

    parser_backend: str  # "openai" | "fake" | "regex" | etc
    model_name: str | None  # "gpt-4o-mini", "gpt-4.1", None for fake
    parser_version: str  # your internal version, e.g. "v1"
    parsed_at: datetime

    yield_percentage: Optional[float]

    reagents: List[str]
    solvents: List[str]
    conditions: Dict[str, str]


class ReactionParsed(BaseModel):
    summary: str
    confidence_score: float
    parser_version: str
    parser_backend: str
    model_name: Optional[str]
    yield_percentage: Optional[float]

    reagents: List[str]
    solvents: List[str]
    conditions: Dict[str, str]
