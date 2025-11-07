"""
登录设置API接口
使用config表存储登录配置
key1 = 'user', key2 = 'login', value = JSON格式存储用户名和密码
"""

from flask import jsonify, request, Blueprint
from src.log import Log
from src.db_manager.index.config import ConfigModel
import json
import hashlib
import traceback

loginSettingsPage = Blueprint('loginSettingsPage', __name__)


def hash_password(password: str) -> str:
    """对密码进行MD5加密"""
    return hashlib.md5(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """验证密码"""
    return hash_password(password) == hashed


@loginSettingsPage.route('/api/login-settings', methods=['GET'])
def get_login_settings():
    """获取登录设置"""
    try:
        # 从config表获取配置
        # key1='user', key2='login' 存储启用状态
        enable_login_value = ConfigModel.get_value('user', 'login', '0')
        enable_login = enable_login_value == '1'
        
        # key1='user', key2='username' 存储用户名
        username = ConfigModel.get_value('user', 'username', '')
        
        # key1='user', key2='external_access' 存储外网访问状态
        external_access_value = ConfigModel.get_value('user', 'external_access', '0')
        allow_external_access = external_access_value == '1'
        
        return jsonify({
            'success': True,
            'data': {
                'enableLogin': enable_login,
                'username': username,
                'password': '',  # 不返回密码
                'allowExternalAccess': allow_external_access
            },
            'message': '获取登录设置成功'
        }), 200
        
    except Exception as e:
        Log().write_log(f"获取登录设置失败: {str(e)}", 'error')
        Log().write_log(traceback.format_exc(), 'error')
        return jsonify({
            'success': False,
            'message': f'获取登录设置失败: {str(e)}'
        }), 500


@loginSettingsPage.route('/api/login-settings', methods=['POST'])
def save_login_settings():
    """保存登录设置"""
    try:
        data = request.get_json()
        
        enable_login = data.get('enableLogin', False)
        username = data.get('username', '')
        password = data.get('password', '')
        allow_external_access = data.get('allowExternalAccess', False)
        
        # 如果启用登录，验证用户名和密码
        if enable_login:
            if not username:
                return jsonify({
                    'success': False,
                    'message': '启用登录验证时，用户名不能为空'
                }), 400
            
            if not password:
                return jsonify({
                    'success': False,
                    'message': '启用登录验证时，密码不能为空'
                }), 400
        
        # 保存启用状态
        ConfigModel.set_value('user', 'login', '1' if enable_login else '0', '登录验证开关')
        
        # 保存用户名
        if username:
            ConfigModel.set_value('user', 'username', username, '登录用户名')
        
        # 保存密码（加密）
        if password:
            hashed_password = hash_password(password)
            ConfigModel.set_value('user', 'password', hashed_password, '登录密码')
        
        # 保存外网访问状态
        ConfigModel.set_value('user', 'external_access', '1' if allow_external_access else '0', '外网访问开关')
        
        Log().write_log(f"登录设置已保存: enableLogin={enable_login}, username={username}, allowExternalAccess={allow_external_access}", 'info')
        
        return jsonify({
            'success': True,
            'message': '登录设置保存成功'
        }), 200
        
    except Exception as e:
        Log().write_log(f"保存登录设置失败: {str(e)}", 'error')
        Log().write_log(traceback.format_exc(), 'error')
        return jsonify({
            'success': False,
            'message': f'保存登录设置失败: {str(e)}'
        }), 500


@loginSettingsPage.route('/api/login-settings/verify', methods=['POST'])
def verify_login():
    """验证登录"""
    try:
        data = request.get_json()
        username = data.get('username', '')
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': '用户名和密码不能为空'
            }), 400
        
        # 检查是否启用登录
        enable_login_value = ConfigModel.get_value('user', 'login', '0')
        if enable_login_value != '1':
            return jsonify({
                'success': False,
                'message': '登录验证未启用'
            }), 403
        
        # 获取存储的用户名和密码
        stored_username = ConfigModel.get_value('user', 'username', '')
        stored_password = ConfigModel.get_value('user', 'password', '')
        
        # 验证用户名
        if username != stored_username:
            Log().write_log(f"登录失败: 用户名错误 - {username}", 'warning')
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401
        
        # 验证密码
        if not verify_password(password, stored_password):
            Log().write_log(f"登录失败: 密码错误 - 用户: {username}", 'warning')
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401
        
        Log().write_log(f"登录成功: {username}", 'info')
        
        return jsonify({
            'success': True,
            'message': '登录成功'
        }), 200
        
    except Exception as e:
        Log().write_log(f"登录验证失败: {str(e)}", 'error')
        Log().write_log(traceback.format_exc(), 'error')
        return jsonify({
            'success': False,
            'message': f'登录验证失败: {str(e)}'
        }), 500

