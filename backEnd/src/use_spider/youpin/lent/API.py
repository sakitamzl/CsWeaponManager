"""
lent Spider V2 API 模块
层级蓝图注册：
- 从 use_spider/youpin/API.py 接收前缀 /backENDV2/src/use_spider/youpin
- 定义所有 lent 路由，添加 /lent/ 路径段
完整 URL 格式: /backENDV2/src/use_spider/youpin/lent/<endpoint>
"""
from flask import Blueprint
from .units.lent_insert import LentInsert
from .units.lent_query import LentQuery

lent_spider_blueprint = Blueprint('lent_spider', __name__)

# 查询类路由
lent_spider_blueprint.route('/lent/selectApexTime/<steamId>',   methods=['GET'])(LentQuery.select_apex_time)
lent_spider_blueprint.route('/lent/getCount/<steamId>',         methods=['GET'])(LentQuery.get_count)
lent_spider_blueprint.route('/lent/getNowLentingList',          methods=['GET'])(LentQuery.get_now_lenting_list)
lent_spider_blueprint.route('/lent/getTimeOutLent',             methods=['GET'])(LentQuery.get_time_out_lent)
lent_spider_blueprint.route('/lent/getBuyoutLentList/<steamId>',methods=['GET'])(LentQuery.get_buyout_lent_list)

# 写入/更新类路由
lent_spider_blueprint.route('/lent/insert_webside_lentdata',    methods=['POST'])(LentInsert.insert_webside_lentdata)
lent_spider_blueprint.route('/lent/insert_main_lentdata',       methods=['POST'])(LentInsert.insert_main_lentdata)
lent_spider_blueprint.route('/lent/updateLentData',             methods=['POST'])(LentInsert.update_lent_data)
lent_spider_blueprint.route('/lent/updateMainLentData',         methods=['POST'])(LentInsert.update_main_lent_data)
