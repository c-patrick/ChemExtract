def test_retry_failed_document(client, monkeypatch, db_session):
    # Force a failure in document processing
    def fail_parse_document(text):
        raise ValueError("Forced failure")

    # Patch in the background module where it's imported
    monkeypatch.setattr("app.services.background.parse_document", fail_parse_document)

    payload = {
        "source_type": "text",
        "original_text": "This is a test document that will fail processing.",
    }

    # Create document
    create_response = client.post("/documents/", json=payload)
    doc = create_response.json()

    # Manually trigger background processing
    from app.services.background import process_document

    process_document(doc["id"], db_session)

    # Now check that status is failed
    get_response = client.get(f"/documents/{doc['id']}")
    assert get_response.json()["status"] == "failed"

    # Now make parser succeed
    def succeed_parse_document(text):
        return {
            "summary": "This is a successful summary after retry.",
            "confidence_score": 0.95,
            "parser_version": "1.0.0",
        }

    # Patch the success version in the background module
    monkeypatch.setattr(
        "app.services.background.parse_document", succeed_parse_document
    )

    # Retry processing the failed document
    retry_response = client.post(f"/documents/{doc['id']}/reprocess")
    assert retry_response.status_code == 200

    # Manually trigger background processing again for the retry
    db_session.expire_all()  # Refresh from DB
    process_document(doc["id"], db_session)

    get_response = client.get(f"/documents/{doc['id']}/reaction")
    assert get_response.status_code == 200
    assert get_response.json()["summary"] == "This is a successful summary after retry."
