"""
Steam inventory Spider V2 API 模块
完整 URL 格式: /backENDV2/src/use_spider/steam/inventory/<endpoint>
"""
from flask import Blueprint
from .units.inventory_handler import InventoryHandler

inventory_spider_blueprint = Blueprint('steam_inventory_spider', __name__)

inventory_spider_blueprint.route('/inventory/insert',                              methods=['POST'])(InventoryHandler.insert_inventory)
inventory_spider_blueprint.route('/inventory/get/<data_user>',                     methods=['GET'])(InventoryHandler.get_inventory_by_user)
inventory_spider_blueprint.route('/inventory/count/<data_user>',                   methods=['GET'])(InventoryHandler.count_inventory)
inventory_spider_blueprint.route('/inventory/delete/<data_user>',                  methods=['DELETE'])(InventoryHandler.delete_user_inventory)
inventory_spider_blueprint.route('/inventory/batch',                               methods=['POST'])(InventoryHandler.insert_inventory_batch)
inventory_spider_blueprint.route('/inventory/buy_price/<steam_id>/<assetid>',      methods=['PUT'])(InventoryHandler.update_buy_price)
