

class WebpageConfig:
    # Server
    HOST_NAME = '0.0.0.0'
    PORT_NUMBER = 7770
    HOST_IOTSERVER = 'some server'  # for running on the server
    # HOST_IOTSERVER = 'localhost:3000'  # for running on local PC

    # Images
    DEFAULT_IMAGE_PATH = "~/../assets/images/AHU2.png"
    LEGEND_IMAGE_PATH = "~/../assets/images/System_legend.png"
    LOGO_IMAGE_PATH = "~/../assets/images/logo.png"

    # Define outliers
    humidity_min = 0
    humidity_max = 100
    temperature_min = 0
    temperature_max = 80

    # Display
    display_digits = 1
    switch_timeout = 30  # Seconds. After switch to a different control system, the switching function is disabled for these seconds.
    orion_refresh_interval = 5  # Seconds. How often do the current values on the system graph refresh.

    # Parameters to display in historical graph
    history_values_display_param_list = {
        'plc': ['Air_Inlet_Temperature', 'Air_Inlet_Humidity',
                'Air_Outlet_Temperature', 'Air_Outlet_Humidity', 'Air_Outlet_VOC',
                'Return_Temperature_Primary', 'Supply_Temperature_Primary',
                'Return_Temperature', 'Supply_Temperature', 'Three_Way_Valve'],
        'ed': ['Air_Inlet_Temperature', 'Air_Inlet_Humidity',
                'Air_Outlet_Temperature', 'Air_Outlet_Humidity', 'Air_Outlet_VOC',
                'Return_Temperature_Primary', 'Supply_Temperature_Primary',
                'Return_Temperature', 'Supply_Temperature', 'Three_Way_Valve'],
        'lcgw': ['Air_Inlet_Temperature', 'Air_Inlet_Humidity',
                 'Air_Outlet_Temperature', 'Air_Outlet_Humidity', 'Air_Outlet_VOC',
                 'Return_Temperature_Primary', 'Supply_Temperature_Primary',
                 'Return_Temperature', 'Supply_Temperature',
                 'Three_Way_Valve']
    }

    # Data structure in orion
    data_structure = {
        'plc': {
            'Air_Inlet_Temperature': {
                'entity': 'sensor:Multisensor:Air_Inlet_PLC',
                'attribute': 'measured_Temperature'
            },
            'Air_Inlet_Humidity': {
                'entity': 'sensor:Multisensor:Air_Inlet_PLC',
                'attribute': 'measured_Relative_Humidity'
            },
            'Air_Outlet_Temperature': {
                'entity': 'sensor:Multisensor:Air_Outlet_PLC',
                'attribute': 'measured_Temperature',
            },
            'Air_Outlet_Humidity': {
                'entity': 'sensor:Multisensor:Air_Outlet_PLC',
                'attribute': 'measured_Relative_Humidity',
            },
            'Air_Outlet_VOC': {
                'entity': 'sensor:Multisensor:Air_Outlet_PLC',
                'attribute': 'measured_VOC',
            },
            'Return_Temperature_Primary': {
                'entity': 'sensor:Temperature:Water_Return_Primary_PLC',
                'attribute': 'measured_Value',
            },
            'Supply_Temperature_Primary': {
                'entity': 'sensor:Temperature:Water_Supply_Primary_PLC',
                'attribute': 'measured_Value',
            },
            'Return_Temperature': {
                'entity': 'sensor:Temperature:Water_Return_PLC',
                'attribute': 'measured_Value',
            },
            'Supply_Temperature': {
                'entity': 'sensor:Temperature:Water_Supply_PLC',
                'attribute': 'measured_Value',
            },
            'Three_Way_Valve': {
                'entity': 'actuator:Three_Way_Valve_PLC',
                'attribute': 'current_State',
            }
        },
        'ed': {
            'Air_Inlet_Temperature': {
                'entity': 'sensor:Multisensor:Air_Inlet_ED',
                'attribute': 'measured_Temperature',
            },
            'Air_Inlet_Humidity': {
                'entity': 'sensor:Multisensor:Air_Inlet_ED',
                'attribute': 'measured_Relative_Humidity',
            },
            'Air_Outlet_Temperature': {
                'entity': 'sensor:Multisensor:Air_Outlet_ED',
                'attribute': 'measured_Temperature',
            },
            'Air_Outlet_Humidity': {
                'entity': 'sensor:Multisensor:Air_Outlet_ED',
                'attribute': 'measured_Relative_Humidity',
            },
            'Air_Outlet_VOC': {
                'entity': 'sensor:Multisensor:Air_Outlet_ED',
                'attribute': 'measured_VOC',
            },
            'Return_Temperature_Primary': {
                'entity': 'sensor:Temperature:Water_Return_Primary_ED',
                'attribute': 'measured_Value',
            },
            'Supply_Temperature_Primary': {
                'entity': 'sensor:Temperature:Water_Supply_Primary_ED',
                'attribute': 'measured_Value',
            },
            'Return_Temperature': {
                'entity': 'sensor:Temperature:Water_Return_ED',
                'attribute': 'measured_Value',
            },
            'Supply_Temperature': {
                'entity': 'sensor:Temperature:Water_Supply_ED',
                'attribute': 'measured_Value',
            },
            'Three_Way_Valve': {
                'entity': 'actuator:Three_Way_Valve_ED',
                'attribute': 'current_State'
            }
        },
        'lcgw': {
            'Air_Inlet_Temperature': {
                'entity': 'sensor:Multisensor:Temperature:Air_Inlet_LCGW',
                'attribute': 'measured_Temperature',
            },
            'Air_Inlet_Humidity': {
                'entity': 'sensor:Multisensor:Humidity:Air_Inlet_LCGW',
                'attribute': 'measured_Relative_Humidity',
            },
            'Air_Outlet_Temperature': {
                'entity': 'sensor:Multisensor:Temperature:Air_Outlet_LCGW',
                'attribute': 'measured_Temperature',
            },
            'Air_Outlet_Humidity': {
                'entity': 'sensor:Multisensor:Humidity:Air_Outlet_LCGW',
                'attribute': 'measured_Relative_Humidity',
            },
            'Air_Outlet_VOC': {
                'entity': 'sensor:Multisensor:VOC:Air_Outlet_LCGW',
                'attribute': 'measured_VOC',
            },
            'Return_Temperature_Primary': {
                'entity': 'sensor:Temperature:Water_Supply_And_Return_Primary_LCGW',
                'attribute': 'measured_Return_Temperature_Primary',
            },
            'Supply_Temperature_Primary': {
                'entity': 'sensor:Temperature:Water_Supply_And_Return_Primary_LCGW',
                'attribute': 'measured_Supply_Temperature_Primary',
            },
            'Return_Temperature': {
                'entity': 'sensor:Temperature:Water_Supply_And_Return_LCGW',
                'attribute': 'measured_Return_Temperature',
            },
            'Supply_Temperature': {
                'entity': 'sensor:Temperature:Water_Supply_And_Return_LCGW',
                'attribute': 'measured_Supply_Temperature',
            },
            'Three_Way_Valve': {
                'entity': 'actuator:Three_Way_Valve_LCGW',
                'attribute': 'current_State'
            }
        }
    }
