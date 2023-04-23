import time
from pathlib import Path
from typing import Tuple

import dash_bootstrap_components as dbc
import pandas as pd
from dash import Dash, Input, Output, State, dash_table, dcc, html
from fealden.fealden.fealden import Fealden

# Set up dash server
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Fealden"
server = app.server  # Export server for use by Passenger framework

# Components for Layout
init_sequence_input = dbc.Row(
    children=[
        dbc.Label("Input sequence", html_for="sequence"),
        dbc.Input(type="text", id="sequence", value="CACGTG"),
        dbc.FormText(
            "Input aptamer or recognition element sequence",
            color="secondary",
        ),
        dbc.Label("Maximum sensor length", html_for="max_length"),
        dbc.Input(type="number", id="max_length", value=50),
        dcc.Checklist(["3' Fixed MB"], inline=True, id="fixed"),
    ]
)

form1 = dbc.Form(children=[init_sequence_input])

intro = dcc.Markdown(
    """
Experimental web-server for the [Fealden](https://github.com/Paradoxdruid/fealden)
biosensor design optimization software.  Use at your own risk.

It may takes up to 20 seconds after hitting **Submit** to get results."""
)

# App layout using dash-bootstrap-components
app.layout = dbc.Container(
    children=[
        dbc.Row(
            children=[
                dbc.Col(
                    dbc.Card(
                        children=[
                            dbc.CardHeader(html.H4("Fealden")),
                            dbc.CardBody(
                                children=[
                                    dbc.Row(
                                        children=[
                                            dbc.Col(
                                                children=[
                                                    intro,
                                                    form1,
                                                ],
                                                xs={"size": 12},
                                                sm={"size": 12},
                                                md={"size": 6},
                                                lg={"size": 6},
                                            ),
                                        ]
                                    ),
                                    dbc.Row(
                                        children=[
                                            dbc.Col(
                                                children=[
                                                    dbc.Button(
                                                        "Submit",
                                                        id="submit-button",
                                                        n_clicks=0,
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    dbc.Row(
                                        dbc.Col(
                                            dbc.Alert(
                                                children=[
                                                    html.H4(
                                                        "Output:",
                                                        className="alert-heading",
                                                    ),
                                                    html.Div(
                                                        id="output-div",
                                                    ),
                                                ],
                                                color="success",
                                                style={"margin-top": "30px"},
                                                is_open=False,
                                                id="recipe",
                                                fade=True,
                                            ),
                                        ),
                                    ),
                                ],
                            ),
                        ],
                        className="shadow-lg border-primary mb-3",
                    ),
                    xs={"size": 12},
                    sm={"size": 10},
                    md={"size": 10},
                    lg={"size": 8},
                ),
            ],
            style={"padding-top": "50px"},
            justify="center",
        ),
    ],
    fluid=True,
    className="bg-secondary",
    style={"min-height": "100vh"},  # fill the whole background
)


# Display recipe on submit, hide initially
@app.callback(
    Output(component_id="output-div", component_property="children"),
    Output(component_id="recipe", component_property="is_open"),
    Output(component_id="recipe", component_property="color"),
    [Input("submit-button", "n_clicks")],
    [
        State("sequence", "value"),
        State("max_length", "value"),
        State("fixed", "value"),
    ],
)  # type: ignore[misc]
def run_Fealden(
    n_clicks: int,
    _sequence: str,
    _max_length: int,
    _fixed: str,
) -> Tuple[str, bool, str]:
    # LOGIC

    fixed = False
    if _fixed == ["3' Fixed MB"]:
        fixed = True

    this_output_file = f'./results/{time.strftime("%Y%m%d-%H%M%S")}-results.csv'

    Fealden(_sequence, 1, int(_max_length), 500, False, this_output_file, fixed)

    results_path = Path.cwd() / this_output_file

    if not results_path.exists():
        output = f"Run failed for: {_sequence}, {_fixed}, {results_path}"
    else:
        df = pd.read_csv(results_path)

        output = dash_table.DataTable(
            df.to_dict("records"),
            [{"name": i, "id": i} for i in df.columns],
            style_table={"overflowX": "auto"},
            style_cell={
                "font_family": "Arial",
                # 'font_size': '26px',
                "text_align": "left",
            },
            style_header={"backgroundColor": "rgb(30, 30, 30)", "color": "white"},
            style_data={"backgroundColor": "rgb(50, 50, 50)", "color": "white"},
        )

    # Return functional recipe
    if n_clicks == 0:  # Initial non-clicked state
        return ("", False, "warning")
    else:
        return (
            output,
            True,
            "success",
        )


# Main magic
if __name__ == "__main__":
    app.run_server(debug=True)
