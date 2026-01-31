from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict


class ReactionResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True  # Allows SQLAlchemy model instances to be converted to Pydantic models
    )

    id: int
    document_id: int
    summary: str
    confidence_score: float
    parser_version: str


class ReactionParsed(BaseModel):
    summary: str
    confidence_score: float
    parser_version: str
    yield_percentage: Optional[float]

    reagents: List[str]
    solvents: List[str]
    conditions: Dict[str, str]
