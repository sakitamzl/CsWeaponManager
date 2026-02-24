"""
Home API 模块
层级蓝图注册：
- 从 web_display/API.py 接收前缀 /backENDV2/src/web_display
- 向下传递给 units 模块，添加 /home 路径段
"""
from flask import Blueprint
from .units.API import home_units_blueprint

home_blueprint = Blueprint('home_v2', __name__)
home_blueprint.register_blueprint(home_units_blueprint, url_prefix='/units')
