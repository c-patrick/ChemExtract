def test_create_document(client):
    payload = {
        "source_type": "text",
        "original_text": "This is a synthetic chemistry write-up",
    }

    response = client.post("/documents/", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["id"] is not None
    assert data["source_type"] == "text"
    assert data["status"] == "pending"


def test_get_document(client):
    # Create a document to retrieve
    payload = {
        "source_type": "text",
        "original_text": "This is a synthetic chemistry write-up",
    }

    create_response = client.post("/documents/", json=payload)
    doc_id = create_response.json()["id"]

    # Now, retrieve the document
    get_response = client.get(f"/documents/{doc_id}")
    assert get_response.status_code == 200
    retrieved_data = get_response.json()

    assert retrieved_data["id"] == doc_id
    assert retrieved_data["source_type"] == "text"
    assert (
        retrieved_data["status"] == "parsed"
    )  # Since background processing runs synchronously in tests


def test_get_nonexistent_document(client):
    response = client.get("/documents/9999")  # Assuming this ID does not exist

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}
