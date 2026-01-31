def test_get_reaction_success(client):
    payload = {
        "source_type": "text",
        "original_text": "This is a test document with a chemical reaction.",
    }

    create_response = client.post("/documents/", json=payload)
    doc_id = create_response.json()["id"]

    response = client.get(f"/documents/{doc_id}/reaction")

    assert response.status_code == 200
    data = response.json()

    assert data["document_id"] == doc_id
    assert "summary" in data
    assert "confidence_score" in data
    assert "parser_version" in data

    def test_get_reaction_processing(client, monkeypatch):
        def slow_parse(text: str):
            import time

            time.sleep(0.1)

            return {
                "summary": "This is a summary of the chemical reaction.",
                "confidence_score": 0.95,
                "parser_version": "1.0.0",
            }

        monkeypatch.setattr("app.services.background.parse_document", slow_parse)

        payload = {
            "source_type": "text",
            "original_text": "Processing reaction.",
        }

        response = client.post("/documents/", json=payload)
        doc_id = response.json()["id"]

        reaction_response = client.get(f"/documents/{doc_id}/reaction")
        assert reaction_response.status_code == 202
