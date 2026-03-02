"""
完美世界 config 处理模块
直接引用 web_side/prefectWorld/prefectworld_config.py 中的处理函数
"""
from src.web_side.prefectWorld.prefectworld_config import get_prefectworld_config


class ConfigHandler:
    get_config = staticmethod(get_prefectworld_config)
