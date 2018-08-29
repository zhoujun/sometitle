# -*- coding: utf-8 -*-
"""
    number.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""


def get_num_digits(num):
    n = 0
    while True:
        if not num:
            break
        n += 1
        num = int(num) >> 1
    return n