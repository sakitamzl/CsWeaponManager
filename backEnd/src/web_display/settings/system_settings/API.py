"""
SystemSettings API 模块
层级蓝图注册：
- 从 settings/API.py 接收前缀 /backENDV2/src/web_display/settings
- 注册所有 SystemSettings 路由，添加 /system_settings/units/xxx 路径段
"""
from flask import Blueprint
from .units.system_settings_login import SystemSettingsLogin

system_settings_blueprint = Blueprint('system_settings_v2', __name__)

# 登录设置
system_settings_blueprint.route('/system_settings/units/login/getSettings', methods=['GET'])(SystemSettingsLogin.get_settings)
system_settings_blueprint.route('/system_settings/units/login/saveSettings', methods=['POST'])(SystemSettingsLogin.save_settings)
system_settings_blueprint.route('/system_settings/units/login/verify', methods=['POST'])(SystemSettingsLogin.verify_login)
