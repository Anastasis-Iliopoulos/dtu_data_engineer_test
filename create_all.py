from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import ResourceManagementClient
import traceback
import os

SUBSCRIPTION_ID = os.environ['data_engineer_test_subscription_id']
RESOURCE_GROUP = os.environ['data_engineer_test_resource_group']
STORAGE_ACCOUNT = os.environ['data_engineer_test_storage_account']
LOCATION = os.environ['data_engineer_test_location']
VNET_NAME = os.environ['data_engineer_test_vnet_name']
SUBNET_NAME = os.environ['data_engineer_test_subnet_name']
VM_NAME = os.environ['data_engineer_test_vm_name']
NIC_NAME = os.environ['data_engineer_test_nic_name']
IP_CONFIG_NAME = os.environ['data_engineer_test_ip_config_name']
IPNAME = os.environ['data_engineer_test_ip_name']
OS_PROFILE_ADMIN_USERNAME = os.environ['data_engineer_test_os_profile_admin_username']
OS_PROFILE_ADMIN_PASSWORD = os.environ['data_engineer_test_os_profile_admin_password']
NSG_NAME = os.environ['data_engineer_test_nsg_name']

credentials = DefaultAzureCredential()

resource_client = ResourceManagementClient(credentials, SUBSCRIPTION_ID)
network_client = NetworkManagementClient(credentials, SUBSCRIPTION_ID)
compute_client = ComputeManagementClient(credentials, SUBSCRIPTION_ID)

def create_vnet(location, resource_group_name, vnet_name):
    try:
        network_client.virtual_networks.begin_create_or_update(
            resource_group_name, 
            vnet_name, 
            {
                "location": location,
                "address_space": {"address_prefixes": ["10.0.0.0/16"]},
            }
        ).result()
        print(f"VNet {vnet_name} created successfully.")
    except Exception as e:
        error_message = traceback.format_exc()
        print(f"An error occurred:")
        print(error_message)
        # Logging in production
        raise e

def create_nsg(resource_group_name, nsg_name, location):
    nsg = None
    try:
        nsg = network_client.network_security_groups.begin_create_or_update(
            resource_group_name,
            nsg_name,
            {
                "location": location,
                "security_rules": [
                    {
                        "name": "AllowSSH",
                        "properties": {
                            "Access": "Allow",
                            "Priority": 3000,
                            "protocol": "Tcp",
                            "Direction": "Inbound",
                            "SourcePortRange": "*",
                            "DestinationAddressPrefix": "*",
                            "SourceAddressPrefix": "*",
                            "DestinationPortRange": "22",
                        },
                    }
                ],
            }
        ).result()
        print(f"NSG {nsg_name} created successfully.")
    except Exception as e:
        error_message = traceback.format_exc()
        print(f"An error occurred while creating NSG:")
        print(error_message)
        # Logging in production
        raise e
    return nsg.id if nsg is not None else None

def create_subnet(resource_group_name, vnet_name, subnet_name, nsg_id):
    try:
        network_client.subnets.begin_create_or_update(
            resource_group_name, 
            vnet_name, 
            subnet_name, 
            {
                "address_prefix": "10.0.0.0/24",
                "network_security_group": {
                    "id": nsg_id
                }
            }
        ).result()
        print(f"Subnet {subnet_name} created successfully.")
    except Exception as e:
        error_message = traceback.format_exc()
        print(f"An error occurred:")
        print(error_message)
        # Logging in production
        raise e

def create_public_ip(resource_group_name, location, ip_name):
    public_ip = None
    try:
        public_ip = network_client.public_ip_addresses.begin_create_or_update(
            resource_group_name,
            ip_name,
            {
                "location": location,
                "public_ip_allocation_method": "Dynamic", # or static
            }
        ).result()
        print(f"Public IP {ip_name} created successfully.")
    except Exception as e:
        error_message = traceback.format_exc()
        print(f"An error occurred while creating Public IP:")
        print(error_message)
        # Logging in production
        raise e
    return public_ip.id if public_ip is not None else None

def create_nic(resource_group_name, vnet_name, subnet_name, location, ip_config_name, nic_name, public_ip_id):
    nic = None
    try:
        nic = network_client.network_interfaces.begin_create_or_update(
            resource_group_name, 
            nic_name, 
            {
                "location": location,
                "ip_configurations": [
                    {
                        "name": ip_config_name,
                        "subnet": {
                            "id": network_client.subnets.get(
                                resource_group_name, vnet_name, subnet_name
                            ).id
                        },
                        "public_ip_address": {
                            "id": public_ip_id
                        },
                    }
                ],
            }
        ).result()
        print(f"NIC {nic_name} created successfully.")
    except Exception as e:
        error_message = traceback.format_exc()
        print(f"An error occurred:")
        print(error_message)
        # Logging in production
        raise e
    return nic.id if nic is not None else None

def create_vm(vm_name, admin_username, admin_password, resource_group_name, nic_id, location):
    try:
        compute_client.virtual_machines.begin_create_or_update(
            resource_group_name, 
            vm_name, 
            {
                "location": location,
                "hardware_profile": {"vm_size": "Standard_DS1_v2"},
                "storage_profile": {
                    "image_reference": {
                        "publisher": "Canonical",
                        "offer": "UbuntuServer",
                        "sku": "18.04-LTS",
                        "version": "latest",
                    }
                },
                "os_profile": {
                    "computer_name": vm_name,
                    "admin_username": admin_username,
                    "admin_password": admin_password,
                },
                "network_profile": {
                    "network_interfaces": [{"id": nic_id}],
                },
            }
        ).result()
        print(f"VM {vm_name} created successfully.")
    except Exception as e:
        error_message = traceback.format_exc()
        print(f"An error occurred:")
        print(error_message)
        # Logging in production
        raise e
    
if __name__ == "__main__":
    create_vnet(LOCATION, RESOURCE_GROUP, VNET_NAME)
    nsg_id = create_nsg(RESOURCE_GROUP, NSG_NAME, LOCATION)
    create_subnet(RESOURCE_GROUP, VNET_NAME, SUBNET_NAME, nsg_id)
    ip_id = create_public_ip(RESOURCE_GROUP, LOCATION, IPNAME)
    nic_id = create_nic(RESOURCE_GROUP, VNET_NAME, SUBNET_NAME, LOCATION, IP_CONFIG_NAME, NIC_NAME, ip_id)
    create_vm(VM_NAME, OS_PROFILE_ADMIN_USERNAME, OS_PROFILE_ADMIN_PASSWORD, RESOURCE_GROUP, nic_id, LOCATION)
    print("All resources created successfully.")