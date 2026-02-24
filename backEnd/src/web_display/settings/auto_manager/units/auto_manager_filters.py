"""
自动化管理筛选数据模块
提供 Steam 账号列表和搜索配置列表的查询功能
（从 inventory_api.py 和 config_v1.py 复制业务逻辑）
"""
from flask import jsonify, request
from src.log import Log
from src.execution_db import Date_base
import json


class AutoManagerFilters:
    """自动化管理筛选类 - 提供 Steam 账号和搜索配置数据"""

    @staticmethod
    def get_steam_accounts():
        """获取所有 Steam 账号配置（key1='steam' AND key2='config'）"""
        try:
            classid_filter = request.args.get('classid', '')

            db = Date_base()

            steam_config_sql = """
            SELECT dataID, dataName, value, steamID
            FROM config
            WHERE key1 = 'steam' AND key2 = 'config'
            ORDER BY dataID
            """

            success, results = db.select(steam_config_sql)

            steam_ids = []

            if success and results:
                for row in results:
                    data_id = row[0]
                    data_name = row[1] if row[1] else None
                    value_json = row[2] if len(row) > 2 else None
                    steam_id_from_field = row[3] if len(row) > 3 else None

                    # 尝试从 value JSON 中解析 steamID
                    steam_id = steam_id_from_field
                    if not steam_id and value_json:
                        try:
                            config_data = json.loads(value_json)
                            steam_id = config_data.get('steamID')
                        except:
                            pass

                    # 如果没有 steamID，跳过这条记录
                    if not steam_id:
                        continue

                    # 如果没有 dataName，使用 steamID 作为名称
                    if not data_name:
                        data_name = steam_id

                    # 查询该 steamID 在库存中的物品数量
                    if classid_filter:
                        count_sql = f"""
                        SELECT COUNT(*)
                        FROM steam_inventory
                        WHERE data_user = '{steam_id}' AND if_inventory = '1' AND classid = '{classid_filter}'
                        """
                    else:
                        count_sql = f"""
                        SELECT COUNT(*)
                        FROM steam_inventory
                        WHERE data_user = '{steam_id}' AND if_inventory = '1'
                        """

                    count_success, count_result = db.select(count_sql)
                    item_count = count_result[0][0] if count_success and count_result else 0

                    steam_ids.append({
                        'dataID': data_id,
                        'dataName': data_name,
                        'steamID': steam_id,
                        'item_count': item_count
                    })

            return jsonify({
                'success': True,
                'data': steam_ids
            }), 200

        except Exception as e:
            Log().write_log(f"查询Steam账号列表失败: {str(e)}", 'error')
            return jsonify({
                'success': False,
                'error': f'查询失败: {str(e)}'
            }), 500

    @staticmethod
    def get_search_configs():
        """获取搜索配置列表（按 key1/key2 筛选）"""
        try:
            key1 = request.args.get('key1')
            key2 = request.args.get('key2')

            # 构建 WHERE 条件
            where_conditions = []
            if key1:
                where_conditions.append(f"key1 = '{key1}'")
            if key2:
                where_conditions.append(f"key2 = '{key2}'")

            if not where_conditions:
                return jsonify({
                    'success': False,
                    'message': '至少需要提供 key1 或 key2 参数'
                }), 400

            where_clause = ' AND '.join(where_conditions)

            sql = f"""
                SELECT dataID, dataName, key1, key2, value, status, steamID,
                       datetime('now') as updated_at
                FROM config
                WHERE {where_clause}
                ORDER BY dataID DESC
            """

            db = Date_base()
            flag, result = db.select(sql)

            data = []
            if result:
                for row in result:
                    data.append({
                        'id': row[0],
                        'dataName': row[1],
                        'key1': row[2],
                        'key2': row[3],
                        'value': row[4],
                        'status': row[5],
                        'steamID': row[6],
                        'updated_at': row[7]
                    })

            return jsonify({
                'success': True,
                'data': data
            }), 200

        except Exception as e:
            Log().write_log(f"获取搜索配置列表失败: {str(e)}", 'error')
            return jsonify({
                'success': False,
                'message': f'获取失败: {str(e)}'
            }), 500
