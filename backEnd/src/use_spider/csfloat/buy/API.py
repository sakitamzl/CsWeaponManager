"""
CSFloat buy Spider V2 API 模块
层级蓝图注册：
- 从 use_spider/csfloat/API.py 接收前缀 /backENDV2/src/use_spider/csfloat
- 定义所有 buy 路由，添加 /buy/ 路径段
完整 URL 格式: /backENDV2/src/use_spider/csfloat/buy/<endpoint>
"""
from flask import Blueprint
from .units.buy_insert import BuyInsert
from .units.buy_query import BuyQuery

buy_spider_blueprint = Blueprint('csfloat_buy_spider', __name__)

# 查询类路由
buy_spider_blueprint.route('/buy/selectNotEnd/<user_id>',              methods=['GET'])(BuyQuery.select_not_end)
buy_spider_blueprint.route('/buy/getLatestData/<user_id>',             methods=['GET'])(BuyQuery.get_latest_data)
buy_spider_blueprint.route('/buy/countData/<user_id>',                 methods=['GET'])(BuyQuery.count_data)
buy_spider_blueprint.route('/buy/getEarliestNotEnd/<user_id>',         methods=['GET'])(BuyQuery.get_earliest_not_end)

# 解析类路由（供 Spider 查询武器/饰品信息）
buy_spider_blueprint.route('/buy/resolveWeapon',                       methods=['POST'])(BuyInsert.resolve_weapon)
buy_spider_blueprint.route('/buy/resolveAccessory',                    methods=['POST'])(BuyInsert.resolve_accessory)

# 写入/更新/删除类路由
buy_spider_blueprint.route('/buy/insert_db',                           methods=['POST'])(BuyInsert.insert_db)
buy_spider_blueprint.route('/buy/updateOrderStatus',                   methods=['POST'])(BuyInsert.update_order_status)
buy_spider_blueprint.route('/buy/deleteRecentDays/<user_id>/<int:days>',methods=['DELETE'])(BuyInsert.delete_recent_days)
buy_spider_blueprint.route('/buy/deleteFromTime/<user_id>',            methods=['POST'])(BuyInsert.delete_from_time)
