"""
This script can be used to provision service groups and devices on a FiWare
platform automatically given a corresponding json file, to patch meta data to
orion after provisioning devices on iot agent, as well as to delete
them given a list of what you want to delete.

Please first install FiLiP via the instruction on https://github.com/RWTH-EBC/FiLiP
Please edit the '.env_template' for the keycloak, and then change the filename to '.env'

Example of using the auto provisioning functions please refer to below section "if __name__ == '__main__':"
"""


import json
import pickle
import logging
import time
import requests
from filip.models.base import FiwareHeader
from filip.models.ngsi_v2.context import Subscription
from filip.models.ngsi_v2.iot import \
    Device, \
    DeviceCommand, \
    DeviceAttribute, \
    ServiceGroup
from filip.clients.ngsi_v2 import HttpClient
from filip.clients.ngsi_v2 import QuantumLeapClient
from filip.clients.ngsi_v2.client import HttpClientConfig
from filip.models.ngsi_v2.context import ContextEntity
from keycloak_python import KeycloakPython


class AutoProvision:
    def __init__(self, cb_url: str, iota_url: str, ql_url: str, fiware_service: str):
        """
        These three values will be used in every functions.
        :param cb_url: url of the context broker, e.g. 'https://api.n5geh.eonerc.rwth-aachen.de'
        :param iota_url: url of the io agent, e.g. 'https://json.iot.n5geh.eonerc.rwth-aachen.de'
        :param fiware_service: fiware service, e.g. 'iotteststand'
        """
        self.cb_url = cb_url
        self.iota_url = iota_url
        self.ql_url = ql_url
        self.fiware_service = fiware_service

    def provision_service_group(self, fiware_service_path: str,
                                service_group_apikey: str,
                                service_group_resource: str,
                                cb_host: str,
                                autoprovision: bool,
                                explicitAttrs: bool):
        """
        This function provisions one service group.
        :param fiware_service_path: the fiware service path, e.g. '/lcgw'
        :param service_group_apikey: the api key of the service group, e.g. 'iotteststand_lcgw'
        :param service_group_resource: the resource of the service group, e.g. '/iot/json'
        :param cb_host: the context broker host, e.g. 'http://orion:1026'
        :param autoprovision: recommended set to False. If set to True and if
            there are incoming data for a non-exist or deleted device, the
            service group would provision a new device for the incoming data
            automatically and with 'Thing' in the newly provisioned name
        :param explicitAttrs: recommended set to True.
        """
        fiware_header = FiwareHeader(service=self.fiware_service,
                                     service_path=fiware_service_path)
        config = HttpClientConfig(cb_url=self.cb_url, iota_url=self.iota_url)

        service_group = ServiceGroup(service=fiware_header.service,
                                     subservice=fiware_header.service_path,
                                     apikey=service_group_apikey,
                                     resource=service_group_resource,
                                     cbHost=cb_host,
                                     autoprovision=autoprovision,
                                     explicitAttrs=explicitAttrs)
        token, in_sec = KeycloakPython().get_access_token()
        client = HttpClient(fiware_header=fiware_header, config=config,
                            headers={'Authorization': 'Bearer %s' % token})
        client.iota.headers.update({'Authorization': 'Bearer %s' % token})
        try:
            logger.info("------Creating service group------")
            client.iota.post_group(service_group=service_group, update=True)
        except Exception as error_message:
            logger.error('Error when provisioning service group (service_group_apikey=%s, service_group_resource=%s).\nError message:\n%s' % (service_group_apikey, service_group_resource, error_message))

    def provision_devices(self, fiware_service_path: str,
                          device_apikey: str,
                          provision_device_filepath: str,
                          provision_all_devices: bool,
                          target_devices: list = None):
        """
        :param fiware_service_path: the fiware service path, e.g. '/lcgw'
        :param device_apikey: apikey of devices
        :param provision_device_filepath: full file path of the json file that
            contains all necessary information about devices
        :param provision_all_devices: if set to True will provision all devices
            provided in the json file 'provision_device_filepath'.
            If set to False please provide a list of target devices to parameter 'target_devices'
        :param target_devices: a list of devices to be provicioned, e.g. ['gw-analog1', 'gw-analog2']
        """
        if target_devices is None:
            target_devices = []
        fiware_header = FiwareHeader(service=self.fiware_service,
                                     service_path=fiware_service_path)
        config = HttpClientConfig(cb_url=self.cb_url, iota_url=self.iota_url)

        file = open(provision_device_filepath)
        provision_device_json = json.load(file)

        if provision_all_devices:
            target_devices = provision_device_json.keys()

        logger.info("------Provisioning devices------")
        for key in target_devices:
            # If a device of the target_devices is not in the json file
            # that contains information about devices, will give error message
            # of this device and continue provisioning other devices in the target_devices
            if not provision_all_devices and key not in provision_device_json.keys():
                logger.error('Device %s not in file %s' % (key, provision_device_filepath))
                continue

            provision_device = provision_device_json[key]
            attributes = []
            for attr_item in provision_device['attributes']:
                if 'object_id' in attr_item.keys():
                    device_attribute = DeviceAttribute(name=attr_item['name'],
                                                       object_id=attr_item[
                                                           'object_id'],
                                                       type=attr_item['type'])
                else:
                    device_attribute = DeviceAttribute(name=attr_item['name'],
                                                       type=attr_item['type'])
                attributes.append(device_attribute)

            commands = [
                DeviceCommand(name=cmd_item['name'], type=cmd_item['type'])
                for cmd_item in provision_device['commands']
            ]

            device = Device(device_id=provision_device['device_id'],
                            entity_name=provision_device['entity_name'],
                            entity_type=provision_device['entity_type'],
                            protocol=provision_device['protocol'],
                            transport=provision_device['transport'],
                            apikey=device_apikey,
                            attributes=attributes,
                            commands=commands,
                            timezone=provision_device['timezone'],
                            lazy=[],
                            explicitAttrs=provision_device['explicitAttrs'])

            token, in_sec = KeycloakPython().get_access_token()
            client = HttpClient(fiware_header=fiware_header, config=config,
                                headers={'Authorization': 'Bearer %s' % token})
            client.iota.headers.update({'Authorization': 'Bearer %s' % token})
            try:
                client.iota.post_device(device=device, update=True)
            except Exception as error_message:
                logger.error('Error when provisioning device %s.\nError message:\n%s' % (
                    key, error_message))

    def patch_metadata(self, fiware_service_path: str,
                       patch_metadata_filepath: str,
                       patch_all_devices: bool,
                       target_devices: list = None):
        """
        After provisioning devices to the iot agent, also need to patch
        metadata to context broker, or the data type may become nonetype.
        :param fiware_service_path: the fiware service path, e.g. '/lcgw'
        :param patch_metadata_filepath: full file path of the json file that
            contains all necessary information about metadata of devices
        :param patch_all_devices: if set to True will patch meta data of
            all devices provided in the json file 'patch_metadata_filepath'.
            If set to False please provide a list of target devices to parameter 'target_devices'
        :param target_devices: a list of devices to patch the metadata for, e.g. ['gw-analog1', 'gw-analog2']
        """
        fiware_header = FiwareHeader(service=self.fiware_service,
                                     service_path=fiware_service_path)
        config = HttpClientConfig(cb_url=self.cb_url, iota_url=self.iota_url)

        file = open(patch_metadata_filepath)
        patch_metadata_json = json.load(file)

        if patch_all_devices:
            target_devices = patch_metadata_json.keys()

        logger.info("------Patching meta data to the provisioned devices------")
        for key in target_devices:
            # If a device of the target_devices is not in the json file
            # that contains information about metadata, will give error message
            # of this device and continue patching metadata of other devices in the target_devices
            if not patch_all_devices and key not in patch_metadata_json.keys():
                logger.error('Device %s not in file %s' % (key, patch_metadata_filepath))
                continue

            data = patch_metadata_json[key]
            entity = ContextEntity(**data)

            token, in_sec = KeycloakPython().get_access_token()
            client = HttpClient(fiware_header=fiware_header, config=config,
                                headers={'Authorization': 'Bearer %s' % token})
            client.cb.headers.update({'Authorization': 'Bearer %s' % token})
            try:
                client.cb.update_entity(entity=entity)
            except Exception as error_message:
                logger.error('Error when patching metadata of device %s.\nError message:\n%s' % (
                    key, error_message))

    def create_database_subscriptions(self, fiware_service_path: str,
                                      subscription_list: list,
                                      backup_file_path: str = None):
        fiware_header = FiwareHeader(service=self.fiware_service,
                                     service_path=fiware_service_path)
        config = HttpClientConfig(cb_url=self.cb_url, iota_url=self.iota_url, ql_url=self.ql_url)
        cb_request_session = requests.Session()
        token, in_sec = KeycloakPython().get_access_token()
        client = HttpClient(fiware_header=fiware_header, config=config,
                            session=cb_request_session,
                         headers={'Authorization': 'Bearer %s' % token})
        client.iota.headers.update({'Authorization': 'Bearer %s' % token})
        client.cb.headers.update({'Authorization': 'Bearer %s' % token})
        def post_subscription(subscription: Subscription):
            returned_sub_id = client.cb.post_subscription(subscription=subscription)
            return returned_sub_id

        def get_subscriptions(backup_file_path: str):
            try:
                i = client.cb.get_subscription_list()
            except Exception as error_message:
                logger.error(
                    'Error when getting subscription\nError message:\n%s' % error_message)
                return []
            if backup_file_path:
                print(backup_file_path)
                try:
                    with open(backup_file_path, 'wb') as f:
                        pickle.dump(i, f)
                except Exception as error_message:
                    logger.error(
                        'Error when backing up subscriptions\nError message:\n%s' % error_message)
            return i

        logger.info("------Posting subscriptions to context broker via QL------")
        returned_sub_id = []
        for i in subscription_list:
            try:
                returned_sub_id.append(post_subscription(subscription=i))
            except Exception as error_message:
                logger.error(
                    'Error when posting subscription ', i, '\nError message:\n%s' % error_message)
        logger.info("------Getting all subscriptions from context broker------")
        return returned_sub_id, get_subscriptions(backup_file_path=backup_file_path)

#%%
    def delete_service_groups(self, fiware_service_path: str,
                              service_group_apikey: str,
                              service_group_resource: str):
        """
        This function deletes a service group.
        :param fiware_service_path: the fiware service path, e.g. '/lcgw'
        :param service_group_apikey: the api key of the service group, e.g. 'iotteststand_lcgw'
        :param service_group_resource: the resource of the service group, e.g. '/iot/json'
        """
        fiware_header = FiwareHeader(service=self.fiware_service,
                                     service_path=fiware_service_path)
        config = HttpClientConfig(cb_url=self.cb_url, iota_url=self.iota_url)
        token, in_sec = KeycloakPython().get_access_token()
        client = HttpClient(fiware_header=fiware_header, config=config,
                            headers={'Authorization': 'Bearer %s' % token})
        client.iota.headers.update({'Authorization': 'Bearer %s' % token})
        try:
            logger.info("------Deleting service group------")
            client.iota.delete_group(resource=service_group_resource, apikey=service_group_apikey)
        except Exception as error_message:
            logger.error('Error when deleting service group (service_group_apikey=%s, service_group_resource=%s).\nError message:\n%s' % (service_group_apikey, service_group_resource, error_message))

    def delete_devices_from_iota(self, fiware_service_path,
                                 delete_all_devices: bool,
                                 target_devices: list = None):
        """
        This function deletes devices in the iot agent.
        :param fiware_service_path: the fiware service path, e.g. '/lcgw'
        :param delete_all_devices: if set to True will delete all devices
            that currently exist in the iot agent under this 'fiware_service_path'
            If set to False please provide a list of target devices to parameter 'target_devices'
        :param target_devices: a list of devices to be deleted, e.g. ['gw-analog1', 'gw-analog2']
        """
        fiware_header = FiwareHeader(service=self.fiware_service,
                                     service_path=fiware_service_path)
        config = HttpClientConfig(cb_url=self.cb_url, iota_url=self.iota_url)
        token, in_sec = KeycloakPython().get_access_token()
        client = HttpClient(fiware_header=fiware_header, config=config,
                            headers={'Authorization': 'Bearer %s' % token})
        client.iota.headers.update({'Authorization': 'Bearer %s' % token})

        try:
            existing_devices = [item.device_id for item in client.iota.get_device_list()]
        except Exception as error_message:
            existing_devices = []
            logger.error(
                'Error when getting all device list on iot agent. \nError message:\n%s' % error_message)

        if delete_all_devices:
            target_devices = existing_devices

        logger.info("------Deleting devices from iot agent------")
        for device_id in target_devices:
            # If a device of the target_devices does not exist in the current iot agent,
            # will give error message of this device and continue deleting other devices in the target_devices
            if not delete_all_devices and device_id not in existing_devices:
                logger.error('Device %s not exist in iot igent' % device_id)
                continue
            try:
                client.iota.delete_device(device_id=device_id)
            except Exception as error_message:
                logger.error('Error when deleting device %s from iot agent. \nError message:\n%s' % (
                    device_id, error_message))

    def delete_devices_from_cb(self, fiware_service_path,
                               delete_all_entities: bool,
                               target_entities: list = None):
        """
        This function deletes devices in the context broker.
        :param fiware_service_path: the fiware service path, e.g. '/lcgw'
        :param delete_all_entities: if set to True will delete all entities
            that currently exist in the context broker under this 'fiware_service_path'
            If set to False please provide a list of target entities to parameter 'target_devices'
        :param target_entities: a list of entities to be deleted
        """
        fiware_header = FiwareHeader(service=self.fiware_service,
                                     service_path=fiware_service_path)
        config = HttpClientConfig(cb_url=self.cb_url, iota_url=self.iota_url)
        token, in_sec = KeycloakPython().get_access_token()
        client = HttpClient(fiware_header=fiware_header, config=config,
                            headers={'Authorization': 'Bearer %s' % token})
        client.cb.headers.update({'Authorization': 'Bearer %s' % token})

        try:
            existing_entities = [item.id for item in client.cb.get_entity_list()]
        except Exception as error_message:
            existing_entities = []
            logger.error(
                'Error when getting all entity list on context broker. \nError message:\n%s' % error_message)

        if delete_all_entities:
            target_entities = existing_entities

        logger.info("------Deleting entities from context broker------")
        for entity_id in target_entities:
            # If an entity of the target_entities does not exist in the current context broker,
            # will give error message of this entity and continue deleting other entities in the target_entities
            if not delete_all_entities and entity_id not in existing_entities:
                logger.error('Device %s not exist in iot igent' % entity_id)
                continue
            try:
                client.cb.delete_entity(entity_id=entity_id)
            except Exception as error_message:
                logger.error('Error when deleting entity %s from context broker. \nError message:\n%s' % (
                    entity_id, error_message))

    def delete_subscriptions(self, fiware_service_path,
                             subscriptions_to_delete: list,
                             delete_all_subscriptions: bool):
        fiware_header = FiwareHeader(service=self.fiware_service,
                                     service_path=fiware_service_path)
        config = HttpClientConfig(cb_url=self.cb_url, iota_url=self.iota_url, ql_url=self.ql_url)
        cb_request_session = requests.Session()
        token, in_sec = KeycloakPython().get_access_token()
        client = HttpClient(fiware_header=fiware_header, config=config,
                            session=cb_request_session,
                         headers={'Authorization': 'Bearer %s' % token})
        client.iota.headers.update({'Authorization': 'Bearer %s' % token})
        client.cb.headers.update({'Authorization': 'Bearer %s' % token})
        if delete_all_subscriptions:
            try:
                temp = client.cb.get_subscription_list()
            except Exception as error_message:
                temp = []
                logger.error(
                    'Error when getting all subscription list on context broker. \nError message:\n%s' % error_message)
            subscriptions_to_delete = [temp[i].id for i in range(len(temp))]
        logger.info("------Deleting subscriptions------")
        for i in subscriptions_to_delete:
            try:
                client.cb.delete_subscription(subscription_id=i)
            except:
                logger.info("------Could not delete subscription------")

#%%
if __name__ == '__main__':
    # Setting up logging
    logging.basicConfig(
        level='INFO',
        format='%(asctime)s %(name)s %(levelname)s: %(message)s')
    logger = logging.getLogger('filip-iot-example')

    # The constants:
    CB_URL = ''
    IOTA_URL = ''
    QL_URL = ''
    DEVICE_APIKEY = ''
    SERVICE_GROUP_APIKEY = ''
    SERVICE_GROUP_RESOURCE = ''
    CB_HOST = ''
    FIWARE_SERVICE = ''
    FIWARE_SERVICE_PATH = ''
    PROVISION_DEVICE_FILEPATH = 'provision_devices.json'
    PATCH_METADATA_FILEPATH = 'patch_metadata.json'
    # PROVISION_SUBSCRIPTIONS_FILEPATH = 'subscriptions.json'
    PROVISION_SUBSCRIPTIONS_FILEPATH = 'subscriptions.data'

    file = open('subscriptions.json')
    provision_subscriptions_json = json.load(file)
    sub = [Subscription(**provision_subscriptions_json[i]) for i in provision_subscriptions_json]
    # sub = [Subscription(**provision_subscriptions_json['SubscriptionWaterTempPrimary'])]
    with open(PROVISION_SUBSCRIPTIONS_FILEPATH, 'rb') as f:
        SUBSCRIPTION_LIST = pickle.load(f)
    subscription_ids = [SUBSCRIPTION_LIST[i].id for i in range(len(SUBSCRIPTION_LIST))]

    # file = open(PROVISION_DEVICE_FILEPATH)
    # provision_device_json = json.load(file)
    # provision_all_devices = True
    # if provision_all_devices:
    #     target_devices = provision_device_json.keys()

    TARGET_DEVICES = []
    TARGET_ENTITIES = []

#%%
    # Initiate object
    provision_object = AutoProvision(CB_URL, IOTA_URL, QL_URL, FIWARE_SERVICE)

#%%
    # Delete service group
    # provision_object.delete_service_groups(FIWARE_SERVICE_PATH, SERVICE_GROUP_APIKEY, SERVICE_GROUP_RESOURCE)

    # # Delete devices from the iot agent
    # provision_object.delete_devices_from_iota(FIWARE_SERVICE_PATH, delete_all_devices=True, target_devices=TARGET_DEVICES)

    # # Delete devices from the context broker
    # provision_object.delete_devices_from_cb(FIWARE_SERVICE_PATH, delete_all_entities=True)#, target_entities=TARGET_ENTITIES)

    # # Delete subscriptions
    # provision_object.delete_subscriptions(FIWARE_SERVICE_PATH, subscriptions_to_delete=subscription_ids, delete_all_subscriptions=True)

#%%
    # Provision a service group
    # provision_object.provision_service_group(FIWARE_SERVICE_PATH, SERVICE_GROUP_APIKEY, SERVICE_GROUP_RESOURCE, CB_HOST, autoprovision=False, explicitAttrs=True)

    # # Provision devices
    # provision_object.provision_devices(FIWARE_SERVICE_PATH, DEVICE_APIKEY, PROVISION_DEVICE_FILEPATH, provision_all_devices=True, target_devices=TARGET_DEVICES)

    # # Patch metadata
    # provision_object.patch_metadata(FIWARE_SERVICE_PATH, PATCH_METADATA_FILEPATH, patch_all_devices=True, target_devices=TARGET_DEVICES)

    # # Create subscriptions
    # # created_subscriptions, all_subscriptions = provision_object.create_database_subscriptions(FIWARE_SERVICE_PATH, backup_file_path=PROVISION_SUBSCRIPTIONS_FILEPATH, subscription_list=SUBSCRIPTION_LIST)
    # created_subscriptions, all_subscriptions = provision_object.create_database_subscriptions(FIWARE_SERVICE_PATH, subscription_list=sub, backup_file_path=PROVISION_SUBSCRIPTIONS_FILEPATH, )
