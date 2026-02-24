"""
Home Units 模块
层级蓝图注册：
- 从 home/API.py 接收前缀 /backENDV2/src/web_display/home/units
- 向下传递给各功能模块（charts, buy_stats, steam_accounts, inventory, components, steamdt）
"""
from flask import Blueprint
from .charts.API import home_charts_blueprint
from .buy_stats.API import home_buy_stats_blueprint
from .steam_accounts.API import home_steam_accounts_blueprint
from .inventory.API import home_inventory_blueprint
from .components.API import home_components_blueprint
from .steamdt.API import home_steamdt_blueprint

home_units_blueprint = Blueprint('home_units', __name__)
home_units_blueprint.register_blueprint(home_charts_blueprint, url_prefix='/charts')
home_units_blueprint.register_blueprint(home_buy_stats_blueprint, url_prefix='/buy_stats')
home_units_blueprint.register_blueprint(home_steam_accounts_blueprint, url_prefix='/steam_accounts')
home_units_blueprint.register_blueprint(home_inventory_blueprint, url_prefix='/inventory')
home_units_blueprint.register_blueprint(home_components_blueprint, url_prefix='/components')
home_units_blueprint.register_blueprint(home_steamdt_blueprint, url_prefix='/steamdt')
