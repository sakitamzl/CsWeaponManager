"""
开发者工具筛选数据模块
提供 Steam 账号列表的查询功能
（从 inventory_api.py 复制业务逻辑）
"""
from flask import jsonify, request
from src.log import Log
from src.execution_db import Date_base
import json


class DevToolsFilters:
    """开发者工具筛选类 - 提供 Steam 账号数据"""

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

                    steam_id = steam_id_from_field
                    if not steam_id and value_json:
                        try:
                            config_data = json.loads(value_json)
                            steam_id = config_data.get('steamID')
                        except:
                            pass

                    if not steam_id:
                        continue

                    if not data_name:
                        data_name = steam_id

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
