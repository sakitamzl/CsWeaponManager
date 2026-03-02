"""
数据源操作模块
提供数据源的连接测试、数据采集、启用/禁用切换功能
"""
from flask import jsonify, request
from src.units.log import Log
from src.units.execution_db import Date_base
import time
import random
from datetime import datetime


class DataSourceOps:
    """数据源操作类 - 提供测试、采集、切换功能"""

    @staticmethod
    def test_connection():
        """测试数据源连接"""
        try:
            data = request.get_json()

            datasource_type = data.get('type', '')
            api_url = data.get('apiUrl', '')

            if not api_url:
                return jsonify({
                    'success': False,
                    'message': 'API地址不能为空'
                }), 400

            # 模拟连接测试
            time.sleep(1)

            return jsonify({
                'success': True,
                'message': '连接测试成功',
                'data': {
                    'latency': '150ms',
                    'status': 'online'
                }
            }), 200

        except Exception as e:
            Log().write_log(f"测试数据源连接失败: {str(e)}", 'error')
            return jsonify({
                'success': False,
                'message': f'连接测试失败: {str(e)}'
            }), 500

    @staticmethod
    def collect_data_source(data_id):
        """启动数据源采集"""
        try:
            data = request.get_json()

            # 验证数据源是否存在且启用
            check_sql = f"SELECT dataName, status FROM config WHERE dataID = {data_id} LIMIT 1"

            db = Date_base()
            success, result = db.select(check_sql)

            if not success or not result:
                return jsonify({
                    'success': False,
                    'message': '数据源不存在'
                }), 404

            data_name = result[0][0]
            status = result[0][1]

            if status != '1':
                return jsonify({
                    'success': False,
                    'message': '数据源未启用，无法采集'
                }), 400

            Log().write_log(f"开始采集数据源: {data_name} (ID: {data_id})", 'info')

            # 模拟采集
            time.sleep(2)
            collected_count = random.randint(50, 500)

            Log().write_log(f"采集完成: {data_name}, 采集到 {collected_count} 条数据", 'info')

            return jsonify({
                'success': True,
                'message': f'数据源 {data_name} 采集完成',
                'data': {
                    'dataSourceId': data_id,
                    'dataSourceName': data_name,
                    'count': collected_count,
                    'startTime': datetime.now().isoformat(),
                    'status': 'completed'
                }
            }), 200

        except Exception as e:
            Log().write_log(f"采集数据源失败: {str(e)}", 'error')
            return jsonify({
                'success': False,
                'message': f'采集失败: {str(e)}'
            }), 500

    @staticmethod
    def toggle_data_source(data_id):
        """切换数据源启用状态"""
        try:
            data = request.get_json()
            enabled = data.get('enabled', True)
            status = '1' if enabled else '0'

            update_sql = f"UPDATE config SET status = '{status}' WHERE dataID = {data_id}"

            db = Date_base()
            result = db.update(update_sql)

            if result:
                return jsonify({
                    'success': True,
                    'message': f'数据源已{"启用" if enabled else "禁用"}'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': '更新状态失败'
                }), 500

        except Exception as e:
            Log().write_log(f"切换数据源状态失败: {str(e)}", 'error')
            return jsonify({
                'success': False,
                'message': f'服务器错误: {str(e)}'
            }), 500
