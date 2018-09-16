# -*- coding: utf-8 -*-
"""
    send_email.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""

import json
import time
import os
from flask_mail import Message
from apps.core.plugin.manager import plugin_manager
from apps.core.utils.get_config import get_config
from apps.utils.async.async import async_process
from apps.app import mail, app, db_sys


def send_email(subject, recipients, text_msg=None, html_msg=None, attach=None, send_independently=True):
    """
    发送email
    :param subject:
    :param recipients:数组
    :param text_msg:
    :param html_msg:
    :param attach:(<filename>,<content_type>)
    :param send_independently:如果为True, 独立给recipients中的每个地址发送信息,
            否则,一次发送, 收件人能看到其他收件人的邮箱
    :return:
    """

    data = plugin_manager.call_plugin(hook_name="send_email",
                                      recipients=recipients,
                                      send_independently=send_independently,
                                      subject=subject,
                                      html=html_msg,
                                      text=text_msg,
                                      attach=attach)
    if data == '__no_plugin__':
        msg = Message(subject,
                      sender=get_config("email", "MAIL_DEFAULT_SENDER"))
        if html_msg:
            msg.html = html_msg
        elif text_msg:
            msg.body = text_msg

        if attach and len(attach) == 2:
            with app.open_resource(attach[0]) as fp:
                msg.attach(os.path.split(attach[0])[-1], attach[1], fp.read())

        send_async_email(app, msg, recipients=recipients, send_independently=send_independently)


@async_process
def send_async_email(app, msg, recipients, send_independently=True):
    db_sys.init_app(reinit=True)
    with app.app_context():
        if send_independently:
            with mail.connect() as conn:
                for recipient in recipients:
                    msg.recipients = [recipient]
                    send_email_process(msg, conn)
        else:
            msg.recipients = recipients
            return send_email_process(msg)


def send_email_process(msg, connected_instance=None):
    error_info = None
    try:
        if connected_instance:
            r = connected_instance.send(msg)
        else:
            r = mail.send(msg)

        if not r:
            status = "normal"
        else:
            status = "abnormal"
    except Exception as e:
        error_info = json.dumps(str(e))
        status = 'error'

    log = {
        "type": "email",
        "error_info": error_info,
        "status": status,
        "subject": msg.subject,
        "from": msg.sender,
        "to": list(msg.send_to),
        "date": msg.date,
        "body": msg.body,
        "html": msg.html,
        "msgid": msg.MsgId,
        "time": time.time()
    }
    db_sys.db.sys_message.insert_one(log)
    if not status:
        return 0
    else:
        return -1