# -*- coding: utf-8 -*-
"""
    get_template.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""

import os
import time
from flask import render_template, url_for


from apps.core.template.template import render_absolute_path_template
from apps.core.utils.get_config import get_config
from apps.utils.format.time_format import time_to_utc_date


def get_email_html(data):
    data["app_name"] = get_config("email", "APP_NAME")
    data["app_logo_url"] = get_config("email", "APP_LOG_URL")
    conf_site_url = get_config("site_config", "SITE_URL")
    if conf_site_url:
        data["site_url"] = url_for("theme_view.index")
    else:
        data["site_url"] = url_for("theme_view.index")
    data["utc_time"] = time_to_utc_date(timestamp=time.time(), formatter="%Y-%m-%d %H:%M:%S")
    path = "{}/pages/module/email/send-temp.html".format(get_config("theme", "CURRENT_THEME_NAME"))
    # absolute_path = os.path.abspath("{}/{}".format(theme_view.template_folder, path))
    # if os.path.isfile(absolute_path):
    #     html = render_template(path, data=data)
    # else:
    #     # 主题不存页面,使用系统自带的页面
    #     path = "{}/module/email/send-temp.html".format(admin_view.template_folder)
    #     html = render_absolute_path_template(path, data=data)
    # return html



