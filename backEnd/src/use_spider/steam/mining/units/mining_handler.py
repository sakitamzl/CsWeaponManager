"""
Steam mining 处理模块
直接引用 web_side/steam/inventory_mining.py 中的处理函数
"""
from src.web_side.steam.inventory_mining import (
    clear_mining_data,
    batch_save_mining_data,
    get_latest_source_steam_id,
    query_mining_data,
    get_mining_stats,
    get_mining_history,
    delete_mining_history,
)


class MiningHandler:
    clear = staticmethod(clear_mining_data)
    batch = staticmethod(batch_save_mining_data)
    latest = staticmethod(get_latest_source_steam_id)
    query = staticmethod(query_mining_data)
    stats = staticmethod(get_mining_stats)
    history = staticmethod(get_mining_history)
    delete_history = staticmethod(delete_mining_history)
