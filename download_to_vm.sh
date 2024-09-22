###### Locally ######

az login
az login --tenant xxxxxxxx
az account set --subscription "<subscription ID or name>"

az account clear
az config set core.enable_broker_on_windows=false
az login

ssh username@vm_public_ip

###### IN VM ######

curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
az login
az account set --subscription SUBSCRIPTION_ID

STORAGE_ACCOUNT_NAME='xxxxxxx'
ACCOUNT_KEY='xxxxxxx'

az storage blob download --account-name $STORAGE_ACCOUNT_NAME --account-key $ACCOUNT_KEY --container-name anastasios-iliopoulos --name Anastasios-Iliopoulos/Anastasios-Iliopoulos.csv --file ~/result-Anastasios.csv

exit