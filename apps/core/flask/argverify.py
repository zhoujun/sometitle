# -*- coding: utf-8 -*-
"""
    argverify.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""
import regex as re


class ArgVerify(object):

    @staticmethod
    def required(**kwargs):
        for args in kwargs.get("reqargs"):
            if not args[1]:
                data = {
                    "msg": 'The "{}" cannot be empty'.format(args[0]),
                    "msg_type": "w",
                    "http_status": 422
                }
                return False, data
        return True, None

    @staticmethod
    def min_len(**kwargs):
        vr = kwargs.get("vr")
        for args in kwargs.get("reqargs"):
            if len(args[1]) < vr:
                data = {
                    "msg": 'The minimum length of "{}" is {} characters'.format(args[0], vr),
                    "msg_type": "w",
                    "http_status": 422
                }
                return False, data
        return True, None

    @staticmethod
    def max_len(**kwargs):
        vr = kwargs.get("vr")
        for args in kwargs.get("reqargs"):
            if len(args[1]) > vr:
                data = {
                    "msg": 'The maximum length of "{}" is {} characters'.format(args[0], vr),
                    "msg_type": "w",
                    "http_status": 422
                }
                return False, data
        return True, None

    @staticmethod
    def need_type(**kwargs):
        vr = kwargs.get("vr")
        for args in kwargs.get("reqargs"):
            if not isinstance(args[1], vr):
                data = {
                    "msg": '"{}" needs to be of type {}'.format(args[0], vr.__name__),
                    "msg_type": "w",
                    "http_status": 422
                }
                return False, data
        return True, None

    
