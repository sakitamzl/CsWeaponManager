"""
Rental API 模块
层级蓝图注册：
- 从 web_display/API.py 接收前缀 /backENDV2/src/web_display
- 注册所有 Rental 页面路由，添加 /rental/units/xxx 路径段
"""
from flask import Blueprint
from .units.rental_data import RentalData
from .units.rental_stats import RentalStats
from .units.rental_filters import RentalFilters

rental_blueprint = Blueprint('rental_v2', __name__)

# 数据查询路由
rental_blueprint.route('/rental/units/data/getRentalData/<int:min>/<int:max>', methods=['GET'])(RentalData.get_rental_data)
rental_blueprint.route('/rental/units/data/getRentalDataByStatus/<status>/<int:min>/<int:max>', methods=['GET'])(RentalData.get_rental_data_by_status)
rental_blueprint.route('/rental/units/data/getRentalDataByStatusSub/<path:last_status>/<int:min>/<int:max>', methods=['GET'])(RentalData.get_rental_data_by_status_sub)
rental_blueprint.route('/rental/units/data/selectRentalWeaponName/<item_name>', methods=['GET'])(RentalData.select_rental_weapon_name)
rental_blueprint.route('/rental/units/data/searchRentalByTimeRange/<start_date>/<end_date>', methods=['GET'])(RentalData.search_rental_by_time_range)

# 统计路由
rental_blueprint.route('/rental/units/stats/getRentalStats', methods=['GET'])(RentalStats.get_rental_stats)
rental_blueprint.route('/rental/units/stats/getRentalStatsByTimeRange/<start_date>/<end_date>', methods=['GET'])(RentalStats.get_rental_stats_by_time_range)

# 筛选选项路由
rental_blueprint.route('/rental/units/filters/getRentalWeaponTypes', methods=['GET'])(RentalFilters.get_rental_weapon_types)
rental_blueprint.route('/rental/units/filters/getRentalFloatRanges', methods=['GET'])(RentalFilters.get_rental_float_ranges)
rental_blueprint.route('/rental/units/filters/getRentalStatusList', methods=['GET'])(RentalFilters.get_rental_status_list)
rental_blueprint.route('/rental/units/filters/getRentalStatusSubList', methods=['GET'])(RentalFilters.get_rental_status_sub_list)
rental_blueprint.route('/rental/units/filters/getRentalStatusSubList/<status>', methods=['GET'])(RentalFilters.get_rental_status_sub_list)
rental_blueprint.route('/rental/units/filters/getRentalPlatformList', methods=['GET'])(RentalFilters.get_rental_platform_list)
rental_blueprint.route('/rental/units/filters/getRentalUserList', methods=['GET'])(RentalFilters.get_rental_user_list)
