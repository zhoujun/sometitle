# -*- coding: utf-8 -*-
"""
    cache.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""

import base64
import time
from functools import wraps
from flask import current_app, request
from apps.utils.format.obj_format import json_to_py_seq


class Cache(object):
    def __init__(self, app=None):
        self.cache_none = type(CacheNone)
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self._get_interface(app)

    def _get_interface(self, app):
        self.config = app.config.copy()
        self.config.setdefault('CACHE_DEFAULT_TIMEOUT', 300)
        self.config.setdefault('CACHE_REDIS', None)
        self.config.setdefault('CACHE_MONGODB', None)
        self.config.setdefault('CACHE_MONGODB_DB', "osr_sys")
        self.config.setdefault('CACHE_MONGODB_COLLECT', "osr_cache")
        self.config.setdefault('CACHE_KEY_PREFIX', 'osr-cache:')
        self.config.setdefault('CACHE_TYPE', 'redis')
        self.config.setdefault('USE_CACHE', True)

        # 需要配置好redis和mongodb, 系统对不同的数据的缓存需要不一样的数据库保存
        if self.config["CACHE_REDIS"]:
            self.redis = self.config["CACHE_REDIS"]
        else:
            raise Exception('Missing configuration "CACHE_REDIS"')

        if self.config["CACHE_MONGODB"]:
            self.mdb_coll = self.config["CACHE_MONGODB"][self.config["CACHE_MONGODB_DB"]][
                self.config["CACHE_MONGODB_COLLECT"]]
        else:
            raise Exception('Missing configuration "CACHE_MONGODB"')

    @property
    def cache(self):
        app = self.app or current_app
        return app.extensions["cache"][self]

    def cached(self, timeout=None, key=None, key_base64=True, db_type=None):
        """
        设置缓存
        :param timeout:缓存保存时间
        :param key: 默认使用func的参数拼接作为key, 没有参数则使用为'osr/{}'.format(request.path)
        :param key_base64: 当key==None时生效.默认使用base64编码key.
                           key_base64为False, 则不编码key
        :param db_type: 不使用系统设置的db type时指定类型mongodb或redis
        """
        def decorator(func):
            @wraps(func)
            def decorated_function(*args, **kwargs):
                if not self.config["USE_CACHE"]:
                    return func(*args, **kwargs)

                if key is None:
                    c_key = func.__name__
                    if args or kwargs:
                        for arg in args:
                            c_key = "{}_{}".format(c_key, str(arg))

                        for k, arg in kwargs.items():
                            c_key = "{}_{}_{}".format(c_key, k, str(arg))
                        cache_key = c_key.lstrip("_")
                    else:
                        cache_key = "{}_{}".format(c_key, request.path)

                    if key_base64:
                        cache_key = base64.b64decode(cache_key.encode()).decode()
                else:
                    cache_key = key

                func_result = self.get(key=cache_key, db_type=db_type)
                if func_result != self.cache_none:
                    return func_result
                else:
                    func_result = func(*args, **kwargs)
                    self.set(cache_key, func_result, ex=timeout, db_type=db_type)
            return decorated_function
        return decorator

    def get(self, key, db_type=None):
        """
        获取一个cache
        :param key:
        :param db_type: 不使用系统设置的db type时指定类型mongodb或redis
        :return:default:获取不到时返回
        """
        key = "{}{}".format(self.config["CACHE_KYE_PREFIX"], key)
        if not db_type:
            if self.config["CACHE_TYPE"] == "redis":
                value = self.redis.get(key)
                if value:
                    value = json_to_py_seq(value.decode("utf-8"))
                    return value
                return self.cache_none

            else:
                value = self.mdb_coll.find_one({"key": key}, {"_id": 0})
                if value and value["expiration"] < time.time():
                    self.delete(key, db_type=db_type)
                elif value:
                    return value["value"]

                # 防止value为None时, 所以查询不到缓存时, 使用cache空类
                return self.cache_none

        else:
            if db_type == "redis":
                value = self.redis.get(key)
                if value:
                    value = json_to_py_seq(value.decode("utf-8"))
                    return value

                # 防止value为None时, 所以查询不到缓存时, 使用cache空类
                return self.cache_none

            elif db_type == "mongodb":
                value = self.mdb_coll.find_one({"key": key}, {"_id": 0})
                if value and value["expiration"] < time.time():
                    self.delete(key, db_type=db_type)
                    return self.cache_none
                elif value:
                    return value["value"]

                return self.cache_none

    def set(self, key, value, ex=None, db_type=None):
        """
        设置一个cache
        :param key:
        :param value:
        :param ex:
        :param db_type: 不使用系统设置的db type时指定类型mongodb或redis
        :return:ex,如果ex为0表示
        """
        key = "{}{}".format(self.config["CACHE_KEY_PREFIX"], key)
        if ex is None:
            ex = self.config["CACHE_DEFAULT_TIMEOUT"]

        if not db_type:
            if self.config["CACHE_TYPE"] == "redis":
                self.redis.set(key, value, ex=ex)
                return value
            else:
                r = self.mdb_coll.update_one({"key": key},
                                             {"$set": {
                                                 "value": value,
                                                 "expiration": time.time() + ex
                                             }},
                                             upsert=True)
                if r.modified_count:
                    return value
                elif not r.modified_count and not r.matched_count:
                    return value
                else:
                    return None

        else:
            if db_type == "redis":
                self.redis.set(key, value, ex=ex)
                return value

            elif db_type == "mongodb":
                r = self.mdb_coll.update_one({"key": key},
                                             {"$set": {
                                                 "value": value,
                                                 "expiration": time.time() + ex
                                             }},
                                             upsert=True)
                if r.modified_count:
                    return value
                elif not r.modified_count and not r.matched_count:
                    return value
                return None

    def delete(self, key, db_type=None, key_regex=False):
        """
        删除cache
        :param key:
        :param db_type: 不使用系统设置的db_type时, 请指定类型mongodb或redis
        :param key_regex:默认关闭正则匹配key, key_regex=True是只能在db_type是mongodb的时候才生效
        :return:
        """
        key = "{}{}".format(self.config["CACHE_KEY_PREFIX"], key)
        if not db_type:
            if self.config["CACHE_TYPE"] == "redis":
                self.redis.delete(key)
            else:
                if key_regex:
                    q = {"key": {"$regex": key}}
                else:
                    q = {"key": key}
                self.mdb_coll.delete_many(q)
        else:
            if db_type == "redis":
                self.redis.delete(key)
            elif db_type == "mongodb":
                if key_regex:
                    q = {"key": {"$regex": key}}
                else:
                    q = {"key": key}
                self.mdb_coll.delete_many(q)

    def clear(self, db_type=None):
        """
        清除所有的cache
        :param db_type: 不使用系统设置的db type时指定类型mongodb或redis
        :return:
        """
        if not db_type:
            if self.config["CACHE_TYPE"] == "redis":
                self.redis.delete(*self.redis.keys())
            else:
                self.mdb_coll.delete_many({})
        elif db_type:
            if db_type == "redis":
                self.redis.delete(*self.redis.keys())

            elif db_type == "mongodb":
                self.mdb_coll.delete_many({})


class CacheNone(object):
    def __init__(self):
        pass

    def __str__(self):
        return "Cache None"