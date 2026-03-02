"""
sys_message API 模块
层级蓝图注册：
- 从 settings/API.py 接收前缀 /backENDV2/src/web_display/settings
- 向下添加 /sys_message 路径段
最终路径示例：
  GET  /backENDV2/src/web_display/settings/sys_message/list/<page>/<limit>
  GET  /backENDV2/src/web_display/settings/sys_message/stats
  GET  /backENDV2/src/web_display/settings/sys_message/types
  GET  /backENDV2/src/web_display/settings/sys_message/sources
  POST /backENDV2/src/web_display/settings/sys_message/mark_read
  POST /backENDV2/src/web_display/settings/sys_message/mark_all_read
  POST /backENDV2/src/web_display/settings/sys_message/delete
  POST /backENDV2/src/web_display/settings/sys_message/search/keyword
  POST /backENDV2/src/web_display/settings/sys_message/search/time
  POST /backENDV2/src/web_display/settings/sys_message/search/filter
  POST /backENDV2/src/web_display/settings/sys_message/create
"""
from flask import Blueprint
from .units.sys_message_handler import SysMessageHandler

sys_message_blueprint = Blueprint('sys_message_v2', __name__)

sys_message_blueprint.add_url_rule('/sys_message/list/<int:page>/<int:limit>', view_func=SysMessageHandler.get_sys_message_data, methods=['GET'])
sys_message_blueprint.add_url_rule('/sys_message/stats', view_func=SysMessageHandler.get_sys_message_stats, methods=['GET'])
sys_message_blueprint.add_url_rule('/sys_message/types', view_func=SysMessageHandler.get_sys_message_types, methods=['GET'])
sys_message_blueprint.add_url_rule('/sys_message/sources', view_func=SysMessageHandler.get_sys_message_sources, methods=['GET'])
sys_message_blueprint.add_url_rule('/sys_message/mark_read', view_func=SysMessageHandler.mark_as_read, methods=['POST'])
sys_message_blueprint.add_url_rule('/sys_message/mark_all_read', view_func=SysMessageHandler.mark_all_as_read, methods=['POST'])
sys_message_blueprint.add_url_rule('/sys_message/delete', view_func=SysMessageHandler.delete_sys_message, methods=['POST'])
sys_message_blueprint.add_url_rule('/sys_message/search/keyword', view_func=SysMessageHandler.search_by_keyword, methods=['POST'])
sys_message_blueprint.add_url_rule('/sys_message/search/time', view_func=SysMessageHandler.search_by_time, methods=['POST'])
sys_message_blueprint.add_url_rule('/sys_message/search/filter', view_func=SysMessageHandler.search_by_filter, methods=['POST'])
sys_message_blueprint.add_url_rule('/sys_message/create', view_func=SysMessageHandler.create_sys_message, methods=['POST'])
