import os
import json

from datetime import datetime

import pytz

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError, AzureError
from azure.storage.blob import BlobServiceClient

from src.logger_utility import LoggerUtility

"""
Explain the purpose of the WebEOCBlobStorage class.
"""


class WebEOCBlobStorage:
    def __init__(self):
        """
        Initializes the WebEOCBlobStorage.
        :return: None
        :rtype: None
        :raises: None
        :param: None
        """
        self.logger = LoggerUtility.get_logger(__name__)
        self.connection_string = os.environ['AzureWebJobsStorage']
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string, logging_enable=True)
        self.container_name = "blob-container"
        self.blob_name = self.create_output_filename()

    def create_output_filename(self):
        """
        Generates and returns the output filename.
        :return: The output filename.
        :rtype: str
        :raises: None
        :param: None
        """
        timezone = pytz.timezone('Australia/Perth')
        local_time = datetime.now(timezone)
        build_number = "001"
        filename = f"JUVARE{build_number}_PATIENT_{local_time.strftime('%Y%m%d_%H%M%S')}_D.JSON"
        self.logger.info(f"Generated output filename: {filename}")
        return filename

    def ingest_to_blob(self, data):
        """
        Ingests the data to Azure Blob Storage.
        :param data: The data to ingest.
        :return: None
        """
        if not data:
            self.logger.error("No data provided for upload.")
            raise ValueError("No data to upload.")
        if not isinstance(data, str):
            data = json.dumps(data)
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=self.blob_name
            )
            self.logger.info("Starting upload of data to Azure Blob Storage %s", self.blob_name)
            blob_client.upload_blob(data)
            self.logger.info("Data successfully uploaded to Azure Blob Storage %s", self.blob_name)
        except ResourceExistsError as e:
            self.logger.error("Blob already exists and overwrite is set to False %s", e)
            raise
        except ResourceNotFoundError as e:
            self.logger.error("Specified container/blob does not exist %s", e)
            raise
        except AzureError as e:
            self.logger.error("Azure storage error occurred %s", e)
            raise
        except Exception as e:
            self.logger.error("Unexpected error during data upload %s", e, exc_info=True)
            raise

    def write_logs_to_blob(self, start_time, end_time, duration, status, records_pulled, log_level, log_message):
        """
        Writes the logs to Azure Blob Storage.
        :param start_time: The start time of the process.
        :param end_time: The end time of the process.
        :param duration: The duration of the process.
        :param status: The status of the process.
        :param records_pulled: The number of records pulled.
        :param log_level: The log level.
        :param log_message: The log message.
        :return: None
        """
        log_data = {
            "file_name": self.create_output_filename(),
            "start_time": start_time.strftime('%Y-%m-%d %H:%M:%S.%f %z'),
            "end_time": end_time.strftime('%Y-%m-%d %H:%M:%S.%f %z'),
            "duration": duration,
            "status": "SUCCESS" if status == "SUCCESS" else "FAILED",
            "records_pulled": records_pulled,
        }

        # Include log_level and log_message only for INFO or ERROR
        if log_level in ("INFO", "ERROR"):
            log_data["log_level"] = log_level
            log_data["log_message"] = log_message

        try:
            log_blob_name = f"api-observability-logs/log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            log_blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=log_blob_name
            )
            log_blob_client.upload_blob(json.dumps(log_data))
        except Exception as e:
            self.logger.error("Error uploading log to Azure Blob Storage %s", e)
            raise
