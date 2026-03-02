"""
Inventory API 模块
层级蓝图注册：
- 从 use_webside/API.py 接收前缀 /backENDV2/src/use_webside
- 注册所有 Inventory 页面路由，添加 /inventory/units/xxx 路径段
"""
from flask import Blueprint
from .units.accounts import InventoryAccounts
from .units.data import InventoryData
from .units.stats import InventoryStats
from .units.price import InventoryPrice

inventory_blueprint = Blueprint('inventory_v2', __name__)

# 账号查询路由
inventory_blueprint.route('/inventory/units/accounts/getSteamIds', methods=['GET'])(InventoryAccounts.get_steam_ids)

# 库存数据路由
inventory_blueprint.route('/inventory/units/data/getInventory/<steam_id>', methods=['GET'])(InventoryData.get_inventory)
inventory_blueprint.route('/inventory/units/data/getGroupedInventory/<steam_id>', methods=['GET'])(InventoryData.get_grouped_inventory)
inventory_blueprint.route('/inventory/units/data/updateBuyPrice/<steam_id>/<assetid>', methods=['PUT'])(InventoryData.update_buy_price)

# 统计路由
inventory_blueprint.route('/inventory/units/stats/getInventoryStats/<steam_id>', methods=['GET'])(InventoryStats.get_inventory_stats)

# 价格查询路由
inventory_blueprint.route('/inventory/units/price/getYYYPLowestPrice', methods=['POST'])(InventoryPrice.get_yyyp_lowest_price)
inventory_blueprint.route('/inventory/units/price/getPendantPrice', methods=['POST'])(InventoryPrice.get_pendant_price)
inventory_blueprint.route('/inventory/units/price/getAllPendants', methods=['GET'])(InventoryPrice.get_all_pendants)