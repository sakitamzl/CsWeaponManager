"""
youpin Spider V2 API 根模块
层级蓝图注册：
- 从 src/API.py 接收前缀 /backENDV2/src
- 向下传递给各子模块，添加 /use_spider/youpin 路径段
完整 URL 格式: /backENDV2/src/use_spider/youpin/<module>/<endpoint>
"""
from flask import Blueprint
from .buy.API import buy_spider_blueprint
from .sell.API import sell_spider_blueprint
from .lent.API import lent_spider_blueprint
from .rental.API import rental_spider_blueprint
from .message.API import message_spider_blueprint
from .select_weapon.API import select_weapon_spider_blueprint

youpin_spider_blueprint = Blueprint('youpin_spider', __name__)
youpin_spider_blueprint.register_blueprint(buy_spider_blueprint,           url_prefix='/use_spider/youpin')
youpin_spider_blueprint.register_blueprint(sell_spider_blueprint,          url_prefix='/use_spider/youpin')
youpin_spider_blueprint.register_blueprint(lent_spider_blueprint,          url_prefix='/use_spider/youpin')
youpin_spider_blueprint.register_blueprint(rental_spider_blueprint,        url_prefix='/use_spider/youpin')
youpin_spider_blueprint.register_blueprint(message_spider_blueprint,       url_prefix='/use_spider/youpin')
youpin_spider_blueprint.register_blueprint(select_weapon_spider_blueprint, url_prefix='/use_spider/youpin')
