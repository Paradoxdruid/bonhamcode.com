# -*- coding: utf-8 -*-
import dash

# import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

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
    [
        dbc.Row(
            [
                dbc.Col(buffer_card),
                dbc.Col(menten_card),
                dbc.Col(dose_card),
            ],
        ),
    ],
)

# Create app layout
nav_text = dbc.NavLink("Designed by", disabled=True, href="#")  # dbc.NavItem()

nav_item = dbc.NavLink("Dr. Andrew J. Bonham", href="https://github.com/Paradoxdruid")
# dbc.NavItem()

BONHAM_LOGO = MyApp.get_asset_url('bonham_logo.png')

side_bar = dbc.Nav(
    [
        dbc.NavItem(nav_text),
        dbc.NavItem(nav_item),
    ],
    fill=True,
    className="ml-auto",
)

navbar = dbc.Navbar(
    [
        dbc.Row(
            [
                dbc.Col(html.Img(src=BONHAM_LOGO, height="60px"), className="mr-0", width=4),
                dbc.Col(dbc.NavbarBrand("Bonham Code", className="ml-0"), width=8),
            ],
            align="center",
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(side_bar, id="navbar-collapse", navbar=True),
    ],
    sticky="top",
)


bottom_bar = dbc.NavbarSimple(
    children=[
        dbc.NavLink(
            "MSU Denver Covid Tracker", href="https://msu-covid-tracker.herokuapp.com"
        ),
        # dbc.NavLink("Bonham Code projects", href="https://bonhamcode.com"),
        dbc.NavLink("Dr. Bonham's Research Lab", href="https://www.bonhamlab.com"),
    ],
    brand="Other Projects:",
    sticky="bottom",
    className="mt-2",
    fluid=True,
)

MyApp.layout = html.Div(
    [
        navbar,
        dbc.Container(
            fluid=True,
            children=[
                dbc.Row(
                    dbc.Col(
                        html.Div(
                            [body_contents],
                            className="m-3",
                        ),
                        width=12,
                        # style={
                        #     "min-width": "750px",
                        #     "max-width": "1400px",
                        # },
                    ),
                    className="mx-auto",
                ),
            ],
        ),
        bottom_bar,
    ],
)


old_layout = dbc.Container(
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


# add callback for toggling the collapse on small screens
@MyApp.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


if __name__ == "__main__":
    MyApp.run_server(debug=True)
