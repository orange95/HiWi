"""
This file contains two classes: GetData and GetQuantumLeap.
GetData uses FiLiP to get data and send commands, and then return the organized results.
GetQuantumLeap inherit class Thread and uses FiLiP to get historical data of different entities/attributes in parallel, and return the organized results.

Currently, a http request that uses an expired token or uses an incorrect url
lead to the same error message and error code. When one day the error message
and error code of an expired token is set, please change the
'self.expired_token_returned_message' and 'self.expired_token_returned_status_code'
in the def __init__ of class GetData accordingly.
Please also comment the codes tagged as "temporary" and uncomment the codes tagged as "hanling expired token".
"""

from helper_function.keycloak_python import KeycloakPython
from helper_function.config import WebpageConfig
import time
from datetime import datetime
from datetime import timedelta
import numpy as np
import requests
from threading import Thread
from filip.models.base import FiwareHeader
from filip.clients.ngsi_v2 import ContextBrokerClient, QuantumLeapClient


class GetData:
    """
    This class uses FiLiP to send http requests to a fiware platform to get data from orion and/or quantumleap.
    This class takes WebpageConfig of helper_function/config.py as input, please adjust config parameters in helper_function/config.py
    """
    def __init__(self, config: WebpageConfig):
        self.null_value = -99.0  # this value should be float
        self.config = config
        self.service = 'iotteststand'
        self.url_quantum_leap = 'http://' + self.config.HOST_IOTSERVER + '/quantum_teststand/'
        self.url_orion = 'http://' + self.config.HOST_IOTSERVER + '/orion_teststand/'
        self.requests_session_cb = requests.Session()
        self.requests_session_ql = requests.Session()
        self.ql_client = QuantumLeapClient(session=self.requests_session_cb, url=self.url_quantum_leap, fiware_header=FiwareHeader(service=self.service))
        self.cb_client = ContextBrokerClient(session=self.requests_session_ql, url=self.url_orion, fiware_header=FiwareHeader(service=self.service))
        self.cb_client.headers.update({'secret': str(datetime.now().microsecond)})
        self.cb_structure = self.construct_cb_structure()
        self.current_values_display_param_list = {system: list(self.config.data_structure[system].keys()) for system in self.config.data_structure}
        self.kp = KeycloakPython()
        self.token = ''
        self.token_expire_time = 0
        self.expired_token_returned_message = ''
        self.expired_token_returned_status_code = 400

    def construct_cb_structure(self):
        """
        This function construct the data structure of the data in the context broker by the data structure provided in the helper_function/config.py
        The returned cb_structure can be used by function get_current_value.
        Illustration of cb_structure:
        {
            'plc':
                {
                    'sensor:Multisensor:Air_Inlet_PLC':
                        {
                            'measured_Temperature': -99.0,
                            'measured_Relative_Humidity': -99.0
                        },
                    'sensor:Multisensor:Air_Outlet_PLC':
                        {
                            'measured_Temperature': -99.0,
                            'measured_Relative_Humidity': -99.0
                        }
                },
            'lcgw':
                {
                    'sensor:Multisensor:Temperature:Air_Inlet_LCGW':
                        {
                            'measured_Temperature': -99.0
                        }
                }
        }
        The purpose of constructing this dictionary is to make it easier to organize the returned data from the context broker for further usage.
        """
        cb_structure = {}
        for system in self.config.data_structure:
            cb_structure[system] = {}
            for param in self.config.data_structure[system]:
                entity = self.config.data_structure[system][param]['entity']
                if entity not in cb_structure[system]:
                    cb_structure[system][entity] = {}
                attribute = self.config.data_structure[system][param]['attribute']
                cb_structure[system][entity][attribute] = self.null_value
        return cb_structure

    def manage_token(self, update_token_anyway=False):
        """
        This function checks if current token has expired, and fetch a new token from keycloak server if it has expired.
        """
        now = time.time()
        if update_token_anyway or now >= self.token_expire_time:  # meaning token has expired and now it needs a new token
            access_token, expires_in = self.kp.get_access_token()
            self.token = access_token
            self.token_expire_time = now + expires_in - 20  # temporary
            # self.token_expire_time = now + expires_in  # hanling expired token
            header_update = {'Authorization': 'Bearer %s' % self.token}
            self.cb_client.headers.update(header_update)
            self.ql_client.headers.update(header_update)

    def get_relais_switch(self):
        """
        This function gets the current value of the relais from the context broker,
        and returns a dictionary of the values.
        Example return:
        {
                'current_State_Relais1': 1,
                'current_State_Relais2': 0,
                'current_State_Relais3': 1,
                'current_State_Relais4': 1
        }
        """

        self.manage_token()
        self.cb_client.headers.update({'fiware-servicepath': '/'})

        try:  # to handle the case with api errors (cannot even return any data)
            data_read = self.cb_client.get_entity_attributes(
                entity_id='actuator:Relais_Switch:DO4-1',
                entity_type='actuator:Relais_Switch'
            )
        ## temporary
        except Exception as error:
            print('in get_relais_switch, error message:\n', error)
            return {
                'current_State_Relais1': self.null_value,
                'current_State_Relais2': self.null_value,
                'current_State_Relais3': self.null_value,
                'current_State_Relais4': self.null_value
                }
        ### hanling expired token
        # except requests.exceptions.RequestException as error:
        #     response_text = error.response.text
        #     response_status_code = error.response.status_code
        #     if response_text == self.expired_token_returned_message and response_status_code == self.expired_token_returned_status_code:
        #         print('token expired, retrying...')
        #         self.manage_token(update_token_anyway=True)
        #         data_read = self.get_relais_switch()
        #     else:
        #         print('in get_relais_switch, error response text:\n', response_text, '\nerror response status_code:\n', response_status_code)
        #         return {
        #             'current_State_Relais1': self.null_value,
        #             'current_State_Relais2': self.null_value,
        #             'current_State_Relais3': self.null_value,
        #             'current_State_Relais4': self.null_value
        #         }

        try:  # to handle the case when the returned data is damaged
            return {
                'current_State_Relais1':
                    data_read['current_State_Relais1'].value,
                'current_State_Relais2':
                    data_read['current_State_Relais2'].value,
                'current_State_Relais3':
                    data_read['current_State_Relais3'].value,
                'current_State_Relais4':
                    data_read['current_State_Relais4'].value
            }
        except:
            return {
                'current_State_Relais1': self.null_value,
                'current_State_Relais2': self.null_value,
                'current_State_Relais3': self.null_value,
                'current_State_Relais4': self.null_value
            }

    def get_current_value(self, system: str):
        """
        This function gets all the data of a specified control system from the context broker.
        This function fetches all data at once instead of requesting data of each entity one by one, so that it takes less data transmission time in total.
        The data returned from the context broker contains data of all attributes of all entities, and the data structure of different control systems may not be the same.
        With the help of self.config.data_structure and the self.cb_structure (previously built via function construct_cb_structure in the __init__(self)),
        this function returns the same format for different control systems.
        Illustration of returned data:
        {
            'Air_Inlet_Temperature': 10,
            'Air_Inlet_Humidity': 50,
            'Air_Outlet_Temperature': 20
        }

        parameter 'system' can be 'plc', 'ed', or 'lcgw'
        """
        self.manage_token()
        self.cb_client.headers.update({'fiware-servicepath': '/%s' % system})

        try:
            data_read = self.cb_client.get_entity_list(response_format='keyValues')
        ## temporary
        except Exception as error:
            print('in get_current_value, error message:\n', error)
            return self.return_null_orion()

        ### hanling expired token
        # except requests.exceptions.RequestException as error:
        #     response_text = error.response.text
        #     response_status_code = error.response.status_code
        #     if response_text == self.expired_token_returned_message and response_status_code == self.expired_token_returned_status_code:
        #         print('token expired, retrying...')
        #         self.manage_token(update_token_anyway=True)
        #         data_read = self.get_current_value(system)
        #     else:
        #         print('in get_current_value, error response text:\n', response_text, '\nerror response status_code:\n', response_status_code)
        #         return self.return_null_orion()

        # organize data returned from the context broker to the same format
        for item in data_read:
            entity = item.id
            if entity in self.cb_structure[system]:
                attrs_list = self.cb_structure[system][entity].keys()
                for attr in attrs_list:
                    exec('self.cb_structure[system][entity][attr] = item.%s' % attr)
                    self.cb_structure[system][entity][attr] = round(float(self.cb_structure[system][entity][attr]), self.config.display_digits)
        return {
            param: self.cb_structure[system][
                self.config.data_structure[system][param]['entity']
            ][self.config.data_structure[system][param]['attribute']]
            for param in self.current_values_display_param_list[system]
        }

    def return_null_orion(self):
        """
        This function is called when it is unable to get or to parse the data from context broker,
        and returns dummy data for each parameter.
        This function is called within this class, but can also be called outside this class (e.g. index.py),
        this is why it is made to be a function instead of two lines of code in other functions.
        Illustration of return data structure:
        {
            'Air_Inlet_Temperature': -99.0,
            'Air_Inlet_Humidity': -99.0,
            'Air_Outlet_Temperature': -99.0
        }
        """
        all_param = []
        for system in self.current_values_display_param_list:
            all_param += self.current_values_display_param_list[system]
        return {param: self.null_value for param in list(set(all_param))}  # eliminate duplicates

    def get_history_thread(self, system: str, fromDate_str: str):
        """
        This function creates multiple threads via the class GetQuantumLeap to get historical data from quantumleap.
        For each parameter in the config.history_values_display_param_list of each control system,
        this function creates a thread for getting the historical data of this function.
        This function take advantage of the feature of python's objects,
        that is to do shallow copy by default, and let all threads share a same dictionary (the data_return) for storing the returned data.

        parameter system: 'plc', 'ed', or 'lcgw'
        parameter fromDate_str: year-month-day, e.g.: '2021-01-31'
        """
        data_return = {'token_expire_time': self.token_expire_time}
        self.ql_client.headers.update({'fiware-servicepath': '/%s' % system})
        for param in self.config.history_values_display_param_list[system]:
            thread_obj = GetQuantumLeap(self.config, param, data_return, self.ql_client, self.config.data_structure[system][param]['entity'],
                                        self.config.data_structure[system][param]['attribute'], fromDate_str)
            thread_obj.start()
        return data_return

    def get_switch_history(self, fromDate_str):
        """
        This function gets the history data of the relais from quantumleap.
        The data in quantumleap is the history values of relai1, relai2, etc.
        This function also transforms the history values into the start time and end time of control systems
        Illustration of return data and how to interprete:
        {
            'plc': [
                [
                    datetime(2021, 1, 2, 8, 0, 0), datetime(2021, 1, 2, 12, 0, 0)
                ],
                [
                    datetime(2021, 1, 2, 9, 59, 59), datetime(2021, 1, 2, 14, 59, 59)
                ]
            ],
            'lcgw': [
                [
                    datetime(2021, 1, 2, 10, 0, 0)
                ],
                [
                    datetime(2021, 1, 2, 11, 59, 59)
                ]
            ]
        }
        The idea is [[list of the starting timestamps], [list of the ending timestamps]]
        For the example above, from 08:00:00 on 2nd of January, the control system is plc, and the control time ends at 09:59:59 on the same day.
        From 10:00:00 on, lcgw starts to control the system, and ends at 11:59:59.
        Afterward, plc takes control again from 12:00:00 untill 14:59:59.

        parameter fromDate_str: year-month-day, e.g.: '2021-01-31'
        """
        start_end_time = {
            'plc': [[], []],  # [[start_time list], [end_time list]]
            'ed': [[], []],
            'lcgw': [[], []]
        }

        # get data
        self.manage_token()
        self.ql_client.headers.update({'fiware-servicepath': '/'})

        try:
            relai1_ql_data = self.ql_client.get_entity_attr_values_by_id(
                    entity_id='actuator:Relais_Switch:DO4-1',
                    attr_name='current_State_Relais1', from_date=fromDate_str)
            relai2_ql_data = self.ql_client.get_entity_attr_values_by_id(
                entity_id='actuator:Relais_Switch:DO4-1',
                attr_name='current_State_Relais2', from_date=fromDate_str)
        ## temporary
        except Exception as error:
            print('in get_switch_history, error message:\n', error)
            return start_end_time
        ### hanling expired token
        # except requests.exceptions.RequestException as error:
        #     response_text = error.response.text
        #     response_status_code = error.response.status_code
        #     if response_text == self.expired_token_returned_message and response_status_code == self.expired_token_returned_status_code:
        #         print('token expired, retrying...')
        #         self.manage_token(update_token_anyway=True)
        #         return self.get_switch_history(fromDate_str)
        #     else:
        #         print('in get_switch_history, error response text:\n',
        #               response_text, '\nerror response status_code:\n',
        #               response_status_code)
        #         return start_end_time

        try:
            time_relai, relai1, relai2 = self.switch_history_filter(
                relai1_ql_data,
                relai2_ql_data)
        except Exception as error:
            print('in get_switch_history, error when parsing data, error message:', error)
            return start_end_time

        if len(relai1) != len(relai2):
            print('relais1 and relais2 have different lengths')
            return start_end_time

        # calculate start time and end time of each control period
        r1_pre, r2_pre, sys_pre = self.null_value, self.null_value, self.null_value
        for i, (r1, r2) in enumerate(zip(relai1, relai2)):
            if (r1, r2) != (r1_pre, r2_pre):
                if i != 0:
                    end_time = time_relai[i] - timedelta(seconds=1)
                    start_end_time[sys_pre][1].append(end_time)
                start_time = time_relai[i]
                if r1 == 1:
                    start_end_time['lcgw'][0].append(start_time)
                    sys_pre = 'lcgw'
                elif r1 == 0 and r2 == 0:
                    start_end_time['plc'][0].append(start_time)
                    sys_pre = 'plc'
                else:
                    start_end_time['ed'][0].append(start_time)
                    sys_pre = 'ed'
            r1_pre, r2_pre = r1, r2
        end_time = datetime.now()
        start_end_time[sys_pre][1].append(end_time)
        return start_end_time

    def switch_history_filter(self, relai1_timeseries_object, relai2_timeseries_object):
        """
        This function transform the data get from quantumleap using FiLiP into numpy array, and then filter out the None values.
        This function is used by function get_switch_history while parsing the historical data of the relais.
        """
        relai1_time = np.array(relai1_timeseries_object.index)
        relai1_value = np.array(relai1_timeseries_object.attributes[0].values)
        # relai2_time = np.array(relai2_timeseries_object.index)
        relai2_value = np.array(relai2_timeseries_object.attributes[0].values)

        # filter out null values
        relai1_select_index = relai1_value != None
        relai2_select_index = relai2_value != None
        select_index = relai1_select_index * relai2_select_index
        relai1_time_filtered, relai1_value_filtered, relai2_value_filtered = \
            relai1_time[select_index], relai1_value[select_index].astype(float), relai2_value[select_index].astype(float)

        return relai1_time_filtered, relai1_value_filtered, relai2_value_filtered

    def send_command(self, system, entity_id, entity_type, command_name, command):
        """
        This function sends command to the context broker

        parameter system: 'plc', 'ed', or 'lcgw'
        parameter entity_id: e.g. 'actuator:Three_Way_Valve_PLC'
        parameter entity_type: e.g. 'actuator:Valve'
        parameter command_name: e.g. 'setpoint'
        parameter command: e.g. {'type': 'command', 'value': '0'}
        """
        self.manage_token()
        self.cb_client.headers.update({'fiware-servicepath': '/%s' % system})
        try:
            self.cb_client.post_command(entity_id=entity_id, entity_type=entity_type, command=command, command_name=command_name)
        ## temporary
        except Exception as error:
            print('in send_command, error message:\n', error)
        ### hanling expired token
        # except requests.exceptions.RequestException as error:
        #     response_text = error.response.text
        #     response_status_code = error.response.status_code
        #     if response_text == self.expired_token_returned_message and response_status_code == self.expired_token_returned_status_code:
        #         print('token expired, retrying...')
        #         self.manage_token(update_token_anyway=True)
        #         self.cb_client.post_command(entity_id=entity_id,
        #                                     entity_type=entity_type,
        #                                     command=command,
        #                                     command_name=command_name)
        #     else:
        #         print('in send_command, error response text:\n', response_text, '\nerror response status_code:\n', response_status_code)

    def __del__(self):
        """
        When this class is terminated, class the request sessions
        """
        self.requests_session_cb.close()
        self.requests_session_ql.close()


class GetQuantumLeap(Thread):
    """
    This class is a thread that gets data from quantumleap, and this class is used in the function get_history_thread in the class GetData.
    """
    def __init__(self, config, param, return_data, ql_client, entity_id, attr_name, from_date):
        Thread.__init__(self)
        """
        The return_data is the same object shared by many threads in the function function get_history_thread in the class GetData.
        When another thread add data to the return_data, the return_data in this thread will also change accordingly.
        """
        self.config = config
        self.param = param
        self.return_data = return_data
        self.ql_client = ql_client
        self.entity_id = entity_id
        self.attr_name = attr_name
        self.from_date = from_date
        self.kp = KeycloakPython()
        self.expired_token_returned_message = ''
        self.expired_token_returned_status_code = 400

    def filter(self, timeseries_object):
        """
        This function filters out the outliers of the data from the quantumleap.
        The definition of outliers is in the helper_function/config.py
        """
        data_time = np.array(timeseries_object.index)
        data_value = np.array(timeseries_object.attributes[0].values)

        # filter out null values
        select_index = data_value != None
        data_time_withoutNone, data_value_withoutNone = data_time[select_index], data_value[select_index].astype(float)

        # filter out temperature abnormal values
        if 'Temperature' in self.param:
            select_index_temp_min = data_value_withoutNone > self.config.temperature_min
            select_index_temp_max = data_value_withoutNone < self.config.temperature_max
            select_index = select_index_temp_min * select_index_temp_max
            data_time_withoutNone, data_value_withoutNone = data_time_withoutNone[select_index], data_value_withoutNone[
                select_index]
        # filter out humidity abnormal values
        if 'Humidity' in self.param:
            select_index_humi_min = data_value_withoutNone > self.config.humidity_min
            select_index_humi_max = data_value_withoutNone < self.config.humidity_max
            select_index = select_index_humi_min * select_index_humi_max
            data_time_withoutNone, data_value_withoutNone = data_time_withoutNone[select_index], data_value_withoutNone[select_index]
        return [data_time_withoutNone, data_value_withoutNone]

    def run(self):
        """
        This function is inherited from Thread, therefore please don't change the function's name.
        When this class is initiated, for example thread_obj = GetQuantumLeap, then thread_obj.start() will run this function in a new thread.
        Illustration of the overall return_data:
        {
            'Air_Inlet_Temperature': [
                [datetime(2021, 1, 2, 8, 0, 0), datetime(2021, 1, 2, 8, 1, 0)],
                [10, 20]
            ],
            'Air_Inlet_Humidity': [
                [datetime(2021, 1, 2, 8, 2, 0), datetime(2021, 1, 2, 8, 3, 0)],
                [60, 70]
            ]
        }
        Each thread corresponds to the data of each key in the return_data (e.g. data of return_data['Air_Inlet_Temperature'])
        """
        now = time.time()
        if now >= self.return_data['token_expire_time']:
            access_token, expires_in = self.kp.get_access_token()
            self.return_data['token_expire_time'] = now + expires_in
            self.ql_client.headers.update(
                {'Authorization': 'Bearer %s' % access_token})

        try:
            read_data = self.ql_client.get_entity_attr_values_by_id(
                    entity_id=self.entity_id,
                    attr_name=self.attr_name, from_date=self.from_date)
        ## temporary
        except Exception as error:
            print('in GetQuantumLeap when getting, error message:\n', error)
            read_data = None
        ### hanling expired token
        # except requests.exceptions.RequestException as error:
        #     response_text = error.response.text
        #     response_status_code = error.response.status_code
        #     if response_text == self.expired_token_returned_message and response_status_code == self.expired_token_returned_status_code:
        #         print('token expired, retrying...')
        #         self.manage_token(update_token_anyway=True)
        #         read_data = self.ql_client.get_entity_attr_values_by_id(
        #             entity_id=self.entity_id,
        #             attr_name=self.attr_name, from_date=self.from_date)
        #     else:
        #         print('in GetQuantumLeap when getting', self.param, 'error response text:\n', response_text, '\nerror response status_code:\n', response_status_code)
        #         read_data = None
        try:
            data = self.filter(read_data)
        except:
            data = [[], []]
        self.return_data[self.param] = data
