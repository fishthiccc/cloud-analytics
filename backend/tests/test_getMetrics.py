def test_get_metrics(client):
    response = client.get("api/v1/metrics/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)