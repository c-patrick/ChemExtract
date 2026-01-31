from app.models.document import Document
from app.models.reaction import Reaction

def test_create_reaction(db_session):
    # Create and add a Document to satisfy the ForeignKey constraint
    doc = Document(
        source_type="text",
        original_text="This is a test reaction write-up."
    )

    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)

    # Create a Reaction linked to the Document
    reaction = Reaction(
        document_id=doc.id,
        summary="This is a summary of the reaction.",
        confidence_score=0.95,
        parser_version="1.0.0"
    )

    # Add the reaction to the session and commit
    db_session.add(reaction)
    db_session.commit()
    db_session.refresh(reaction)

    # Verify that the reaction was created
    assert reaction.id is not None
    assert reaction.document_id == doc.id
    assert reaction.summary == "This is a summary of the reaction."
    assert reaction.confidence_score == 0.95
    assert reaction.parser_version == "1.0.0"

    # Close the session
    db_session.close()