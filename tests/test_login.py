from werkzeug.security import generate_password_hash

from conftest import fetch_user
from database.db import create_user

VALID = {
    "name": "Nitish Kumar",
    "email": "nitish@example.com",
    "password": "supersecret",
}

INVALID_MESSAGE = "Invalid email or password."


def _create_test_user():
    create_user(VALID["name"], VALID["email"], generate_password_hash(VALID["password"]))


def test_login_with_correct_credentials_redirects_to_landing(client):
    _create_test_user()
    response = client.post(
        "/login", data={"email": VALID["email"], "password": VALID["password"]}
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_login_sets_session_flashes_and_lands_on_index(client):
    _create_test_user()
    response = client.post(
        "/login",
        data={"email": VALID["email"], "password": VALID["password"]},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"flash-success" in response.data
    assert b"Sign out" in response.data


def test_login_wrong_password_shows_generic_error_and_no_session(client):
    _create_test_user()
    response = client.post(
        "/login", data={"email": VALID["email"], "password": "wrongpassword"}
    )

    assert response.status_code == 200
    assert INVALID_MESSAGE.encode() in response.data
    assert b"Sign out" not in response.data
    assert b"Sign in" in response.data


def test_login_nonexistent_email_shows_same_generic_error(client):
    response = client.post(
        "/login", data={"email": "nobody@example.com", "password": "whatever1"}
    )

    assert response.status_code == 200
    assert INVALID_MESSAGE.encode() in response.data


def test_login_email_is_case_insensitive(client):
    _create_test_user()
    response = client.post(
        "/login",
        data={"email": "NITISH@Example.COM", "password": VALID["password"]},
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_login_repopulates_email_on_error(client):
    _create_test_user()
    response = client.post(
        "/login", data={"email": VALID["email"], "password": "wrongpassword"}
    )

    assert VALID["email"].encode() in response.data
    assert b"wrongpassword" not in response.data


def test_login_form_posts_to_url_for(client):
    import os

    template = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "templates",
        "login.html",
    )
    with open(template, encoding="utf-8") as handle:
        source = handle.read()

    assert "url_for('login')" in source
    assert 'action="/login"' not in source

    response = client.get("/login")
    assert response.status_code == 200
    assert b'action="/login"' in response.data


def test_logout_clears_session_flashes_and_redirects(client):
    _create_test_user()
    client.post("/login", data={"email": VALID["email"], "password": VALID["password"]})

    response = client.get("/logout", follow_redirects=True)

    assert response.status_code == 200
    assert b"flash-success" in response.data
    assert b"Sign in" in response.data
    assert b"Sign out" not in response.data


def test_logout_redirects_to_landing(client):
    _create_test_user()
    client.post("/login", data={"email": VALID["email"], "password": VALID["password"]})

    response = client.get("/logout")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_logout_while_logged_out_does_not_error(client):
    response = client.get("/logout")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_login_does_not_create_or_modify_users(client):
    _create_test_user()
    client.post("/login", data={"email": VALID["email"], "password": "wrongpassword"})

    assert fetch_user(VALID["email"])["name"] == VALID["name"]


def test_login_page_redirects_when_already_logged_in(client):
    _create_test_user()
    client.post("/login", data={"email": VALID["email"], "password": VALID["password"]})

    response = client.get("/login")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_register_page_redirects_when_already_logged_in(client):
    _create_test_user()
    client.post("/login", data={"email": VALID["email"], "password": VALID["password"]})

    response = client.get("/register")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")
