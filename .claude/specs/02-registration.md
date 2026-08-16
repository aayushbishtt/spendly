# Spec: Registration

## Overview
This step wires up the `/register` page so visitors can actually create a
Spendly account. The `register.html` template and `GET /register` route
already exist and render correctly; this step adds the `POST /register`
handling that validates the submitted form, hashes the password, inserts a
new row into `users`. On success the user is shown with a success message and then sends the person on to sign in. It's the first
piece of real write-path logic in the app, building directly on the schema
and DB helpers from Step 1.

## Depends on
- Step 1 (Database setup) — `database/db.py` must have a working
  `get_db()` and the `users` table must exist. Confirmed complete.

## Routes
- `POST /register` — validate and create a new account, redirect to
  `/login` on success, re-render `register.html` with an error on failure —
  public
- `GET /register` — unchanged, already implemented

## Database changes
No schema changes. The `users` table already has everything needed
(`name`, `email`, `password_hash`). This step adds two functions to
`database/db.py` (logic only, no schema change):
- `create_user(name, email, password_hash)` — inserts a row into `users`,
  returns the new user id
- `get_user_by_email(email)` — returns the matching row or `None`, used to
  check for duplicate emails before inserting

## Templates
- **Create:** none
- **Modify:** `templates/register.html` — change the hardcoded
  `action="/register"` to `action="{{ url_for('register') }}"` per the
  no-hardcoded-URLs rule; no structural changes needed, the `{% if error %}`
  block already exists for validation feedback

## Files to change
- `app.py` — add `methods=["GET", "POST"]` to the `register` route and
  implement the POST branch
- `database/db.py` — add `create_user()` and `get_user_by_email()`
- `templates/register.html` — fix hardcoded form action

## Files to create
None.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with `werkzeug.security.generate_password_hash`
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- All DB access (insert, lookup) lives in `database/db.py`, not inline in
  the route
- Server-side validation is required even though the form has HTML5
  `required`/`type="email"` — never trust client-side validation alone:
  - `name` and `email` must be non-empty after `.strip()`
  - `password` must be at least 8 characters
  - `email` must not already exist (check via `get_user_by_email()` before
    insert, and treat a `sqlite3.IntegrityError` on the unique constraint
    as a fallback duplicate-email error)
- On any validation failure, re-render `register.html` with `error` set to
  a user-facing message — do not use `abort()` for form validation errors
  (`abort()` is for HTTP-level errors, this is expected user input)
- On success, redirect to `url_for('login')` — do not start a session or
  auto-login; that is out of scope for this step

## Definition of done
- [ ] Visiting `/register` and submitting valid name/email/password
      creates a new row in the `users` table with a hashed password
- [ ] After successful registration, the browser is redirected to `/login`
- [ ] Submitting with an already-registered email re-renders the register
      page with an error and does not create a duplicate row
- [ ] Submitting with a password under 8 characters re-renders the page
      with an error and does not create a row
- [ ] Submitting with an empty name or email re-renders the page with an
      error and does not create a row
- [ ] The register form posts to `url_for('register')`, not a hardcoded
      path
- [ ] `pytest` passes with no new failures
- [ ] App still starts cleanly on port 5001 with no errors
