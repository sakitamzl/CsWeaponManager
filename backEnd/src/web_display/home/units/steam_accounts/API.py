"""
Home Steam 账号列表 API Blueprint
层级蓝图注册：
- 从 units/API.py 接收前缀 /backENDV2/src/web_display/home/units/steam_accounts
- 注册 Steam 账号列表路由
"""
from flask import Blueprint
from .steam_accounts import get_steam_ids

home_steam_accounts_blueprint = Blueprint('home_steam_accounts', __name__)
home_steam_accounts_blueprint.route('/steam_ids', methods=['GET'])(get_steam_ids)
