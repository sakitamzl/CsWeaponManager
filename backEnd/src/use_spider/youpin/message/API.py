"""
message Spider V2 API 模块
层级蓝图注册：
- 从 use_spider/youpin/API.py 接收前缀 /backENDV2/src/use_spider/youpin
- 定义所有 message 路由，添加 /message/ 路径段
完整 URL 格式: /backENDV2/src/use_spider/youpin/message/<endpoint>
"""
from flask import Blueprint
from .units.message_handler import MessageHandler

message_spider_blueprint = Blueprint('message_spider', __name__)

# 查询类路由
message_spider_blueprint.route('/message/selectApexTime/<steamId>', methods=['GET'])(MessageHandler.select_apex_time)
message_spider_blueprint.route('/message/getCount/<steamId>',       methods=['GET'])(MessageHandler.get_count)

# 写入类路由
message_spider_blueprint.route('/message/insert_message_data',      methods=['POST'])(MessageHandler.insert_message_data)
