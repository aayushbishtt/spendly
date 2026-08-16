import os
import sqlite3

from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash

from database.db import create_user, get_db, get_user_by_email, init_db, seed_db

app = Flask(__name__)

# The fallback below is a KNOWN PUBLIC STRING — anyone who knows it can forge
# session cookies. Export SECRET_KEY for any non-local use. Flask sessions are
# signed, not encrypted, either way.
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-insecure-secret-change-me")


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    # Lowercased so that case variants cannot become separate accounts —
    # SQLite's default collation makes both the UNIQUE index and the lookup
    # case-sensitive. Step 3's login lookup must normalise identically.
    email = request.form.get("email", "").strip().lower()
    # Not stripped — leading and trailing spaces are legitimate password
    # characters, and trimming them would silently change the password.
    password = request.form.get("password", "")

    error = None
    if not name:
        error = "Please enter your name."
    elif not email:
        error = "Please enter your email address."
    elif len(password) < 8:
        error = "Password must be at least 8 characters."
    elif get_user_by_email(email) is not None:
        error = "An account with that email already exists."

    if error is None:
        try:
            create_user(name, email, generate_password_hash(password))
        except sqlite3.IntegrityError:
            # Two simultaneous posts can both pass the check above; the UNIQUE
            # index on email is what actually guarantees uniqueness.
            error = "An account with that email already exists."
        else:
            flash("Account created. Please sign in.", "success")
            return redirect(url_for("login"))

    return render_template("register.html", error=error, name=name, email=email)


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/login")
def login():
    return render_template("login.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    return "Logout — coming in Step 3"


@app.route("/profile")
def profile():
    return "Profile page — coming in Step 4"


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


with app.app_context():
    init_db()
    seed_db()


if __name__ == "__main__":
    app.run(debug=True, port=5001)
