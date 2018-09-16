# -*- coding: utf-8 -*-
"""
    pyssh.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""

import paramiko


class MySSH(object):
    def __init__(self, host, port, username, password, pkey_file="", pkey_pwd=""):
        self.client = paramiko.SSHClient()
        if pkey_file:
            key = paramiko.RSAKey.from_private_key(pkey_file, password=pkey_pwd)
            # 通过公共方式进行认证 (不需要在known_hosts 文件中存在)
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
            self.client.connect(host, port, username=username, password=password, pkey=key)
        else:
            # 允许连接不在know_hosts文件中的主机
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
            # 连接服务器
            self.client.connect(host, port, username=username, password=password)

    def exec_cmd(self, cmd):
        return self.client.exec_command(cmd)

    def close(self):
        self.client.close()


def audit_host_info(host_info):
    """
    查看host信息是否符合连接
    :param host_info:
    :return:
    """
    if not "port" in host_info or not "username" in host_info or not "password" in host_info:
        data = {
            "msg": "Please improve the host information",
            "msg_type": "w",
            "http_status": 400
        }
        return False, data
    return True, None
