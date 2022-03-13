import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_daq as daq
from helper_function.config import WebpageConfig

config = WebpageConfig()

from helper_function.organize_data import GetData
get_data = GetData(config)

Dropdown_choose_control_system = dcc.Dropdown(
    id='Dropdown-choose-control-system',
    options=[
        {'label': '', 'value': 'blank'},
        {'label': 'PLC', 'value': 'plc'},
        {'label': 'ED', 'value': 'ed'},
        {'label': 'LCGW', 'value': 'lcgw'},
    ],
    value='blank',
    disabled=False
)

Dropdown_refresh_rate = dcc.Dropdown(
    id='Dropdown-refresh-rate',
    options=[
        {'label': '30 Seconds', 'value': '30'},
        {'label': '1 Minute', 'value': '60'},
        {'label': '5 Minutes', 'value': '300'},
        {'label': '15 Minutes', 'value': '900'},
    ],
    value='60'
)

Dropdown_history_duration = dcc.Dropdown(
    id='Dropdown-history-duration',
    options=[
        {'label': '5 Minutes', 'value': '5'},
        {'label': '15 Minutes', 'value': '15'},
        {'label': '30 Minutes', 'value': '30'},
        {'label': '1 Hour', 'value': '60'},
        {'label': '5 Hour', 'value': '300'},
        {'label': '1 Day', 'value': '1440'},
        {'label': '7 Day', 'value': '10080'},
        {'label': '15 Day', 'value': '21600'},
        {'label': '60 Day', 'value': '86400'}
    ],
    value='21600'
)

Dropdown_display_system = dcc.Dropdown(
    id='Dropdown-display-system',
    options=[
        {'label': 'ALL', 'value': 'ALL'},
        {'label': 'PLC', 'value': 'plc'},
        {'label': 'ED', 'value': 'ed'},
        {'label': 'LCGW', 'value': 'lcgw'},
    ],
    value='ALL'
)

Modal_command_sent_fan = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader('Fan Power Command Sent.'),
                dbc.ModalFooter(
                    dbc.Button('Close', id='close-fan', className='ml-auto')
                ),
            ],
            id='Modal-command-sent-fan',
        ),
    ]
)

Modal_command_sent_valve = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader('Valve Opening Command Sent.'),
                dbc.ModalFooter(
                    dbc.Button('Close', id='close-valve', className='ml-auto')
                ),
            ],
            id='Modal-command-sent-valve',
        ),
    ]
)

Modal_command_sent_temperature = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader('Temperature Control Command Sent.'),
                dbc.ModalFooter(
                    dbc.Button('Close', id='close-temperature', className='ml-auto')
                ),
            ],
            id='Modal-command-sent-temperature',
        ),
    ]
)

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=config.LOGO_IMAGE_PATH, height='30px')),
                        dbc.Col(dbc.NavbarBrand('IoT building automation', className='ml-2')),
                    ],
                    align='center',
                    no_gutters=True,
                ),
                href='/home',
            ),
            dbc.NavbarToggler(id='navbar-toggler'),
        ]
    ),
    color='dark',
    dark=True,
    className='mb-4',
)

Indicator_PLC = daq.Indicator(
    id='Indicator-PLC',
    label='PLC',
    labelPosition="top",
    color='gray',
    value=False
)

# ToggleSwitch_PLC = html.Div([
#     daq.ToggleSwitch(
#         id='ToggleSwitch-PLC',
#         value=False,
#         label='PLC',
#         labelPosition='top',
#         disabled=True,
#         color='#17becf'
#     )
# ])

Indicator_ED = daq.Indicator(
    id='Indicator-ED',
    label='ED',
    labelPosition="top",
    value=False,
    color='gray'
)

# ToggleSwitch_ED = html.Div([
#     daq.ToggleSwitch(
#         id='ToggleSwitch-ED',
#         value=False,
#         label='ED',
#         labelPosition='top',
#         disabled=True,
#         color='#17becf'
#     )
# ])

Indicator_LCGW = daq.Indicator(
    id='Indicator-LCGW',
    label='LCGW',
    labelPosition="top",
    value=False,
    color='gray'
)

# ToggleSwitch_LCGW = html.Div([
#     daq.ToggleSwitch(
#         id='ToggleSwitch-LCGW',
#         value=False,
#         label='LCGW',
#         labelPosition='top',
#         disabled=True,
#         color='#17becf'
#     )
# ])


PowerButton_heat_generator = daq.PowerButton(
    id='PowerButton-heat-generator',
    on='False',
    label='Status',
    labelPosition='top',
    color='#17becf',
    disabled=True
)

switch = get_data.get_relais_switch()
if switch['current_State_Relais3'] == 1:
    ToggleSwitch_heat_generator_init_value = True
else:
    ToggleSwitch_heat_generator_init_value = False
ToggleSwitch_heat_generator = html.Div([
    daq.ToggleSwitch(
        id='ToggleSwitch-heat-generator',
        value=ToggleSwitch_heat_generator_init_value,
        label='Control',
        labelPosition='top',
        disabled=True,
        color='#17becf'
    )
])

PowerButton_fan_pump = daq.PowerButton(
    id='PowerButton-fan-pump',
    on='False',
    label='Status',
    labelPosition='top',
    color='#17becf',
    disabled=True
)

if switch['current_State_Relais4'] == 1:
    ToggleSwitch_fan_pump_init_value = True
else:
    ToggleSwitch_fan_pump_init_value = False
ToggleSwitch_fan_pump = html.Div([
    daq.ToggleSwitch(
        id='ToggleSwitch-fan-pump',
        value=ToggleSwitch_fan_pump_init_value,
        label='Control',
        labelPosition='top',
        disabled=True,
        color='#17becf'
    )
])

Input_temperature_control = dcc.Input(
    id='input-temperature-control',
    type='number',
    min=0,
    max=100,
    disabled=True
)

Input_fan_power = dcc.Input(
    id='input-fan-power',
    type='number',
    value=50,
    min=0,
    max=100
)

Input_valve_opening = dcc.Input(
    id='input-valve-opening',
    type='number',
    value=50,
    min=0,
    max=100
)

Tabs = html.Div([
    dcc.Tabs(id='Tabs', value='tab-1', children=[
        dcc.Tab(label='Air Inlet/Outlet Temperature/RH', children=[
            html.Div([
                dcc.Graph(
                    id='tab_temp_rh_air',
                    figure={},
                    className='graph__1',
                )
            ]),
        ]),
        dcc.Tab(label='Water Supply/Return Temperature', children=[
            html.Div([
                dcc.Graph(
                    id='tab_temp_water',
                    figure={},
                    className='graph__1',
                )
            ]),
        ]),
        dcc.Tab(label='voc', children=[
            html.Div([
                dcc.Graph(
                    id='tab_voc',
                    figure={},
                    className='graph__1',
                )
            ]),
        ]),
        dcc.Tab(label='valve opening', children=[
            html.Div([
                dcc.Graph(
                    id='tab_valve',
                    figure={},
                    className='graph__1',
                )
            ]),
        ]),
    ])
])


Checklist_enable_temperature_control = dcc.Checklist(
    id='Checklist-enable-temperature-control',
    options=[
        {'label': 'Enable', 'value': 'enable'},
    ],
    value=[],
    labelStyle={'display': 'inline-block'}
)
