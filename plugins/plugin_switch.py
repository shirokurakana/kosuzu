from nonebot import CommandSession, on_command
from nonebot.permission import *
from utils import get_global_switch, set_global_switch


@on_command('set_plugin_gloabal_switch',
            aliases=('设置全局开关', '全局开关'),
            permission=SUPERUSER,
            only_to_me=False)
async def set_plugin_gloabal_switch(session: CommandSession):
    text = session.get('text', prompt='格式：<插件名> <状态> [<类型>]')
    cmd = text.split()
    n = len(cmd)
    if n == 2:
        plugin_name = cmd[0]
        switch_status_str = cmd[1]
        switch_type = 'command'
    elif n == 3:
        plugin_name = cmd[0]
        switch_status_str = cmd[1]
        switch_type = cmd[2]
    else:
        session.finish(f'参数数量错误，需要2或3个参数，给出{n}个')
    if switch_status_str in ['1', 'on', 'true', 'True', 'enable', '开', '开启', '启用']:
        if get_global_switch(plugin_name, switch_type) is True:
            session.finish('已全局启用该插件，无需重复启用')
        else:
            set_global_switch(plugin_name, True, switch_type)
            session.finish('该插件已成功全局启用')
    elif switch_status_str in ['0', 'off', 'false', 'False', 'disable', '关', '关闭', '禁用']:
        if get_global_switch(plugin_name, switch_type) is False:
            session.finish('已全局禁用该插件，无需重复禁用')
        else:
            set_global_switch(plugin_name, False, switch_type)
            session.finish('该插件已成功全局禁用')


@set_plugin_gloabal_switch.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_arg:
            session.state['text'] = stripped_arg


@on_command('check_plugin_gloabal_switch',
            aliases=('查看全局开关', '检查全局开关'),
            permission=SUPERUSER,
            only_to_me=False)
async def check_plugin_gloabal_switch(session: CommandSession):
    text = session.get('text', prompt='格式：<插件名> [<类型>]')
    cmd = text.split()
    n = len(cmd)
    if n == 1:
        plugin_name = cmd[0]
        switch_type = 'command'
    elif n == 2:
        plugin_name = cmd[0]
        switch_type = cmd[1]
    else:
        session.finish(f'参数数量错误，需要1或2个参数，给出{n}个')
    switch_status = get_global_switch(plugin_name, switch_type)
    if switch_status is None:
        session.finish('未找到该配置项，请检查')
    if switch_status is True:
        session.finish('该插件已全局启用')
    else:
        session.finish('该插件已全局禁用')


@check_plugin_gloabal_switch.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_arg:
            session.state['text'] = stripped_arg
