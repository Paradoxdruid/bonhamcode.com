#!/home/drparadox/opt/python-3.8.1/bin/python3

"""
Dash web app for fitting Michaelis-Menten enzyme kinetics.
"""

from typing import Any, Dict, List, Tuple, Union

# Imports
import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas
import plotly.graph_objs as go
from dash import Input, Output, State, dash_table, dcc, html
from scipy.optimize import curve_fit

NDArray = np.ndarray[Any, np.dtype[np.float64]]

INITIAL_DATA: List[Dict[str, float]] = [
    {"X": 0.0, "Y1": 0.0, "Y2": 1.0},
    {"X": 1.0, "Y1": 8.0, "Y2": 7.0},
    {"X": 2.0, "Y1": 9.0, "Y2": 10.0},
    {"X": 3.0, "Y1": 10.0, "Y2": 11.0},
    {"X": 4.0, "Y1": 11.0, "Y2": 12.0},
    {"X": 5.0, "Y1": 12.0, "Y2": 13.0},
]

INITIAL_COLUMNS: List[Dict[str, Union[str, bool]]] = [
    {"id": "X", "name": "X"},
    {"id": "Y1", "name": "Y1"},
    {"id": "Y2", "name": "Y2", "deletable": True},
]

# Initialize app
app: dash.Dash = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

server: Any = app.server  # server initialization for passenger wsgi

# Layout Widgets
xaxis_label: html.Div = html.Div(
    children=[
        dbc.Label("X-axis label:", className="mr-2"),
        dbc.Input(type="x-axis", id="x-axis", value="Concentration"),
    ],
    className="mr-3",
)

yaxis_label: html.Div = html.Div(
    children=[
        dbc.Label("Y-axis label:", className="mr-2"),
        dbc.Input(type="y-axis", id="y-axis", value="Enzyme Activity"),
    ],
    className="mr-3",
)

input_form: dbc.Col = dbc.Col([dbc.Form(children=[xaxis_label, yaxis_label])])

row_button: dbc.Col = dbc.Col(
    children=[
        dbc.Button(
            "Add Column",
            id="adding-rows-button",
            n_clicks=0,
            className="float-right mb-1",
        ),
    ]
)

entry_table: dash_table.DataTable = dash_table.DataTable(
    id="adding-rows-table",
    columns=INITIAL_COLUMNS,
    data=INITIAL_DATA,
    editable=True,
    row_deletable=True,
    style_table={
        "padding-top": "5px",
        "padding-bottom": "5px",
        "padding-left": "15px",
        "padding-right": "15px",
    },
    style_cell={"font-family": "lato"},
    style_header={"font-weight": "bold"},
)

table_input: dbc.Col = dbc.Col(
    children=[
        dbc.Card(children=[entry_table], className="border-secondary p-2"),
        dbc.Button(
            "Add Row",
            id="editing-rows-button",
            n_clicks=0,
            className="mt-1",
        ),
    ],
)

card_header: dbc.CardHeader = dbc.CardHeader(
    children=[
        html.H3(
            "Bonham Code: Michaelis-Menten Fitting",
            className="card-title",
        ),
        html.H6(
            "Input x and y data (with replicates) for Michaelis-Menten fitting",
            className="card-subtitle",
        ),
    ]
)

graph_output: dbc.Col = dbc.Col(
    children=[
        dbc.Card(
            children=[
                dcc.Graph(id="adding-rows-graph", config={"displayModeBar": True})
            ],
            className="mt-3 border-primary p-1",
        ),
    ]
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
                                        dbc.Row([row_button]),
                                        dbc.Row([table_input]),
                                        dbc.Row([graph_output]),
                                    ],
                                ),
                            ],  # card content end bracket
                            color="dark",
                            outline=True,
                            className="shadow-lg",
                        ),
                    ],  # main column content end bracket
                    width={"size": 10},
                ),
            ],  # main row content end bracket
            style={"padding-top": "50px"},
            justify="center",
        ),
    ],  # container content end bracket
    fluid=True,
    className="bg-secondary",
    style={"min-height": "100vh"},  # fill the whole background
)


# Functions
def clean_up_y_data(ys: pandas.DataFrame) -> Tuple[NDArray, List[float]]:
    """Take user entered Y values and return average and std dev for plotting.

    Args:
        ys (pandas.DataFrame): user-entered y-value columns

    Returns:
        Tuple[NDArray, List[float]]: average Y and std dev of Y values
    """
    ys = ys.replace("", 0)
    ys = ys.fillna(0)
    ys = ys.astype(float).values
    y = ys.mean(axis=1)
    y_std = ys.std(axis=1)
    y_std = [value if value > 0 else 0.00000001 for value in y_std]
    # fitting fails with zero std values; this is a kludge

    return (y, y_std)


def equation(x: NDArray, vmax: float, km: float) -> NDArray:
    """Michaelis-Menten equation for testing and plotting.

    Args:
        x (NDArray): x values
        vmax (float): guess or value for Vmax
        km (float): guess or value for Km

    Returns:
        NDArray: return predicted y values
    """
    return (vmax * x) / (km + x)


def fit_data(x: NDArray, y: NDArray, y_std: List[float]) -> Tuple[NDArray, NDArray]:
    """Perform curve fitting against the average data.

    Args:
        x (List[float]): x values
        y (NDArray): average y values
        y_std (List[float]): y std dev values

    Returns:
        Tuple[NDArray, NDArray]: fitting variables and associated errors
    """
    variable_guesses = [np.max(y), np.min(y)]  # FIXME: better guesses!
    variables, cov = curve_fit(equation, x, y, p0=variable_guesses, sigma=y_std)
    var_errors: NDArray = np.sqrt(np.diag(cov))

    return (variables, var_errors)


def find_r_squared(x: NDArray, y: NDArray, variables: NDArray) -> float:
    """Find r squared value of fit

    Args:
        x (NDArray): x values
        y (NDArray): average y values
        variables (NDArray): fitting variables

    Returns:
        float: r squared value
    """
    residuals: NDArray = y - equation(x, *variables)
    ss_res: float = np.sum(residuals**2)
    ss_tot: float = np.sum((y - np.mean(y)) ** 2)
    r_squared: float = 1 - (ss_res / ss_tot)

    return r_squared


def generate_plot1(x: NDArray, y: NDArray, y_std: List[float]) -> go.Scatter:
    """Generate plot of actual average data.

    Args:
        x (NDArray): x values
        y (NDArray): average y values
        y_std (List[float]): y std dev values

    Returns:
        go.Scatter: scatter plot of data
    """
    return go.Scatter(
        x=x,
        y=y,
        mode="markers",
        error_y={"type": "data", "array": y_std, "visible": True},
    )


def generate_plot2(x_range: NDArray, variables: NDArray) -> go.Scatter:
    """Generate plot of predicted Michaelis-Menten curve values.

    Args:
        x_range (NDArray): evenly spaced range of x values
        variables (NDArray): fitting variables

    Returns:
        go.Scatter: scatter plot of data
    """
    return go.Scatter(x=x_range, y=equation(x_range, *variables), mode="lines")


def generate_graph_layout(
    r_squared: float,
    variables: NDArray,
    var_errors: NDArray,
    x_title: str,
    y_title: str,
) -> go.Layout:
    """Return formatted layout and annotations for final display.

    Args:
        r_squared (float): r squared value
        variables (NDArray): fitting variables
        var_errors (NDArray): fitting variable errors
        x_title (str): x axis title
        y_title (str): y axis title

    Returns:
        go.Layout: plotly figure layout
    """
    return go.Layout(
        title={"text": "Michaelis-Menten Fit", "font": {"family": "lato"}},
        # width=600,
        template="seaborn",
        annotations=[
            {
                "x": 0.5,
                "y": 0.5,
                "xref": "paper",
                "yref": "paper",
                "text": f"R squared = {round(r_squared, 3)}",
                "showarrow": False,
            },
            {
                "x": 0.5,
                "y": 0.44,
                "xref": "paper",
                "yref": "paper",
                "text": f"Km = {variables[1]:0.3e} \u00B1 {var_errors[1]:0.3e}",
                "showarrow": False,
            },
            {
                "x": 0.5,
                "y": 0.38,
                "xref": "paper",
                "yref": "paper",
                "text": "Vmax = {:0.3e} \u00B1 {:0.3e}".format(
                    variables[0], var_errors[0]
                ),
                "showarrow": False,
            },
        ],
        xaxis={
            "title": x_title,
            "showline": True,
            "linewidth": 1,
            "linecolor": "black",
            "titlefont": {"family": "lato"},
        },
        yaxis={
            "title": y_title,
            "showline": True,
            "linewidth": 1,
            "linecolor": "black",
            "titlefont": {"family": "lato"},
        },
        showlegend=False,
        margin={"t": 40, "r": 40, "l": 40, "b": 40},
    )


@app.callback(
    Output("adding-rows-table", "data"),
    [Input("editing-rows-button", "n_clicks")],
    [State("adding-rows-table", "data"), State("adding-rows-table", "columns")],
)  # type: ignore[misc]
def add_row(
    n_clicks: int,
    rows: List[Dict[str, float]],
    columns: List[Dict[str, Union[str, bool]]],
) -> List[Dict[str, float]]:
    """Add additional data entry row.

    Args:
        n_clicks (int): number of times function has been clicked
        rows (List[Dict[str, float]]): existing rows
        columns (List[Dict[str, Union[str, bool]]]): existing columns

    Returns:
        List[Dict[str, float]]: rows with an additional row
    """
    if n_clicks > 0:
        rows.append({c["id"]: 0.0 for c in columns})  # type: ignore[misc]
    return rows


@app.callback(
    Output("adding-rows-table", "columns"),
    [Input("adding-rows-button", "n_clicks")],
    [State("adding-rows-table", "columns")],
)  # type: ignore[misc]
def update_columns(
    n_clicks: int, existing_columns: List[Dict[str, Union[str, bool]]]
) -> List[Dict[str, Union[str, bool]]]:
    """Add additional data entry column.

    Args:
        n_clicks (int): number of times function has been clicked
        existing_columns (List[Dict[str, Union[str, bool]]]): existing columns

    Returns:
        List[Dict[str, Union[str, bool]]]: existing columns with new column appended
    """
    if n_clicks > 0:
        count: int = 2 + n_clicks
        counter: str = f"Y{count}"
        existing_columns.append(
            {"id": counter, "name": counter, "editable": True, "deletable": True}
        )
    return existing_columns


@app.callback(
    Output("adding-rows-graph", "figure"),
    [
        Input("adding-rows-table", "data"),
        Input("adding-rows-table", "columns"),
        Input("x-axis", "value"),
        Input("y-axis", "value"),
    ],
)  # type: ignore[misc]
def update_graph(
    rows: List[Dict[str, float]],
    columns: List[Dict[str, Union[str, bool]]],
    x_title: str,
    y_title: str,
) -> Dict[str, Any]:
    """Take user data and perform nonlinear regression to Michaelis-Menten model.

    Args:
        rows (List[Dict[str, float]]): data entry rows
        columns (List[Dict[str, Union[str, bool]]]): data entry columns
        x_title (str): x axis title
        y_title (str): y axis title

    Returns:
        Dict(str, Any): plot data and layout to update displayed graph
    """

    df = pandas.DataFrame(rows, columns=[c["name"] for c in columns])

    x: NDArray = df["X"].astype(float).values

    ys: pandas.DataFrame = df.iloc[:, 1:]  # all but X column
    y, y_std = clean_up_y_data(ys)

    variables, var_errors = fit_data(x, y, y_std)

    r_squared: float = find_r_squared(x, y, variables)

    # Calculate useful range for plotting
    DEFAULT_INCREMENTS: int = 100
    x_range: NDArray = np.arange(
        np.min(x), np.max(x), abs(np.max(x) / DEFAULT_INCREMENTS)
    )

    # Return plots and a graph data layout
    plot1: go.Scatter = generate_plot1(x, y, y_std)
    plot2: go.Scatter = generate_plot2(x_range, variables)
    plot_data: List[go.Scatter] = [plot1, plot2]

    layout: go.Layout = generate_graph_layout(
        r_squared, variables, var_errors, x_title, y_title
    )

    return {"data": plot_data, "layout": layout}


# Main magic
if __name__ == "__main__":
    app.run_server(debug=True)
