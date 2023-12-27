import os
import azure.functions as func
from azure.storage.blob import BlobServiceClient, ContainerClient
import logging
import re

import BlobDetails,Checkpoint,nsg_Sender

# app = func.FunctionApp()
# container_name = ""
connection_string = os.environ["AzureWebJobsStorage"]

# @app.blob_trigger(arg_name="myblob", path="insights-logs-networksecuritygroupflowevent",connection="blobconnectionstring") 
def main(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob"
                f"Name: {myblob.name}"
                f"Blob Size: {myblob.length} bytes")
    
    blobDetails = BlobDetails.BlobDetails(str(myblob.name))
    checkpointDB = Checkpoint.Checkpoint(connection_string)
    checkpoint = checkpointDB.get_checkpoint(blobDetails)

    container_name, blob_name = myblob.name.split('/', 1)

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name,blob=blob_name)
    block_list = blob_client.get_block_list()
    starting_byte = sum(item['size'] for index, item in enumerate(block_list[0]) if index < checkpoint['CheckpointIndex'])
    ending_byte = sum(item['size'] for index, item in enumerate(block_list[0]) if index < len(block_list[0]) - 1)
    data_length = ending_byte - starting_byte

    logging.info(f"Blob: {blobDetails}, starting byte: {starting_byte}, ending byte: {ending_byte}, number of bytes: {data_length}")
    
    attributes = {
        'BlobPath': f"{myblob.name}",
        'connection': connection_string
    }

    blob_data=blob_client.download_blob(offset=(starting_byte),length=data_length)
    blob_content = blob_data.readall()
    
    if blob_content and blob_content[0] == 0x2C:
        blob_content = blob_content[1:]

    with open("/home/anesh-zt668/Documents/NSG_PYTHON_VS/output.json", 'wb') as file:
        file.write(blob_content)
    nsg_Sender.processData(blob_content)
    checkpoint['CheckpointIndex'] = (len(block_list[0])-1)
    checkpointDB.put_checkpoint(checkpoint)
    # nsg_source_data_account = os.environ["nsgSourceDataAccount"]
    # blob_container_name = os.environ["blobContainerName"]
    # blob_details = BlobDetails(myblob.name)
