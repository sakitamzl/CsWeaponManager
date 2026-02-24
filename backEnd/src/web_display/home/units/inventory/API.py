"""
Home 指定账号库存 API Blueprint
层级蓝图注册：
- 从 units/API.py 接收前缀 /backENDV2/src/web_display/home/units/inventory
- 注册指定账号库存路由
"""
from flask import Blueprint
from .inventory import get_inventory

home_inventory_blueprint = Blueprint('home_inventory', __name__)
home_inventory_blueprint.route('/<steam_id>', methods=['GET'])(get_inventory)
