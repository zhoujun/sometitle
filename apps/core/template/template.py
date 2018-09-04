# -*- coding: utf-8 -*-
"""
    template.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""

from flask import render_template_string


def render_absolute_path_template(path, **context):
    with open(path) as html:
        source = html.read()
    return render_template_string(source=source, **context)