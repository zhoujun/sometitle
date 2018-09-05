# -*- coding: utf-8 -*-
"""
    text_parsing.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""

from lxml import etree


def rich_text_extract_img(rich_text=""):
    s = etree.HTML(rich_text.lower())
    src = s.xpath("//img/@src")
    return src