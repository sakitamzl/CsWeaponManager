"""
Steam market Spider V2 API 模块
完整 URL 格式: /backENDV2/src/use_spider/steam/market/<endpoint>
"""
from flask import Blueprint
from .units.market_handler import MarketHandler

market_spider_blueprint = Blueprint('steam_market_spider', __name__)

market_spider_blueprint.route('/market/countData/<data_user>',       methods=['GET'])(MarketHandler.count_data)
market_spider_blueprint.route('/market/getLatestData/<data_user>',   methods=['GET'])(MarketHandler.get_latest_data)
market_spider_blueprint.route('/market/getEarliestData/<data_user>', methods=['GET'])(MarketHandler.get_earliest_data)
market_spider_blueprint.route('/market/insertNewData',               methods=['POST'])(MarketHandler.insert_new_data)
