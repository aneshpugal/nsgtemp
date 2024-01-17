import logging,os
import azure.functions as func
from azure.storage.blob import BlobServiceClient
from azure.data.tables import TableServiceClient
from logger import configure_logging
from BlobForwarder import BlobDetails,Checkpoint,blob_Sender
from datetime import datetime

blob_connection_string = os.environ["blobconnectionstring"]

initialized = False

def initialize_app():
    global initialized
    if not initialized:
        with TableServiceClient.from_connection_string(blob_connection_string) as table_service_client:
            table_service_client.create_table_if_not_exists(table_name="Checkpoints")
        initialized = True

try:
    initialize_app()
except Exception as e:
    print(str(e))

try:
    timestamp = os.environ["CollectionTime"]
except Exception as e:
    print(str(e))


# timestamp = datetime.fromisoformat(timestamp_str)

def main(myblob: func.InputStream,context: func.Context):
    try:
        logging.info(f"Python blob trigger function processed blob Name: {myblob.name}")
        current_time_str = myblob.blob_properties["LastModified"]
        current_time = datetime.fromisoformat(current_time_str)
        if current_time < int(timestamp):
            return
        azure_logger = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
        azure_logger.setLevel(logging.WARNING)
        trigger_id = context.invocation_id
        logger = configure_logging(trigger_id)
        blobDetails = BlobDetails.BlobDetails(str(myblob.name))
        serviceName = blobDetails.serviceName
        
        checkpointDB = Checkpoint.Checkpoint(blob_connection_string)
        checkpoint = checkpointDB.get_checkpoint(blobDetails)
        logger.info("Checkpoint : " + str(checkpoint))
        container_name, blob_name = myblob.name.split('/', 1)

        blob_service_client = BlobServiceClient.from_connection_string(blob_connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name,blob=blob_name)
        block_list = blob_client.get_block_list()
        starting_byte = sum(item['size'] for index, item in enumerate(block_list[0]) if index < checkpoint['CheckpointIndex'])
        ending_byte = sum(item['size'] for index, item in enumerate(block_list[0]) if index < len(block_list[0]) - 1)
        data_length = ending_byte - starting_byte

        logger.info(f"Blob: {blobDetails}, starting byte: {starting_byte}, ending byte: {ending_byte}, number of bytes: {data_length}")
        blob_data=blob_client.download_blob(offset=(starting_byte),length=data_length)
        blob_content = blob_data.readall()
        
        if blob_content and blob_content[0] == 0x2C:
            blob_content = blob_content[1:]
        blob_Sender.processData(blob_content,serviceName)
        checkpoint['CheckpointIndex'] = (len(block_list[0])-1)
        checkpointDB.put_checkpoint(checkpoint)
        return
    except Exception as e:
        print(str(e))