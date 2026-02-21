def test_post_metrics(client):
    payload = {
        "name": "Temperature", 
        "value": 30.7
    }

    response = client.post(
        "/api/v1/metrics/",
          json=payload
          )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["value"] == payload["value"]