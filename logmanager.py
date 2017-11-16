#!/usr/bin/env python
import logging
from logging.config import fileConfig


class LogManager(object):
    def __init__(self):
        self.log_level = "INFO"
        fileConfig('logging_config.ini')

    @property
    def logger(self):
        return logging.getLogger()
