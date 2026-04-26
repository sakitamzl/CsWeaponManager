"""
C5GAME buy Spider V2 API 模块
完整 URL 格式: /backENDV2/src/use_spider/c5game/buy/<endpoint>
"""
from flask import Blueprint
from .units.buy_insert import BuyInsert
from .units.buy_query import BuyQuery

buy_spider_blueprint = Blueprint("c5game_buy_spider", __name__)
buy_spider_blueprint.route("/buy/insert_db", methods=["POST"])(BuyInsert.insert_db)
buy_spider_blueprint.route("/buy/getLatestData/<user_id>", methods=["GET"])(BuyQuery.get_latest_data)
buy_spider_blueprint.route("/buy/countData/<user_id>", methods=["GET"])(BuyQuery.count_data)

