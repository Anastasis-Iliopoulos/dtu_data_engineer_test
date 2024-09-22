from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import pandas as pd
import os
import tempfile
import traceback

ACCOUNT_NAME = os.environ['data_engineer_test_storage_account']

credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(account_url=f"https://{ACCOUNT_NAME}.blob.core.windows.net", credential=credential)

def load_blob(container_name, blob_name, save_local_path=None):
    container_client = blob_service_client.get_container_client(container_name)
    if not container_client.exists():
        raise ValueError(f"Container '{container_name}' does not exist.")
        
    blob_client = container_client.get_blob_client(blob_name)
    if not blob_client.exists():
        raise ValueError(f"Blob '{blob_name}' does not exist in container '{container_name}'.")
    
    try:
        downloaded_object = blob_client.download_blob()
        data = downloaded_object.readall()
        
        if save_local_path is not None:
            with open(os.path.join(".", os.path.normpath(save_local_path)), "wb") as file:
                file.write(data)
            print(f"Blob downloaded to {os.path.join('.', save_local_path)}")
        
        with tempfile.TemporaryDirectory() as tmpdirname:
            temp_file_path = os.path.join(tmpdirname, 'temp_blob.csv')
            with open(temp_file_path, 'wb') as temp_file:
                temp_file.write(data)
            df = pd.read_csv(temp_file_path)
    except Exception as e:
        error_message = traceback.format_exc()
        print(f"An error occurred:")
        print(error_message)
        # Logging in production
        raise e
    return df

def aggregate_data(df):
    # SQL Equivalent:
    # SELECT Country, AVG(Rating) as average_rating FROM tourism_dataset 
    # GROUP BY Country;
    grouped_data = df.groupby('Country')['Rating'].mean().reset_index().rename(columns={'Rating':'average_rating'})
    return grouped_data

def aggregate_and_get_top(df, n_top):
    # SQL Equivalent:
    # SELECT Country, AVG(Rating) as average_rating FROM tourism_dataset 
    # GROUP BY Country;
    grouped_data = df.groupby('Country')['Rating'].mean().reset_index().rename(columns={'Rating':'average_rating'})

    # SQL Equivalent:
    # SELECT Country, AVG(Rating) as average_rating FROM tourism_dataset 
    # GROUP BY Country 
    # ORDER BY average_rating DESC LIMIT 3;
    top_3_countries = grouped_data.nlargest(n_top, 'average_rating')
    return top_3_countries

def write_to_csv(df, save_local_path):
    try:
        df.to_csv(os.path.join(".", os.path.normpath(save_local_path)), index=False)
    except Exception as e:
        error_message = traceback.format_exc()
        print(f"An error occurred:")
        print(error_message)
        # Logging in production
        raise e
    
    return os.path.join(".", os.path.normpath(save_local_path))

def upload_to_azure_storage(container_name, blob_name, local_file_path):
    container_client = blob_service_client.get_container_client(container_name)
    
    try:
        if not container_client.exists():
            container_client.create_container()
        else:
            print(f"Container '{container_name}' already exists.")
    except Exception as e:
        error_message = traceback.format_exc()
        print(f"An error occurred:")
        print(error_message)
        # Logging in production
        raise e

    blob_client = container_client.get_blob_client(blob_name)

    try:
        with open(local_file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        print("Blob uploaded succefully!")
    except Exception as e:
        error_message = traceback.format_exc()
        print(f"An error occurred:")
        print(error_message)
        # Logging in production
        raise e
    
if __name__ == "__main__":
    df = load_blob(container_name="raw", blob_name="tourism_dataset.csv", save_local_path=f"./tourism_dataset.csv")
    aggregated_df = aggregate_data(df)
    top_countries = aggregate_and_get_top(df, 3)
    filepath = write_to_csv(top_countries, "./Anastasios-Iliopoulos.csv")
    upload_to_azure_storage(container_name="anastasios-iliopoulos", blob_name="Anastasios-Iliopoulos/Anastasios-Iliopoulos.csv", local_file_path="./Anastasios-Iliopoulos.csv")