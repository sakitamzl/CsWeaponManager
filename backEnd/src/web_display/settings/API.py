"""
Settings API 模块
层级蓝图注册：
- 从 web_display/API.py 接收前缀 /backENDV2/src/web_display
- 向下传递给各设置子模块，添加 /settings 路径段
"""
from flask import Blueprint
from .data_source.API import data_source_blueprint
from .auto_manager.API import auto_manager_blueprint
from .steam_inventory_history.API import steam_inventory_history_blueprint
from .dev_tools.API import dev_tools_blueprint
from .system_settings.API import system_settings_blueprint

settings_blueprint = Blueprint('settings_v2', __name__)
settings_blueprint.register_blueprint(data_source_blueprint, url_prefix='/settings')
settings_blueprint.register_blueprint(auto_manager_blueprint, url_prefix='/settings')
settings_blueprint.register_blueprint(steam_inventory_history_blueprint, url_prefix='/settings')
settings_blueprint.register_blueprint(dev_tools_blueprint, url_prefix='/settings')
settings_blueprint.register_blueprint(system_settings_blueprint, url_prefix='/settings')
