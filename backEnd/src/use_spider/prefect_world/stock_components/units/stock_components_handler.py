"""
完美世界 stock_components 处理模块
直接引用 web_side/prefectWorld/stock_components_api.py 中的处理函数
"""
from src.web_side.prefectWorld.stock_components_api import (
    batch_insert_components,
    insert_single_component,
    delete_component,
    delete_component_by_assetid_and_user,
)


class StockComponentsHandler:
    batch = staticmethod(batch_insert_components)
    single = staticmethod(insert_single_component)
    delete = staticmethod(delete_component)
    delete_by_assetid_steam = staticmethod(delete_component_by_assetid_and_user)
