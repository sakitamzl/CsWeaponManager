# -*- coding: utf-8 -*-
"""
CSQAQ stock_components Spider 调用接口
完整 URL 示例: /backENDV2/src/use_spider/csqaq/stock_components/<endpoint>
"""
from flask import Blueprint
from .units.stock_components_handler import CsqaqStockComponentsHandler

csqaq_stock_components_blueprint = Blueprint("csqaq_stock_components_spider", __name__)

csqaq_stock_components_blueprint.route(
    "/stock_components/getHashNames/<steam_id>",
    methods=["GET"],
)(CsqaqStockComponentsHandler.get_hash_names)
csqaq_stock_components_blueprint.route(
    "/stock_components/writePrices",
    methods=["POST"],
)(CsqaqStockComponentsHandler.write_prices)
