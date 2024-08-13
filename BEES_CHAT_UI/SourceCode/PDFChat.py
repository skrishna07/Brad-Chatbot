import os
from azure.storage.blob import BlobServiceClient
from . import AzureCosmosVectorStoreContianer
from . import Download_AzureBlobFiles
from urllib.parse import urlparse
from . import Extract_PDF
from django.http import JsonResponse
from urllib.parse import unquote
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

def fileUpload(files):
    try:
        # Azure Blob Storage account credentials
        connection_string = os.getenv('Azure_Blob_ConnectionString')
        container_name = os.getenv('Azure_Blob_ContainerName')

        # Create a BlobServiceClient object using the connection string

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        # Create a client to interact with the container

        container_client = blob_service_client.get_container_client(container_name)

        # Get the files from the request

        for file in files:
            blob_client = container_client.get_blob_client(file.name)
            blob_client.upload_blob(file, overwrite=True)

            # Get the URL of the uploaded blob
            blob_url = blob_client.url
            # Extract the file name from the URL
            parsed_url = urlparse(blob_url)
            filename = os.path.basename(parsed_url.path)
            filename = unquote(filename)
            # Call the function to download and process the file
            filepath, file_exist = Download_AzureBlobFiles.Download_File(filename)

            if file_exist:
                # Process the file further as needed
                # (e.g., create vectors/chunks based on the file content)
                # You can call additional processing functions here
                Pdf_content = Extract_PDF.process_documents(filepath, "General", '1')
                if Pdf_content[0].page_content == '':
                    error_details = f'Data is empty -1'
                    continue
                else:
                    print("pdf_content", Pdf_content)
                    AzureCosmosVectorStoreContianer.Load_ChunkData(Pdf_content)
            else:
                return JsonResponse(
                    {'message': f'File could not be downloaded for processing: {file.name}', 'status': 'error'},
                    status=500)

        # Return a JSON response indicating success
        return JsonResponse({'message': 'File uploaded successfully!', 'status': 'success'})
    except Exception as e:
        return JsonResponse({'message': f"An error occurred: {str(e)}", 'status': 'error'}, status=500)