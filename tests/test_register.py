import os

from werkzeug.security import check_password_hash

from conftest import count_users, fetch_user
from database.db import DEFAULT_DB_PATH, get_db_path

VALID = {
    "name": "Nitish Kumar",
    "email": "nitish@example.com",
    "password": "supersecret",
}


def test_register_creates_user_with_hashed_password(client):
    client.post("/register", data=VALID)

    user = fetch_user("nitish@example.com")
    assert user is not None
    assert user["name"] == "Nitish Kumar"
    assert user["password_hash"] != "supersecret"
    assert "supersecret" not in user["password_hash"]
    assert check_password_hash(user["password_hash"], "supersecret")
    assert count_users() == 1


def test_register_redirects_to_login(client):
    response = client.post("/register", data=VALID)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_register_flashes_success_message(client):
    response = client.post("/register", data=VALID, follow_redirects=True)

    assert response.status_code == 200
    assert b"Account created" in response.data
    assert b"flash-success" in response.data
    assert b"Welcome back" in response.data


def test_register_rejects_duplicate_email(client):
    client.post("/register", data=VALID)
    response = client.post("/register", data={**VALID, "name": "Someone Else"})

    assert response.status_code == 200
    assert b"already exists" in response.data
    assert count_users() == 1
    assert fetch_user("nitish@example.com")["name"] == "Nitish Kumar"


def test_register_email_is_case_insensitive(client):
    client.post("/register", data=VALID)
    response = client.post(
        "/register", data={**VALID, "email": "NITISH@Example.COM"}
    )

    assert response.status_code == 200
    assert b"already exists" in response.data
    assert count_users() == 1


def test_register_stores_email_lowercased(client):
    client.post("/register", data={**VALID, "email": "MiXeD@Example.COM"})

    assert fetch_user("mixed@example.com") is not None
    assert fetch_user("MiXeD@Example.COM") is None


def test_register_rejects_short_password(client):
    # "short12" is exactly 7 characters.
    response = client.post("/register", data={**VALID, "password": "short12"})

    assert response.status_code == 200
    assert b"at least 8" in response.data
    assert count_users() == 0


def test_register_rejects_empty_name(client):
    response = client.post("/register", data={**VALID, "name": "   "})

    assert response.status_code == 200
    assert b"Please enter your name" in response.data
    assert count_users() == 0


def test_register_rejects_empty_email(client):
    response = client.post("/register", data={**VALID, "email": "   "})

    assert response.status_code == 200
    assert b"Please enter your email" in response.data
    assert count_users() == 0


def test_register_form_posts_to_url_for(client):
    # Asserting on the rendered output would be vacuous: url_for('register')
    # and a hardcoded "/register" render identically. Check the source.
    template = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "templates",
        "register.html",
    )
    with open(template, encoding="utf-8") as handle:
        source = handle.read()

    assert "url_for('register')" in source
    assert 'action="/register"' not in source

    response = client.get("/register")
    assert response.status_code == 200
    assert b'action="/register"' in response.data


def test_tests_do_not_use_the_real_database(tmp_path):
    """Canary: fail loudly if DB isolation ever breaks."""
    assert get_db_path() != DEFAULT_DB_PATH
    assert str(tmp_path) in get_db_path()
