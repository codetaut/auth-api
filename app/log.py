import logging
import sys
import pathlib
import os

from app import config

logging.basicConfig(level=config.LOG_LEVEL)
LOG = logging.getLogger("app")
boto3_logger = logging.getLogger('botocore')
boto3_logger.setLevel(logging.ERROR)
urllib3_logger = logging.getLogger('urllib3')
urllib3_logger.setLevel(logging.ERROR)
LOG.propagate = False

INFO_FORMAT = "[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s"
DEBUG_FORMAT = "[%(asctime)s] [%(process)d] [%(levelname)s] [in %(pathname)s:%(lineno)d] %(message)s"
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S %z"

if config.APP_ENV == "dev" or config.APP_ENV == "live":
    from logging.handlers import RotatingFileHandler
    log_file = file = pathlib.Path("log/app.log")
    if not file.exists():
        os.makedirs("log")
        with open("log/app.log", "w") as fp:
            pass
    file_handler = RotatingFileHandler("log/app.log", "a", 1 * 1024 * 1024, 10)
    formatter = logging.Formatter(INFO_FORMAT, TIMESTAMP_FORMAT)
    file_handler.setFormatter(formatter)
    LOG.addHandler(file_handler)

if config.APP_ENV == "local":
    stream_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(DEBUG_FORMAT, TIMESTAMP_FORMAT)
    stream_handler.setFormatter(formatter)
    LOG.addHandler(stream_handler)


def get_logger():
    return LOG
