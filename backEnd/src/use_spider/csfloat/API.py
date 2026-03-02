"""
CSFloat Spider V2 API 模块
层级蓝图注册：
- 从 use_spider/API.py 接收前缀 /backENDV2/src/use_spider/csfloat
- 向下传递给各子模块（不再添加路径段，由子模块路由自身定义 /buy/、/sell/ 等）
完整 URL 格式: /backENDV2/src/use_spider/csfloat/<module>/<endpoint>
"""
from flask import Blueprint
from .buy.API import buy_spider_blueprint
from .sell.API import sell_spider_blueprint

csfloat_spider_blueprint = Blueprint('csfloat_spider', __name__)
csfloat_spider_blueprint.register_blueprint(buy_spider_blueprint)
csfloat_spider_blueprint.register_blueprint(sell_spider_blueprint)
