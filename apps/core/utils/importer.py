# -*- coding: utf-8 -*-
"""
    importer.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""

from importlib import import_module


def import_modules(modules):
    for mod in modules:
        import_module(mod)
