"""
Settings API 模块
层级蓝图注册：
- 从 web_display/API.py 接收前缀 /backENDV2/src/web_display
- 向下传递给各设置子模块，添加 /settings 路径段
"""
from flask import Blueprint
from .data_source.API import data_source_blueprint

settings_blueprint = Blueprint('settings_v2', __name__)
settings_blueprint.register_blueprint(data_source_blueprint, url_prefix='/settings')
