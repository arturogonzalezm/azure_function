import os
import json
import pytest
from unittest.mock import patch, MagicMock
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError, AzureError
from src.webeoc_blob import WebEOCBlobStorage


@patch('os.environ')
@patch('azure.storage.blob.BlobServiceClient.from_connection_string')
def test_init(mock_from_connection_string, mock_os_environ):
    mock_os_environ.__getitem__.return_value = 'connection_string'
    WebEOCBlobStorage()
    mock_from_connection_string.assert_called_once_with('connection_string', logging_enable=True)


@patch.object(WebEOCBlobStorage, 'logger')
def test_create_output_filename(mock_logger):
    blob_storage = WebEOCBlobStorage()
    filename = blob_storage.create_output_filename()
    assert filename.startswith('JUVARE001_PATIENT_')
    mock_logger.info.assert_called_once()


@patch.object(WebEOCBlobStorage, 'logger')
@patch('azure.storage.blob.BlobServiceClient.get_blob_client')
def test_ingest_to_blob_success(mock_get_blob_client, mock_logger):
    blob_storage = WebEOCBlobStorage()
    mock_blob_client = MagicMock()
    mock_get_blob_client.return_value = mock_blob_client
    blob_storage.ingest_to_blob('data')
    mock_blob_client.upload_blob.assert_called_once_with('data')


@patch.object(WebEOCBlobStorage, 'logger')
@patch('azure.storage.blob.BlobServiceClient.get_blob_client')
def test_ingest_to_blob_failure_no_data(mock_get_blob_client, mock_logger):
    blob_storage = WebEOCBlobStorage()
    with pytest.raises(ValueError):
        blob_storage.ingest_to_blob(None)


@patch.object(WebEOCBlobStorage, 'logger')
@patch('azure.storage.blob.BlobServiceClient.get_blob_client')
def test_ingest_to_blob_failure_resource_exists(mock_get_blob_client, mock_logger):
    blob_storage = WebEOCBlobStorage()
    mock_blob_client = MagicMock()
    mock_blob_client.upload_blob.side_effect = ResourceExistsError('error')
    mock_get_blob_client.return_value = mock_blob_client
    with pytest.raises(ResourceExistsError):
        blob_storage.ingest_to_blob('data')


@patch.object(WebEOCBlobStorage, 'logger')
@patch('azure.storage.blob.BlobServiceClient.get_blob_client')
def test_write_logs_to_blob_success(mock_get_blob_client, mock_logger):
    blob_storage = WebEOCBlobStorage()
    mock_blob_client = MagicMock()
    mock_get_blob_client.return_value = mock_blob_client
    blob_storage.write_logs_to_blob('start_time', 'end_time', 'duration', 'status', 'records_pulled', 'log_level',
                                    'log_message')
    mock_blob_client.upload_blob.assert_called_once()


@patch.object(WebEOCBlobStorage, 'logger')
@patch('azure.storage.blob.BlobServiceClient.get_blob_client')
def test_write_logs_to_blob_failure(mock_get_blob_client, mock_logger):
    blob_storage = WebEOCBlobStorage()
    mock_blob_client = MagicMock()
    mock_blob_client.upload_blob.side_effect = Exception('error')
    mock_get_blob_client.return_value = mock_blob_client
    with pytest.raises(Exception):
        blob_storage.write_logs_to_blob('start_time', 'end_time', 'duration', 'status', 'records_pulled', 'log_level',
                                        'log_message')
