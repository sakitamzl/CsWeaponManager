"""
完美世界 Spider V2 API 模块
层级蓝图注册：
- 从 use_spider/API.py 接收前缀 /backENDV2/src/use_spider/prefect_world
- 向下传递给各子模块（不再添加路径段，由子模块路由自身定义）
完整 URL 格式: /backENDV2/src/use_spider/prefect_world/<module>/<endpoint>
"""
from flask import Blueprint
from .config.API import config_spider_blueprint
from .stock_components.API import stock_components_spider_blueprint

prefect_world_spider_blueprint = Blueprint('prefect_world_spider', __name__)
prefect_world_spider_blueprint.register_blueprint(config_spider_blueprint)
prefect_world_spider_blueprint.register_blueprint(stock_components_spider_blueprint)
