"""This module configures the loggers for the plugin"""

import logging
from src.config.paths import LOGS_PATH
from src.config.debug import BACKEND_DEBUG, NAS_DEBUG, PLATFORM_DEBUG


def set_logger(logger: logging.Logger) -> None:
    """Configure the given logger

    Args:
        logger: the logger to configure.

    Example:

        >>> logger = logging.getLogger('MyLogger')
        ... set_logger(logger)
    """
    for hdlr in logger.handlers:
        logger.removeHandler(hdlr)
        del hdlr
    log_formatter = logging.Formatter(
        '[%(name)s][%(filename)s:%(lineno)d][%(asctime)s][%(levelname)-5.5s]: %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)

    file_handler = logging.FileHandler(f'{LOGS_PATH}', mode='a')
    file_handler.setFormatter(log_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.setLevel(logging.ERROR)


PLATFORM_LOGGER = logging.getLogger('Platform')
set_logger(PLATFORM_LOGGER)
if PLATFORM_DEBUG is True:
    PLATFORM_LOGGER.setLevel(logging.DEBUG)

NAS_LOGGER = logging.getLogger('Nas')
set_logger(NAS_LOGGER)
if NAS_DEBUG is True:
    NAS_LOGGER.setLevel(logging.DEBUG)

BACKEND_LOGGER = logging.getLogger('Backend')
set_logger(BACKEND_LOGGER)
if BACKEND_DEBUG is True:
    BACKEND_LOGGER.setLevel(logging.DEBUG)
