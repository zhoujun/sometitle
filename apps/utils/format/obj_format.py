# -*- coding: utf-8 -*-
"""
    obj_format.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""

import json
import sys
import regex as re
from pymongo.cursor import Cursor


def obj_id_to_str(data, fields=["_id"]):
    if isinstance(data, (list, Cursor)):
        _data = []
        for d in data:
            for field in fields:
                d[field] = str(d[field])
            _data.append(d)
        return _data
    else:
        data_keys = data.keys()
        for field in fields:
            if field in data_keys:
                data[field] = str(data[field])
        return data


def json_to_py_seq(json_):
    if json_ in [None, "None"]:
        return None
    elif not isinstance(json_, (list, dict, tuple)) and json_ != "":
        if isinstance(json_, (str, bytes)) and json_[0] not in ["{", "["]:
            return json_
        try:
            json_ = json.loads(json_)
        except:
            json_ = eval(json_)
        else:
            if isinstance(json_, str):
                json_ = eval(json_)
    return json_


def str_to_num(str_):
    try:
        return int(str_)
    except:
        if str_:
            return 1
        elif not str_ or str_.lower() == "false":
            return 0


class ConfigToClass(object):
    def __init__(self, config, key=None):
        if not isinstance(config, dict):
            print("[Error] config must be a dictionary")
            sys.exit(-1)

        if key == "value":
            for k, v in config.items():
                if not re.search(r"^__.*__$", k):
                    self.__dict__[k] = v["value"]
        else:
            for k, v in config.items():
                self.__dict__[k] = v


