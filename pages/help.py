"""Starting points for people seeking support."""

from dash import Input, Output, callback, dcc, html, register_page

register_page(__name__, path="/help", name="Get help")

OPTIONS = [
    (
        "helping",
        "I'm starting to help a parent or loved one.",
        [
            "Start with a conversation about what support they want and what decisions they want to keep making themselves.",
            "With their permission, list trusted contacts and gather questions about bills, benefits, and care.",
            "Explore Caregiver support and Community Programs for possible next steps.",
        ],
    ),
    (
        "planning",
        "I'm planning ahead.",
        [
            "Write down your priorities and who you would trust to support you.",
            "Discuss financial and care preferences with your chosen support network.",
            "Ask a qualified professional about legal arrangements and explore Government Benefits and Community Programs.",
        ],
    ),
    (
        "scam",
        "I'm worried about a scam.",
        [
            "Pause before sending money or sharing passwords, account details, or verification codes.",
            "Contact your financial institution using the number on your card or statement, not a number supplied by a suspicious caller or message.",
            "If money or information was shared, contact your financial institution promptly and ask about securing your accounts. Talk with someone you trust.",
        ],
    ),
    (
        "care",
        "We need help finding care.",
        [
            "Talk together about daily needs, preferences, budget, and the kind of help that would be welcome.",
            "Explore Caregiver support, Transportation, and Meal programs as starting points.",
            "Verify providers, costs, availability, and eligibility directly before making arrangements.",
        ],
    ),
    (
        "unsure",
        "I'm not sure, just need help.",
        [
            "You do not need to have everything figured out. Start with the one thing that feels most pressing.",
            "Ask a trusted person to help you write down questions and choose a manageable next step.",
            "Explore Community Programs and Caregiver support to learn what kinds of assistance may be available.",
        ],
    ),
]

layout = html.Div(
    [
        html.H2("How can we help?"),
        html.P("Choose the starting point that feels right for you."),
        dcc.RadioItems(
            id="help-choice",
            options=[{"label": label, "value": key} for key, label, _ in OPTIONS],
            value=None,
            className="help-menu",
        ),
        html.Div(id="help-guidance", role="region", **{"aria-live": "polite"}),
        html.P(
            "General guidance only, not legal, financial, or medical advice. "
            "The Resources page contains fictional demo programs.",
            className="card-note",
        ),
    ]
)


@callback(Output("help-guidance", "children"), Input("help-choice", "value"))
def show_guidance(choice):
    if choice is None:
        return html.P("Select an option above to see suggested next steps.")
    for key, label, steps in OPTIONS:
        if key == choice:
            return html.Section(
                [
                    html.H3(label),
                    html.Ul([html.Li(step) for step in steps]),
                    html.Div(
                        [
                            dcc.Link("Explore resources", href="/resources"),
                            dcc.Link("Who are you?", href="/who-are-you"),
                        ],
                        className="help-links",
                    ),
                ],
                className="help-guidance",
            )
    raise ValueError(f"Unknown help option: {choice!r}")
