from azure.storage.blob import BlobServiceClient
from Utilities.Log import Logger
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
from dotenv import load_dotenv, find_dotenv
import os
from urllib.parse import unquote
load_dotenv(find_dotenv())
logger = Logger()


def download_blob_from_azure(container_name, blob_name, download_file_path, connection_string):
    try:
        # Create BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        # Create a BlobClient
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        # Check if the blob exists
        if not blob_client.exists():
            logger.log(f"Blob '{blob_name}' does not exist in container '{container_name}'", "Info")
            return
        # Download the blob to a local file
        with open(download_file_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())

        logger.log(f"Blob '{blob_name}' downloaded successfully to '{download_file_path}'.", "Info")
        return True

    except ResourceNotFoundError:
        logger.log(
            f"Resource not found: The specified blob '{blob_name}' or container '{container_name}' does not exist.",
            "Error")
        return False
    except HttpResponseError as e:
        logger.log(f"HTTP response error: {e}", "Error")
        raise

    except Exception as e:
        logger.log(f"An unexpected error occurred: {e}", "Error")
        raise


def Download_File(blob_name):
    try:
        connection_string = os.getenv('Azure_Blob_ConnectionString')
        container_name = os.getenv('Azure_Blob_ContainerName')
        current_dir = os.getcwd()
        download_file_path = os.path.join(current_dir, "Files", blob_name)

         # URL-encode the file name
        file_name = unquote(blob_name)
        # print("connection_string:" , connection_string)
        # print("container_name :" , container_name)
        # print("download_file_path :" , download_file_path)
        os.makedirs(os.path.dirname(download_file_path), exist_ok=True)
        file_exist = download_blob_from_azure(container_name, file_name, download_file_path, connection_string)
        return download_file_path, file_exist
    except Exception as e:
        error_details = logger.log(f"An error in downloading blob file: {e}", "Error")
        raise Exception(error_details)
