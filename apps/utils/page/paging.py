# -*- coding: utf-8 -*-
"""
    paging.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""


def to_page(pre=10, page_num=1, data_cnt=0, data=[]):

    if data_cnt % pre == 0:
        page_total = data_cnt // pre
    else:
        page_total = data_cnt // pre + 1
    return {
        "data": data,
        "page_total": page_total,
        "current_page": page_num,
        "data_total": data_cnt
    }

