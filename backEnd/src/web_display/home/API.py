"""
Home API 模块
层级蓝图注册：
- 从 web_display/API.py 接收前缀 /backENDV2/src/web_display
- 注册所有 Home 页面路由，添加 /home/units/xxx 路径段
"""
from flask import Blueprint
from .units.home_charts import HomeCharts
from .units.buy_stats import HomeBuyStats
from .units.steam_accounts import SteamAccounts
from .units.inventory import HomeInventory
from .units.components import HomeComponents
from .units.steamdt_homepage import SteamDTHomepage

home_blueprint = Blueprint('home_v2', __name__)

# 图表数据路由
home_blueprint.route('/home/units/charts/inventory/all', methods=['GET'])(HomeCharts.get_all_inventory)
home_blueprint.route('/home/units/charts/components/all', methods=['GET'])(HomeCharts.get_all_components)
home_blueprint.route('/home/units/charts/buy/all', methods=['GET'])(HomeCharts.get_all_buy)
home_blueprint.route('/home/units/charts/sell/all', methods=['GET'])(HomeCharts.get_all_sell)

# 购买统计路由
home_blueprint.route('/home/units/buy_stats/getBuyStats', methods=['GET'])(HomeBuyStats.get_buy_stats)

# Steam 账号列表路由
home_blueprint.route('/home/units/steam_accounts/steam_ids', methods=['GET'])(SteamAccounts.get_steam_ids)

# 指定账号库存路由
home_blueprint.route('/home/units/inventory/<steam_id>', methods=['GET'])(HomeInventory.get_inventory)

# 指定账号组件路由
home_blueprint.route('/home/units/components/<steam_id>', methods=['GET'])(HomeComponents.get_components)

# SteamDT 首页数据路由
home_blueprint.route('/home/units/steamdt/homepage-data', methods=['GET'])(SteamDTHomepage.get_homepage_data)
