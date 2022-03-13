# iot-development.software.FIWAREControls

To run the dashboard of the iotteststand, please first check:

The "HOST_IOTSERVER" in webpage/helper_function/config.py

The settings of "app.run_server" in the "if __name__ == '__main__':" of webpage/index.py.

Please provide the information listed in the webpage/.env_template and change the filename to webpage/.env

And then please execute the webpage/index.py

### To be done
The temperature control function is not implemented, only the enabling check box. 
When implementing temperature control functions, please refer to the doc string in webpage/index.py and there is a template call-back function in the same file.

The error handling of expired token is not completed yet, the reasons for that and what can be done in the future please refer to the doc string in webpage/helper_function/organize_data.py
