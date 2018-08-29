# -*- coding: utf-8 -*-
"""
    import_module.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""

from importlib import import_module


def import_module(modules):
    for mod in modules:
        import_module(mod)
