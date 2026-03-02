"""
完美世界 config Spider V2 API 模块
完整 URL 格式: /backENDV2/src/use_spider/prefect_world/config/<endpoint>
"""
from flask import Blueprint
from .units.config_handler import ConfigHandler

config_spider_blueprint = Blueprint('prefect_world_config_spider', __name__)

config_spider_blueprint.route('/config/get/<steam_id>', methods=['GET'])(ConfigHandler.get_config)
