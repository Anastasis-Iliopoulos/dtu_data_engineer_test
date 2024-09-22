from azure.identity import DefaultAzureCredential
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.storage.models import VirtualNetworkRule
import traceback
import os

# Authentication using Azure Identity
credential = DefaultAzureCredential()

SUBSCRIPTION_ID = os.environ['data_engineer_test_subscription_id']
RESOURCE_GROUP = os.environ['data_engineer_test_resource_group']
VNET_NAME = os.environ['data_engineer_test_vnet_name']
SUBNET_NAME = os.environ['data_engineer_test_subnet_name']
STORAGE_ACCOUNT = os.environ['data_engineer_test_storage_account']
LOCATION = os.environ['data_engineer_test_location']

network_client = NetworkManagementClient(credential, SUBSCRIPTION_ID)

def add_storage_service_endpoint():
    try:
        # Get the subnet configuration
        subnet = network_client.subnets.get(RESOURCE_GROUP, VNET_NAME, SUBNET_NAME)
        
        # Add the Microsoft.Storage service endpoint to the existing list of service endpoints
        if not subnet.service_endpoints:
            subnet.service_endpoints = []
        
        subnet.service_endpoints.append({
            'service': 'Microsoft.Storage',
            'locations': [LOCATION]  # location is the region where your resources are located
        })
        
        # Update the subnet with the new service endpoint
        network_client.subnets.begin_create_or_update(
            RESOURCE_GROUP,
            VNET_NAME,
            SUBNET_NAME,
            subnet
        ).result()

        print(f"Microsoft.Storage endpoint added to subnet {SUBNET_NAME} in VNet {VNET_NAME}.")
    
    except Exception as e:
        error_message = traceback.format_exc()
        print(f"An error occurred while adding the service endpoint:")
        print(error_message)
        raise e


def add_VNet_to_settings():

    # Initialize StorageManagementClient and NetworkManagementClient
    storage_client = StorageManagementClient(credential, SUBSCRIPTION_ID)
    network_client = NetworkManagementClient(credential, SUBSCRIPTION_ID)

    # Get VNet and Subnet details
    vnet = network_client.virtual_networks.get(RESOURCE_GROUP, VNET_NAME)
    subnet = network_client.subnets.get(RESOURCE_GROUP, VNET_NAME, SUBNET_NAME)

    # Get the storage account
    storage_account = storage_client.storage_accounts.get_properties(RESOURCE_GROUP, STORAGE_ACCOUNT)

    # Get the existing network rules (if any)
    network_rule_set = storage_account.network_rule_set

    # Add the Virtual Network rule (if the rule set is None, initialize it)
    if network_rule_set is None:
        network_rule_set = {}

    vnet_rule = VirtualNetworkRule(virtual_network_resource_id=subnet.id, action="Allow")

    if network_rule_set.virtual_network_rules is None:
        network_rule_set.virtual_network_rules = [vnet_rule]
    else:
        network_rule_set.virtual_network_rules.append(vnet_rule)

    try:
        # Update the storage account with the new network rule
        storage_client.storage_accounts.update(
            RESOURCE_GROUP,
            STORAGE_ACCOUNT,
            {
                "network_rule_set": {
                    "virtual_network_rules": network_rule_set.virtual_network_rules,
                }
            }
        )
    except Exception as e:
        error_message = traceback.format_exc()
        print(f"An error occurred:")
        print(error_message)
        # Logging in production
        raise e

    print(f"VNet {VNET_NAME} added to {STORAGE_ACCOUNT}")