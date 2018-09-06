# -*- coding: utf-8 -*-
"""
    config_process.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""

import time
from apps.app import db_sys, cache, app
from apps.configs.sys_config import PLUGIN_CONFIG_CACHE_KEY, CONFIG_CACHE_TIMEOUT


def import_plugin_config(plugin_name, config):
    current_time = time.time()
    for k, v in config.items():
        if "value_type" not in v:
            assert Exception('Plugin configuration import database error, missing "value_type"" ')
        if "reactivate" not in v:
            v["reactivate"] = True
        if ["info"] not in v:
            v["info"] = ""

        r = db_sys.db.plugin_config.find_one({"plugin_name": plugin_name,
                                             "key": k,
                                              "value_type": v["value_type"]
                                              })
        if not r:
            db_sys.db.plugin_config.insert_one({"plugin_name": plugin_name,
                                                "key": k,
                                                "value_type": v["value_type"],
                                                "value": v["value"],
                                                "reactivate": v["reactivate"],
                                                "info": v["info"]})
        elif r and r["update_time"] < current_time:
            db_sys.db.plugin_config.update_one({"_id": r["_id"], "update_time": {"$lt": current_time}},
                                               {"$set": {
                                                   "update_time": current_time,
                                                   "reactivate": v["reactivate"],
                                                   "info": v["info"]
                                               }})
    # 删除已不需要的配置
    db_sys.db.plugin_config.delete_many({
        "plugin_name": plugin_name,
        "update_time": {"$lt": current_time}
    })
    # 更新插件配置缓存, 删除缓存，达到更新缓存
    cache.delete(key=PLUGIN_CONFIG_CACHE_KEY)


@cache.cached(timeout=CONFIG_CACHE_TIMEOUT, key=PLUGIN_CONFIG_CACHE_KEY)
def get_all_config():
    """
    从数据库中查询当前的配置返回
    :return:
    """
    all_configs = db_sys.db.plugin_config.find({})
    configs = {}
    for config in all_configs:
        configs.setdefault(config["plugin_name"], {})
        configs[config["plugin_name"]][config["key"]] = config["value"]
    return configs


def get_plugin_config(plugin_name, key):
    """
    获取网站动态配置中对应的project中key的值
    :param plugin_name:
    :param key:
    :return:
    """
    with app.app_context():
        return get_all_config()[plugin_name][key]


def get_plugin_configs(plugin_name):
    """
    获取网站动态配置中对应的project
    :param plugin_name:
    :return:
    """
    with app.app_context():
        return get_all_config()[plugin_name]