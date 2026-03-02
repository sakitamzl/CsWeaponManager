"""
Steam Spider V2 API 模块
层级蓝图注册：
- 从 use_spider/API.py 接收前缀 /backENDV2/src/use_spider/steam
- 向下传递给各子模块（不再添加路径段，由子模块路由自身定义）
完整 URL 格式: /backENDV2/src/use_spider/steam/<module>/<endpoint>
"""
from flask import Blueprint
from .market.API import market_spider_blueprint
from .inventory_history.API import inventory_history_spider_blueprint
from .inventory.API import inventory_spider_blueprint
from .select_weapon.API import select_weapon_spider_blueprint
from .mining.API import mining_spider_blueprint

steam_spider_blueprint = Blueprint('steam_spider', __name__)
steam_spider_blueprint.register_blueprint(market_spider_blueprint)
steam_spider_blueprint.register_blueprint(inventory_history_spider_blueprint)
steam_spider_blueprint.register_blueprint(inventory_spider_blueprint)
steam_spider_blueprint.register_blueprint(select_weapon_spider_blueprint)
steam_spider_blueprint.register_blueprint(mining_spider_blueprint)
