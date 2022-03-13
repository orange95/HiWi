import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import random
from app import app
import dash_daq as daq

DEFAULT_IMAGE_PATH = "assets/images/AHU.PNG"

external_stylesheets = [dbc.themes.LUX]

n=random.randint(0,100)

layout = html.Div( 
            [   
                dbc.Row([
                    dbc.Col([
                        dbc.Container(
                        [
                            html.Img(src=DEFAULT_IMAGE_PATH, alt='AHU', className='orion_img'),
                            html.Button('0',id='t1_output', className='t1'),
                            html.Button('14',id='t2_output', className='t2'),
                            html.Button('14',id='t3_output', className='t3'),
                            html.Button('14',id='t4_output', className='t4'),
                            html.Button('14',id='t5_output', className='t5'),
                            html.Button('14',id='t6_output', className='t6'),
                            html.Button('64',id='rh1_output', className='rh1'),
                            html.Button('64',id='rh2_output', className='rh2'),
                            html.Button('4.3',id='voc1_output', className='voc1'),
                            html.Button('ON',id='val1_output', className='valve1'),
                        ]),
                    ],md=8,className='container'), 
                    dbc.Col([
                        dbc.Row([
                            dbc.Col(
                                html.H5(children='FAN SPEED: 2000 rpm', className="text-center"),
                                
                            )
                        ]),
                        dbc.Row([           
                            dbc.Col(
                                html.Div([
                                    daq.Gauge(
                                        id='my-daq-gauge',
                                        color={"gradient":True,"ranges":{"green":[0,60],"yellow":[60,80],"red":[80,100]}},
                                        min=0,
                                        max=100,
                                        value=60,
                                        size=200
                                )], className='gauge_fan')
                            )                                                    
                        ])
                        
                    ], md=3), 
                    dbc.Col(md=1)
                ]),               
                dcc.Interval(id='interval1', interval=5 * 1000, n_intervals=0)
            ]
)

@app.callback([Output('t1_output', 'children'),
                Output('t2_output', 'children'),
                Output('t3_output', 'children'),
                Output('t4_output', 'children'),
                Output('t5_output', 'children'),
                Output('t6_output', 'children'),
                Output('rh1_output', 'children'),
                Output('rh2_output', 'children'),
                Output('voc1_output', 'children'),
                Output('val1_output', 'children')],
              Input('interval1', 'n_intervals'))
def image_data_change(value):
    # alert(n)
    val = random.randint(0,100)
    print('T1 Val edited to : {}', val)
    return str(val),str(val),str(val),str(val),str(val),str(val),str(val),str(val),str(val),'OFF'
