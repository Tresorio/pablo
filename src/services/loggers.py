import logging

def set_logger(logger: logging.Logger, level: int):
    """Configurates the given logger"""
    if len(logger.handlers) != 0: # check if logger already has handler
        return
    log_formatter = logging.Formatter(
    f'[{logger.name}][%(asctime)s] [%(levelname)-5.5s] %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)
    logger.setLevel(logging.DEBUG)

PLATFORM_LOGGER = logging.getLogger('Platform')
set_logger(PLATFORM_LOGGER, logging.DEBUG)

NAS_LOGGER = logging.getLogger('Nas')
set_logger(NAS_LOGGER, logging.DEBUG)
