def test_get_towns(client):
    response = client.get("/api/v1/towns/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)