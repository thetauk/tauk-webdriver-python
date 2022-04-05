"""Helper package to facilitate reporting for webdriver-based tests on Tauk"""
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

__project__ = "tauk"
__version__ = "develop"
__author__ = "Nathan Krishnan"
__url__ = "https://github.com/thetauk/tauk-webdriver-python"
__platforms__ = "ALL"
__classifiers__ = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
__requires__ = ["requests", "Appium-Python-Client", "selenium"]

__extra_requires__ = {
}


def _init_logger():
    log_filename = os.path.join(Path.home(), '.tauk', 'logs', 'tauk-webdriver.log')
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)
    os.environ['TAUK_HOME'] = os.path.join(Path.home(), '.tauk')

    tauk_logger = logging.getLogger('tauk')
    log_level = os.getenv('TAUK_LOG_LEVEL', 'INFO')
    if log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        log_level = 'INFO'
    tauk_logger.setLevel(logging.getLevelName(log_level))
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z')

    file_handler = RotatingFileHandler(log_filename, maxBytes=10000000, backupCount=3)
    file_handler.setFormatter(formatter)
    tauk_logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    # stream_handler.setLevel(logging.ERROR)
    stream_handler.setFormatter(formatter)
    tauk_logger.addHandler(stream_handler)


_init_logger()
