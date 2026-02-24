"""
Home 图表数据 API Blueprint
层级蓝图注册：
- 从 units/API.py 接收前缀 /backENDV2/src/web_display/home/units/charts
- 注册 4 个图表数据路由
"""
from flask import Blueprint
from .home_charts import get_all_inventory, get_all_components, get_all_buy, get_all_sell

home_charts_blueprint = Blueprint('home_charts', __name__)
home_charts_blueprint.route('/inventory/all', methods=['GET'])(get_all_inventory)
home_charts_blueprint.route('/components/all', methods=['GET'])(get_all_components)
home_charts_blueprint.route('/buy/all', methods=['GET'])(get_all_buy)
home_charts_blueprint.route('/sell/all', methods=['GET'])(get_all_sell)
