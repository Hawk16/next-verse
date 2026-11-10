"""Simple financial planning suggestions."""

from dash import dcc, html, register_page

register_page(__name__, path="/financial-checklist", name="Financial Checklist")

SUGGESTIONS = [
    "Write down your financial goals, priorities, and questions.",
    "List your income, essential expenses, debts, and savings.",
    "Create a realistic budget that includes irregular bills and unexpected costs.",
    "Review bill payments, subscriptions, and debt repayment options.",
    "Set an emergency savings goal that fits your circumstances.",
    "Review retirement income, benefits, and upcoming enrollment or withdrawal deadlines.",
    "Review insurance coverage and plan for healthcare, housing, and potential care costs.",
    "Review investment goals, risk, diversification, and fees with a qualified advisor.",
    "Ask a qualified tax professional about filing requirements and the tax effects of major decisions.",
    "Protect accounts with unique passwords, multifactor authentication, and transaction alerts.",
    "Choose trusted supporters, discuss boundaries, and arrange authorized access without sharing passwords.",
    "Keep financial records secure and schedule regular reviews as your needs change.",
]

layout = html.Div(
    [
        html.H2("Financial Checklist"),
        html.P("Use these suggestions as starting points for your financial planning."),
        html.Ul([html.Li(item) for item in SUGGESTIONS], className="planning-suggestions"),
        html.P(
            "General educational information, not personalized financial or tax advice. "
            "Consult qualified professionals about your circumstances.",
            className="card-note",
        ),
        dcc.Link("Explore resources", href="/resources"),
    ],
    className="checklist-page",
)
