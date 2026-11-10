"""Home page listing trusted financial contacts."""

import re

from dash import ALL, Input, Output, State, callback, clientside_callback, ctx, dcc, html, no_update, register_page
from dash.exceptions import PreventUpdate

register_page(__name__, path="/", name="Contacts")

CONTACTS = [
    {
        "name": "Mr. Jones",
        "title": "Attorney",
        "role": "Power of Attorney",
        "phone": "(202) 555-0101",
        "email": "jones@example.com",
        "organization": "Jones Legal (fictional)",
        "address": "101 Example Lane, Demo City",
        "availability": "Monday-Friday, 9 AM-5 PM",
    },
    {
        "name": "Ms. Rivera",
        "title": "Financial Advisor",
        "role": "Financial Planning",
        "phone": "(202) 555-0102",
        "email": "rivera@example.com",
        "organization": "Rivera Financial Planning (fictional)",
        "address": "202 Sample Avenue, Demo City",
        "availability": "Monday-Thursday, 10 AM-4 PM",
    },
    {
        "name": "Mrs. Chen",
        "title": "Daughter",
        "role": "Trusted Contact",
        "phone": "(202) 555-0103",
        "email": "chen@example.com",
        "organization": "Family",
        "address": "303 Placeholder Court, Demo City",
        "availability": "Evenings and weekends",
    },
    {
        "name": "Mr. Patel",
        "title": "Accountant",
        "role": "Tax Preparation",
        "phone": "(202) 555-0104",
        "email": "patel@example.com",
        "organization": "Patel Accounting (fictional)",
        "address": "404 Demo Street, Demo City",
        "availability": "Monday-Friday, 8 AM-4 PM",
    },
]

FIELDS = [
    ("Name", "name", "Mr. Jones"),
    ("Title", "title", "Attorney, Daughter, Financial Advisor"),
    ("Role", "role", "Power of Attorney, Trusted Contact"),
    ("Phone", "phone", "(202) 555-0101"),
    ("Email", "email", "name@example.com"),
    ("Organization", "organization", "Organization or Family"),
    ("Address", "address", "Street address and city"),
    ("Availability", "availability", "Weekdays, 9 AM-5 PM"),
]


def contact_rows(contacts):
    return [
        html.Tr(
            [
                html.Th(contact["name"], scope="row"),
                html.Td(contact["title"]),
                html.Td(contact["role"]),
                html.Td(
                    html.Button(
                        "Connect",
                        id={"type": "connect-contact", "index": index},
                        n_clicks=0,
                        className="connect-button",
                        **{"aria-label": f"Connect with {contact['name']}"},
                    )
                ),
                html.Td(
                    html.Button(
                        [
                            html.Span(className="video-icon", **{"aria-hidden": "true"}),
                            "Video call",
                        ],
                        id={"type": "video-contact", "index": index},
                        n_clicks=0,
                        className="connect-button video-button",
                        **{"aria-label": f"Video call with {contact['name']}"},
                    )
                ),
            ],
            className="contacts-page",
        )
        for index, contact in enumerate(contacts)
    ]


layout = html.Div(
    [
        html.H2("Contacts"),
        html.P("The people who support you with your finances. These are fictional examples."),
        html.Div(
            html.Table(
                [
                    html.Caption("Financial support contacts"),
                    html.Thead(
                        html.Tr(
                            [
                                html.Th(column, scope="col")
                                for column in ["Name", "Title", "Role", "Connect", "Video call"]
                            ]
                        )
                    ),
                    html.Tbody(
                        contact_rows(CONTACTS),
                        id="contact-rows",
                    ),
                ],
                className="contacts-table",
                id="contacts-table",
            ),
            className="contacts-scroll",
            tabIndex=0,
            role="region",
            **{"aria-label": "Financial support contacts"},
        ),
        html.Dialog(
            [
                html.Div(id="connect-status"),
                html.Form(
                    html.Button("Close", type="submit", autoFocus=True),
                    method="dialog",
                ),
            ],
            id="contact-modal",
            className="contact-modal",
            **{"aria-labelledby": "contact-card-name"},
        ),
        dcc.Store(id="contact-modal-state"),
        dcc.Store(id="contacts-data", storage_type="local", data=CONTACTS),
        html.Button("+ Add contacts", id="add-contact", n_clicks=0, className="add-contact"),
        html.Dialog(
            [
                html.H2("Add a contact", id="add-contact-heading"),
                html.P("Name, title, and role are required. Saved only in this browser."),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Label(label, htmlFor=f"contact-{key}"),
                                dcc.Input(
                                    id=f"contact-{key}",
                                    type="email" if key == "email" else "text",
                                    placeholder=example,
                                    value="",
                                    maxLength=300,
                                ),
                            ]
                        )
                        for label, key, example in FIELDS
                    ],
                    className="add-contact-fields",
                ),
                html.P(id="add-contact-error", role="alert"),
                html.Button("Save contact", id="save-contact", n_clicks=0, type="button"),
                html.Form(html.Button("Cancel", type="submit"), method="dialog"),
            ],
            id="add-contact-modal",
            className="contact-modal",
            **{"aria-labelledby": "add-contact-heading"},
        ),
        dcc.Store(id="add-modal-state"),
        html.P(id="add-contact-success", role="status"),
        html.P(id="video-status", role="status", **{"aria-live": "polite"}),
    ]
)


@callback(
    Output("video-status", "children"),
    Input({"type": "video-contact", "index": ALL}, "n_clicks"),
    State("contacts-data", "data"),
    prevent_initial_call=True,
)
def video_contact(clicks, contacts):
    if not any(clicks) or ctx.triggered_id is None:
        raise PreventUpdate
    contact = contacts[ctx.triggered_id["index"]]
    return f"Video call with {contact['name']}: demo only, no call was started."


@callback(
    Output("connect-status", "children"),
    Input({"type": "connect-contact", "index": ALL}, "n_clicks"),
    State("contacts-data", "data"),
    prevent_initial_call=True,
)
def connect_contact(clicks, contacts):
    if not any(clicks) or ctx.triggered_id is None:
        raise PreventUpdate
    contact = contacts[ctx.triggered_id["index"]]
    return html.Div(
        [
            html.P("next verse", className="card-brand"),
            html.H2(contact["name"], id="contact-card-name"),
            html.P(contact["title"], className="card-title"),
            html.Hr(),
            html.Dl(
                [
                    element
                    for label, key in [
                        ("Role", "role"),
                        ("Phone", "phone"),
                        ("Email", "email"),
                        ("Organization", "organization"),
                        ("Address", "address"),
                        ("Availability", "availability"),
                    ]
                    for element in [html.Dt(label), html.Dd(contact[key])]
                ]
            ),
            html.P(
                "Demo only: no message was sent.",
                className="card-note",
            ),
        ],
        className="contact-card",
    )


@callback(Output("contact-rows", "children"), Input("contacts-data", "data"))
def render_contacts(contacts):
    return contact_rows(contacts)


@callback(
    Output("contacts-data", "data"),
    Output("add-contact-error", "children"),
    Output("add-contact-success", "children"),
    *[Output(f"contact-{key}", "value") for _, key, _ in FIELDS],
    Input("save-contact", "n_clicks"),
    State("contacts-data", "data"),
    *[State(f"contact-{key}", "value") for _, key, _ in FIELDS],
    prevent_initial_call=True,
)
def save_contact(clicks, contacts, *values):
    if not clicks:
        raise PreventUpdate
    contact = {key: (value or "").strip() for (_, key, _), value in zip(FIELDS, values)}
    missing = [label for label, key, _ in FIELDS[:3] if not contact[key]]
    error = ""
    if missing:
        error = f"Please enter: {', '.join(missing)}."
    elif any(len(value) > 300 for value in contact.values()):
        error = "Each field must be 300 characters or fewer."
    elif contact["email"] and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", contact["email"]):
        error = "Please enter a valid email address."
    if error:
        return (no_update, error, no_update, *[no_update for _ in FIELDS])
    return (
        contacts + [contact],
        "",
        f"Added {contact['name']} in this browser.",
        *["" for _ in FIELDS],
    )


clientside_callback(
    """
    function(clicks, contacts) {
        const dialog = document.getElementById("add-contact-modal");
        if (dash_clientside.callback_context.triggered_id === "add-contact" && clicks) {
            if (!dialog.open) dialog.showModal();
            document.getElementById("contact-name").focus();
        } else if (dialog.open) {
            dialog.close();
        }
        return Date.now();
    }
    """,
    Output("add-modal-state", "data"),
    Input("add-contact", "n_clicks"),
    Input("contacts-data", "data"),
    prevent_initial_call=True,
)


clientside_callback(
    """
    function(card) {
        if (!card) {
            return dash_clientside.no_update;
        }
        const dialog = document.getElementById("contact-modal");
        if (!dialog.open) {
            dialog.showModal();
        }
        return Date.now();
    }
    """,
    Output("contact-modal-state", "data"),
    Input("connect-status", "children"),
    prevent_initial_call=True,
)
