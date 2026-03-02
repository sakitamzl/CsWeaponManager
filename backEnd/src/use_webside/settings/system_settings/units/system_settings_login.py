"""
系统设置 - 登录设置模块
提供登录验证配置的查询、保存和验证功能
（从 login_settings.py 移植，ConfigModel → Date_base 原生 SQL）
"""
from flask import jsonify, request
from src.log import Log
from src.execution_db import Date_base
import hashlib
import traceback


class SystemSettingsLogin:
    """系统设置登录类 - 登录验证配置"""

    @staticmethod
    def _get_config_value(db, key1, key2, default_value=None):
        """从config表获取配置值"""
        sql = f"SELECT value FROM config WHERE key1 = '{key1}' AND key2 = '{key2}'"
        success, results = db.select(sql)
        if success and results:
            return results[0][0]
        return default_value

    @staticmethod
    def _set_config_value(db, key1, key2, value, data_name=None):
        """设置config表配置值（存在则更新，不存在则插入）"""
        check_sql = f"SELECT dataID FROM config WHERE key1 = '{key1}' AND key2 = '{key2}'"
        success, results = db.select(check_sql)
        escaped_value = value.replace("'", "''")
        if success and results:
            if data_name:
                escaped_name = data_name.replace("'", "''")
                sql = f"UPDATE config SET value = '{escaped_value}', dataName = '{escaped_name}' WHERE key1 = '{key1}' AND key2 = '{key2}'"
            else:
                sql = f"UPDATE config SET value = '{escaped_value}' WHERE key1 = '{key1}' AND key2 = '{key2}'"
            db.update(sql)
        else:
            escaped_name = (data_name or '').replace("'", "''")
            sql = f"INSERT INTO config (key1, key2, value, dataName, status) VALUES ('{key1}', '{key2}', '{escaped_value}', '{escaped_name}', '1')"
            db.insert(sql)

    @staticmethod
    def _hash_password(password):
        """对密码进行MD5加密"""
        return hashlib.md5(password.encode()).hexdigest()

    @staticmethod
    def _verify_password(password, hashed):
        """验证密码"""
        return SystemSettingsLogin._hash_password(password) == hashed

    @staticmethod
    def get_settings():
        """获取登录设置"""
        try:
            db = Date_base()

            enable_login_value = SystemSettingsLogin._get_config_value(db, 'user', 'login', '0')
            enable_login = enable_login_value == '1'

            username = SystemSettingsLogin._get_config_value(db, 'user', 'username', '')

            external_access_value = SystemSettingsLogin._get_config_value(db, 'user', 'external_access', '0')
            allow_external_access = external_access_value == '1'

            return jsonify({
                'success': True,
                'data': {
                    'enableLogin': enable_login,
                    'username': username,
                    'password': '',
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

    @staticmethod
    def save_settings():
        """保存登录设置"""
        try:
            data = request.get_json()

            enable_login = data.get('enableLogin', False)
            username = data.get('username', '')
            password = data.get('password', '')
            allow_external_access = data.get('allowExternalAccess', False)

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

            db = Date_base()

            SystemSettingsLogin._set_config_value(db, 'user', 'login', '1' if enable_login else '0', '登录验证开关')

            if username:
                SystemSettingsLogin._set_config_value(db, 'user', 'username', username, '登录用户名')

            if password:
                hashed_password = SystemSettingsLogin._hash_password(password)
                SystemSettingsLogin._set_config_value(db, 'user', 'password', hashed_password, '登录密码')

            SystemSettingsLogin._set_config_value(db, 'user', 'external_access', '1' if allow_external_access else '0', '外网访问开关')

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

    @staticmethod
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

            db = Date_base()

            enable_login_value = SystemSettingsLogin._get_config_value(db, 'user', 'login', '0')
            if enable_login_value != '1':
                return jsonify({
                    'success': False,
                    'message': '登录验证未启用'
                }), 403

            stored_username = SystemSettingsLogin._get_config_value(db, 'user', 'username', '')
            stored_password = SystemSettingsLogin._get_config_value(db, 'user', 'password', '')

            if username != stored_username:
                Log().write_log(f"登录失败: 用户名错误 - {username}", 'warning')
                return jsonify({
                    'success': False,
                    'message': '用户名或密码错误'
                }), 401

            if not SystemSettingsLogin._verify_password(password, stored_password):
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
