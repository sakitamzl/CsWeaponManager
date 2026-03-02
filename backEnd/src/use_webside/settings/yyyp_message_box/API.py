"""
YyypMessageBox API 模块
层级蓝图注册：
- 从 settings/API.py 接收前缀 /backENDV2/src/use_webside/settings
- 注册所有 YyypMessageBox 路由，添加 /yyyp_message_box/units/data/xxx 路径段
"""
from flask import Blueprint
from .units.yyyp_message_box_data import YyypMessageBoxData

yyyp_message_box_blueprint = Blueprint('yyyp_message_box_v2', __name__)

yyyp_message_box_blueprint.route('/yyyp_message_box/units/data/getMessageData/<int:page>/<int:limit>', methods=['GET'])(YyypMessageBoxData.get_message_data)
yyyp_message_box_blueprint.route('/yyyp_message_box/units/data/getMessageStats', methods=['GET'])(YyypMessageBoxData.get_message_stats)
yyyp_message_box_blueprint.route('/yyyp_message_box/units/data/getMessageTypes', methods=['GET'])(YyypMessageBoxData.get_message_types)
yyyp_message_box_blueprint.route('/yyyp_message_box/units/data/searchByKeyword', methods=['POST'])(YyypMessageBoxData.search_by_keyword)
yyyp_message_box_blueprint.route('/yyyp_message_box/units/data/searchByTime', methods=['POST'])(YyypMessageBoxData.search_by_time)
yyyp_message_box_blueprint.route('/yyyp_message_box/units/data/searchByType', methods=['POST'])(YyypMessageBoxData.search_by_type)
