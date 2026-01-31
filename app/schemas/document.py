from pydantic import BaseModel, ConfigDict
from typing import List


class DocumentCreate(BaseModel):
    source_type: str
    original_text: str


class DocumentResponse(BaseModel):
    id: int
    source_type: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class PaginatedDocuments(BaseModel):
    items: List[DocumentResponse]
    total: int
    page: int
    page_size: int
