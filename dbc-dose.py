#!/usr/bin/env python3

"""
Dash web app for fitting dose-response data.
"""

# Imports
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import numpy
from scipy.optimize import leastsq
import plotly.graph_objs as go


# Initialize app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

server = app.server  # server initialization for passenger wsgi

xaxis_label = dbc.FormGroup(
    [
        dbc.Label("X values:", className="mr-2"),
        dbc.Input(type="input-1-state", id="input-1-state", value="0,1,2,3,4"),
    ],
    className="mr-3",
)

yaxis_label = dbc.FormGroup(
    [
        dbc.Label("Y values:", className="mr-2"),
        dbc.Input(type="input-2-state", id="input-2-state", value="1,2,5,8,9"),
    ],
    className="mr-3",
)

input_form = dbc.Col(
    [
        dbc.Form(
            [
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
            inline=True,
        ),
    ],
)

card_header = dbc.CardHeader(
    [
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
    [
        dbc.Card(
            [
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


app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                card_header,
                                dbc.CardBody(
                                    [
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
    [
        html.Button(
            id="submit-button",
            n_clicks=0,
            children="Submit",
        ),
    ],
    style={"margin": "auto", "width": "50%"},
)


# Functions
def residuals(y, fitinfo):
    fit_error = 0
    fit_variance = 0

    for i in range(len(fitinfo["fvec"])):
        fit_error += (fitinfo["fvec"][i]) ** 2
        fit_variance += (y[i] - numpy.mean(y)) ** 2
    r_squared = 1 - (fit_error / fit_variance)
    return r_squared


@app.callback(
    Output("indicator-graphic", "figure"),
    [Input("submit-button", "n_clicks")],
    [State("input-1-state", "value"), State("input-2-state", "value")],
)
def update_graph2(click, xs, ys):
    if click == -1:
        x = numpy.zeros(5)
        y = numpy.zeros(5)
    else:
        x = numpy.array(xs.split(","), dtype=float)
        y = numpy.array(ys.split(","), dtype=float)

    def equation(variables, x):
        return variables[0] + (
            (variables[1] - variables[0]) / (1 + 10 ** (variables[2] - x))
        )

    def error(variables, x, y):
        return equation(variables, x) - y

    variable_guesses = [numpy.min(y), numpy.max(y), numpy.mean(x)]
    output = leastsq(error, variable_guesses, args=(x, y), full_output=1)
    variables = output[0]
    fitinfo = output[2]
    r_squared = residuals(y, fitinfo)
    x_range = numpy.arange(numpy.min(x), numpy.max(x), abs(numpy.max(x) / 100))
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