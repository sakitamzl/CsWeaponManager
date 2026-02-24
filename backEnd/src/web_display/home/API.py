"""
Home API 模块
层级蓝图注册：
- 从 web_display/API.py 接收前缀 /backENDV2/src/web_display
- 注册所有 Home 页面路由，添加 /home/units/xxx 路径段
"""
from flask import Blueprint
from .units.home_charts import get_all_inventory, get_all_components, get_all_buy, get_all_sell
from .units.buy_stats import get_buy_stats
from .units.steam_accounts import get_steam_ids
from .units.inventory import get_inventory
from .units.components import get_components
from .units.steamdt_homepage import get_homepage_data

home_blueprint = Blueprint('home_v2', __name__)

# 图表数据路由
home_blueprint.route('/home/units/charts/inventory/all', methods=['GET'])(get_all_inventory)
home_blueprint.route('/home/units/charts/components/all', methods=['GET'])(get_all_components)
home_blueprint.route('/home/units/charts/buy/all', methods=['GET'])(get_all_buy)
home_blueprint.route('/home/units/charts/sell/all', methods=['GET'])(get_all_sell)

# 购买统计路由
home_blueprint.route('/home/units/buy_stats/getBuyStats', methods=['GET'])(get_buy_stats)

# Steam 账号列表路由
home_blueprint.route('/home/units/steam_accounts/steam_ids', methods=['GET'])(get_steam_ids)

# 指定账号库存路由
home_blueprint.route('/home/units/inventory/<steam_id>', methods=['GET'])(get_inventory)

# 指定账号组件路由
home_blueprint.route('/home/units/components/<steam_id>', methods=['GET'])(get_components)

# SteamDT 首页数据路由
home_blueprint.route('/home/units/steamdt/homepage-data', methods=['GET'])(get_homepage_data)
