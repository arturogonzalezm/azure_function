import os
import pytest
from unittest.mock import patch, MagicMock
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from requests.exceptions import RequestException
from src.webeoc_client import WebEOCClient


@patch('os.environ')
@patch('azure.identity.DefaultAzureCredential')
@patch('azure.keyvault.secrets.SecretClient')
def test_init(mock_secret_client, mock_default_credential, mock_os_environ):
    mock_os_environ.__getitem__.return_value = 'connection_string'
    WebEOCClient('uat')
    mock_default_credential.assert_called_once()


@patch.object(WebEOCClient, 'get_secret')
def test_get_password(mock_get_secret):
    client = WebEOCClient('uat')
    client.get_password()
    mock_get_secret.assert_called_once_with('uat-pwd-secret')


@patch.object(WebEOCClient, 'get_secret')
def test_get_username(mock_get_secret):
    client = WebEOCClient('uat')
    client.get_username()
    mock_get_secret.assert_called_once_with('uat-username-secret')


@patch.object(WebEOCClient, 'get_secret')
def test_get_base_uri(mock_get_secret):
    client = WebEOCClient('uat')
    client.get_base_uri()
    mock_get_secret.assert_called_once_with('uat-url-secret')


@patch('requests.Session.post')
def test_authenticate_success(mock_post):
    client = WebEOCClient('uat')
    mock_post.return_value.status_code = 200
    client.authenticate()


@patch('requests.Session.post')
def test_authenticate_failure(mock_post):
    client = WebEOCClient('uat')
    mock_post.return_value.status_code = 400
    with pytest.raises(RequestException):
        client.authenticate()


@patch('requests.Session.get')
def test_pull_data_success(mock_get):
    client = WebEOCClient('uat')
    mock_get.return_value.status_code = 200
    client.pull_data()


@patch('requests.Session.get')
def test_pull_data_failure(mock_get):
    client = WebEOCClient('uat')
    mock_get.return_value.status_code = 400
    with pytest.raises(RequestException):
        client.pull_data()
