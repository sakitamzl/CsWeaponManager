"""
BuffMessageBox API 模块
层级蓝图注册：
- 从 settings/API.py 接收前缀 /backENDV2/src/web_display/settings
- 注册所有 BuffMessageBox 路由，添加 /buff_message_box/units/data/xxx 路径段
"""
from flask import Blueprint
from .units.buff_message_box_data import BuffMessageBoxData

buff_message_box_blueprint = Blueprint('buff_message_box_v2', __name__)

buff_message_box_blueprint.route('/buff_message_box/units/data/getMessageData/<int:page>/<int:limit>', methods=['GET'])(BuffMessageBoxData.get_message_data)
buff_message_box_blueprint.route('/buff_message_box/units/data/getMessageTypes', methods=['GET'])(BuffMessageBoxData.get_message_types)
