"""Resources for older adults and the people who support them."""

from dash import ALL, Input, Output, callback, clientside_callback, ctx, dcc, html, register_page
from dash.exceptions import PreventUpdate

register_page(__name__, path="/resources", name="Resources", redirect_from=["/trends"])

RESOURCES = [
    ("Caregiver support", "Support groups, respite care, and guidance for family caregivers."),
    ("Government Benefits", "Information about Social Security, Medicare, and benefits eligibility."),
    ("Community Programs", "Senior centers, social activities, and local support services."),
    ("Transportation", "Accessible rides, community shuttles, and transportation assistance."),
    ("Meal programs", "Home-delivered meals, community dining, and nutrition assistance."),
    ("Financial Planning", "Support with budgeting, retirement goals, and planning for future expenses."),
    ("Estate Planning", "Information about wills, trusts, beneficiaries, and planning with a qualified attorney."),
]

RESOURCE_ICONS = [
    "\N{HEAVY BLACK HEART}",
    "\N{CLASSICAL BUILDING}",
    "\N{BUSTS IN SILHOUETTE}",
    "\N{BUS}",
    "\N{FORK AND KNIFE}",
    "\N{CHART WITH UPWARDS TREND}",
    "\N{SCROLL}",
]

MOCK_PROGRAMS = [
    {
        "name": "Together Caregiver Circle",
        "services": "Weekly peer support, caregiver workshops, and respite planning.",
        "eligibility": "Family members and friends supporting an older adult.",
        "schedule": "Tuesdays, 2-3 PM; mock appointments available.",
        "cost": "Free in this fictional example.",
        "phone": "(202) 555-0111",
        "email": "caregivers@example.com",
    },
    {
        "name": "Benefits Navigation Desk",
        "services": "Help organizing questions about Social Security, Medicare, and benefit applications.",
        "eligibility": "Older adults and caregivers; actual benefit eligibility requires official review.",
        "schedule": "Monday-Friday, 9 AM-4 PM.",
        "cost": "Free information session in this fictional example.",
        "phone": "(202) 555-0112",
        "email": "benefits@example.com",
    },
    {
        "name": "Neighbor Connections Center",
        "services": "Social clubs, gentle exercise classes, and digital skills workshops.",
        "eligibility": "Community members aged 60 and older in this fictional example.",
        "schedule": "Monday-Friday, 10 AM-3 PM.",
        "cost": "Mock membership: $10 per month.",
        "phone": "(202) 555-0113",
        "email": "community@example.com",
    },
    {
        "name": "Friendly Rides",
        "services": "Accessible rides to appointments, grocery stores, and community activities.",
        "eligibility": "Older adults needing transportation within the fictional Demo City service area.",
        "schedule": "Weekdays, 8 AM-5 PM; request a ride two days ahead.",
        "cost": "Mock fare: $3 per one-way trip.",
        "phone": "(202) 555-0114",
        "email": "rides@example.com",
    },
    {
        "name": "Shared Table Meals",
        "services": "Home-delivered lunches and community dining with dietary options.",
        "eligibility": "Older adults needing meal support; mock intake appointment required.",
        "schedule": "Lunch delivery Monday-Friday, 11 AM-1 PM.",
        "cost": "Mock suggested contribution: $5 per meal; optional.",
        "phone": "(202) 555-0115",
        "email": "meals@example.com",
    },
    {
        "name": "Next Chapter Planning Desk",
        "services": "Budget reviews, retirement planning discussions, and guidance on preparing for care expenses.",
        "eligibility": "Older adults and trusted supporters attending with their permission.",
        "schedule": "Monday-Friday, 9 AM-4 PM; mock appointments available.",
        "cost": "Free introductory session in this fictional example.",
        "phone": "(202) 555-0116",
        "email": "planning@example.com",
    },
    {
        "name": "Estate Planning Guidance Desk",
        "services": "Discussions about wills, trusts, beneficiary designations, and questions to ask a qualified attorney.",
        "eligibility": "Adults planning ahead and trusted supporters attending with their permission.",
        "schedule": "Tuesday-Thursday, 9 AM-4 PM; mock appointments available.",
        "cost": "Free introductory information session in this fictional example.",
        "phone": "(202) 555-0117",
        "email": "estate@example.com",
    },
]

layout = html.Div(
    [
        html.H2("Resources"),
        html.P("Explore support for you and the people who care for you. Availability and eligibility vary by location."),
        html.Div(
            html.Table(
                [
                    html.Caption("Support resources"),
                    html.Thead(
                        html.Tr(
                            [html.Th(label, scope="col") for label in ["#", "Resource", "Description", "Explore"]]
                        )
                    ),
                    html.Tbody(
                        [
                            html.Tr(
                                [
                                    html.Td(index),
                                    html.Th(
                                        [
                                            html.Span(
                                                RESOURCE_ICONS[index - 1],
                                                className="resource-icon",
                                                **{"aria-hidden": "true"},
                                            ),
                                            html.Span(name),
                                        ],
                                        scope="row",
                                    ),
                                    html.Td(
                                        html.Span(
                                            description,
                                            className="resource-description",
                                            title=description,
                                        )
                                    ),
                                    html.Td(
                                        html.Button(
                                            "Explore",
                                            id={"type": "explore-resource", "index": index - 1},
                                            n_clicks=0,
                                            className="connect-button",
                                            **{"aria-label": f"Explore {name}"},
                                        )
                                    ),
                                ]
                            )
                            for index, (name, description) in enumerate(RESOURCES, start=1)
                        ]
                    ),
                ],
                className="contacts-table",
                id="resources-table",
            ),
            className="contacts-scroll",
            tabIndex=0,
            role="region",
            **{"aria-label": "Support resources"},
        ),
        html.Dialog(
            [
                html.Div(id="resource-details"),
                html.Form(
                    html.Button("Close", type="submit", autoFocus=True),
                    method="dialog",
                ),
            ],
            id="resource-modal",
            className="contact-modal",
            **{"aria-labelledby": "resource-card-heading"},
        ),
        dcc.Store(id="resource-modal-state"),
    ]
)


@callback(
    Output("resource-details", "children"),
    Input({"type": "explore-resource", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def explore_resource(clicks):
    if not any(clicks) or ctx.triggered_id is None:
        raise PreventUpdate
    index = ctx.triggered_id["index"]
    program = MOCK_PROGRAMS[index]
    return html.Div(
        [
            html.H2(RESOURCES[index][0], id="resource-card-heading"),
            html.P("Mock resource: all details below are fictional.", className="card-note"),
            html.H3(program["name"]),
            html.Dl(
                [
                    element
                    for label, key in [
                        ("Services", "services"),
                        ("Eligibility", "eligibility"),
                        ("Schedule", "schedule"),
                        ("Cost", "cost"),
                        ("Phone", "phone"),
                        ("Email", "email"),
                    ]
                    for element in [html.Dt(label), html.Dd(program[key])]
                ]
            ),
            html.P(
                "Not a referral or enrollment. Check actual programs for current availability and eligibility.",
                className="card-note",
            ),
        ],
        className="contact-card",
    )


clientside_callback(
    """
    function(details) {
        if (!details) return dash_clientside.no_update;
        const dialog = document.getElementById("resource-modal");
        if (!dialog.open) dialog.showModal();
        return Date.now();
    }
    """,
    Output("resource-modal-state", "data"),
    Input("resource-details", "children"),
    prevent_initial_call=True,
)
