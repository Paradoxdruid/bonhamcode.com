#!/usr/bin/env python3

"""
Dash web app for fitting dose-response data.
"""

from typing import Any, Dict, List

# Imports
import dash
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objs as go
from dash import Input, Output, State, dcc, html
from scipy.optimize import leastsq

NDArray = np.ndarray[Any, np.dtype[np.float64]]

# Initialize app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

server = app.server  # server initialization for passenger wsgi

xaxis_label = html.Div(
    children=[
        dbc.Label("X values:", className="mr-2"),
        dbc.Input(type="input-1-state", id="input-1-state", value="0,1,2,3,4"),
    ],
    className="mr-3",
)

yaxis_label = html.Div(
    children=[
        dbc.Label("Y values:", className="mr-2"),
        dbc.Input(type="input-2-state", id="input-2-state", value="1,2,5,8,9"),
    ],
    className="mr-3",
)

input_form = dbc.Col(
    children=[
        dbc.Form(
            children=[
                xaxis_label,
                yaxis_label,
                dbc.Button(
                    "Submit",
                    id="submit-button",
                    n_clicks=0,
                    color="primary",
                    className="mr-1",
                ),
            ],
        ),
    ],
)

card_header = dbc.CardHeader(
    children=[
        html.H3(
            "Bonham Code: Dose Response Fitting",
            className="card-title",
        ),
        html.H6(
            "Input x and y data for dose response / Langmuir isothem fitting",
            className="card-subtitle",
        ),
    ]
)

graph_output = dbc.Col(
    children=[
        dbc.Card(
            children=[
                dcc.Graph(
                    id="indicator-graphic",
                    config={"displayModeBar": True},
                ),
            ],
            className="mt-3 border-primary p-1",
        ),
    ]
)

card_footer = dbc.Row(
    children=[
        dbc.Col(
            html.P(
                children=[
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
                children=[
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


app.layout = dbc.Container(
    children=[
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        dbc.Card(
                            children=[
                                card_header,
                                dbc.CardBody(
                                    children=[
                                        dbc.Row([input_form]),
                                        dbc.Row([graph_output]),
                                    ],
                                ),
                                dbc.CardFooter(card_footer),
                            ],
                            color="dark",
                            outline=True,
                            className="shadow-lg",
                        ),
                    ],
                    xs={"size": 10, "offset": 1},
                    lg={"size": 6, "offset": 3},
                ),
            ],
            style={"padding-top": "50px"},
        ),
    ],
    fluid=True,
    className="bg-secondary",
    style={"min-height": "100vh"},  # fill the whole background
)


old_layout = html.Div(
    children=[
        html.Button(
            id="submit-button",
            n_clicks=0,
            children="Submit",
        ),
    ],
    style={"margin": "auto", "width": "50%"},
)


# Functions
def residuals(y: NDArray, fitinfo: Dict[str, Any]) -> float:
    fit_error = 0
    fit_variance = 0

    for i in range(len(fitinfo["fvec"])):
        fit_error += (fitinfo["fvec"][i]) ** 2
        fit_variance += (y[i] - np.mean(y)) ** 2
    r_squared = 1 - (fit_error / fit_variance)
    return r_squared


@app.callback(
    Output("indicator-graphic", "figure"),
    [Input("submit-button", "n_clicks")],
    [State("input-1-state", "value"), State("input-2-state", "value")],
)  # type: ignore[misc]
def update_graph2(click: int, xs: str, ys: str) -> Dict[str, Any]:
    if click == -1:
        x = np.zeros(5)
        y = np.zeros(5)
    else:
        x = np.array(xs.split(","), dtype=float)
        y = np.array(ys.split(","), dtype=float)

    def equation(variables: List[float], x: NDArray) -> NDArray:
        return variables[0] + (
            (variables[1] - variables[0]) / (1 + 10 ** (variables[2] - x))
        )

    def error(variables: List[float], x: NDArray, y: NDArray) -> NDArray:
        return equation(variables, x) - y

    variable_guesses = [np.min(y), np.max(y), np.mean(x)]
    output = leastsq(error, variable_guesses, args=(x, y), full_output=1)
    variables = output[0]
    fitinfo = output[2]
    r_squared = residuals(y, fitinfo)
    x_range = np.arange(np.min(x), np.max(x), abs(np.max(x) / 100))
    plot1 = go.Scatter(x=x, y=y, mode="markers", showlegend=False)
    plot2 = go.Scatter(
        x=x_range, y=equation(variables, x_range), mode="lines", showlegend=False
    )
    plot_data = [plot1, plot2]
    layout = go.Layout(
        title="Dose Response",
        # width=600,
        template="ggplot2",
        annotations=[
            dict(
                x=0.5,
                y=0.9,
                xref="paper",
                yref="paper",
                text="R squared = {}".format(round(r_squared, 3)),
                showarrow=False,
            ),
            dict(
                x=0.5,
                y=0.85,
                xref="paper",
                yref="paper",
                text="Kd = {}".format(round(variables[2], 3)),
                showarrow=False,
            ),
        ],
        xaxis=dict(title="Concentration"),
        yaxis=dict(title="Response"),
    )
    return {"data": plot_data, "layout": layout}


# Main magic
if __name__ == "__main__":
    app.run_server(debug=True)
