"""
Sell API 模块
层级蓝图注册：
- 从 web_display/API.py 接收前缀 /backENDV2/src/web_display
- 注册所有 Sell 页面路由，添加 /sell/units/xxx 路径段
"""
from flask import Blueprint
from .units.sell_data import SellData
from .units.sell_stats import SellStats
from .units.sell_filters import SellFilters
from .units.price_info import SellPriceInfo

sell_blueprint = Blueprint('sell_v2', __name__)

# 数据查询路由
sell_blueprint.route('/sell/units/data/getSellDataFiltered', methods=['POST'])(SellData.get_sell_data_filtered)
sell_blueprint.route('/sell/units/data/searchSellByTimeRange/<start_date>/<end_date>', methods=['GET'])(SellData.search_sell_by_time_range)
sell_blueprint.route('/sell/units/data/searchByTypeAndWear', methods=['POST'])(SellData.search_by_type_and_wear)

# 统计路由
sell_blueprint.route('/sell/units/stats/getSellStatsFiltered', methods=['POST'])(SellStats.get_sell_stats_filtered)
sell_blueprint.route('/sell/units/stats/getSellStatsByTimeRange/<start_date>/<end_date>', methods=['GET'])(SellStats.get_sell_stats_by_time_range)
sell_blueprint.route('/sell/units/stats/getStatsByTypeAndWear', methods=['POST'])(SellStats.get_stats_by_type_and_wear)

# 筛选选项路由
sell_blueprint.route('/sell/units/filters/getDataUserList', methods=['GET'])(SellFilters.get_data_user_list)
sell_blueprint.route('/sell/units/filters/getWeaponTypes', methods=['GET'])(SellFilters.get_weapon_types)
sell_blueprint.route('/sell/units/filters/getFloatRanges', methods=['GET'])(SellFilters.get_float_ranges)
sell_blueprint.route('/sell/units/filters/getStatusList', methods=['GET'])(SellFilters.get_status_list)
sell_blueprint.route('/sell/units/filters/getStatusSubList', methods=['GET'])(SellFilters.get_status_sub_list)

# 价格查询路由
sell_blueprint.route('/sell/units/price_info/getYyypPriceInfo/<steam_hash_name>', methods=['GET'])(SellPriceInfo.get_yyyp_price_info)
