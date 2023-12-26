import os
import BlobDetails
from azure.data.tables import TableClient,TableServiceClient,UpdateMode
from azure.core.exceptions import ResourceExistsError,HttpResponseError
from typing_extensions import TypedDict
import logging


class Checkpoint:
    def __init__(self,connection_string):
        self.connection_string = connection_string
        self.table_name = "checkpoints"
        # self.PartitionKey = partitionKey
        # self.RowKey = rowKey
        # self.CheckpointIndex = index

    def entityMethod(self,partitionKey,rowKey,index):
        return {
            "PartitionKey" : partitionKey,
            "RowKey" : rowKey,
            "CheckpointIndex" : index
        }


    def put_checkpoint(self,entityObj):
        with TableClient.from_connection_string(self.connection_string,self.table_name) as table_client:
            try:
                table_client.create_table()
            except HttpResponseError:
                logging.error("Table already exists")
            try:
                table_client.create_entity(entity=entityObj)
            except ResourceExistsError:
                table_client.update_entity(mode=UpdateMode.REPLACE,entity=entityObj)
    
    def get_checkpoint(self,blob_details):
        with TableClient.from_connection_string(self.connection_string,self.table_name) as table_client:        
            try:
                result = table_client.get_entity(blob_details.get_partition_key(), blob_details.get_row_key())
                checkpoint = self.entityMethod(result['PartitionKey'],result['RowKey'],result['CheckpointIndex'])
            except:
                checkpoint = self.entityMethod(blob_details.get_partition_key(),blob_details.get_row_key(),1)

            if checkpoint['CheckpointIndex'] == 0:
                checkpoint['CheckpointIndex'] = 1

            return checkpoint


