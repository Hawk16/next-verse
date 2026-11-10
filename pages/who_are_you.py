"""A simple role selection page."""

from dash import dcc, html, register_page

register_page(__name__, path="/who-are-you", name="Who are you?")

ROLES = [
    ("individual", "Individual seeking help"),
    ("family", "Family Member"),
    ("friend", "Friend"),
    ("healthcare", "Healthcare provider"),
    ("attorney", "Attorney"),
    ("accountant", "Accountant"),
    ("other", "Other"),
]

layout = html.Div(
    [
        html.H2("Who are you?"),
        html.P("Choose the option that best describes you."),
        dcc.RadioItems(
            id="visitor-role",
            options=[{"label": label, "value": value} for value, label in ROLES],
            value=None,
            persistence=True,
            persistence_type="session",
            className="help-menu",
        ),
        html.P(
            "This selection is saved for this browser session only. "
            "It does not verify your identity or grant access to someone else's information.",
            className="card-note",
        ),
    ]
)
