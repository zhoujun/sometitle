# -*- coding: utf-8 -*-
"""
    routing.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""

import time
from werkzeug.routing import BaseConverter
from apps.app import db_sys, cache


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


def push_url_to_db(app):
    """
    同步url到数据库
    :param app:
    :return:
    """
    now = time.time()
    for rule in app.url_map.iter_rules():
        if not rule.endpoint.startswith("api.") and not rule.endpoint.startswith("open_api."):
            continue
        type_ = "api"

        r = db_sys.dbs["sys_urls"].find_one({"url": rule.rule.rstrip("/")})
        if not r:
            db_sys.dbs["sys_urls"].insert_one({
                "url": rule.rule.rstrip("/"),
                "methods": list(rule.methods),
                "endpoint": rule.endpoint,
                "custom_permission": {},
                "type": type_,
                "create": "auto",
                "update_time": now
            })
        elif r and r["update_time"] < now:
            # 如果存在, 并且更新时间比现在前(防止同时启动多个进程时错乱，导致下面程序当旧数据清理)
            db_sys.dbs["sys_urls"].update_one({
                "_id": r["_id"], "update_time": {"$lt": now}},
                {"$set": {
                    "methods": list(rule.methods),
                    "endpoint": rule.endpoint,
                    "type": type_,
                    "create": "auto",
                    "update_time": now
                }})
        urls = db_sys.dbs["sys_urls"].find({})
        for url in urls:
            if "url" in url:
                cache.delete(key="get_sys_url_url_{}".format(url["url"]), db_type="redis")

        # 清理不存在的api
        db_sys.dbs["sys_urls"].delete_many({
            "type": {"$ne": "page"},
            "update_time": {"$lt": now}
        })



