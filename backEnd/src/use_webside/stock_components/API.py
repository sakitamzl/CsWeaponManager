"""
StockComponents API 模块
层级蓝图注册：
- 从 use_webside/API.py 接收前缀 /backENDV2/src/use_webside
- 注册所有 StockComponents 页面路由，添加 /stock_components/units/xxx 路径段
"""
from flask import Blueprint
from .units.accounts import StockComponentsAccounts
from .units.data import StockComponentsData
from .units.stats import StockComponentsStats
from .units.filters import StockComponentsFilters
from .units.price import StockComponentsPrice

stock_components_blueprint = Blueprint('stock_components_v2', __name__)

# 账号查询路由
stock_components_blueprint.route('/stock_components/units/accounts/getSteamIds', methods=['GET'])(StockComponentsAccounts.get_steam_ids)
stock_components_blueprint.route('/stock_components/units/accounts/getComponentCount/<steam_id>', methods=['GET'])(StockComponentsAccounts.get_component_count)

# 筛选选项路由
stock_components_blueprint.route('/stock_components/units/filters/getWeaponTypes/<steam_id>', methods=['GET'])(StockComponentsFilters.get_weapon_types)
stock_components_blueprint.route('/stock_components/units/filters/getFloatRanges/<steam_id>', methods=['GET'])(StockComponentsFilters.get_float_ranges)

# 数据查询路由
stock_components_blueprint.route('/stock_components/units/data/getComponentInventory/<steam_id>', methods=['GET'])(StockComponentsData.get_component_inventory)
stock_components_blueprint.route('/stock_components/units/data/getComponents/<steam_id>', methods=['GET'])(StockComponentsData.get_components)
stock_components_blueprint.route('/stock_components/units/data/getGroupedComponents/<steam_id>', methods=['GET'])(StockComponentsData.get_grouped_components)

# 统计路由
stock_components_blueprint.route('/stock_components/units/stats/getComponentsStats/<steam_id>', methods=['GET'])(StockComponentsStats.get_components_stats)

# 价格操作路由
stock_components_blueprint.route('/stock_components/units/price/updateBuyPrice/<steam_id>/<goods_assetid>', methods=['PUT'])(StockComponentsPrice.update_buy_price)
stock_components_blueprint.route('/stock_components/units/price/autoFillPrices/<steam_id>', methods=['POST'])(StockComponentsPrice.auto_fill_prices)
stock_components_blueprint.route('/stock_components/units/price/fillReferencePrice/<steam_id>/<source>', methods=['POST'])(StockComponentsPrice.fill_reference_price)
