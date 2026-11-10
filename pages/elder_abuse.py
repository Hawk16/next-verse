"""Practical tips for preventing and responding to elder abuse."""

from dash import dcc, html, register_page

register_page(__name__, path="/elder-abuse", name="Elder Abuse")

TIPS = [
    "Stay connected with people you trust. Regular conversations and visits can make it easier to ask for help early.",
    "Keep control of your own money and decisions as much as possible. Choose supporters who respect your wishes and boundaries.",
    "Review bank and credit-card statements regularly, and ask your financial institution about alerts for unusual activity.",
    "Use strong, unique passwords and multifactor authentication. Do not share passwords, PINs, or one-time verification codes.",
    "Pause before sending money, signing documents, or changing account access. Verify unexpected requests using a trusted contact method.",
    "Keep important financial, legal, and identity documents secure, and tell a trusted person how to reach them if needed.",
    "Before signing a power of attorney or other legal document, talk privately with an independent, qualified professional about what it allows.",
    "If you receive care, discuss your preferences and concerns with someone you trust. Where possible, speak with health or care professionals privately.",
    "Learn the warning signs, such as unexplained injuries, missing money, unpaid bills despite available funds, or someone preventing private contact.",
    "If you suspect abuse, tell someone you trust and contact local adult protective services or an equivalent support agency. You do not need to be certain before asking for help.",
    "If someone is in immediate danger, contact your local emergency number. Avoid confronting a suspected abuser if doing so could increase risk.",
]

layout = html.Div(
    [
        html.H2("Preventing Elder Abuse"),
        html.P(
            "Everyone deserves to be safe, respected, and in control of their choices. "
            "These steps can help reduce risk and make it easier to get support."
        ),
        html.Ul([html.Li(tip) for tip in TIPS], className="planning-suggestions"),
        html.P(
            "Abuse can be physical, emotional, sexual, or financial, and may include neglect. "
            "If you are worried, seek confidential help from a trusted local service. "
            "General educational information only; services and reporting options vary by location.",
            className="card-note",
        ),
        dcc.Link("Explore resources", href="/resources"),
        html.Span(" | "),
        dcc.Link("Get help", href="/help"),
    ]
)
