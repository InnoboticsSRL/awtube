#!/usr/bin/env python3

"""
    Contains the config dict for the the loggers.
"""

import logging.config
from pythonjsonlogger import jsonlogger

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            # "format": "%(asctime)s %(levelname)s %(message)s",
            # "format": "[%(name)s %(clientip)-15s %(levelname)s %(message)s]",
            "format": "%(name)s %(levelname)s %(message)s",
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
        }
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "json",
        }
    },
    "loggers": {"": {"handlers": ["stdout"], "level": "ERROR"}},
}


# when imported it automatically configures your module logger
logging.config.dictConfig(LOGGING)