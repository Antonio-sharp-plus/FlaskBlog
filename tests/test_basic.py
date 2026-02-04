def test_app_starts():
    from app import create_app

    app = create_app()
    app.config.from_object("app.config.TestConfig")

    client = app.test_client()
    response = client.get("/")

    assert response.status_code in (200, 302)
