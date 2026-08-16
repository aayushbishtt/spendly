# Spec: Login and Logout

## Overview
This step wires up authentication for Spendly. `GET /login` and its
template already exist and render correctly; this step adds `POST /login`
so a registered user can actually sign in, plus a real `GET /logout` to
end that session. It introduces Flask's signed-cookie `session` as the
app's auth mechanism, storing the logged-in user's id. This is the
foundation every later protected page (profile, expenses) will read from,
building directly on the `users` table and `get_user_by_email()` helper
from Step 2.

## Depends on
- Step 1 (Database setup) — `users` table and `get_db()`. Confirmed complete.
- Step 2 (Registration) — `get_user_by_email()` in `database/db.py` and
  working account creation with hashed passwords. Confirmed complete.

## Routes
- `POST /login` — validate email/password against the `users` table,
  start a session on success, re-render `login.html` with an error on
  failure — public
- `GET /login` — unchanged, already implemented
- `GET /logout` — clear the session and redirect to the landing page —
  logged-in (safe to hit while logged out too; it just becomes a no-op
  redirect)

## Database changes
No schema changes and no new functions. `get_user_by_email()` (added in
Step 2) is sufficient to look up the row to check the password against.

## Templates
- **Create:** none
- **Modify:**
  - `templates/login.html` — change the hardcoded `action="/login"` to
    `action="{{ url_for('login') }}"` per the no-hardcoded-URLs rule
  - `templates/base.html` — nav currently always shows "Sign in" /
    "Get started". Make it session-aware: when `session.user_id` is set,
    show a "Sign out" link (`url_for('logout')`) instead of those two
    links, so logout is actually reachable from the UI

## Files to change
- `app.py` — add `methods=["GET", "POST"]` to the `login` route and
  implement the POST branch; implement `logout` (replace the stub, remove
  it from the placeholder-routes section)
- `templates/login.html` — fix hardcoded form action
- `templates/base.html` — session-aware nav links

## Files to create
None.

## New dependencies
No new dependencies. Flask's built-in `session` (already signed with
`app.secret_key`, already configured in `app.py`) is what backs the
logged-in state — no new package needed for this.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug — verify with
  `werkzeug.security.check_password_hash`, never compare hashes or
  plaintext directly
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- All DB access stays in `database/db.py`; the route only calls
  `get_user_by_email()`, it does not run SQL itself
- On `POST /login`:
  - Look up the user by email (normalise with `.strip().lower()`, same as
    registration, since emails are stored lowercased)
  - If no user matches, or `check_password_hash()` fails, show one
    generic error ("Invalid email or password") — do not reveal whether
    the email exists, that's a user-enumeration leak
  - On success, set `session["user_id"] = user["id"]`, flash a success
    message, and redirect to `url_for('landing')` (`/profile` is still a
    stub, so it isn't a valid redirect target yet)
  - Use `abort()` only for actual HTTP errors, not for bad credentials —
    that's expected user input and belongs in the `error` re-render, same
    pattern as registration
- On `GET /logout`:
  - `session.clear()`, flash a "Signed out" message, redirect to
    `url_for('landing')`
  - No error if the visitor wasn't logged in — just clears an
    already-empty session and redirects the same way
- Out of scope for this step: a `login_required` decorator / route
  protection. No route needs to enforce login yet (`/profile` and the
  expense routes are still stubs owned by later steps) — adding a guard
  now would be untested and premature. That decorator belongs to the step
  that protects its first real route.

## Definition of done
- [ ] Signing in with the seeded demo account (`demo@spendly.com` /
      `demo123`) redirects to `/` and the nav shows "Sign out" instead of
      "Sign in" / "Get started"
- [ ] Signing in with a wrong password re-renders `/login` with "Invalid
      email or password" and does not start a session
- [ ] Signing in with an email that doesn't exist shows the same "Invalid
      email or password" message (no distinct "no such user" text)
- [ ] Visiting `/logout` while logged in clears the session, flashes a
      signed-out message, and redirects to `/`, after which the nav shows
      "Sign in" / "Get started" again
- [ ] Visiting `/logout` while logged out doesn't error — redirects to `/`
      the same way
- [ ] The login form posts to `url_for('login')`, not a hardcoded path
- [ ] `pytest` passes with no new failures
- [ ] App still starts cleanly on port 5001 with no errors
