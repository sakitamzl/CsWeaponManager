"""
StockComponents 页面账号查询模块
提供完美世界账号列表查询及组件数量统计
"""
from flask import jsonify, request
from src.db_manager.database import DatabaseManager
import json


class StockComponentsAccounts:

    @staticmethod
    def get_steam_ids():
        """获取所有完美世界配置列表（从 config 表 key1='perfectworld'），并统计每个账号的组件数量"""
        try:
            db = DatabaseManager()

            # 获取查询参数，判断是否只统计特定classid的物品
            classid_filter = request.args.get('classid', '')

            sql = """
            SELECT dataID, dataName, value FROM config
            WHERE key1 = 'perfectworld'
            ORDER BY dataID
            """

            results = db.execute_query(sql)

            if not results:
                return jsonify({
                    'success': True,
                    'data': [],
                    'message': '未找到完美世界配置'
                }), 200

            config_list = []

            for row in results:
                data_id = row[0]
                data_name = row[1] if row[1] else None
                value = row[2]

                if value:
                    try:
                        if isinstance(value, str):
                            config_data = json.loads(value)
                        else:
                            config_data = value

                        steam_id = config_data.get('steamID')
                        if not steam_id:
                            continue

                        if not data_name:
                            data_name = config_data.get('dataName', steam_id)

                        # 查询该steamID在库存组件中的物品数量
                        item_count = 0
                        try:
                            if classid_filter:
                                count_sql = """
                                SELECT COUNT(*)
                                FROM steam_stockComponents
                                WHERE data_user = ? AND classid = ?
                                """
                                count_result = db.execute_query(count_sql, (steam_id, classid_filter))
                            else:
                                count_sql = """
                                SELECT COUNT(*)
                                FROM steam_stockComponents
                                WHERE data_user = ?
                                """
                                count_result = db.execute_query(count_sql, (steam_id,))

                            if count_result and len(count_result) > 0 and count_result[0]:
                                item_count = count_result[0][0] or 0
                        except Exception:
                            item_count = 0

                        config_item = {
                            'dataID': data_id,
                            'dataName': data_name,
                            'steamID': steam_id,
                            'item_count': item_count,
                            'status': config_data.get('status', '1')
                        }
                        config_list.append(config_item)

                    except Exception:
                        continue

            return jsonify({
                'success': True,
                'data': config_list
            }), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': f'查询失败: {str(e)}'
            }), 500

    @staticmethod
    def get_component_count(steam_id):
        """获取指定用户的库存组件数量（按assetid去重）"""
        try:
            db = DatabaseManager()

            sql = """
            SELECT COUNT(DISTINCT assetid) as component_count
            FROM steam_stockComponents
            WHERE data_user = ?
              AND assetid IS NOT NULL
              AND assetid != ''
            """

            result = db.execute_query(sql, (steam_id,))

            component_count = 0
            if result and result[0][0] is not None:
                component_count = result[0][0]

            return jsonify({
                'success': True,
                'data': {
                    'component_count': component_count
                }
            }), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': f'查询失败: {str(e)}'
            }), 500
