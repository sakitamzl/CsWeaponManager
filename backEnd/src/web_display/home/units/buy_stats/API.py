"""
Home 购买统计 API Blueprint
层级蓝图注册：
- 从 units/API.py 接收前缀 /backENDV2/src/web_display/home/units/buy_stats
- 注册购买统计路由
"""
from flask import Blueprint
from .buy_stats import get_buy_stats

home_buy_stats_blueprint = Blueprint('home_buy_stats', __name__)
home_buy_stats_blueprint.route('/getBuyStats', methods=['GET'])(get_buy_stats)
