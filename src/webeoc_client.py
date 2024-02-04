import os
import json
import logging
import requests

from requests.exceptions import RequestException

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from src.logger_utility import LoggerUtility

"""
Explains the purpose of the WebEOCClient class.
"""


class WebEOCClient:
    """
    A client for pulling data from the WebEOC API.
    param: environment: The deployment environment.
    return: None
    """

    def __init__(self, environment):
        """
        Initializes the WebEOCClient.
        param: environment: The deployment environment.
        return: None
        """
        self.environment = environment  # Initialize the environment attribute
        self.logger = LoggerUtility.get_logger(__name__)
        self.api_session = requests.Session()
        self.base_uri = self.get_base_uri()
        self.authenticate()

    credential = None  # Class-level credential caching

    @classmethod
    def get_credential(cls):
        """
        Retrieves the Azure credential.
        param: None
        return: The Azure credential.
        """
        if cls.credential is None:
            try:
                cls.credential = DefaultAzureCredential()
                logging.info("Azure Credential acquired successfully")
            except Exception as e:
                logging.error("Failed to acquire Azure Credential %s", e)
                raise
        return cls.credential

    def get_secret(self, secret_name):
        """
        Retrieves a secret from Azure Key Vault.
        param: secret_name: The name of the secret to retrieve.
        return: The secret.
        """
        vault_url = os.environ['AZURE_KEYVAULT_URL']
        credential = WebEOCClient.get_credential()
        secret_client = SecretClient(vault_url=vault_url, credential=credential)
        try:
            secret = secret_client.get_secret(secret_name)
            self.logger.info("Secret '%s' retrieved successfully", secret_name)
            return secret
        except Exception as e:
            self.logger.error("Failed to retrieve secret '%s' %s", secret_name, e)
            raise

    def get_password(self):
        """
        Returns the password based on the deployment environment.
        param: None
        return: The password.
        """
        secret_name = f"{self.environment}-pwd-secret"
        return self.get_secret(secret_name).value

    def get_username(self):
        """
        Returns the username based on the deployment environment.
        param: None
        return: The username.
        """
        secret_name = f"{self.environment}-username-secret"
        return self.get_secret(secret_name).value

    def get_position(self):
        """
        Returns the password based on the deployment environment.
        param: None
        return: The password.
        """
        if self.environment == "uat":
            return 'API_Position'
        return 'API_Position'

    def get_base_uri(self):
        """
        Returns the base URI based on the deployment environment.
        param: None
        return: The base URI.
        """
        secret_name = f"{self.environment}-url-secret"
        return self.get_secret(secret_name).value

    def get_webeoc_incident(self):
        """
        Returns the WebEOC incident name based on the deployment environment.
        param: None
        return: The WebEOC incident name.
        """
        return "QRM Data Test" if self.environment == "uat" else "LIVE PaTCH Operations"

    def get_webeoc_board(self):
        """
        Returns the WebEOC board name based on the deployment environment.
        param: None
        return: The WebEOC board name.
        """
        if self.environment == "uat":
            return 'Patient Transport'
        return 'Patient Transport'

    def get_webeoc_display(self):
        """
        Returns the WebEOC display name based on the deployment environment.
        param: None
        return: The WebEOC display name.
        """
        if self.environment == "uat":
            return 'API Power BI Dashboard'
        return 'API Power BI Dashboard'

    def authenticate(self):
        """
        Authenticates the session with the API.
        param: None
        return: None
        """
        headers = {"Content-Type": "application/json"}
        body = {"username": self.get_username(),
                "password": self.get_password(),
                "position": self.get_position(),
                "incident": self.get_webeoc_incident()
                }
        auth_url = f"{self.base_uri}/sessions"

        try:
            self.logger.debug("Sending authentication request to %s with body %s", auth_url, body)
            auth_response = self.api_session.post(auth_url, headers=headers, data=json.dumps(body))
            auth_response.raise_for_status()
            self.logger.info("Successfully authenticated to WebEOC API")
        except RequestException as e:
            self.logger.error("Authentication request failed for %s %s", auth_url, e, exc_info=True)
            raise
        except json.JSONDecodeError as e:
            self.logger.error("Invalid JSON in response from %s %s", auth_url, e, exc_info=True)
            raise
        except Exception as e:
            self.logger.error("Unexpected error during authentication to %s %s", auth_url, e, exc_info=True)
            raise

    def pull_data(self):
        """
        Pulls data from the API.
        param: None
        return: The data from the API.
        """
        url = f"{self.base_uri}/board/{self.get_webeoc_board()}/display/{self.get_webeoc_display()}"
        try:
            self.logger.info("Starting data pull from URL %s", url)
            data_response = self.api_session.get(url)
            data_response.raise_for_status()
            return data_response.json()
        except RequestException as e:
            self.logger.error("Error during data pull from %s %s", url, e, exc_info=True)
            raise
        except json.JSONDecodeError as e:
            self.logger.error("Invalid JSON in response from %s %s", url, e, exc_info=True)
            raise
        except Exception as e:
            self.logger.error("Unexpected error during data pull from %s %s", url, e, exc_info=True)
            raise
