"""
BUFF sell Spider V2 API 模块
层级蓝图注册：
- 从 use_spider/buff/API.py 接收前缀 /backENDV2/src/use_spider/buff
- 定义所有 sell 路由，添加 /sell/ 路径段
完整 URL 格式: /backENDV2/src/use_spider/buff/sell/<endpoint>
"""
from flask import Blueprint
from .units.sell_insert import SellInsert
from .units.sell_query import SellQuery

sell_spider_blueprint = Blueprint('buff_sell_spider', __name__)

# 查询类路由
sell_spider_blueprint.route('/sell/selectNotEnd/<user_id>',  methods=['GET'])(SellQuery.select_not_end)
sell_spider_blueprint.route('/sell/ApexTimeUrl/<user_id>',   methods=['GET'])(SellQuery.apex_time_url)
sell_spider_blueprint.route('/sell/getLatestData/<user_id>', methods=['GET'])(SellQuery.get_latest_data)
sell_spider_blueprint.route('/sell/countData/<user_id>',     methods=['GET'])(SellQuery.count_data)

# 写入/更新类路由
sell_spider_blueprint.route('/sell/insert_db',               methods=['POST'])(SellInsert.insert_db)
sell_spider_blueprint.route('/sell/updateOrderStatus',       methods=['POST'])(SellInsert.update_order_status)
