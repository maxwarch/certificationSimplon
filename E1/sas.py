import datetime
import errno
import os
from azure.storage.blob import (
    BlobServiceClient,
)
from dotenv import load_dotenv

load_dotenv()

def download_blob_to_file(blob_service_client: BlobServiceClient, container_name: str, file: str, dest: str = 'data'):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dest = dir_path + '/' + dest
    try:
        os.makedirs(dest)
    except OSError as e:
        if e.errno != errno.EEXIST:  # Ignorer l'erreur si le répertoire existe déjà
            raise
        
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file)

    with open(file=f"{dest}/{os.path.basename(file)}", mode="wb") as sample_blob:
        download_stream = blob_client.download_blob()
        sample_blob.write(download_stream.readall())
        
if __name__ == '__main__':
    account_url = os.getenv("DATA_URL")
    account_key = os.getenv("KEY")

    blob_service_client = BlobServiceClient(account_url, credential=account_key)    
    blob_client = blob_service_client.get_blob_client(container='data', blob='product_eval/test-00001-of-00003.parquet')

    download_blob_to_file(blob_service_client, 'data', 'product_eval/test-00001-of-00003.parquet')
