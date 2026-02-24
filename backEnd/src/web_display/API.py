"""
web_display API 模块
层级蓝图注册：
- 从 src/API.py 接收前缀 /backENDV2/src
- 向下传递给 home 模块，添加 /web_display 路径段
"""
from flask import Blueprint
from .home.API import home_blueprint

web_display_blueprint = Blueprint('web_display', __name__)
web_display_blueprint.register_blueprint(home_blueprint, url_prefix='/web_display')
