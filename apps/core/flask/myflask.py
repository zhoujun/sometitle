# -*- coding: utf-8 -*-
"""
    myflask.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""

from flask import Flask
from apps.core.flask.response import MyResponse


class App(Flask):
    response_class = MyResponse