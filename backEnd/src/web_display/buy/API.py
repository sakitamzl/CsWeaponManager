"""
Buy API 模块
层级蓝图注册：
- 从 web_display/API.py 接收前缀 /backENDV2/src/web_display
- 注册所有 Buy 页面路由，添加 /buy/units/xxx 路径段
"""
from flask import Blueprint
from .units.buy_data import get_buy_data_filtered, count_buy_number, search_buy_by_time_range, search_by_type_and_wear
from .units.buy_stats import get_buy_stats_filtered, get_buy_stats_by_time_range, get_stats_by_type_and_wear
from .units.buy_filters import get_data_user_list, get_weapon_types, get_float_ranges, get_status_list, get_status_sub_list
from .units.price_info import get_yyyp_price_info

buy_blueprint = Blueprint('buy_v2', __name__)

# 数据查询路由
buy_blueprint.route('/buy/units/data/getBuyDataFiltered', methods=['POST'])(get_buy_data_filtered)
buy_blueprint.route('/buy/units/data/countBuyNumber', methods=['GET'])(count_buy_number)
buy_blueprint.route('/buy/units/data/searchBuyByTimeRange/<start_date>/<end_date>', methods=['GET'])(search_buy_by_time_range)
buy_blueprint.route('/buy/units/data/searchByTypeAndWear', methods=['POST'])(search_by_type_and_wear)

# 统计路由
buy_blueprint.route('/buy/units/stats/getBuyStatsFiltered', methods=['POST'])(get_buy_stats_filtered)
buy_blueprint.route('/buy/units/stats/getBuyStatsByTimeRange/<start_date>/<end_date>', methods=['GET'])(get_buy_stats_by_time_range)
buy_blueprint.route('/buy/units/stats/getStatsByTypeAndWear', methods=['POST'])(get_stats_by_type_and_wear)

# 筛选选项路由
buy_blueprint.route('/buy/units/filters/getDataUserList', methods=['GET'])(get_data_user_list)
buy_blueprint.route('/buy/units/filters/getWeaponTypes', methods=['GET'])(get_weapon_types)
buy_blueprint.route('/buy/units/filters/getFloatRanges', methods=['GET'])(get_float_ranges)
buy_blueprint.route('/buy/units/filters/getStatusList', methods=['GET'])(get_status_list)
buy_blueprint.route('/buy/units/filters/getStatusSubList', methods=['GET'])(get_status_sub_list)

# 价格查询路由
buy_blueprint.route('/buy/units/price_info/getYyypPriceInfo/<steam_hash_name>', methods=['GET'])(get_yyyp_price_info)
