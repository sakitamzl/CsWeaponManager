"""
Home SteamDT 首页数据 API Blueprint
层级蓝图注册：
- 从 units/API.py 接收前缀 /backENDV2/src/web_display/home/units/steamdt
- 注册 SteamDT 首页数据路由
"""
from flask import Blueprint
from .steamdt_homepage import get_homepage_data

home_steamdt_blueprint = Blueprint('home_steamdt', __name__)
home_steamdt_blueprint.route('/homepage-data', methods=['GET'])(get_homepage_data)
