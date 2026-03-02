"""
Steam mining Spider V2 API 模块
完整 URL 格式: /backENDV2/src/use_spider/steam/mining/<endpoint>
"""
from flask import Blueprint
from .units.mining_handler import MiningHandler

mining_spider_blueprint = Blueprint('steam_mining_spider', __name__)

mining_spider_blueprint.route('/mining/clear',                    methods=['POST'])(MiningHandler.clear)
mining_spider_blueprint.route('/mining/batch',                    methods=['POST'])(MiningHandler.batch)
mining_spider_blueprint.route('/mining/latest',                   methods=['GET'])(MiningHandler.latest)
mining_spider_blueprint.route('/mining/query',                    methods=['POST'])(MiningHandler.query)
mining_spider_blueprint.route('/mining/stats',                    methods=['POST'])(MiningHandler.stats)
mining_spider_blueprint.route('/mining/history',                  methods=['GET'])(MiningHandler.history)
mining_spider_blueprint.route('/mining/history/<steam_id>',       methods=['DELETE'])(MiningHandler.delete_history)
