"""Practical tips for recognizing and avoiding scams."""

from dash import dcc, html, register_page

register_page(__name__, path="/scams", name="Avoiding Scams")

TIPS = [
    "Pause when a message or caller creates urgency, fear, or secrecy. Take time to check the request before acting.",
    "Verify unexpected requests using a phone number or website you find independently, such as the number on your card or a known official website.",
    "Never share passwords, PINs, or one-time verification codes. A legitimate organization should not ask you to read these codes to them.",
    "Do not send money by gift card, cryptocurrency, wire transfer, or payment app because someone insists it is urgent or confidential.",
    "Be cautious with links and attachments in unexpected messages. Visit the organization’s official website directly instead of following a link.",
    "Do not allow an unexpected caller to access your computer or phone remotely or install software. Contact a trusted technician using a number you already know.",
    "Be skeptical of requests to move money to a ‘safe’ account, pay a fee to claim a prize, or provide personal information to fix an urgent problem.",
    "Discuss unusual financial requests with someone you trust before sending money or sharing information. A real request can wait while you verify it.",
    "Use unique passwords and multifactor authentication, enable account alerts, and review statements for unfamiliar charges or transfers.",
    "If you shared information or sent money, contact your financial institution promptly using a trusted number and ask how to secure your accounts.",
    "Save suspicious messages and report them to the relevant organization or local consumer-protection agency. If you are in immediate danger, contact your local emergency number.",
]

layout = html.Div(
    [
        html.H2("Tips for Avoiding Scams"),
        html.P(
            "Scammers may pretend to be a bank, government agency, business, "
            "or someone you know. These habits can help you protect your money "
            "and personal information."
        ),
        html.Ul([html.Li(tip) for tip in TIPS], className="planning-suggestions"),
        html.P(
            "If you think you have been targeted, it is okay to ask for help. "
            "Contact your financial institution using a trusted number and consider "
            "speaking with someone you trust. General educational information only.",
            className="card-note",
        ),
        dcc.Link("Get help", href="/help"),
        html.Span(" | "),
        dcc.Link("Explore resources", href="/resources"),
    ]
)
