"""
SteamInventoryHistory API 模块
层级蓝图注册：
- 从 settings/API.py 接收前缀 /backENDV2/src/web_display/settings
- 注册所有 SteamInventoryHistory 路由，添加 /steam_inventory_history/units/xxx 路径段
"""
from flask import Blueprint
from .units.steam_inventory_history_data import SteamInventoryHistoryData

steam_inventory_history_blueprint = Blueprint('steam_inventory_history_v2', __name__)

# 数据查询
steam_inventory_history_blueprint.route(
    '/steam_inventory_history/units/data/getList', methods=['GET']
)(SteamInventoryHistoryData.get_list)
