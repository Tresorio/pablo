import logging
from src.config.paths import LOGS_PATH

def set_logger(logger: logging.Logger, level: int):
    """Configurates the given logger"""
    for hdlr in logger.handlers:
        logger.removeHandler(hdlr)
        del hdlr
    log_formatter = logging.Formatter(
    '[%(name)s][%(filename)s:%(lineno)d][%(asctime)s][%(levelname)-5.5s]: %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)

    file_handler = logging.FileHandler(f'{LOGS_PATH}', mode='w')
    file_handler.setFormatter(log_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.setLevel(logging.DEBUG)

PLATFORM_LOGGER = logging.getLogger('Platform')
set_logger(PLATFORM_LOGGER, logging.DEBUG)

NAS_LOGGER = logging.getLogger('Nas')
set_logger(NAS_LOGGER, logging.DEBUG)

BACKEND_LOGGER = logging.getLogger('Backend')
set_logger(BACKEND_LOGGER, logging.DEBUG)
