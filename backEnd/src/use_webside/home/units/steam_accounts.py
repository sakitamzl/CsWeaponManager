"""
Home 页面 Steam 账号列表模块
从 webInventoryV1/steam_ids 分离的独立实现
"""
from flask import jsonify, request
from src.db_manager.database import DatabaseManager
import json


class SteamAccounts:

    @staticmethod
    def get_steam_ids():
        """从config表获取所有Steam配置（key1='steam' AND key2='config'）"""
        try:
            classid_filter = request.args.get('classid', '')

            db = DatabaseManager()

            steam_config_sql = """
            SELECT [dataID], [dataName], [value], [steamID]
            FROM config
            WHERE [key1] = 'steam' AND [key2] = 'config'
            ORDER BY [dataID]
            """
            steam_config_results = db.execute_query(steam_config_sql)

            steam_ids = []

            for row in steam_config_results:
                data_id = row[0]
                data_name = row[1] if row[1] else None
                value_json = row[2] if len(row) > 2 else None
                steam_id_from_field = row[3] if len(row) > 3 else None

                # 尝试从value JSON中解析steamID
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

                # 查询该steamID在库存中的物品数量
                if classid_filter:
                    count_sql = """
                    SELECT COUNT(*)
                    FROM steam_inventory
                    WHERE data_user = ? AND if_inventory = '1' AND classid = ?
                    """
                    count_result = db.execute_query(count_sql, (steam_id, classid_filter))
                else:
                    count_sql = """
                    SELECT COUNT(*)
                    FROM steam_inventory
                    WHERE data_user = ? AND if_inventory = '1'
                    """
                    count_result = db.execute_query(count_sql, (steam_id,))

                item_count = count_result[0][0] if count_result else 0

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
            print(f"查询Steam ID列表失败: {e}")
            import traceback
            print(f"详细错误信息: {traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': f'查询失败: {str(e)}'
            }), 500
