import os
import datetime
import pytest
from unittest.mock import patch, MagicMock
from azure.functions import TimerRequest
from src.logger_utility import LoggerUtility
from src.webeoc_client import WebEOCClient
from src.webeoc_blob import WebEOCBlobStorage


@patch('os.getenv')
@patch.object(LoggerUtility, 'get_logger')
@patch.object(WebEOCBlobStorage, '__init__')
def should_initialize_with_default_values_when_no_environment_variables(mock_storage_init, mock_get_logger,
                                                                        mock_getenv):
    mock_getenv.return_value = 'uat'
    mock_storage_init.return_value = None
    mock_get_logger.return_value = MagicMock()
    from function_app import test_function
    test_function(TimerRequest(is_past_due=False))
    mock_get_logger.assert_called_once_with('__main__')
    mock_storage_init.assert_called_once()


@patch('os.getenv')
@patch.object(LoggerUtility, 'get_logger')
@patch.object(WebEOCBlobStorage, '__init__')
def should_log_error_when_exception_occurs(mock_storage_init, mock_get_logger, mock_getenv):
    mock_getenv.return_value = 'uat'
    mock_storage_init.side_effect = Exception('error')
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger
    from function_app import test_function
    with pytest.raises(Exception):
        test_function(TimerRequest(is_past_due=False))
    mock_logger.error.assert_called_once()


@patch('os.getenv')
@patch.object(LoggerUtility, 'get_logger')
@patch.object(WebEOCBlobStorage, '__init__')
@patch.object(WebEOCBlobStorage, 'ingest_to_blob')
@patch.object(WebEOCBlobStorage, 'write_logs_to_blob')
@patch.object(WebEOCClient, 'pull_data')
def should_pull_data_and_upload_to_blob_when_no_errors(mock_pull_data, mock_write_logs_to_blob, mock_ingest_to_blob,
                                                       mock_storage_init, mock_get_logger, mock_getenv):
    mock_getenv.return_value = 'uat'
    mock_storage_init.return_value = None
    mock_get_logger.return_value = MagicMock()
    mock_pull_data.return_value = ['data']
    from function_app import test_function
    test_function(TimerRequest(is_past_due=False))
    mock_ingest_to_blob.assert_called_once_with(['data'])
    mock_write_logs_to_blob.assert_called_once()
