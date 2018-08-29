# -*- coding: utf-8 -*-
"""
    update_db_collection.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""
from apps.models.collection import collections
from apps.core.logger.logging import start_logger


def update(db_sys, db_site, db_user):
    dbs = {
        "sys": db_sys,
        "site": db_site,
        "user": db_user
    }

    for k, colls in collections.items():
        mongodb = dbs[k]
        for collection in colls:
            try:
                mongodb.db.create_collection(collection)
                start_logger.info("[DB: {}] Create collection - '{}'").format(mongodb.name, collection)
            except Exception as e:
                if "already exists" in str(e):
                    start_logger.info(e)
                else:
                    start_logger.warning(e)




