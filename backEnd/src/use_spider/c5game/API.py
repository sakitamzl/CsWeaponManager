"""
C5GAME Spider V2 API 模块
层级蓝图注册：
- 从 use_spider/API.py 接收前缀 /backENDV2/src/use_spider/c5game
- 向下传递给 sell 子模块
"""
from flask import Blueprint
from .sell.API import sell_spider_blueprint

c5game_spider_blueprint = Blueprint("c5game_spider", __name__)
c5game_spider_blueprint.register_blueprint(sell_spider_blueprint)

