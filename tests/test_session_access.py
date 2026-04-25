from flask import Flask, session


def test_session_contains_sets_vary_cookie():
    app = Flask(__name__)
    app.secret_key = "secret"

    @app.route("/")
    def index():
        "user_id" in session
        return "ok"

    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    assert "Vary" in response.headers
    assert "Cookie" in response.headers["Vary"]
