"""
完美世界 stock_components Spider V2 API 模块
完整 URL 格式: /backENDV2/src/use_spider/prefect_world/stock_components/<endpoint>
"""
from flask import Blueprint
from .units.stock_components_handler import StockComponentsHandler

stock_components_spider_blueprint = Blueprint('prefect_world_stock_components_spider', __name__)

stock_components_spider_blueprint.route('/stock_components/batch',                            methods=['POST'])(StockComponentsHandler.batch)
stock_components_spider_blueprint.route('/stock_components/single',                           methods=['POST'])(StockComponentsHandler.single)
stock_components_spider_blueprint.route('/stock_components/delete/<goods_assetid>',           methods=['DELETE'])(StockComponentsHandler.delete)
stock_components_spider_blueprint.route('/stock_components/delete/<assetid>/<steam_id>',      methods=['DELETE'])(StockComponentsHandler.delete_by_assetid_steam)
