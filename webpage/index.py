"""
Please run this file to execute the dashboard of the iotteststand.
This file describe the layout of the dashboard as well as all the call back functions.
Details of widgets used in the layout can be found in webpage/views/display_widgets.py

The temperature control function is not yet implemented.
In the moment, when clicking the check-box of enabling the temperature control function,
the input text box will be enabled or disabled accordingly.
However, when clicking "apply", the temperature value set by user in the text box has no effect.
When implementing temperature control functions, can refer to the template at " # temperature control (template for futurn implementation)"
"""

import datetime
from dash.dependencies import Input, Output, State
from app import app
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from helper_function.config import WebpageConfig
from helper_function.organize_data import GetData
from assets.views.display_widgets import *
import time
import pytz

# building the navigation bar
# https://github.com/facultyai/dash-bootstrap-components/blob/master/examples/advanced-component-usage/Navbars.py

# global variables
current_control_sys = 'lcgw'  # will be overwrite in call back function "image_data_update"
config = WebpageConfig()
get_data = GetData(config)
timezone = pytz.timezone('UTC')

# Define layout of the dashboard
app.layout = html.Div([
    html.Div([
        dcc.Location(id='url', refresh=False),
        navbar,

        dbc.Row([
            dbc.Col([
                dbc.Container(
                    [
                        html.Img(src=config.DEFAULT_IMAGE_PATH, alt='AHU', className='orion_img'),
                        html.Button('', id='button-return-temperature-primary', className='button-return-temperature-primary'),
                        html.Button('', id='button-supply-temperature-primary', className='button-supply-temperature-primary'),
                        html.Button('', id='button-return-temperature', className='button-return-temperature'),
                        html.Button('', id='button-supply-temperature', className='button-supply-temperature'),
                        html.Button('', id='button-air-inlet-temperature', className='button-air-inlet-temperature'),
                        html.Button('', id='button-air-outlet-temperature', className='button-air-outlet-temperature'),
                        html.Button('', id='button-air-inlet-humidity', className='button-air-inlet-humidity'),
                        html.Button('', id='button-air-outlet-humidity', className='button-air-outlet-humidity'),
                        html.Button('', id='button-air-outlet-voc', className='button-air-outlet-voc'),
                        html.Button('', id='button-three-way-valve', className='button-three-way-valve')]),
            ], md=6, className='container'),

            dbc.Col([
                html.H6(children='Current Control System', style={'text-align': 'center'}),
                dbc.Row([
                    dbc.Col(Indicator_PLC),
                    dbc.Col(Indicator_ED),
                    dbc.Col(Indicator_LCGW),
                ]),
                html.Br(),
                html.H6(children='Switch to this control system:', style={'text-align': 'center'}),
                Dropdown_choose_control_system,
                html.Button('Apply', id='button-apply-system'),
                html.Br(), html.Br(),
                dbc.Row([
                    dbc.Col([html.H6('Heat Generator', style={'text-align': 'center'}),
                             dbc.Row([
                                 dbc.Col(PowerButton_heat_generator),
                                 dbc.Col(ToggleSwitch_heat_generator)])]),
                    dbc.Col([html.H6('Fan and Pump', style={'text-align': 'center'}),
                             dbc.Row([
                                 dbc.Col(PowerButton_fan_pump),
                                 dbc.Col(ToggleSwitch_fan_pump)])]),
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col(html.H6('Temperature Control', style={'text-align': 'center'})),
                    dbc.Col(html.H6('Set fan power (%)\n(between 0 and 100)', style={'text-align': 'center'})),
                    dbc.Col(html.H6('Set valve open (%)\n(between 0 and 100)', style={'text-align': 'center'}))
                ]),
                dbc.Row([
                    dbc.Col([
                        Checklist_enable_temperature_control,
                        Input_temperature_control,
                        html.Button('Apply', id='button-apply-temperature-control'),
                    ]),
                    dbc.Col([
                        Input_fan_power,
                        html.Button('Apply', id='button-apply-fan'),
                    ]),
                    dbc.Col([
                        Input_valve_opening,
                        html.Button('Apply', id='button-apply-valve'),
                    ]),
                ]),

                Modal_command_sent_fan,
                Modal_command_sent_valve,
                Modal_command_sent_temperature,
                html.Br(), html.Br(),
                html.Img(src=config.LEGEND_IMAGE_PATH, alt='legend', className='legend_img')
            ], md=5),
            dbc.Col(md=1)
        ]),
    ]),

    html.Div([
        dbc.Row(
            children=[dbc.Col([html.H6('display duration'), Dropdown_history_duration], md=2, width={'offset': 1}),
                      dbc.Col([html.H6('refresh rate'), Dropdown_refresh_rate], md=2),
                      dbc.Col([html.H6('display system'), Dropdown_display_system], md=2)]),
        html.Br(), html.Br(),
    ]),
    Tabs,

    dcc.Interval(
        id='interval-refresh',
        interval=15 * 1000,  # in milliseconds
        n_intervals=0
    ),

    dcc.Interval(
        id='Interval-switch-system-timeout',
        interval=config.switch_timeout * 1000,  # in milliseconds
        n_intervals=0
    ),

    dcc.Interval(
        id='Interval-current-value-refresh',
        interval=config.orion_refresh_interval * 1000,  # in milliseconds
        n_intervals=0
    ),
])


"""" Callback Functions """

"""
In the initialization of the dashboard, all callback functions are automatically called once.
This is designed by DASH.
"""


# send fan power command
@app.callback(
    Output('Modal-command-sent-fan', 'is_open'),
    [Input('button-apply-fan', 'n_clicks'), Input('close-fan', 'n_clicks')],
    [State('Modal-command-sent-fan', 'is_open'), State('input-fan-power', 'value')],
)
def toggle_modal(n1, n2, is_open, fan_value):
    if n1 or n2:  # Because of this condition, this function is not called during the initialization.
        if not is_open:
            get_data.send_command(system=current_control_sys,
                                  entity_id='actuator:Fan_%s' % current_control_sys.upper(),
                                  entity_type='actuator:Fan',
                                  command={'type': 'command', 'value': str(fan_value)},
                                  command_name='setpoint')
        return not is_open
    return is_open


# send valve opening command
@app.callback(
    Output('Modal-command-sent-valve', 'is_open'),
    [Input('button-apply-valve', 'n_clicks'), Input('close-valve', 'n_clicks')],
    [State('Modal-command-sent-valve', 'is_open'), State('input-valve-opening', 'value')],
)
def toggle_modal(n1, n2, is_open, valve_value):
    if n1 or n2:
        if not is_open:  # Because of this condition, this function is not called during the initialization.
            get_data.send_command(system=current_control_sys,
                                  entity_id='actuator:Three_Way_Valve_%s' % current_control_sys.upper(),
                                  entity_type='actuator:Valve',
                                  command={'type': 'command', 'value': str(valve_value)},
                                  command_name='setpoint')
        return not is_open
    return is_open


# display history graph
@app.callback([Output('tab_temp_rh_air', 'figure'),
               Output('tab_temp_water', 'figure'),
               Output('tab_voc', 'figure'),
               Output('tab_valve', 'figure')],
              [Input('Dropdown-history-duration', 'value'),
               Input('Dropdown-display-system', 'value'),
               Input('interval-refresh', 'n_intervals')])
def update_plots(minutes, system, _):
    fromDate = datetime.datetime.utcnow() - datetime.timedelta(minutes=int(minutes))
    fromDate_str = datetime.datetime.strftime(fromDate, '%Y-%m-%dT%H:%M:%S')
    system_color = {'plc': 'rgb(255, 0, 0)', 'ed': 'rgb(0, 255, 0)', 'lcgw': 'rgb(0, 0, 255)'}

    # Get all data needed via thread
    if system in ['plc', 'ALL']:
        data_plc = get_data.get_history_thread('plc', fromDate_str)
    if system in ['ed', 'ALL']:
        data_ed = get_data.get_history_thread('ed', fromDate_str)
    if system in ['lcgw', 'ALL']:
        data_lcgw = get_data.get_history_thread('lcgw', fromDate_str)

    # Wait until all data have arrived
    expected_keys_plc = len(config.history_values_display_param_list['plc']) + 1  # + 1 because of "token_expire_time"
    expected_keys_ed = len(config.history_values_display_param_list['ed']) + 1
    expected_keys_lcgw = len(config.history_values_display_param_list['lcgw']) + 1
    reading_data = True
    while reading_data:
        if system == 'plc':
            if len(data_plc.keys()) == expected_keys_plc:
                reading_data = False
        elif system == 'ed':
            if len(data_ed.keys()) == expected_keys_ed:
                reading_data = False
        elif system == 'lcgw':
            if len(data_lcgw.keys()) == expected_keys_lcgw:
                reading_data = False
        else:
            if len(data_plc.keys()) == expected_keys_plc and \
                    len(data_ed.keys()) == expected_keys_ed and \
                    len(data_lcgw.keys()) == expected_keys_lcgw:
                reading_data = False
        time.sleep(1)

    # Tab1 Temperature & Humidity of Air Side
    param_temp_rh_air = ['Air_Inlet_Temperature', 'Air_Inlet_Humidity', 'Air_Outlet_Temperature', 'Air_Outlet_Humidity']
    fig_air = make_subplots(specs=[[{'secondary_y': True}]])
    # the x_min, y_min, y_max are simply stored and calculated for the location of the system's label on the plot
    x_min = timezone.localize(datetime.datetime.now())
    y_min = float('Inf')
    y_max = -float('Inf')
    for param in param_temp_rh_air:
        if 'Humidity' in param:
            y2_axis = True
        else:
            y2_axis = False
        if system in ['plc', 'ALL'] and param in data_plc:
            fig_air.add_trace(
                go.Scatter(x=data_plc[param][0], y=data_plc[param][1], name='PLC_%s' % param),
                secondary_y=y2_axis
            )
            try:  # use try-except here because data_plc may contain no data when something's wrong during the getting data process from the quantumleap
                x_min = min(x_min, data_plc[param][0][0])
                y_min = min(y_min, min(data_plc[param][1]))
                y_max = max(y_max, max(data_plc[param][1]))
            except:
                pass
        if system in ['ed', 'ALL'] and param in data_ed:
            fig_air.add_trace(
                go.Scatter(x=data_ed[param][0], y=data_ed[param][1], name='ED_%s' % param),
                secondary_y=y2_axis
            )
            try:
                x_min = min(x_min, data_ed[param][0][0])
                y_min = min(y_min, min(data_ed[param][1]))
                y_max = max(y_max, max(data_ed[param][1]))
            except:
                pass
        if system in ['lcgw', 'ALL'] and param in data_lcgw:
            fig_air.add_trace(
                go.Scatter(x=data_lcgw[param][0], y=data_lcgw[param][1], name='LCGW_%s' % param),
                secondary_y=y2_axis
            )
            try:
                x_min = min(x_min, data_lcgw[param][0][0])
                y_min = min(y_min, min(data_lcgw[param][1]))
                y_max = max(y_max, max(data_lcgw[param][1]))
            except:
                pass
    # axis name
    fig_air.update_yaxes(
        title_text='Temperature',
        secondary_y=False)
    fig_air.update_yaxes(
        title_text='Humidity',
        secondary_y=True)

    # add annotation
    if y_max > y_min:  # filter out the case when there is no data
        # add little legend box saying 'plc'
        fig_air.add_annotation(
            x=x_min, y=y_max, xref='x', yref='y', text='PLC',
            font=dict(family='Courier New, monospace', size=16, color='rgb(0, 0, 0)'),
            align='center', borderwidth=2, borderpad=4, bgcolor='rgb(250, 0, 0)', opacity=0.7, width=50
        )
        # add little legend box saying 'ED'
        fig_air.add_annotation(
            x=x_min, y=y_min + 0.9*(y_max-y_min), xref='x', yref='y', text='ED',
            font=dict(family='Courier New, monospace', size=16, color='rgb(0, 0, 0)'),
            align='center', borderwidth=2, borderpad=4, bgcolor='rgb(0, 250, 0)', opacity=0.7, width=50
        )
        # add little legend box saying 'LCGW'
        fig_air.add_annotation(
            x=x_min, y=y_min + 0.8*(y_max-y_min), xref='x', yref='y', text='LCGW',
            font=dict(family='Courier New, monospace', size=16, color='rgb(0, 0, 0)'),
            align='center', borderwidth=2, borderpad=4, bgcolor='rgb(139, 161, 231)', opacity=0.8, width=50
        )

    # Tab2 Temperature of Water Side
    param_temp_water = ['Return_Temperature_Primary', 'Supply_Temperature_Primary', 'Return_Temperature', 'Supply_Temperature']
    fig_water = make_subplots()
    x_min = timezone.localize(datetime.datetime.now())
    y_min = float('Inf')
    y_max = -float('Inf')
    for param in param_temp_water:
        if system in ['plc', 'ALL'] and param in data_plc:
            fig_water.add_trace(
                go.Scatter(x=data_plc[param][0], y=data_plc[param][1], name='PLC_%s' % param)
            )
            try:
                x_min = min(x_min, data_plc[param][0][0])
                y_min = min(y_min, min(data_plc[param][1]))
                y_max = max(y_max, max(data_plc[param][1]))
            except:
                pass
        if system in ['ED', 'ALL'] and param in data_ed:
            fig_water.add_trace(
                go.Scatter(x=data_ed[param][0], y=data_ed[param][1], name='ED_%s' % param)
            )
            try:
                x_min = min(x_min, data_ed[param][0][0])
                y_min = min(y_min, min(data_ed[param][1]))
                y_max = max(y_max, max(data_ed[param][1]))
            except:
                pass
        if system in ['lcgw', 'ALL'] and param in data_lcgw:
            fig_water.add_trace(
                go.Scatter(x=data_lcgw[param][0], y=data_lcgw[param][1], name='LCGW_%s' % param)
            )
            try:
                x_min = min(x_min, data_lcgw[param][0][0])
                y_min = min(y_min, min(data_lcgw[param][1]))
                y_max = max(y_max, max(data_lcgw[param][1]))
            except:
                pass

    # add annotation
    if y_max > y_min:  # filter out the case when there is no data
        # add little legend box saying 'PLC'
        fig_water.add_annotation(
            x=x_min, y=y_max, xref='x', yref='y', text='PLC',
            font=dict(family='Courier New, monospace', size=16, color='rgb(0, 0, 0)'),
            align='center', borderwidth=2, borderpad=4, bgcolor='rgb(250, 0, 0)', opacity=0.7, width=50
        )
        # add little legend box saying 'ED'
        fig_water.add_annotation(
            x=x_min, y=y_min + 0.9*(y_max-y_min), xref='x', yref='y', text='ED',
            font=dict(family='Courier New, monospace', size=16, color='rgb(0, 0, 0)'),
            align='center', borderwidth=2, borderpad=4, bgcolor='rgb(0, 250, 0)', opacity=0.7, width=50
        )
        # add little legend box saying 'LCGW'
        fig_water.add_annotation(
            x=x_min, y=y_min + 0.8*(y_max-y_min), xref='x', yref='y', text='LCGW',
            font=dict(family='Courier New, monospace', size=16, color='rgb(0, 0, 0)'),
            align='center', borderwidth=2, borderpad=4, bgcolor='rgb(139, 161, 231)', opacity=0.8, width=50
        )

    # Tab3 VOC
    fig_voc = make_subplots()
    x_min = timezone.localize(datetime.datetime.now())
    y_min = float('Inf')
    y_max = -float('Inf')
    param = 'Air_Outlet_VOC'
    if system in ['plc', 'ALL'] and param in data_plc:
        fig_voc.add_trace(
            go.Scatter(x=data_plc[param][0], y=data_plc[param][1], name='PLC', line=dict(color=system_color['plc']))
        )
        try:
            x_min = min(x_min, data_plc[param][0][0])
            y_min = min(y_min, min(data_plc[param][1]))
            y_max = max(y_max, max(data_plc[param][1]))
        except:
            pass
    if system in ['ed', 'ALL'] and param in data_ed:
        fig_voc.add_trace(
            go.Scatter(x=data_ed[param][0], y=data_ed[param][1], name='ED', line=dict(color=system_color['ed']))
        )
        try:
            x_min = min(x_min, data_ed[param][0][0])
            y_min = min(y_min, min(data_ed[param][1]))
            y_max = max(y_max, max(data_ed[param][1]))
        except:
            pass
    if system in ['lcgw', 'ALL'] and param in data_lcgw:
        fig_voc.add_trace(
            go.Scatter(x=data_lcgw[param][0], y=data_lcgw[param][1], name='LCGW', line=dict(color=system_color['lcgw']))
        )
        try:
            x_min = min(x_min, data_lcgw[param][0][0])
            y_min = min(y_min, min(data_lcgw[param][1]))
            y_max = max(y_max, max(data_lcgw[param][1]))
        except:
            pass

    # add annotation
    if y_max > y_min:  # filter out the case when there is no data
        # add little legend box saying 'PLC'
        fig_voc.add_annotation(
            x=x_min, y=y_max, xref='x', yref='y', text='PLC',
            font=dict(family='Courier New, monospace', size=16, color='rgb(0, 0, 0)'),
            align='center', borderwidth=2, borderpad=4, bgcolor='rgb(250, 0, 0)', opacity=0.7, width=50
        )
        # add little legend box saying 'ED'
        fig_voc.add_annotation(
            x=x_min, y=y_min + 0.9*(y_max-y_min), xref='x', yref='y', text='ED',
            font=dict(family='Courier New, monospace', size=16, color='rgb(0, 0, 0)'),
            align='center', borderwidth=2, borderpad=4, bgcolor='rgb(0, 250, 0)', opacity=0.7, width=50
        )
        # add little legend box saying 'LCGW'
        fig_voc.add_annotation(
            x=x_min, y=y_min + 0.8*(y_max-y_min), xref='x', yref='y', text='LCGW',
            font=dict(family='Courier New, monospace', size=16, color='rgb(0, 0, 0)'),
            align='center', borderwidth=2, borderpad=4, bgcolor='rgb(139, 161, 231)', opacity=0.8, width=50
        )

    # Tab4 Valve
    fig_valve = make_subplots()
    x_min = timezone.localize(datetime.datetime.now())
    y_min = float('Inf')
    y_max = -float('Inf')
    param = 'Three_Way_Valve'
    if system in ['plc', 'ALL'] and param in data_plc:
        fig_valve.add_trace(
            go.Scatter(x=data_plc[param][0], y=data_plc[param][1], name='PLC', line=dict(color=system_color['plc']))
        )
        try:
            x_min = min(x_min, data_plc[param][0][0])
            y_min = min(y_min, min(data_plc[param][1]))
            y_max = max(y_max, max(data_plc[param][1]))
        except:
            pass
    if system in ['ed', 'ALL'] and param in data_ed:
        fig_valve.add_trace(
            go.Scatter(x=data_ed[param][0], y=data_ed[param][1], name='ED', line=dict(color=system_color['ed']))
        )
        try:
            x_min = min(x_min, data_ed[param][0][0])
            y_min = min(y_min, min(data_ed[param][1]))
            y_max = max(y_max, max(data_ed[param][1]))
        except:
            pass
    if system in ['lcgw', 'ALL'] and param in data_lcgw:
        fig_valve.add_trace(
            go.Scatter(x=data_lcgw[param][0], y=data_lcgw[param][1], name='LCGW', line=dict(color=system_color['lcgw']))
        )
        try:
            x_min = min(x_min, data_lcgw[param][0][0])
            y_min = min(y_min, min(data_lcgw[param][1]))
            y_max = max(y_max, max(data_lcgw[param][1]))
        except:
            pass

    # add annotation
    if y_max > y_min:  # filter out the case when there is no data
        # add little legend box saying 'PLC'
        fig_valve.add_annotation(
            x=x_min, y=y_max, xref='x', yref='y', text='PLC',
            font=dict(family='Courier New, monospace', size=16, color='rgb(0, 0, 0)'),
            align='center', borderwidth=2, borderpad=4, bgcolor='rgb(250, 0, 0)', opacity=0.7, width=50
        )
        # add little legend box saying 'ED'
        fig_valve.add_annotation(
            x=x_min, y=y_min + 0.9*(y_max-y_min), xref='x', yref='y', text='ED',
            font=dict(family='Courier New, monospace', size=16, color='rgb(0, 0, 0)'),
            align='center', borderwidth=2, borderpad=4, bgcolor='rgb(0, 250, 0)', opacity=0.7, width=50
        )
        # add little legend box saying 'LCGW'
        fig_valve.add_annotation(
            x=x_min, y=y_min + 0.8*(y_max-y_min), xref='x', yref='y', text='LCGW',
            font=dict(family='Courier New, monospace', size=16, color='rgb(0, 0, 0)'),
            align='center', borderwidth=2, borderpad=4, bgcolor='rgb(139, 161, 231)', opacity=0.8, width=50
        )

    # Backgroud color of the plot. The color is different for different control systems.
    start_end_time = get_data.get_switch_history(fromDate_str)
    for sys in start_end_time:
        if start_end_time[sys] != [[], []]:
            for (start_time, end_time) in zip(start_end_time[sys][0], start_end_time[sys][1]):
                fig_air.add_vrect(
                    x0=start_time, x1=end_time,
                    fillcolor=system_color[sys], opacity=0.15,
                    layer='below', line_width=0,
                )
                fig_water.add_vrect(
                    x0=start_time, x1=end_time,
                    fillcolor=system_color[sys], opacity=0.15,
                    layer='below', line_width=0,
                )
                fig_voc.add_vrect(
                    x0=start_time, x1=end_time,
                    fillcolor=system_color[sys], opacity=0.15,
                    layer='below', line_width=0,
                )
                fig_valve.add_vrect(
                    x0=start_time, x1=end_time,
                    fillcolor=system_color[sys], opacity=0.15,
                    layer='below', line_width=0,
                )
    return fig_air, fig_water, fig_voc, fig_valve


# update refresh rate of history graph
@app.callback(Output('interval-refresh', 'interval'),
              [Input('Dropdown-refresh-rate', 'value')])
def update_refresh_rate(seconds):
    return int(seconds) * 1000


# update current values on image of the system diagram
@app.callback([Output('button-return-temperature-primary', 'children'),
               Output('button-supply-temperature-primary', 'children'),
                Output('button-return-temperature', 'children'),
                Output('button-supply-temperature', 'children'),
                Output('button-air-inlet-temperature', 'children'),
                Output('button-air-outlet-temperature', 'children'),
                Output('button-air-inlet-humidity', 'children'),
                Output('button-air-outlet-humidity', 'children'),
                Output('button-air-outlet-voc', 'children'),
                Output('button-three-way-valve', 'children'),
               Output('Indicator-PLC', 'color'),
               Output('Indicator-ED', 'color'),
               Output('Indicator-LCGW', 'color'),
               Output('PowerButton-heat-generator', 'color'),
               Output('PowerButton-fan-pump', 'color')],
              [Input('Interval-current-value-refresh', 'n_intervals')])
def image_data_update(value):
    switch = get_data.get_relais_switch()
    if switch['current_State_Relais1'] == 1:  # LCGW
        switch_output = ['gray', 'gray', 'green']
        current_control_sys = 'lcgw'
        data = get_data.get_current_value(current_control_sys)
    elif switch['current_State_Relais2'] == 0:  # PLC
        switch_output = ['green', 'gray', 'gray']
        current_control_sys = 'plc'
        data = get_data.get_current_value(current_control_sys)
    elif switch['current_State_Relais2'] == 1:  # ED
        switch_output = ['gray', 'green', 'gray']
        current_control_sys = 'ed'
        data = get_data.get_current_value(current_control_sys)
    else:  # cannot read anything
        switch_output = ['gray'] * 3
        data = get_data.return_null_orion()
    output = [
        data['Return_Temperature_Primary'],
        data['Supply_Temperature_Primary'],
        data['Return_Temperature'],
        data['Supply_Temperature'],
        data['Air_Inlet_Temperature'],
        data['Air_Outlet_Temperature'],
        data['Air_Inlet_Humidity'],
        data['Air_Outlet_Humidity'],
        data['Air_Outlet_VOC'],
        data['Three_Way_Valve']
    ]

    # add about heat generor and fan pump
    if switch['current_State_Relais3'] == 1:
        switch_output.append('green')
    else:
        switch_output.append('gray')
    if switch['current_State_Relais4'] == 1:
        switch_output.append('green')
    else:
        switch_output.append('gray')

    return output + switch_output


# control system switch
@app.callback([Output('Interval-switch-system-timeout', 'disabled'),
               Output('Dropdown-choose-control-system', 'disabled')],
              [Input('button-apply-system', 'n_clicks'),
               Input('Interval-switch-system-timeout', 'n_intervals')],
              [State('Dropdown-choose-control-system', 'value'),
               State('Dropdown-choose-control-system', 'disabled')])
def system_switch_timeout(button, interval, choosen_system, dropdown_disabled):
    """
    This function sends command to control the relais as well as controlling the dropdown on the dashboard.
    The idea is, when a user sends a command to switch the iotteststand to a different control system,
    the dropdown on the dashboard is disabled for a predefined time period (WebpageConfig.switch_timeout of helper_function/config.py)
    This is implemented by using an interval widget of DASH.
    The interval time of the interval widget 'Interval-switch-system-timeout' is set to be the switch_timeout.
    'Interval-switch-system-timeout' is initially disabled.
    But when a user switches the relais, this interval widget is enabled, and the dropdown widget is disabled.
    After the predefined time period has passed, 'Interval-switch-system-timeout' triggers this function
    (this function takes 'Interval-switch-system-timeout' as input)
    and 'Interval-switch-system-timeout' is disabled by this function and the dropdown widget is enabled by this function.
    """
    if (button is not None and dropdown_disabled) or button is None:
        #  In the initialization, the 'button' (Input('button-apply-system', 'n_clicks')) is None,
        #  therefore 'Interval-switch-system-timeout' is disabled in initialization.
        #  When (button is not None and dropdown_disabled),
        #  meaning a user just send a command and now the timeout has reached,
        #  so dropdown_disabled should be set to False again and 'Interval-switch-system-timeout' should again be disabled
        return [True, False]
    entity_id = 'actuator:Relais_Switch:DO4-1'
    entity_type = 'actuator:Relais_Switch'
    if choosen_system == 'plc':
        relai1, relai2 = 0, 0
        # print('switch to PLC')
    elif choosen_system == 'ed':
        relai1, relai2 = 0, 1
        # print('switch to ED')
    elif choosen_system == 'lcgw':
        relai1, relai2 = 1, 0
        # print('switch to LCGW')
    else:  # nothing chosen
        return [True, False]
    get_data.send_command(system='', entity_id=entity_id,
                          entity_type=entity_type, command_name='setpoint_relais1',
                          command={'type': 'command', 'value': relai1})
    get_data.send_command(system='', entity_id=entity_id,
                          entity_type=entity_type, command_name='setpoint_relais2',
                          command={'type': 'command', 'value': relai2})
    return [False, True]


# control heat generator switch
@app.callback(Output('ToggleSwitch-heat-generator', 'disabled'),
              [Input('ToggleSwitch-heat-generator', 'value')],
              [State('ToggleSwitch-heat-generator', 'disabled')])
def heat_generator_switch(switch_input, switch_disabled):
    if switch_disabled:
        return False  # so that it doesn't send command during initialization
    entity_id = 'actuator:Relais_Switch:DO4-1'
    entity_type = 'actuator:Relais_Switch'
    command = {'type': 'command', 'value': int(switch_input)}
    command_name = 'setpoint_relais3'
    get_data.send_command(system='', entity_id=entity_id,
                          entity_type=entity_type, command_name=command_name,
                          command=command)
    return False  # always has to return something, so return disabled = False to change nothing


# control fan pump switch
@app.callback(Output('ToggleSwitch-fan-pump', 'disabled'),
              [Input('ToggleSwitch-fan-pump', 'value')],
              [State('ToggleSwitch-fan-pump', 'disabled')])
def fan_pump_switch(switch_input, switch_disabled):
    if switch_disabled:
        return False  # so that it doesn't send command during initialization
    entity_id = 'actuator:Relais_Switch:DO4-1'
    entity_type = 'actuator:Relais_Switch'
    command = {'type': 'command', 'value': int(switch_input)}
    command_name = 'setpoint_relais4'
    get_data.send_command(system='', entity_id=entity_id,
                          entity_type=entity_type, command_name=command_name,
                          command=command)
    return False  # always has to return something, so return disabled = False to change nothing


# enable temperature control
@app.callback(Output('input-temperature-control', 'disabled'),
              [Input('Checklist-enable-temperature-control', 'value')])
def enable_temperature_control(enable_check_box):
    return 'enable' not in enable_check_box


# temperature control (template for futurn implementation)
@app.callback(
    Output('Modal-command-sent-temperature', 'is_open'),
    [Input('button-apply-temperature-control', 'n_clicks'), Input('close-temperature', 'n_clicks')],
    [State('Modal-command-sent-temperature', 'is_open'), State('input-temperature-control', 'value')],
)
def toggle_modal_temperature_control(n1, n2, is_open, temperature_value):
    if n1 or n2:
        if not is_open:  # Because of this condition, this function is not called during the initialization.
            # scripts implementing temperature control function
            # variable "temperature_value" is the temperature value set by user
            pass
        return not is_open
    return is_open


if __name__ == '__main__':
    app.run_server(host=config.HOST_NAME, port=config.PORT_NUMBER, debug=False)  # to run on cluster
    # app.run_server(host='127.0.0.1', debug=True)  # to run on pc
