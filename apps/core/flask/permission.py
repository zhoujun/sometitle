# -*- coding: utf-8 -*-
"""
    permission.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""
from flask_login import current_user
from functools import wraps
from flask import request
from werkzeug.utils import redirect

from apps.app import db_sys, cache
from apps.core.flask.response import format_response
from apps.core.utils.get_config import get_config, get_configs


def permission_required(permission):
    """
    权限验证
    :param permission:
    :return:
    """
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            custom_permission = custom_url_permissions()
            if custom_permission:
                allow = current_user.can(custom_permission)
                keys = " or ".join(get_permission_key(custom_permission))
            else:
                allow = current_user.can(permission)
                keys = " or ".join(get_permission_key(permission))

            if not allow:
                return format_response({
                    "msg": 'Permission denied, requires "{}" permission'.format(keys),
                    "msg_type": "w",
                    "http_status": 401
                })
            return func(*args, **kwargs)
        return decorated_function
    return decorator


def page_permission_required():
    """
    页面路由权限验证
    :return:
    """
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            custom_login_required = custom_url_login_auth()
            if custom_login_required and current_user.is_anonymous:
                return redirect(get_config("login_manager", "LOGIN_VIEW"))

            custom_permission = custom_url_permissions()
            if custom_permission:
                allow = current_user.can(custom_permission)
                if not allow:
                    keys = " or ".join(get_permission_key(custom_permission))
                    return format_response({
                        "msg": 'Permission denied, requires "{}" permission'.format(keys),
                        "msg_type": "w",
                        "http_status": 401
                    })
            return func(*args, **kwargs)
        return decorated_function
    return decorator


def permissions(names):
    value = 0b0
    for name in names:
        value = value | get_config("permission", name)
    return value


def get_permission_key(permission):
    keys = []
    for k, v in get_configs("permission").items():
        if int(v) & int(permission):
            keys.append(k)
    return keys


def custom_url_permissions(url=None, method="GET"):
    """
    获取自定义权限
    :param url:
    :param method:
    :return:
    """
    if not url:
        url = request.path
        method = request.c_method

    url_per = get_sys_url(url=url.rstrip("/"))
    if url_per and method in url_per["custom_permission"]:
        return url_per["custom_permission"]["method"]


def custom_url_login_auth(url=None, method="GET"):
    """
    获取自定义权限
    :param url:
    :param method:
    :return:
    """
    if not url:
        url = request.path
        method = request.c_method

    url_per = get_sys_url(url=url.rstrip("/"))
    if url_per and url_per["type"] != "page"  and method in url_per["login_auth"]:
        return url_per["login_auth"][method]


@cache.cached(timeout=3600, key_base64=False, db_type="redis")
def get_sys_url(url):
    """
    获取url权限等信息
    :param url:
    :return:
    """
    value = db_sys.db.sys_urls.find_one({"url": url}, {"_id": 0})
    return value