import time
from os import path
from typing import Union

import toml

from config import data_path

########################################################################
# CONFIG

config_file = path.join(data_path, 'config.toml')

config = {}


def load_config():
    '''从文件读取全部配置'''
    global config
    config = toml.load(config_file)


def dump_config():
    '''将全部配置写入文件'''
    with open(config_file, 'w', encoding='utf-8') as f:
        toml.dump(config, f)


def get_config(key: str):
    '''获取指定配置'''
    load_config()
    return config.get(key)


def get_plugin_config(plugin_name: str, config_name: str):
    '''获取插件配置项'''
    plugin_config = get_config(plugin_name)
    if plugin_config is None:
        return None
    return plugin_config.get(config_name)


def add_config(key: str, value):
    '''新增或更新配置'''
    global config
    config[key] = value
    if key != 'ctime':
        config['ctime'] = int(time.time())
    dump_config()


def add_plugin_config(plugin_name: str, config_name: str, config_value):
    '''新增或更新插件配置项'''
    global config
    add_config(plugin_name, {config_name: config_value})


def del_config(key: str):
    '''删除指定配置'''
    global config
    del config[key]
    config['ctime'] = int(time.time())
    dump_config()


if path.isfile(config_file):
    load_config()
else:
    # 若不存在配置文件，则从默认配置文件获取
    config = toml.load(path.join(data_path, 'config_example.toml'))
    dump_config()

# END CONFIG
########################################################################


########################################################################
# SWITCH

def get_global_switch(plugin_name: str, switch_type: str = 'command') -> Union[bool,None]:
    '''获取指定插件的全局启用状态'''
    switch = get_config('switch')
    if switch is None:
        switch = {}
    plugin_switch = switch.get(plugin_name)
    if plugin_switch is None:
        plugin_switch = {}
    switch_status = plugin_switch.get(switch_type)
    return switch_status


def set_global_switch(plugin_name: str, switch_status: bool, switch_type: str = 'command'):
    '''设置指定插件的全局启用状态'''
    switch = get_config('switch')
    if switch is None:
        switch = {}
    plugin_switch = {switch_type: switch_status}
    switch[plugin_name] = plugin_switch
    add_config('switch', switch)

# END SWITCH
########################################################################
