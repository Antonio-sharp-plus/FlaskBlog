def test_app_starts():
    from main import app
    client = app.test_client()
    response = client.get("/")
    assert response.status_code in [200, 302]
