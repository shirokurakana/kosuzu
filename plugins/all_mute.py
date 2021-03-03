from datetime import datetime

from nonebot import get_bot, scheduler
from utils import get_config, get_global_switch, get_plugin_config

bot = get_bot()


@scheduler.scheduled_job('cron', hour='*', minute='*')
async def _():
    if get_global_switch('plugins.all_mute', 'auto') is False:
        return
    start_time = get_plugin_config('plugins.all_mute', 'start_time')
    end_time = get_plugin_config('plugins.all_mute', 'end_time')
    main_group_id = get_config('main_group_id')
    now = datetime.now()
    if now.hour == start_time['hour']:
        if now.minute == start_time['minute']:
            await bot.set_group_whole_ban(
                group_id=main_group_id, enable=True)
    elif now.hour == end_time['hour']:
        if now.minute == end_time['minute']:
            await bot.set_group_whole_ban(
                group_id=main_group_id, enable=False)
