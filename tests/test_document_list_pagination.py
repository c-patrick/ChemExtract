def test_document_list_pagination(client, db_session):
    for i in range(15):
        client.post(
            "/documents/", json={"source_type": "text", "original_text": f"Doc {i}"}
        )

    response = client.get("/documents/?page=2&page_size=5")
    data = response.json()

    assert response.status_code == 200
    assert len(data["items"]) == 5
    assert data["page"] == 2
    assert data["page_size"] == 5
    assert data["total"] >= 15
