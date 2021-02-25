"""
Logger

Used by other modules to get a common logger
"""

import logging
from os import environ

LOG_LEVEL: str = environ.get("LOG_AT_LEVEL", "INFO")

# CRITICAL: 50
# ERROR: 40
# WARNING: 30
# INFO: 20
# DEBUG: 10
# NOTSET: 0


def get_logger(name):
    """Logger with formatting and such"""

    # create logger
    logger = logging.getLogger(name)

    log_level = LOG_LEVEL if LOG_LEVEL else logging.INFO

    logger.setLevel(log_level)

    if len(logger.handlers) == 0:
        # create console handler and set level to debug
        streamhandle = logging.StreamHandler()

        # create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # add formatter to streamhandle
        streamhandle.setFormatter(formatter)

        # add streamhandle to logger
        logger.addHandler(streamhandle)

        # dont double log to root logger
        logger.propagate = False

    return logger
