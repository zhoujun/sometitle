# -*- coding: utf-8 -*-
"""
    collection.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""

collections = {
    'site': [
        'post',             # 发布的文章内容
        'comment',          # 评论
        'category',         # 文章分类
        'access_record',    # 访问记录
        'verify_code',      # 验证
        'temp_file',        # 用户保存临时文件
        'media'             # 用户保存媒体信息，如图片，视频，音频等
    ],

    'sys': [
        'sys_token',        # 秘钥
        'audit_rules',      # 审核角色
        'sys_message',      # 系统消息
        'sys_msg_img',      # 系统消息图片
        'sys_config',       # 配置信息
        'sys_host',         # 系统域名
        'sys_call_record',  # 用户一些操作频率记录
        'plugin',           # 插件
        'plugin_config',    # 插件配置
        'theme'             # 系统主题
    ],

    'user': [
        'role',             # 用户角色
        'user',             # 用户
        'user_login_log',   # 用户登录日志
        'user_op_log',      # 用户操作日志
        'user_like',        # 用户点赞
        'message',          # 用户消息
        'user_follow'       # 用户关注
    ]
}