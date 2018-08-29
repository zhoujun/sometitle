# -*- coding: utf-8 -*-
"""
    process.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""
import os
import regex as re


def traversal(path, regex_filter=".*", keep=True):
    """

    :param path:
    :param regex_filter:
    :param keep:  如果为True保留符合规则的，否则去除符合正则的
    :return:
    """
    temp_files = []
    for root, dirs, files in os.walk(path):
        if re.search(regex_filter, root):
            continue

        if keep:
            for file in files:
                file_path = "{}:{}".format(root, file)
                if re.search(regex_filter, file_path):
                    temp_files.append({
                        "path": root,
                        "name": file
                    })
        else:
            for file in files:
                file_path = "{}:{}".format(root, file)
                if not re.search(regex_filter, file_path):
                    temp_files.append({
                        "path": root,
                        "name": file
                    })

        for dir_ in dirs:
            temp_files.extend(traversal("{}/{}".format(root, dir_)))
    return temp_files
