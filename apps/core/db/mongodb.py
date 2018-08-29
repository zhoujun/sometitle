# -*- coding: utf-8 -*-
"""
    mongodb.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""

from pymongo import MongoClient


class PyMongo(object):

    def __init__(self, app=None, config_prefix="MONGO", db_config=None):

        if app or db_config:
            self.init_app(app, config_prefix, db_config)

    def init_app(self, app=None, config_prefix="MONGO", db_config=None, reinit=False):
        if not reinit:
            if not app and not db_config:
                raise Exception("Parameter: app or db_config must provide one")

            if app:
                def key(suffix):
                    return "%s_%s" % (config_prefix, suffix)

                if key('URI') in app.config:
                    self.config = app.config[key("URI")]
                else:
                    raise Exception("{} is not in the database configuration file".format(key["URI"]))

            elif db_config:
                self.config = db_config

        self.client = MongoClient(self.config["mongodb"])
        self.name = self.config["db"]

        self.db = self.client[self.config["db"]]
        self.db_collections = MongoDBCollections(self.db)


class MongoDBCollections(object):
    def __init__(self, db=None):
        if db:
            self.collection_object(db)

    def collection_object(self, db):
        for collection_name in db.collection_names():
            self.__dict__[collection_name] = db[collection_name]