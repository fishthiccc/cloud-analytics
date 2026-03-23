def test_get_weather_observations(client):
    response = client.get("/api/v1/weather/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
