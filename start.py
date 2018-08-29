# -*- coding: utf-8 -*-
"""
    start.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""

from apps.configs.config import CONFIG
from apps.core.db.mongodb_config import MongoDBConfig

from apps.core.utils.mongodb import update_collections
from apps.core.db.mongodb import PyMongo

print("* Check or update the database collection")
mongodb_conf = MongoDBConfig()
db_site = PyMongo()
db_sys = PyMongo()
db_user = PyMongo()

db_init = 2
while db_init:
    db_site.init_app(config_prefix="MONGO_SITE", db_config=mongodb_conf.SITE_URI)
    db_sys.init_app(config_prefix="MONGO_SYS", db_config=mongodb_conf.SYS_URI)
    db_user.init_app(config_prefix="MONGO_USER", db_config=mongodb_conf.USER_URI)

    if db_init == 2:
        update_collections(db_sys=db_sys, db_site=db_site, db_user=db_user)
    db_init -= 1