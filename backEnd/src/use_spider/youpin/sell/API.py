"""
sell Spider V2 API 模块
层级蓝图注册：
- 从 use_spider/youpin/API.py 接收前缀 /backENDV2/src/use_spider/youpin
- 定义所有 sell 路由，添加 /sell/ 路径段
完整 URL 格式: /backENDV2/src/use_spider/youpin/sell/<endpoint>
"""
from flask import Blueprint
from .units.sell_insert import SellInsert
from .units.sell_query import SellQuery

sell_spider_blueprint = Blueprint('sell_spider', __name__)

# 查询类路由
sell_spider_blueprint.route('/sell/selectApexTime/<data_user>',            methods=['GET'])(SellQuery.select_apex_time)
sell_spider_blueprint.route('/sell/getWeaponNotEndStatusList/<data_user>', methods=['GET'])(SellQuery.get_weapon_not_end_status_list)
sell_spider_blueprint.route('/sell/getCount/<data_user>',                  methods=['GET'])(SellQuery.get_count)

# 写入/更新类路由
sell_spider_blueprint.route('/sell/insert_webside_selldata',               methods=['POST'])(SellInsert.insert_webside_selldata)
sell_spider_blueprint.route('/sell/insert_main_selldata',                  methods=['POST'])(SellInsert.insert_main_selldata)
sell_spider_blueprint.route('/sell/updateSellData',                        methods=['POST'])(SellInsert.update_sell_data)
sell_spider_blueprint.route('/sell/updateSaleAfterWithdrawal',             methods=['POST'])(SellInsert.update_sale_after_withdrawal)
