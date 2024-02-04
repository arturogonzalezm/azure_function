"""
This module provides a utility for configuring and retrieving loggers.
It ensures that each logger is configured to use a consistent format
and level across the application. This setup is particularly useful
for applications deployed in environments like Azure Functions,
where it can integrate with Azure's monitoring tools.
"""

import logging


class LoggerUtility:
    """
    A utility class for configuring and retrieving named loggers
    with a predefined logging format and level.
    """
    _configured = False

    @classmethod
    def configure_logger(cls):
        """
        Configure the logger to use the default settings. This method sets
        the basic configuration for the logging system, adjusting the log level
        and format. It is designed to work with Azure Functions, enabling
        integration with Application Insights and other monitoring tools.
        """
        if not cls._configured:
            logging.basicConfig(level=logging.INFO,
                                format='%(asctime)s - %(levelname)s - %(message)s')
            cls._configured = True

    @staticmethod
    def get_logger(name):
        """
        Retrieves a logger with the specified name. If the logging system
        has not been configured yet, it configures it with default settings.

        :param name: The name of the logger to retrieve.
        :return: A logger instance configured with a standard format.
        """
        LoggerUtility.configure_logger()
        return logging.getLogger(name)
