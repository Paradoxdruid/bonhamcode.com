# -*- coding: utf-8 -*-
import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, State, html

# Set up dash server
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Buffer Adjustment Calculator"
server = app.server  # Export server for use by Passenger framework

# Components for Layout
init_buffer_input = dbc.Row(
    [
        dbc.Label("Initial Buffer Concentration", html_for="init-buffer"),
        dbc.Input(type="init-buffer", id="buff_init_conc", value="1.0"),
        dbc.FormText(
            "Input initial stock buffer concentration",
            color="secondary",
        ),
    ]
)

final_buffer_input = dbc.Row(
    [
        dbc.Label("Final Buffer Concentration", html_for="final-buffer"),
        dbc.Input(type="final-buffer", id="buff_final_conc", value="0.15"),
        dbc.FormText(
            "Input final buffer concentration in the solution",
            color="secondary",
        ),
    ]
)

buffer_pka_input = dbc.Row(
    [
        dbc.Label("Buffer pKa", html_for="buffer-pka"),
        dbc.Input(type="buffer-pka", id="buff_pka", value="8.0"),
        dbc.FormText(
            "Input buffer pKa",
            color="secondary",
        ),
    ]
)


final_vol_input = dbc.Row(
    [
        dbc.Label("Final Solution Volume", html_for="final_vol"),
        dbc.Input(type="final_vol", id="final_volume", value="1.5"),
        dbc.FormText(
            "Input final solution volume (L)",
            color="secondary",
        ),
    ]
)

form1 = dbc.Form(
    [init_buffer_input, final_buffer_input, buffer_pka_input, final_vol_input]
)

hcl_conc_input = dbc.Row(
    [
        dbc.Label("Stock HCl concentration", html_for="hcl_conc"),
        dbc.Input(type="hcl_conc", id="hcl_conc", value="12.0"),
        dbc.FormText(
            "Input stock HCl (or strong acid titrant) concentration (M)",
            color="secondary",
        ),
    ]
)

naoh_conc_input = dbc.Row(
    [
        dbc.Label("Stock NaOH concentration", html_for="naoh_conc"),
        dbc.Input(type="naoh_conc", id="naoh_conc", value="10.0"),
        dbc.FormText(
            "Input stock NaOH (or strong acid titrant) concentration (M)",
            color="secondary",
        ),
    ]
)

init_ph_input = dbc.Row(
    [
        dbc.Label("Initial Buffer pH", html_for="init_ph"),
        dbc.Input(type="init_ph", id="init_ph", value="7.0"),
        dbc.FormText(
            "Input initial buffer pH",
            color="secondary",
        ),
    ]
)

final_ph_input = dbc.Row(
    [
        dbc.Label("Final Solution pH", html_for="final_ph"),
        dbc.Input(type="final_ph", id="final_ph", value="8.3"),
        dbc.FormText(
            "Input final solution pH",
            color="secondary",
        ),
    ]
)

form2 = dbc.Form([hcl_conc_input, naoh_conc_input, init_ph_input, final_ph_input])

# App layout using dash-bootstrap-components
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(html.H4("Buffer Titration Solving")),
                            dbc.CardBody(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                form1,
                                                xs={"size": 12},
                                                sm={"size": 12},
                                                md={"size": 6},
                                                lg={"size": 6},
                                            ),
                                            dbc.Col(
                                                form2,
                                                xs={"size": 12},
                                                sm={"size": 12},
                                                md={"size": 6},
                                                lg={"size": 6},
                                            ),
                                        ]
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
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
                                                [
                                                    html.H4(
                                                        "Recipe:",
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
        State("buff_init_conc", "value"),
        State("buff_final_conc", "value"),
        State("buff_pka", "value"),
        State("final_volume", "value"),
        State("hcl_conc", "value"),
        State("naoh_conc", "value"),
        State("init_ph", "value"),
        State("final_ph", "value"),
        State("recipe", "is_open"),
    ],
)
def Buffer_Solver(
    n_clicks,
    buffer_conc_initial,
    buffer_conc_final,
    buffer_pKa,
    total_volume,
    HCl_stock_conc,
    NaOH_stock_conc,
    initial_pH,
    final_pH,
    is_open,
):
    # Sanitize input and catch unusable input
    try:
        buffer_conc_initial = float(buffer_conc_initial)
        buffer_conc_final = float(buffer_conc_final)
        buffer_pKa = float(buffer_pKa)
        total_volume = float(total_volume)
        HCl_stock_conc = float(HCl_stock_conc)
        NaOH_stock_conc = float(NaOH_stock_conc)
        initial_pH = float(initial_pH)
        final_pH = float(final_pH)
    except ValueError:
        return "Invalid input values, try again", True, "warning"

    # Remove common nonsense conditions
    if not (0.0 < buffer_conc_initial <= 100.0):
        return "Invalid initial buffer concentration", True, "warning"
    if not (0.0 < buffer_conc_final <= 100.0):
        return "Invalid final buffer concentration", True, "warning"
    if not (0.0 < HCl_stock_conc <= 100.0):
        return "Invalid HCl concentration", True, "warning"
    if not (0.0 < NaOH_stock_conc <= 100.0):
        return "Invalid NaOH concentration", True, "warning"
    if buffer_conc_final > buffer_conc_initial:
        return "Can't increase concentration through dilution", True, "warning"
    if not (0.0 < buffer_pKa <= 100.0):
        return "Invalid pKa value", True, "warning"
    if not (0.0 < initial_pH <= 20.0):
        return "Invalid initial pH", True, "warning"
    if not (0.0 < final_pH <= 20.0):
        return "Invalid final pH", True, "warning"

    # First find moles of buffer and volume of buffer:
    buffer_volume = (buffer_conc_final * total_volume) / buffer_conc_initial
    moles_of_buffer = buffer_volume * buffer_conc_initial

    # Then, find initial conditions:
    initial_ratio = 10 ** (initial_pH - buffer_pKa)
    initial_HA = moles_of_buffer / (1 + initial_ratio)

    # Then, final conditions:
    final_ratio = 10 ** (final_pH - buffer_pKa)
    final_HA = moles_of_buffer / (1 + final_ratio)

    # Then, solve for titrant:
    difference = final_HA - initial_HA

    # Set titrant
    if difference < 0:
        titrant = "NaOH"
        difference = abs(difference)
        volume_titrant = difference / NaOH_stock_conc
    else:
        titrant = "HCl"
        volume_titrant = difference / HCl_stock_conc

    # Solve for volume of water
    volume_water = total_volume - (volume_titrant + buffer_volume)

    # Return functional recipe
    if n_clicks == 0:  # Initial non-clicked state
        return ("", False, "warning")
    else:
        return (
            (
                "Buffer recipe: add {0} liters stock buffer, "
                "{1} liters of stock {2}, and {3} liters of water."
            ).format(
                round(buffer_volume, 4),
                round(volume_titrant, 4),
                titrant,
                round(volume_water, 4),
            ),
            True,
            "success",
        )


# Main magic
if __name__ == "__main__":
    app.run_server(debug=True)
