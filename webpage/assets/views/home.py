import datetime

import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from assets.views import plot_common

# DEFAULT_IMAGE_PATH = "assets/images/AHU.PNG"

external_stylesheets = [dbc.themes.LUX]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server
app.title = "AHU04 Display Draft"

# display current sensor values
current_values = [
    dbc.Card(
        id="sidebar-card",
        children=[
            dbc.CardHeader("Current Sensor Values"),
            dbc.CardBody(
                [
                    html.H6("Current Temperature", className="card-title"),
                    # Label class chosen with buttons
                    html.Div(
                        id="temperature",
                        children=[dcc.Textarea(
                            value='25',
                            style={'width': '25%', 'height': 50}
                        )],
                    ),
                    html.Br(),
                    html.H6("Current Humidity", className="card-title"),
                    # Label class chosen with buttons
                    html.Div(
                        id="humidity",
                        children=[dcc.Textarea(
                            value='50',
                            style={'width': '25%', 'height': 50}
                        )],
                    )
                ]
            ),
        ],
    ),
]


# For users to adjust setpoints
setpoints = [
    dbc.Card(
        id="sidebar-card",
        children=[
            dbc.CardHeader("Adjust Setpoints"),
            dbc.CardBody(
                [
                    html.H6("Pump Speed Input", className="card-title"),
                    html.Div(dcc.Input(id='input_pump_speed', type='text')),
                    html.Button('Submit', id='submit_pump_speed'),
                    html.Br(), html.Br(),
                    html.H6("Pump On/Off", className="card-title"),
                    html.Div(dcc.Input(id='input_pump_power', type='text')),
                    html.Button('Submit', id='submit_pump_power'),
                    html.Br(), html.Br(),
                    html.Div(
                        id="system_dialog",
                        children=[dcc.Textarea(
                            value='nothing submitted',
                            style={'width': '100%', 'height': 50}
                        )],
                    )
                ]
            ),
        ],
    ),
]

history_temperature = dcc.Graph(
    id='history_temperature',
    figure={
        'data': [
            {'x': [1, 2, 3], 'y': [20, 23, 25],
             'type': 'scatter'}
        ],
        'layout': {'width': 1300, 'height': 400, 'title': 'History Temperature'}
    }
)

history_humidity = dcc.Graph(
    figure={
        'data': [
            {'x': [1, 2, 3], 'y': [20, 23, 25],
             'type': 'scatter'}
        ],
        'layout': {'width': 1300, 'height': 400, 'title': 'History Humidity'}
    }
)


# the date range selector
date_selector = dbc.Row(children=[
    html.H4("Select Start Time:"),
    dcc.DatePickerSingle(
        id='date_selector',
        date=datetime.date.today() - datetime.timedelta(days=1),
        display_format='DD.MM.YYYY',
        style={"margin-left": "15px", 'margin-right': '15px'}
    ),
    html.H4("Select End Time:"),
    dcc.DatePickerSingle(
        id='date_selector',
        date=datetime.date.today(),
        display_format='DD.MM.YYYY',
        style={"margin-left": "15px"}
    )
])


layout = html.Div(
    [
        dbc.Container(
            [
                dbc.Row([
                    dbc.Col(md=2),
                    dbc.Col(dbc.Card(html.H3(children='PLC',
                                            className="text-center text-light bg-dark"), body=True, color="dark")
                    , className="mt-4 mb-4", md=8)
                ]),
                dbc.Row(
                    children=[
                        dbc.Col([dbc.Row(children=current_values), dbc.Row(children=setpoints)], md=2, width={'offset': 1}),
                        dbc.Col([date_selector, dbc.Row(children=history_temperature), dbc.Row(children=history_humidity)], md=9)]
                ),
                # dbc.Row([
                #     dbc.Col(
                #         dcc.Graph(
                #             figure={
                #                 'data': [
                #                     {'x': [1, 2, 3], 'y': [20, 23, 25],
                #                         'type': 'scatter'},
                #                 ]
                #             }
                #         ), md=6
                #     ),
                #     dbc.Col(
                #         dcc.Graph(
                #             figure={
                #                 'data': [
                #                     {'x': [1, 2, 3], 'y': [20, 23, 25],
                #                         'type': 'scatter'},
                #                 ]
                #             }
                #         ),md=6
                #     ),
                # ]),
            ],
            fluid=True,
        ),
    ]
)

# potential callback for submitting setpoints (not yet working...)
@app.callback(
    dash.dependencies.Output('system_dialog', 'value'),
    [dash.dependencies.Input('submit_pump_speed', 'n_clicks')],
    [dash.dependencies.State('input_pump_speed', 'value')])
def update_output(n_clicks, value):
    with open('pump_speed.txt', 'w') as f_out:
        f_out.write(value)
    return 'pump speed "{}" submitted'.format(value)


# potential callback for adjusting start/end dates (not yet in use)
@app.callback(
    dash.dependencies.Output('history_temperature', 'figure'),
    [dash.dependencies.Input('date_selector', 'start_date'),
     dash.dependencies.Input('date_selector', 'end_date')])
def update_output(start_date, end_date):
    start_date_object = date.fromisoformat(start_date)
    end_date_object = date.fromisoformat(end_date)

