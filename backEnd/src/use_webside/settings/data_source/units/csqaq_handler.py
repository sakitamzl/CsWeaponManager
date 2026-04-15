# -*- coding: utf-8 -*-
"""
CSQAQ 数据源处理器
迁移自 backEnd/src/web_side/CSQAQ/csqaq_api.py
统一使用 DatabaseManager + 参数化 SQL
"""

import json
from flask import request, jsonify
from src.db_manager.database import DatabaseManager


class CsqaqHandler:

    @staticmethod
    def upload_mapping():
        """
        上传CSQAQ映射文件
        接收txt文件（JSON格式），解析并更新weapon_classID表的csqaq_id字段
        """
        try:
            if 'file' not in request.files:
                return jsonify({'success': False, 'message': '未找到上传文件'}), 400

            file = request.files['file']

            if file.filename == '':
                return jsonify({'success': False, 'message': '文件名为空'}), 400

            if not file.filename.endswith('.txt'):
                return jsonify({'success': False, 'message': '仅支持.txt文件'}), 400

            file_content = file.read().decode('utf-8')
            result = CsqaqHandler._process_mapping_file(file_content)
            status_code = 200 if result['success'] else 400
            return jsonify(result), status_code

        except Exception as e:
            return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500

    @staticmethod
    def _process_mapping_file(file_content: str) -> dict:
        """处理CSQAQ映射文件内容"""
        try:
            data = json.loads(file_content)

            if not isinstance(data, list):
                return {
                    'success': False,
                    'message': '文件格式错误：期望JSON数组',
                    'total': 0, 'updated': 0, 'not_found': 0, 'failed': 0
                }

            total = len(data)
            updated = 0
            inserted = 0
            failed = 0

            db = DatabaseManager()

            for item in data:
                try:
                    csqaq_id = item.get('id')
                    market_hash_name = item.get('market_hash_name')

                    if not csqaq_id or not market_hash_name:
                        failed += 1
                        continue

                    chk = db.execute_query(
                        "SELECT 1 FROM weapon_classID WHERE [steam_hash_name] = ? LIMIT 1",
                        (market_hash_name,),
                    )
                    if chk:
                        db.execute_update(
                            "UPDATE weapon_classID SET [csqaq_id] = ? WHERE [steam_hash_name] = ?",
                            (csqaq_id, market_hash_name),
                        )
                        updated += 1
                    else:
                        failed += 1

                except Exception:
                    failed += 1
                    continue

            return {
                'success': True,
                'message': f'处理完成：共 {total} 条，更新 {updated} 条，失败 {failed} 条',
                'total': total,
                'updated': updated,
                'inserted': inserted,
                'failed': failed
            }

        except json.JSONDecodeError as e:
            return {
                'success': False,
                'message': f'JSON解析失败: {str(e)}',
                'total': 0, 'updated': 0, 'not_found': 0, 'failed': 0
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'处理失败: {str(e)}',
                'total': 0, 'updated': 0, 'not_found': 0, 'failed': 0
            }

    @staticmethod
    def get_config():
        """
        获取CSQAQ配置（包含ApiToken）
        从数据库config表中查询 key1='csqaq' AND key2='config' 的配置
        """
        try:
            rows = DatabaseManager().execute_query(
                "SELECT [dataID], [dataName], [value] FROM config WHERE [key1] = ? AND [key2] = ? LIMIT 1",
                ("csqaq", "config"),
            )

            if not rows or not rows[0]:
                return jsonify({
                    'success': False,
                    'code': 404,
                    'message': 'CSQAQ配置不存在，请先在【设置 > 数据源管理】中添加CSQAQ数据源'
                }), 404

            data_id, data_name, value = rows[0][0], rows[0][1], rows[0][2]

            try:
                config_data = json.loads(value)
                api_token = config_data.get('ApiToken', '')

                if not api_token:
                    return jsonify({
                        'success': False,
                        'code': 400,
                        'message': 'CSQAQ ApiToken未配置'
                    }), 400

                return jsonify({
                    'success': True,
                    'code': 200,
                    'data': {
                        'ApiToken': api_token,
                        'dataName': data_name,
                        'dataID': data_id
                    }
                }), 200

            except json.JSONDecodeError as e:
                return jsonify({
                    'success': False,
                    'code': 500,
                    'message': f'配置数据格式错误: {str(e)}'
                }), 500

        except Exception as e:
            return jsonify({
                'success': False,
                'code': 500,
                'message': f'获取配置失败: {str(e)}'
            }), 500
