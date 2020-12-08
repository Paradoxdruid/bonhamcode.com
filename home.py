# -*- coding: utf-8 -*-
import dash
# import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc


MyApp = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

MyApp.title = "Bonham Code"

server = MyApp.server

layout_title = html.H4("Bonham Code")

footer = dbc.Row(
    [
        dbc.Col(
            html.P(
                [
                    "Visit ",
                    html.A(
                        "Bonham Chemistry",
                        href="http://www.bonhamchemistry.com",
                        className="card-text",
                    ),
                ],
                className="card-text",
            ),
        ),
        dbc.Col(
            html.P(
                [
                    "Designed by ",
                    html.A(
                        "Dr. Andrew J. Bonham",
                        href="https://github.com/Paradoxdruid",
                        className="card-text",
                    ),
                ],
                className="card-text text-right",
            ),
        ),
    ],
    justify="between",
)


def make_card(name, explanation, link):
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H5(name, className="card-title"),
                    html.P(explanation, className="card-text"),
                    dbc.Button("Try it", color="primary", className="mr-1", href=link),
                ]
            )
        ],
    )


buffer_card = make_card(
    "Buffer Adjustment Solver",
    "A calculator for adjusting pH and concentration of buffers from stock solutions",
    "https://buffer.bonhamcode.com",
)
menten_card = make_card(
    "Michaelis-Menten Fitting",
    "Create interactive graphs that fit replicate data to the Michaelis-Menten kinetics equation",
    "https://michaelis.bonhamcode.com",
)
dose_card = make_card(
    "Dose-Response Fitting",
    "Create interactive graphs that fit data to a Langmuir-Isotherm reversible binding equation",
    "https://doseresponse.bonhamcode.com",
)

body_contents = html.Div(
    [dbc.Row([dbc.Col(buffer_card), dbc.Col(menten_card), dbc.Col(dose_card), ], ), ],
)


MyApp.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(layout_title),
                                dbc.CardBody(body_contents),
                                dbc.CardFooter(footer),
                            ],
                            className="border-primary mb-3 border rounded bg-white shadow-lg",
                            style={"min-height": "25vh"},
                        ),
                    ],
                    width=8,
                    md=6,
                    lg=6,
                ),
            ],
            justify="center",
            className="pt-5",
        ),
    ],
    fluid=True,
    className="bg-secondary",
    style={"min-height": "100vh"},
)


if __name__ == "__main__":
    MyApp.run_server(debug=True)
