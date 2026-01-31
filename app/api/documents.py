from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db, SessionLocal
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentResponse, PaginatedDocuments
from app.models.reaction import Reaction
from app.schemas.reaction import ReactionResponse
from app.services.background import process_document

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.post("/", response_model=DocumentResponse)
def create_document(
    payload: DocumentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    doc = Document(
        source_type=payload.source_type,
        original_text=payload.original_text,
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)

    background_tasks.add_task(
        process_document, doc.id, SessionLocal()
    )  # Background tasks cannot reuse request DB sessions, so need to explicitly create a new session

    return doc


@router.get("/{document_id}/reaction", response_model=ReactionResponse)
def get_document_reaction(document_id: int, db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.status in {"pending", "processing"}:
        raise HTTPException(status_code=202, detail="Document is still being processed")

    if doc.status == "failed":
        raise HTTPException(
            status_code=422,
            detail="Document processing failed",  # Unprocessable content error
        )

    reaction = db.query(Reaction).filter(Reaction.document_id == document_id).first()

    if not reaction:
        raise HTTPException(
            status_code=500, detail="Document processed but no reaction found"
        )

    return reaction


@router.get("/", response_model=PaginatedDocuments)
def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * page_size

    total = db.scalar(select(func.count(Document.id)))

    documents = (
        db.execute(
            select(Document)
            .order_by(Document.id.desc())
            .offset(offset)
            .limit(page_size)
        )
        .scalars()
        .all()
    )

    return {
        "items": documents,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/{document_id}/reprocess", response_model=DocumentResponse)
def reprocess_document(
    document_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    doc = db.get(Document, document_id)

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.status != "failed":
        raise HTTPException(
            status_code=300,
            detail="Only failed documents can be retried",  # Only process documents that previously failed
        )

    # Reset document status and clear existing reaction
    doc.status = "pending"
    db.commit()
    db.refresh(doc)

    background_tasks.add_task(
        process_document, doc.id, SessionLocal()
    )  # Background tasks cannot reuse request DB sessions, so need to explicitly create a new session

    return doc
