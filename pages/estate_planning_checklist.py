"""Simple estate planning suggestions."""

from dash import dcc, html, register_page

register_page(__name__, path="/estate-planning-checklist", name="Estate Planning Checklist")

SUGGESTIONS = [
    "Write down your wishes for your assets, care, and the people who depend on you.",
    "Inventory property, financial accounts, debts, insurance, and important documents.",
    "Consult a qualified local attorney about creating or updating a will.",
    "Discuss whether a trust is appropriate for your goals and circumstances.",
    "Choose an executor or trustee and discuss the responsibilities with them.",
    "Review beneficiary designations and account ownership for consistency with your plan.",
    "Discuss a financial power of attorney, its scope, and when it takes effect.",
    "Review healthcare decision-making documents and advance care preferences.",
    "Plan for dependents, pets, digital assets, and final expenses where applicable.",
    "Ask about legal and tax consequences before making gifts or transferring ownership.",
    "Store signed documents securely and tell authorized people where to find them.",
    "Review your plan after major life changes and periodically with your attorney.",
]

layout = html.Div(
    [
        html.H2("Estate Planning Checklist"),
        html.P("Use these suggestions to prepare for a conversation about your estate plans."),
        html.Ul([html.Li(item) for item in SUGGESTIONS], className="planning-suggestions"),
        html.P(
            "General educational information, not legal or tax advice. Requirements vary "
            "by location; consult a qualified attorney and tax professional.",
            className="card-note",
        ),
        dcc.Link("Explore resources", href="/resources"),
    ],
    className="checklist-page",
)
