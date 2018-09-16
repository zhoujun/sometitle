# -*- coding: utf-8 -*-
"""
    send_message.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""

import time
from apps.app import db_sys
from apps.core.plugin.manager import plugin_manager


def send_mobile_msg(numbers, content):
    data = plugin_manager.call_plugin(hook_name="send_msg",
                                      to_numbers=numbers,
                                      content=content)
    if data == "__no_plugin__":
        msg = "There is no plugin for sending SMS messages to mobile phones, please install the relevant plugin"
        status = "abnormal"
        result = (False, msg)
    elif not data:
        status = "abnormal"
        result = (False, "Failed to send")
    else:
        status = "normal"
        result = (True, "SMS send successfully")

    log = {
        "type": "sms",
        "error_info": msg,
        "status": status,
        "subject": "",
        "from": "",
        "to": numbers,
        "date": time.time(),
        "body": content,
        "html": "",
        "msgid": None,
        "time": time.time()
    }
    db_sys.db.sys_message.insert_one(log)
    return result
