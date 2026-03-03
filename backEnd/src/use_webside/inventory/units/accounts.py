"""
Inventory 页面账号查询模块
提供 Steam 账号列表查询及库存数量统计，以及 Steam 配置（Cookie）的读写
"""
from flask import jsonify, request
from src.db_manager.database import DatabaseManager
import json


class InventoryAccounts:

    @staticmethod
    def get_steam_ids():
        """从config表获取所有Steam配置（key1='steam' AND key2='config'）"""
        try:
            classid_filter = request.args.get('classid', '')

            db = DatabaseManager()

            steam_config_sql = """
            SELECT dataID, dataName, value, steamID
            FROM config
            WHERE key1 = ? AND key2 = ?
            ORDER BY dataID
            """
            steam_config_results = db.execute_query(steam_config_sql, ('steam', 'config'))

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
                    except (json.JSONDecodeError, TypeError):
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
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': f'查询失败: {str(e)}'
            }), 500

    @staticmethod
    def get_steam_config(steam_id):
        """
        根据 steamId 从 config 表获取 Steam 配置（Cookie 等）
        GET /inventory/units/accounts/steam_config/<steam_id>
        返回: {"success": true, "data": {"steamID": "...", "inventoryCookies": "...", ...}}
        """
        try:
            db = DatabaseManager()
            sql = """
            SELECT dataID, dataName, value, steamID
            FROM config
            WHERE key1 = ? AND key2 = ? AND (steamID = ? OR value LIKE ?)
            ORDER BY dataID
            LIMIT 1
            """
            results = db.execute_query(sql, ('steam', 'config', steam_id, f'%"steamID":"{steam_id}"%'))

            if not results:
                return jsonify({'success': False, 'error': f'未找到 steamId={steam_id} 的配置'}), 404

            row = results[0]
            data_id = row[0]
            data_name = row[1]
            value_json = row[2]
            steam_id_field = row[3]

            config_data = {}
            if value_json:
                try:
                    config_data = json.loads(value_json)
                except (json.JSONDecodeError, TypeError):
                    pass

            # 补充顶层字段
            config_data['dataID'] = data_id
            config_data['dataName'] = data_name
            config_data['steamID'] = steam_id_field or config_data.get('steamID', steam_id)

            return jsonify({'success': True, 'data': config_data}), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': f'查询失败: {str(e)}'}), 500

    @staticmethod
    def save_steam_config():
        """
        保存/更新 Steam 配置（Cookie 等）到 config 表
        POST /inventory/units/accounts/steam_config
        请求体: {"steamID": "...", "inventoryCookies": "...", "baseCookies": "...", "dataName": "...", ...}
        """
        try:
            data = request.get_json() or {}
            steam_id = data.get('steamID') or data.get('steamId')
            if not steam_id:
                return jsonify({'success': False, 'message': 'steamID 不能为空'}), 400

            db = DatabaseManager()

            # 查询是否已存在
            check_sql = """
            SELECT dataID FROM config
            WHERE key1 = ? AND key2 = ? AND (steamID = ? OR value LIKE ?)
            LIMIT 1
            """
            existing = db.execute_query(check_sql, ('steam', 'config', steam_id, f'%"steamID":"{steam_id}"%'))

            value_json = json.dumps(data, ensure_ascii=False)
            data_name = data.get('dataName', steam_id)

            if existing:
                data_id = existing[0][0]
                update_sql = """
                UPDATE config SET value = ?, dataName = ?, steamID = ?
                WHERE dataID = ?
                """
                db.execute_query(update_sql, (value_json, data_name, steam_id, data_id))
            else:
                insert_sql = """
                INSERT INTO config (key1, key2, dataName, value, steamID)
                VALUES (?, ?, ?, ?, ?)
                """
                db.execute_query(insert_sql, ('steam', 'config', data_name, value_json, steam_id))

            return jsonify({'success': True, 'message': '保存成功'}), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'message': f'保存失败: {str(e)}'}), 500
