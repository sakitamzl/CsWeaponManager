"""
rental Spider V2 API 模块
层级蓝图注册：
- 从 use_spider/youpin/API.py 接收前缀 /backENDV2/src/use_spider/youpin
- 定义所有 rental 路由，添加 /rental/ 路径段
完整 URL 格式: /backENDV2/src/use_spider/youpin/rental/<endpoint>
"""
from flask import Blueprint
from .units.rental_handler import RentalHandler

rental_spider_blueprint = Blueprint('rental_spider', __name__)

# 查询类路由
rental_spider_blueprint.route('/rental/selectApexTime/<steamId>',          methods=['GET'])(RentalHandler.select_apex_time)
rental_spider_blueprint.route('/rental/selectApexTime/<steamId>/<data_from>', methods=['GET'])(RentalHandler.select_apex_time)
rental_spider_blueprint.route('/rental/getCount/<steamId>',                methods=['GET'])(RentalHandler.get_count)
rental_spider_blueprint.route('/rental/getCount/<steamId>/<data_from>',    methods=['GET'])(RentalHandler.get_count)
rental_spider_blueprint.route('/rental/getNowRentalList',                  methods=['GET'])(RentalHandler.get_now_rental_list)
rental_spider_blueprint.route('/rental/getNowRentalList/<data_from>',      methods=['GET'])(RentalHandler.get_now_rental_list)
rental_spider_blueprint.route('/rental/getTimeOutRental',                  methods=['GET'])(RentalHandler.get_time_out_rental)

# 写入/更新类路由
rental_spider_blueprint.route('/rental/insert_rental_data',                methods=['POST'])(RentalHandler.insert_rental_data)
rental_spider_blueprint.route('/rental/updateRentalData',                  methods=['POST'])(RentalHandler.update_rental_data)
rental_spider_blueprint.route('/rental/updateMainRentalData',              methods=['POST'])(RentalHandler.update_main_rental_data)
