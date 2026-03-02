"""
buy Spider V2 API 模块
层级蓝图注册：
- 从 use_spider/youpin/API.py 接收前缀 /backENDV2/src/use_spider/youpin
- 定义所有 buy 路由，添加 /buy/ 路径段
完整 URL 格式: /backENDV2/src/use_spider/youpin/buy/<endpoint>
"""
from flask import Blueprint
from .units.buy_insert import BuyInsert
from .units.buy_query import BuyQuery

buy_spider_blueprint = Blueprint('buy_spider', __name__)

# 查询类路由
buy_spider_blueprint.route('/buy/selectApexTime/<data_user>',            methods=['GET'])(BuyQuery.select_apex_time)
buy_spider_blueprint.route('/buy/selectApexTime',                        methods=['GET'])(BuyQuery.select_apex_time)
buy_spider_blueprint.route('/buy/getWeaponNotEndStatusList/<data_user>', methods=['GET'])(BuyQuery.get_weapon_not_end_status_list)
buy_spider_blueprint.route('/buy/selectNotEndID/<data_user>',            methods=['GET'])(BuyQuery.select_not_end_id)
buy_spider_blueprint.route('/buy/getCount/<data_user>',                  methods=['GET'])(BuyQuery.get_count)

# 写入/更新类路由
buy_spider_blueprint.route('/buy/insert_webside_buydata',                methods=['POST'])(BuyInsert.insert_webside_buydata)
buy_spider_blueprint.route('/buy/insert_main_buydata',                   methods=['POST'])(BuyInsert.insert_main_buydata)
buy_spider_blueprint.route('/buy/updateBuyData',                         methods=['POST'])(BuyInsert.update_buy_data)
buy_spider_blueprint.route('/buy/updateSaleAfterWithdrawal',             methods=['POST'])(BuyInsert.update_sale_after_withdrawal)
