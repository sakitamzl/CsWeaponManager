"""
Steam inventory_history Spider V2 API 模块
完整 URL 格式: /backENDV2/src/use_spider/steam/inventory_history/<endpoint>
"""
from flask import Blueprint
from .units.inventory_history_handler import InventoryHistoryHandler

inventory_history_spider_blueprint = Blueprint('steam_inventory_history_spider', __name__)

inventory_history_spider_blueprint.route('/inventory_history/selectMaxTime/<steam_ID>',    methods=['GET'])(InventoryHistoryHandler.select_max_time)
inventory_history_spider_blueprint.route('/inventory_history/selectMinTime/<steam_ID>',    methods=['GET'])(InventoryHistoryHandler.select_min_time)
inventory_history_spider_blueprint.route('/inventory_history/insert_inventory_history',    methods=['POST'])(InventoryHistoryHandler.insert_inventory_history)
inventory_history_spider_blueprint.route('/inventory_history/resolve_sticker',             methods=['POST'])(InventoryHistoryHandler.resolve_sticker)
inventory_history_spider_blueprint.route('/inventory_history/resolve_pendant',             methods=['POST'])(InventoryHistoryHandler.resolve_pendant)
inventory_history_spider_blueprint.route('/inventory_history/resolve_market_item',         methods=['POST'])(InventoryHistoryHandler.resolve_market_item)
