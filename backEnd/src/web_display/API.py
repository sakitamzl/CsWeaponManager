"""
web_display API 模块
层级蓝图注册：
- 从 src/API.py 接收前缀 /backENDV2/src
- 向下传递给各页面模块，添加 /web_display 路径段
"""
from flask import Blueprint
from .home.API import home_blueprint
from .buy.API import buy_blueprint
from .sell.API import sell_blueprint
from .rental.API import rental_blueprint
from .lent.API import lent_blueprint
from .on_sale.API import on_sale_blueprint

web_display_blueprint = Blueprint('web_display', __name__)
web_display_blueprint.register_blueprint(home_blueprint, url_prefix='/web_display')
web_display_blueprint.register_blueprint(buy_blueprint, url_prefix='/web_display')
web_display_blueprint.register_blueprint(sell_blueprint, url_prefix='/web_display')
web_display_blueprint.register_blueprint(rental_blueprint, url_prefix='/web_display')
web_display_blueprint.register_blueprint(lent_blueprint, url_prefix='/web_display')
web_display_blueprint.register_blueprint(on_sale_blueprint, url_prefix='/web_display')
