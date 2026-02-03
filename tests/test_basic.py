def test_app_starts():
    from app import create_app
    from app.extensions import db

    app = create_app()
    app.config.from_object("app.config.TestConfig")

    with app.app_context():
        db.create_all()

    client = app.test_client()
    response = client.get("/")

    assert response.status_code in (200, 302)
