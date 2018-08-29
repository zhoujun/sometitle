# -*- coding: utf-8 -*-
"""
    url_format.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""
from tld import get_tld


def get_domain(url):
    """
    获取url中的全域名
    :param url:
    :return:
    """
    res = get_tld(url, as_object=True)
    return "{}:{}".format(res.subdomain, res.tld)