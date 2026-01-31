from app.models.document import Document
from app.models.reaction import Reaction
from app.services.background import process_document


def test_background_processing(db_session):
    # Create a new document
    doc = Document(
        source_type="text",
        original_text="This is a test document containing chemical reactions write-ups.",
    )

    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)

    # Process the document in the background
    process_document(doc.id, db_session)

    # Fetch the updated document and verify status has changed to 'parsed'
    updated_doc = db_session.get(Document, doc.id)
    assert updated_doc.status == "parsed"

    # Verify that a reaction was created
    reactions = db_session.query(Reaction).all()
    assert len(reactions) == 1
    assert reactions[0].document_id == doc.id


def test_background_processing_failure(db_session, monkeypatch):
    # Create a new document with text that will cause parsing to fail
    doc = Document(
        source_type="text",
        original_text="This document will cause a parsing error.",
    )

    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)

    # Patch the fake_parse_document function to raise an exception
    def fake_fail(text: str):
        raise ValueError("Parsing failed intentionally")

    monkeypatch.setattr("app.services.background.parse_document", fake_fail)

    # Process the document in the background
    process_document(doc.id, db_session)

    # Fetch the updated document and verify status has changed to 'failed'
    updated_doc = db_session.get(Document, doc.id)
    assert updated_doc.status == "failed"

    # Verify that no reaction was created
    reactions = db_session.query(Reaction).all()
    assert len(reactions) == 0
