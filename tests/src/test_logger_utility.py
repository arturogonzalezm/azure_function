import logging
import pytest
from unittest.mock import patch
from src.logger_utility import LoggerUtility


@patch('logging.basicConfig')
def should_configure_logger_when_not_configured_yet(mock_basicConfig):
    LoggerUtility._configured = False
    LoggerUtility.configure_logger()
    mock_basicConfig.assert_called_once_with(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@patch('logging.basicConfig')
def should_not_configure_logger_when_already_configured(mock_basicConfig):
    LoggerUtility._configured = True
    LoggerUtility.configure_logger()
    mock_basicConfig.assert_not_called()


@patch('logging.getLogger')
@patch.object(LoggerUtility, 'configure_logger')
def should_configure_and_retrieve_logger_when_get_logger_called(mock_configure_logger, mock_getLogger):
    LoggerUtility.get_logger('test')
    mock_configure_logger.assert_called_once()
    mock_getLogger.assert_called_once_with('test')


@patch('logging.getLogger')
@patch.object(LoggerUtility, 'configure_logger')
def should_not_configure_logger_when_get_logger_called_and_already_configured(mock_configure_logger, mock_getLogger):
    LoggerUtility._configured = True
    LoggerUtility.get_logger('test')
    mock_configure_logger.assert_not_called()
    mock_getLogger.assert_called_once_with('test')
