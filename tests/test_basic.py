from app.config import TestConfig


def test_app_starts():
    from app import create_app

    app = create_app(config_class=TestConfig)  # config applied first

    client = app.test_client()
    response = client.get("/")

    assert response.status_code in (200, 302)
