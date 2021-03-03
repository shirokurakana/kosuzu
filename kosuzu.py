from os import path

import nonebot

import config

ROOT_PATH = path.dirname(__file__)

if __name__ == '__main__':

    nonebot.init(config)

    nonebot.load_plugins(
        path.join(ROOT_PATH, 'plugins'),
        'plugins'
    )

    nonebot.run()
