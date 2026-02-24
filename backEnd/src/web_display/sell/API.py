"""
Sell API 模块
层级蓝图注册：
- 从 web_display/API.py 接收前缀 /backENDV2/src/web_display
- 注册所有 Sell 页面路由，添加 /sell/units/xxx 路径段
"""
from flask import Blueprint
from .units.sell_data import get_sell_data_filtered, search_sell_by_time_range, search_by_type_and_wear
from .units.sell_stats import get_sell_stats_filtered, get_sell_stats_by_time_range, get_stats_by_type_and_wear
from .units.sell_filters import get_data_user_list, get_weapon_types, get_float_ranges, get_status_list, get_status_sub_list
from .units.price_info import get_yyyp_price_info

sell_blueprint = Blueprint('sell_v2', __name__)

# 数据查询路由
sell_blueprint.route('/sell/units/data/getSellDataFiltered', methods=['POST'])(get_sell_data_filtered)
sell_blueprint.route('/sell/units/data/searchSellByTimeRange/<start_date>/<end_date>', methods=['GET'])(search_sell_by_time_range)
sell_blueprint.route('/sell/units/data/searchByTypeAndWear', methods=['POST'])(search_by_type_and_wear)

# 统计路由
sell_blueprint.route('/sell/units/stats/getSellStatsFiltered', methods=['POST'])(get_sell_stats_filtered)
sell_blueprint.route('/sell/units/stats/getSellStatsByTimeRange/<start_date>/<end_date>', methods=['GET'])(get_sell_stats_by_time_range)
sell_blueprint.route('/sell/units/stats/getStatsByTypeAndWear', methods=['POST'])(get_stats_by_type_and_wear)

# 筛选选项路由
sell_blueprint.route('/sell/units/filters/getDataUserList', methods=['GET'])(get_data_user_list)
sell_blueprint.route('/sell/units/filters/getWeaponTypes', methods=['GET'])(get_weapon_types)
sell_blueprint.route('/sell/units/filters/getFloatRanges', methods=['GET'])(get_float_ranges)
sell_blueprint.route('/sell/units/filters/getStatusList', methods=['GET'])(get_status_list)
sell_blueprint.route('/sell/units/filters/getStatusSubList', methods=['GET'])(get_status_sub_list)

# 价格查询路由
sell_blueprint.route('/sell/units/price_info/getYyypPriceInfo/<steam_hash_name>', methods=['GET'])(get_yyyp_price_info)
