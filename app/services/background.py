from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.reaction import Reaction

from app.services.parser import parse_document


def process_document(document_id: int, db: Session):
    doc = db.get(Document, document_id)
    if not doc:
        return

    doc.status = "processing"
    db.commit()

    existing_reaction = (
        db.query(Reaction).filter(Reaction.document_id == doc.id).first()
    )
    if existing_reaction:
        db.delete(existing_reaction)
        db.commit()

    try:
        result = parse_document(doc.original_text)

        reaction = Reaction(
            document_id=doc.id,
            summary=result["summary"],
            confidence_score=result["confidence_score"],
            parser_version=result["parser_version"],
        )

        db.add(reaction)
        doc.status = "parsed"
        db.commit()

    except Exception as e:
        doc.status = "failed"
        db.commit()
        print(f"Failed to process document {doc.id}: {e}")
