from app.models.document import Document

def test_create_document(db_session):
    doc = Document(
        source_type="text",
        original_text="This is a test reaction write-up."
    )

    # Add the document to the session and commit
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)

    # Verify that the document was created
    assert doc.id is not None
    assert doc.source_type == "text"
    assert doc.original_text == "This is a test reaction write-up."
    assert doc.status == "pending"

    # Close the session
    db_session.close()