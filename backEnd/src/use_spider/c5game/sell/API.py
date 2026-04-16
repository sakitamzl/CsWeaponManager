"""
C5GAME sell Spider V2 API 模块
完整 URL 格式: /backENDV2/src/use_spider/c5game/sell/<endpoint>
"""
from flask import Blueprint
from .units.sell_insert import SellInsert

sell_spider_blueprint = Blueprint("c5game_sell_spider", __name__)
sell_spider_blueprint.route("/sell/insert_db", methods=["POST"])(SellInsert.insert_db)

