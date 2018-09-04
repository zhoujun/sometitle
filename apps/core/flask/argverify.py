# -*- coding: utf-8 -*-
"""
    argverify.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""
import regex as re


class ArgVerify(object):

    def required(self, **kwargs):
        for args in kwargs.get("reqargs"):
            if not args[1]:
                data = {
                    "msg": 'The "{}" cannot be empty'.format(args[0]),
                    "msg_type": "w",
                    "http_status": 422
                }
                return False, data
        return True, None

    def min_len(self, **kwargs):
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

    def max_len(self, **kwargs):
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

    def need_type(self, **kwargs):
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

    def only(self, **kwargs):
        vr = kwargs.get("vr")
        for args in kwargs.get("reqargs"):
            if not args[1] in vr:
                data = {
                    "msg": 'The value of parameter "{}" can only be one of "{}"'.format(args[0], ",".join(vr)),
                    "msg_type": "w",
                    "http_status": 422
                }
                return False, data
        return True, None

    def can_not(self, **kwargs):
        vr = kwargs.get("vr")
        for args in kwargs.get("reqargs"):
            if args[1] in vr:
                data = {
                    "msg": 'The value of parameter "{}" can not be "{}"'.format(args[0], ",".join(vr)),
                    "msg_type": "w",
                    "http_status": 422
                }
                return False, data
        return True, None

    def allowed_type(self, **kwargs):
        vr = kwargs.get("vr")
        for args in kwargs.get("reqargs"):
            if type(args[1]) not in vr:
                data = {
                    "msg": 'Parameter {} can only be of the following type: "{}"'.format("args[0]", ",".join(vr)),
                    "msg_type": "error",
                    "http_status": 422
                }
                return False, data
        return True, None

    def regex_rule(self, **kwargs):
        vr = kwargs.get("vr")
        if vr["is_match"]:
            for args in kwargs.get("reqargs"):
                if not re.search(vr["rule"], args[1]):
                    data = {
                        "msg": 'The value of parameter "{}" is illegal'.format(args[0]),
                        "msg_type": "w",
                        "http_status": 422
                    }
                    return False, data
        else:
            for args in kwargs.get("reqargs"):
                if re.search(vr["rule"], args[1]):
                    data = {
                        "msg": 'The value of parameter "{}" is illegal'.format(args[0]),
                        "msg_type": "w",
                        "http_status": 422
                    }
                    return False, data
        return True, None


arg_ver = ArgVerify()


def arg_verify(args, **kwargs):
    """

    :param args: 数组, 如: [(arg_key, arg_value)]

    required: bool,  为True表示不能为空
    min_len: int, 最小长度
    max_len: int, 最大长度
    need_type: 类型如int, dict, list .tuple
    only: 数组, 只能是only数组中的元素
    can_not: 数组, 不能是can_not中的元素
    allowed_type: 数组, 允许数据的类型是allowed_type中的元素
    regex_rule: Such as::{
        "rule":r".*",
        "is_match":True
    }
    is_match ：True 表示需要匹配成功, False 表示需要不匹配该规则的

    :param kwargs:
    :return:
    """
    for k, v in kwargs.items():
        s, r = getattr(arg_ver, k)(args=args, vr=v)
        if not s:
            return s, r
    return True, None


