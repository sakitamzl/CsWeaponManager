"""
Home 指定账号组件 API Blueprint
层级蓝图注册：
- 从 units/API.py 接收前缀 /backENDV2/src/web_display/home/units/components
- 注册指定账号组件路由
"""
from flask import Blueprint
from .components import get_components

home_components_blueprint = Blueprint('home_components', __name__)
home_components_blueprint.route('/<steam_id>', methods=['GET'])(get_components)
