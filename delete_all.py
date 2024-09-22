import os
import traceback
from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient

# configuration
subscription_id = os.environ['data_engineer_test_subscription_id']
resource_group_name = os.environ['data_engineer_test_resource_group']
vnet_name = os.environ['data_engineer_test_vnet_name']
subnet_name = os.environ['data_engineer_test_subnet_name']
vm_name = os.environ['data_engineer_test_vm_name']
nic_name = os.environ['data_engineer_test_nic_name']
nsg_name = os.environ['data_engineer_test_nsg_name']
location = os.environ['data_engineer_test_location']

credential = DefaultAzureCredential()
network_client = NetworkManagementClient(credential, subscription_id)
compute_client = ComputeManagementClient(credential, subscription_id)

def delete_vm(resource_group_name, vm_name):
    try:
        compute_client.virtual_machines.begin_delete(resource_group_name, vm_name).result()
        print(f"VM {vm_name} deleted successfully.")
    except Exception as e:
        error_message = traceback.format_exc()
        print(f"An error occurred:")
        print(error_message)
        # Logging in production
        raise e

def delete_nic(resource_group_name, nic_name):
    try:
        network_client.network_interfaces.begin_delete(resource_group_name, nic_name).result()
        print(f"NIC {nic_name} deleted successfully.")
    except Exception as e:
        error_message = traceback.format_exc()
        print(f"An error occurred:")
        print(error_message)
        # Logging in production
        raise e

def delete_subnet(resource_group_name, vnet_name, subnet_name):
    try:
        network_client.subnets.begin_delete(resource_group_name, vnet_name, subnet_name).result()
        print(f"Subnet {subnet_name} deleted successfully.")
    except Exception as e:
        error_message = traceback.format_exc()
        print(f"An error occurred:")
        print(error_message)
        # Logging in production
        raise e

def delete_nsg(resource_group_name, nsg_name):
    try:
        network_client.network_security_groups.begin_delete(resource_group_name, nsg_name).result()
        print(f"NSG {nsg_name} deleted successfully.")
    except Exception as e:
        error_message = traceback.format_exc()
        print(f"An error occurred:")
        print(error_message)
        # Logging in production
        raise e

def delete_vnet(resource_group_name, vnet_name):
    try:
        network_client.virtual_networks.begin_delete(resource_group_name, vnet_name).result()
        print(f"VNet {vnet_name} deleted successfully.")
    except Exception as e:
        error_message = traceback.format_exc()
        print(f"An error occurred:")
        print(error_message)
        # Logging in production
        raise e

def delete_all_resources():
    try:
        delete_vm(resource_group_name, vm_name)
        delete_nic(resource_group_name, nic_name)
        delete_subnet(resource_group_name, vnet_name, subnet_name)
        delete_nsg(resource_group_name, nsg_name)
        delete_vnet(resource_group_name, vnet_name)
        
        print("All resources deleted successfully.")
    except Exception as e:
        error_message = traceback.format_exc()
        print(f"An error occurred:")
        print(error_message)
        # Logging in production
        raise e
