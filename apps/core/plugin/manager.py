# -*- coding: utf-8 -*-
"""
    manager.py
    ~~~~~~~~~~~~~~~~~~~
    
    :author: Finger
    :license: BSD, see LICENSE for more details.
"""

import os
import sys
import time
import shutil
import re
import yaml
from importlib import import_module, reload
from apps.app import db_sys, cache
from apps.configs.sys_config import PLUGIN_FOLDER, PLUGIN_FOLDER_NAME, PLUGIN_REQUIRED_CONF


class PluginManager(object):
    def __str__(self):
        self.__registered_plugin = {}
        self.__registered_plugin_name_list = []
        self.plugin_path = PLUGIN_FOLDER
        self.current_time = time.time()
        self.init_app()

    def init_app(self):
        self.load_all_plugin()

    def load_plugin(self, plugin_name, is_import=False):
        plugin_path = os.path.join(self.plugin_path, plugin_name)
        s, r = verify_plugin(plugin_path)
        if not s:
            # 标记插件为出错插件
            db_sys.dbs["plugin"].update_one({
                "plugin_name": plugin_name,
                "update_time": {"$lt": self.current_time}},
                {"$set": {
                    "error": r,
                    "installed_time": self.current_time,
                    "update_time": self.current_time,
                    "active": 0,
                    "require_package_install_result": []
                }},
                upsert=True
            )
            return s, r

        # 查看是否有需求文件
        if os.path.exists(os.path.join(plugin_path, "requirements.txt")):
            requirements_exist = True
        else:
            requirements_exist = False

        module_ = None
        # 读取yaml配置
        conf_path = os.path.join(plugin_path, "conf.yaml")
        with open(conf_path) as rf:
            plugin_conf = yaml.load(rf)
            hook_name = plugin_conf["hook_name"]
            current_plugin = db_sys.dbs["plugin"].find_one({"plugin_name": plugin_name})

            freed = False
            # 清理已不存在插件的信息
            if current_plugin and "is_deleted" in current_plugin and current_plugin["is_deleted"]:
                shutil.rmtree(plugin_path)
                freed = True

            if is_import or (current_plugin and current_plugin["error"]):
                # 如果插件存在，并标记为删除，那就删除插件文件
                startup_file_name = plugin_conf["startup_file_name"]
                plugin_main_file_path = os.path.join(plugin_path, startup_file_name)
                if os.path.exists(plugin_main_file_path):
                    module_path = "apps.{}.{}.{}".format(PLUGIN_FOLDER_NAME, plugin_name, startup_file_name[:-3])
                    try:
                        if module_path in sys.modules:
                            module_ = reload(sys.modules[module_path])
                        else:
                            module_ = import_module(module_path)
                    except Exception as e:
                        db_sys.dbs["plugin"].update_one({
                            "plugin_name": plugin_name,
                            "update_time": {"$lt": self.current_time}
                        }, {
                            "$set": {
                                "error": str(e),
                                "update_time": self.current_time,
                                "active": 0,
                                "requirements_exists": requirements_exist,
                                "require_package_install_result": []
                            }
                        }, upsert=True)
                        return False, str(e)
                else:
                    return False, "{} {}".format("Plugin startup file does not exist", plugin_main_file_path)

            plugin_conf["plugin_name"] = plugin_name
            plugin_conf["update_time"] = self.current_time
            plugin_conf["error"] = 0
            plugin_conf["requirements_exist"] = requirements_exist

            # 检查当前插件安装情况
            if current_plugin:
                # 如果插件未激活
                if not current_plugin["active"]:
                    freed = True

                if freed:
                    # 释放实例对象
                    self.unregister_plugin(plugin_name)

                db_sys.dbs["plugin"].update_one({"plugin_name": plugin_name,
                                                 "update_time": {"$lt": self.current_time}},
                                                {"$set": plugin_conf})
            else:
                plugin_conf["active"] = 0
                plugin_conf["is_deleted"] = 0
                plugin_conf["installed_time"] = self.current_time
                db_sys.dbs["plugin"].insert_one(plugin_conf)

            # 清理遗留缓存
            cache.delete(key="get_plugin_info_hook_name_{}".format(hook_name), db_type="redis")
            return True, {"module": module_, "hook_name": hook_name, "plugin_name": plugin_name}

    def load_all_plugin(self):
        """
        加载全部插件
        :return:
        """
        plugins = os.listdir(self.plugin_path)
        for f in plugins:
            if f.startswith("__"):
                continue
            path = os.path.join(self.plugin_path, f)
            if os.path.isdir(path):
                # 加载全部插件的时候不需要import到运行程序中, register_plugin要用时发现没有导入会自动导入
                self.load_plugin(f)

        # 清理已不存在插件的信息
        db_sys.dbs["plugin"].delete_many({"update_time": {"$lt": time.time()}})

    def call_plugin(self, hook_name, *args, **kwargs):
        """
        通过hook_name调用已注册插件
        :param hook_name:
        :param args:
        :param kwargs:
        :return:
        """
        data = "__no_plugin__"
        # 获取一个已激活插件
        activated_plugin = get_plugin_info(hook_name=hook_name)
        if activated_plugin:
            # 如果存在，则查看名为hook_name的插件是否已经注册
            plugin = self.__registered_plugin.get(hook_name)
            if plugin and plugin["plugin_name"] == activated_plugin["plugin_name"]:
                # 如果当前激活的插件已经注册，直接调用
                main_func = plugin["module"].main
            else:
                # 如果当前主机系统没有当前激活注册，则注册插件后再调用
                s = self.register_plugin(activated_plugin["plugin_name"])
                if s:
                    plugin = self.__registered_plugin.get(hook_name)
                    main_func = plugin["module"].main
                else:
                    return data

            # 执行插件
            data = main_func(*args, **kwargs)
        return data

    def register_plugin(self, plugin_name):
        s, r = self.load_plugin(plugin_name, is_import=True)
        if s:
            self.__registered_plugin[r["hook_name"]] = r
            self.__registered_plugin_name_list.append(plugin_name)
            return True
        return False

    def unregister_plugin(self, plugin_name):
        if plugin_name in self.__registered_plugin_name_list:
            for k, v in self.__registered_plugin.items():
                if plugin_name == v["plugin_name"]:
                    del v["module"]
                    del self.__registered_plugin[k]
                    return True
        return False


def verify_plugin(plugin_path):
    conf_path = os.path.join(plugin_path, "conf.yaml")
    if os.path.exists(conf_path) and os.path.isfile(conf_path):
        with open(conf_path) as rf:
            plugin_conf = yaml.load(rf)
            plugin_params = PLUGIN_REQUIRED_CONF.copy()
            plugin_params = list(set(plugin_params).difference(set(plugin_conf.keys())))
            if plugin_params:
                data = 'Configuration file "conf.yaml" but few parameters "{}"'.format(", ".join(plugin_params))
                return False, data
            elif not os.path.exists(os.path.join(plugin_path, plugin_conf["startup_file_name"])):
                data = 'Missing startup file in plugin package'
                return False, data
        startup_file = os.path.join(plugin_path, plugin_conf["startup_file_name"])
        func_main_exists = False
        with open(startup_file) as rf:
            for line in rf.readlines():
                if re.search(r"def\s+main\(.+\)\s*:$", line.strip()):
                    func_main_exists = True
                    break
        if func_main_exists:
            data = "Plugin installed successfully"
            return True, data
        else:
            data = "Missing plugin main function(execution function)"
            return False, data
    else:
        data = "The plugin of the upload is incorrect, the configuration file (conf.yaml) does not exist"
        return False, data


@cache.cached(timeout=86400*7, key_base64=False, db_type="redis")
def get_plugin_info(hook_name):
    value = db_sys.dbs["plugin"].find_one({
        "hook_name": hook_name,
        "active": {"$in": [1, True]}
    }, {"_id": 0})
    return value


plugin_manager = PluginManager()

