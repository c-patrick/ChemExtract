from pydantic import BaseModel, ConfigDict


class ReactionResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True  # Allows SQLAlchemy model instances to be converted to Pydantic models
    )

    id: int
    document_id: int
    summary: str
    confidence_score: float
    parser_version: str
