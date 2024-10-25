#!/usr/bin/env python3

"""
    Config dict for loggers.
"""

import logging.config
from pythonjsonlogger import jsonlogger

# LEVEL = "DEBUG"
LEVEL = "ERROR"

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
    "loggers": {"": {"handlers": ["stdout"], "level": LEVEL}},
}


# when imported it automatically configures your module logger
logging.config.dictConfig(LOGGING)
