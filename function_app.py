import os
import datetime
import azure.functions as func
from src.logger_utility import LoggerUtility
from src.webeoc_client import WebEOCClient
from src.webeoc_blob import WebEOCBlobStorage

"""
This module defines an Azure Function that periodically pulls data from a source and uploads it to Azure Blob Storage.
The function is scheduled to run every minute and logs its progress and results.
"""

# Constants
DEFAULT_ENV = 'uat'
DEFAULT_LOG_LEVEL = 'INFO'
DEFAULT_LOG_MESSAGE = 'Data pulled and uploaded successfully'

app = func.FunctionApp()  # Initialize the Azure Function


@app.function_name(name="azure-function")  # Set the name of the function
@app.schedule(schedule="0 */1 * * * *", arg_name="mytimer", run_on_startup=True, use_monitor=True)  # Set the schedule
def test_function(mytimer: func.TimerRequest) -> None:
    """
    A test function for the Azure Function that pulls data and uploads it to Blob Storage.
    """
    deployment_env = os.getenv('DEPLOYMENT_ENV', DEFAULT_ENV)
    logger = LoggerUtility.get_logger(__name__)

    start_time = datetime.datetime.utcnow()
    end_time = start_time
    duration = 0
    status = "SUCCESS"
    records_pulled = 0
    log_level = DEFAULT_LOG_LEVEL
    log_message = DEFAULT_LOG_MESSAGE

    storage = WebEOCBlobStorage()

    try:
        logger.info("Scheduler started.")
        client = WebEOCClient(deployment_env)
        data = client.pull_data()
        end_time = datetime.datetime.utcnow()
        storage.ingest_to_blob(data)
        duration = (end_time - start_time).total_seconds()
        records_pulled = len(data) if isinstance(data, list) else 0
        if mytimer.past_due:
            logger.info("The timer is past due!")
    except Exception as e:
        logger.error("Error during process: %s", e)  # Corrected logging format
        status = "FAILED"
        log_message = f"Error during process: {e}"
        log_level = "ERROR"

    logger.info("Process completed")
    storage.write_logs_to_blob(start_time, end_time, duration, status, records_pulled, log_level, log_message)
