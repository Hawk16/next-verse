"""Entry point for the two-page Dash application."""

import hmac
import secrets
from datetime import timedelta

from dash import Dash, dcc, html, page_container
from flask import (
    Flask,
    abort,
    has_request_context,
    redirect,
    render_template,
    request,
    session,
)


server = Flask(__name__)
server.config.update(
    SECRET_KEY=secrets.token_hex(32),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
)


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]


def validate_csrf():
    expected = session.get("csrf_token", "")
    supplied = request.form.get("csrf_token", "")
    if not expected or not hmac.compare_digest(expected.encode(), supplied.encode()):
        abort(400, description="Invalid form token. Reload the page and try again.")


@server.before_request
def require_login():
    if request.path == "/logout":
        return None
    if request.path == "/" and request.method == "POST":
        return None
    if request.path in {
        "/assets/style.css", "/assets/next-verse.png", "/assets/welcome-photo.png"
    } and request.method == "GET":
        return None
    if session.get("demo_logged_in"):
        return None
    if request.path == "/" and request.method == "GET":
        return render_template("login.html", csrf_token=csrf_token())
    if request.path.startswith("/_dash"):
        abort(401, description="Click Log in to open the demo dashboard.")
    return redirect("/")


@server.post("/")
def login():
    validate_csrf()
    action = request.form.get("action", "login")
    if action not in {"login", "get-started"}:
        abort(400, description="Unknown welcome action.")
    session.clear()
    session.permanent = True
    session["demo_logged_in"] = True
    csrf_token()
    return redirect("/help" if action == "get-started" else "/")


@server.post("/logout")
def logout():
    validate_csrf()
    session.clear()
    return redirect("/")


@server.after_request
def prevent_page_caching(response):
    response.headers["Cache-Control"] = "no-store"
    return response


app = Dash(__name__, server=server, use_pages=True, title="next verse")


def dashboard_layout():
    token = csrf_token() if has_request_context() else ""
    return html.Div(
        [
            html.Header(
                [
                    html.Nav(
                        [
                            dcc.Link("Contacts", href="/"),
                            dcc.Link("Resources", href="/resources"),
                            dcc.Link("Get help", href="/help"),
                            dcc.Link("Who are you?", href="/who-are-you"),
                            dcc.Link("Financial Checklist", href="/financial-checklist"),
                            dcc.Link("Estate Planning Checklist", href="/estate-planning-checklist"),
                            dcc.Link("Preventing Elder Abuse", href="/elder-abuse"),
                            dcc.Link("Avoiding Scams", href="/scams"),
                        ],
                        className="navigation",
                    ),
                    html.Form(
                        [
                            dcc.Input(type="hidden", name="csrf_token", value=token),
                            html.Button("Sign out", type="submit"),
                        ],
                        action="/logout",
                        method="post",
                    ),
                ]
            ),
            html.Main(page_container),
            html.Footer(
                [
                    html.Img(
                        src="/assets/next-verse.png",
                        alt="Next Verse",
                        className="footer-logo",
                    ),
                    html.P(
                        "Navigate what comes next, together",
                        className="footer-tagline",
                    ),
                ],
                className="site-footer",
            ),
        ],
        className="container",
    )


app.layout = dashboard_layout

if __name__ == "__main__":
    app.run(debug=True)
