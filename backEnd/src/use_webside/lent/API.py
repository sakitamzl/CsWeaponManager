"""
Lent API 模块
层级蓝图注册：
- 从 use_webside/API.py 接收前缀 /backENDV2/src/use_webside
- 注册所有 Lent 页面路由，添加 /lent/units/xxx 路径段
"""
from flask import Blueprint
from .units.lent_data import LentData
from .units.lent_stats import LentStats
from .units.lent_filters import LentFilters

lent_blueprint = Blueprint('lent_v2', __name__)

# 数据查询路由
lent_blueprint.route('/lent/units/data/getLentData/<int:min>/<int:max>', methods=['GET'])(LentData.get_lent_data)
lent_blueprint.route('/lent/units/data/getLentDataByStatus/<status>/<int:min>/<int:max>', methods=['GET'])(LentData.get_lent_data_by_status)
lent_blueprint.route('/lent/units/data/getLentDataByStatusSub/<path:last_status>/<int:min>/<int:max>', methods=['GET'])(LentData.get_lent_data_by_status_sub)
lent_blueprint.route('/lent/units/data/getLentDataFiltered', methods=['POST'])(LentData.get_lent_data_filtered)
lent_blueprint.route('/lent/units/data/searchLentByTimeRange/<start_date>/<end_date>', methods=['GET'])(LentData.search_lent_by_time_range)
lent_blueprint.route('/lent/units/data/searchByTypeAndWear', methods=['POST'])(LentData.search_by_type_and_wear)

# 统计路由
lent_blueprint.route('/lent/units/stats/getLentStatsFiltered', methods=['POST'])(LentStats.get_lent_stats_filtered)
lent_blueprint.route('/lent/units/stats/getLentStatsByTimeRange/<start_date>/<end_date>', methods=['GET'])(LentStats.get_lent_stats_by_time_range)
lent_blueprint.route('/lent/units/stats/getStatsByTypeAndWear', methods=['POST'])(LentStats.get_stats_by_type_and_wear)

# 筛选选项路由
lent_blueprint.route('/lent/units/filters/getWeaponTypes', methods=['GET'])(LentFilters.get_weapon_types)
lent_blueprint.route('/lent/units/filters/getFloatRanges', methods=['GET'])(LentFilters.get_float_ranges)
lent_blueprint.route('/lent/units/filters/getStatusList', methods=['GET'])(LentFilters.get_status_list)
lent_blueprint.route('/lent/units/filters/getStatusSubList', methods=['GET'])(LentFilters.get_status_sub_list)
lent_blueprint.route('/lent/units/filters/getPlatformList', methods=['GET'])(LentFilters.get_platform_list)
lent_blueprint.route('/lent/units/filters/getLenterList', methods=['GET'])(LentFilters.get_lenter_list)
