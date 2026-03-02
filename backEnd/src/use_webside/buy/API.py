"""
Buy API 模块
层级蓝图注册：
- 从 use_webside/API.py 接收前缀 /backENDV2/src/use_webside
- 注册所有 Buy 页面路由，添加 /buy/units/xxx 路径段
"""
from flask import Blueprint
from .units.buy_data import BuyData
from .units.buy_stats import BuyStats
from .units.buy_filters import BuyFilters
from .units.price_info import BuyPriceInfo

buy_blueprint = Blueprint('buy_v2', __name__)

# 数据查询路由
buy_blueprint.route('/buy/units/data/getBuyDataFiltered', methods=['POST'])(BuyData.get_buy_data_filtered)
buy_blueprint.route('/buy/units/data/countBuyNumber', methods=['GET'])(BuyData.count_buy_number)
buy_blueprint.route('/buy/units/data/searchBuyByTimeRange/<start_date>/<end_date>', methods=['GET'])(BuyData.search_buy_by_time_range)
buy_blueprint.route('/buy/units/data/searchByTypeAndWear', methods=['POST'])(BuyData.search_by_type_and_wear)

# 统计路由
buy_blueprint.route('/buy/units/stats/getBuyStatsFiltered', methods=['POST'])(BuyStats.get_buy_stats_filtered)
buy_blueprint.route('/buy/units/stats/getBuyStatsByTimeRange/<start_date>/<end_date>', methods=['GET'])(BuyStats.get_buy_stats_by_time_range)
buy_blueprint.route('/buy/units/stats/getStatsByTypeAndWear', methods=['POST'])(BuyStats.get_stats_by_type_and_wear)

# 筛选选项路由
buy_blueprint.route('/buy/units/filters/getDataUserList', methods=['GET'])(BuyFilters.get_data_user_list)
buy_blueprint.route('/buy/units/filters/getWeaponTypes', methods=['GET'])(BuyFilters.get_weapon_types)
buy_blueprint.route('/buy/units/filters/getFloatRanges', methods=['GET'])(BuyFilters.get_float_ranges)
buy_blueprint.route('/buy/units/filters/getStatusList', methods=['GET'])(BuyFilters.get_status_list)
buy_blueprint.route('/buy/units/filters/getStatusSubList', methods=['GET'])(BuyFilters.get_status_sub_list)

# 价格查询路由
buy_blueprint.route('/buy/units/price_info/getYyypPriceInfo/<steam_hash_name>', methods=['GET'])(BuyPriceInfo.get_yyyp_price_info)
