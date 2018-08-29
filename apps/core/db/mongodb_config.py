# -*- coding: utf-8 -*-
"""
    mongodb_config.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""

from urllib.parse import quote_plus
from apps.configs.db_config import DB_CONFIG


class MongoDBConfig(object):

    def __init__(self):
        mongodbs = DB_CONFIG["mongodb"]
        for prefix, conf in mongodbs.items():
            if prefix == 'sys':
                self.session_db_name = conf["db_name"]
            uri = "mongodb://{username}:{password}@{host}:{port}".format(
                username=quote_plus(conf["username"]),
                password=quote_plus(conf["password"]),
                host=conf["host"],
                port=conf["port"]
            )
            config = {
                "mongodb": uri,
                "db": conf["db_name"],
            }
            config_prefix = prefix.upper()
            # print(config_prefix, config)
            self.__dict__["{}_URI".format(config_prefix)] = config