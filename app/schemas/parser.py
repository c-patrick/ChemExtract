from pydantic import BaseModel
from typing import List, Optional, Dict


class Reagent(BaseModel):
    name: str
    quantity: Optional[str] = None


class ReactionParsed(BaseModel):
    summary: str
    reagents: List[Reagent]
    solvents: List[str]
    conditions: Dict[str, Optional[str]]  # Temperature, time, atmosphere, etc.
    yield_percentage: Optional[float] = None
    confidence_score: float
    parser_version: str
