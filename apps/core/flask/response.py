# -*- coding: utf-8 -*-
"""
    response.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""
from flask import Response, jsonify


class MyResponse(Response):
    @classmethod
    def force_type(cls, ret, environ=None):
        if isinstance(ret, dict):
            ret = jsonify(ret)
        return super(Response, cls).force_type(ret, environ)


def format_response(data, status=200):
    if not isinstance(data, dict):
        return data, status

    if "http_status" not in data.keys():
        return data, status

    return data, data["http_status"]