# -*- coding: utf-8 -*-
"""
    logging.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""

import time
import logging
import os
import logging.config
from logging.handlers import TimedRotatingFileHandler
from uuid import uuid1
from flask import request, g
from flask_login import current_user
from apps.configs.sys_config import *


class Logger(object):

    def __init__(self):
        pass

    def init_app(self, app):

        filename = os.path.abspath("{}/{}".format(LOG_PATH, LOG_INFO_FILENAME))
        info_log, info_handler = self.set_logger(LOG_NORMAL_LEVEL, filename, 'info')

        filename = os.path.abspath("{}/{}".format(LOG_PATH, LOG_ERROR_FILENAME))
        error_log, error_handler = self.set_logger(LOG_ERROR_LEVEL, filename, 'error')

        @app.before_request
        def before_request_log():
            global _g

            _g = {
                "log": {}
            }
            g.request_id = request_id = uuid1()

            _g["log"] = {
                "request_id": request_id,
                "st": time.time(),
                "ip": request.remote_addr,
                "url": request.url
            }

            if current_user.is_authenticated:
                _g["log"]["user_id"] = current_user.str_id

        @app.teardown_request
        def teardown_request_log(exception):
            try:
                _g["log"]["method"] = request.c_method
                _g["log"]["u_t_m"] = "{} ms".format((time.time() - _g["log"]["st"]) * 1000)
                info_log.info("[api|view] {}".format(_g["log"]))
                if exception:
                    error_log.error(_g["log"])
                    error_log.exception(exception)
            except Exception as e:
                error_log.error({
                    "type": "logger error",
                    "exception": e
                })

    def start_log(self):
        filename = os.path.abspath("{}/{}".format(LOG_PATH, LOG_START_FILENAME))
        start_log, start_handler = self.set_logger(logging.INFO, filename, 'start')
        return start_log

    def set_logger(self, log_level=logging.INFO, logfile="{}.log".format(time.time()),
                   get_log_name="logger", formatter=LOG_FORMATTER):
        if not os.path.exists(os.path.split(logfile)[0]):
            os.makedirs(os.path.split(logfile)[0])

        # 每天保存一个日志, 最多保存7个
        file_handler = TimedRotatingFileHandler(logfile, "midnight", 1, 7)
        file_handler.suffix = "%Y-%m-%d"
        # According to the size
        # file_handler = RotatingFileHandler(filename, maxBytes=10*1024*1024, backupCount=3)
        file_handler.setLevel(log_level)
        _formatter = logging.Formatter(formatter)
        file_handler.setFormatter(_formatter)

        logging.getLogger('{}'.format(get_log_name)).addHandler(file_handler)
        logging.getLogger('{}'.format(get_log_name)).setLevel(logging.INFO)
        log = logging.getLogger(get_log_name)
        return log, file_handler

start_logger = Logger().start_log()