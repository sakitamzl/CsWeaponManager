"""
backEND V2 API 根模块
层级蓝图注册：
- 从 backEnd.py 接收前缀 /backENDV2
- 向下传递给 web_display 模块，添加 /src 路径段
"""
from flask import Blueprint
from .web_display.API import web_display_blueprint

backendV2_blueprint = Blueprint('backendV2_src', __name__)
backendV2_blueprint.register_blueprint(web_display_blueprint, url_prefix='/src')
