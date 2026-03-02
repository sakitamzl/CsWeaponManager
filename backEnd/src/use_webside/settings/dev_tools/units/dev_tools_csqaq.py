"""
开发者工具 CSQAQ 模块
提供 CSQAQ 映射文件上传处理功能
（从 csqaq_api.py + upload_mapping.py 复制）
"""
from flask import jsonify, request
import json


class DevToolsCsqaq:
    """开发者工具 CSQAQ 类 - 映射文件上传"""

    @staticmethod
    def upload_mapping():
        """
        上传CSQAQ映射文件
        接收txt文件（JSON格式），解析并更新weapon_classID表的csqaq_id字段
        """
        try:
            if 'file' not in request.files:
                return jsonify({
                    'success': False,
                    'message': '未找到上传文件'
                }), 400

            file = request.files['file']

            if file.filename == '':
                return jsonify({
                    'success': False,
                    'message': '文件名为空'
                }), 400

            if not file.filename.endswith('.txt'):
                return jsonify({
                    'success': False,
                    'message': '仅支持.txt文件'
                }), 400

            file_content = file.read().decode('utf-8')

            result = DevToolsCsqaq._process_csqaq_mapping_file(file_content)

            status_code = 200 if result['success'] else 400
            return jsonify(result), status_code

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'服务器错误: {str(e)}'
            }), 500

    @staticmethod
    def _process_csqaq_mapping_file(file_content):
        """
        处理CSQAQ映射文件内容

        Args:
            file_content: 文件内容（JSON格式的字符串）

        Returns:
            Dict: 处理结果
        """
        try:
            from src.db_manager.index.model.weapon_classID import WeaponClassIDModel

            data = json.loads(file_content)

            if not isinstance(data, list):
                return {
                    'success': False,
                    'message': '文件格式错误：期望JSON数组',
                    'total': 0,
                    'updated': 0,
                    'not_found': 0,
                    'failed': 0
                }

            total = len(data)
            updated = 0
            inserted = 0
            failed = 0

            db = WeaponClassIDModel().db

            for item in data:
                try:
                    csqaq_id = item.get('id')
                    market_hash_name = item.get('market_hash_name')
                    item_name_cn = item.get('name', '')

                    if not csqaq_id or not market_hash_name:
                        failed += 1
                        continue

                    existing_records = WeaponClassIDModel.find_by_steam_hash_name(market_hash_name)

                    if existing_records:
                        sql = f'''UPDATE {WeaponClassIDModel.get_table_name()}
                                 SET [csqaq_id] = ?
                                 WHERE [steam_hash_name] = ?'''

                        affected_rows = db.execute_update(sql, (csqaq_id, market_hash_name))

                        if affected_rows > 0:
                            updated += 1
                        else:
                            failed += 1
                    else:
                        sql = f'''INSERT INTO {WeaponClassIDModel.get_table_name()}
                                 ([steam_hash_name], [market_listing_item_name], [csqaq_id])
                                 VALUES (?, ?, ?)'''

                        affected_rows = db.execute_insert(sql, (market_hash_name, item_name_cn, csqaq_id))

                        if affected_rows > 0:
                            inserted += 1
                        else:
                            failed += 1

                except Exception as e:
                    failed += 1
                    print(f"处理记录失败: {e}, item={item}")
                    continue

            success = (updated + inserted) > 0
            message = f"处理完成：总计 {total} 条，更新 {updated} 条，新增 {inserted} 条，失败 {failed} 条"

            return {
                'success': success,
                'message': message,
                'total': total,
                'updated': updated,
                'inserted': inserted,
                'failed': failed
            }

        except json.JSONDecodeError as e:
            return {
                'success': False,
                'message': f'JSON解析失败: {str(e)}',
                'total': 0,
                'updated': 0,
                'inserted': 0,
                'failed': 0
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'处理失败: {str(e)}',
                'total': 0,
                'updated': 0,
                'inserted': 0,
                'failed': 0
            }
