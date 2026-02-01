from app.models.reaction import Reaction


def test_reaction_structured_fields(db_session):
    reaction = Reaction(
        document_id=1,
        summary="Test",
        confidence_score=0.9,
        parser_version="test",
        yield_percentage=75.0,
        reagents=["A", "B"],
        solvents=["THF"],
        conditions={"temp": "25 C"},
    )

    db_session.add(reaction)
    db_session.commit()

    stored = db_session.query(Reaction).first()

    assert stored.reagents == ["A", "B"]
    assert stored.conditions["temp"] == "25 C"
