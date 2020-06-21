# -*- coding: utf-8 -*-

import configparser
import os

UUID_LEN = 10
UUID_ALPHABET = "".join(map(chr, range(48, 58)))

APP_ENV = os.environ.get("APP_ENV") or "dev"  # or 'live' to load live
ENV_FILE = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "../conf/{}.env".format(APP_ENV)
)
CONFIG = configparser.ConfigParser()
CONFIG.read(ENV_FILE)

CONFIG.set("aws", "ACCESS_KEY_ID", os.environ.get("ACCESS_KEY_ID", ""))
CONFIG.set("aws", "SECRET_ACCESS_KEY", os.environ.get("SECRET_ACCESS_KEY", ""))

# determine the log level from ini files
LOG_LEVEL = CONFIG["logging"]["level"]
init = True
