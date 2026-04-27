"""
Steam库存历史数据模块
提供库存历史记录的分页、筛选、搜索查询功能
（从 steamInventoryHistory.py 移植，改用 Date_base 原生 SQL）
"""
from flask import jsonify, request
from src.units.log import Log
from src.db_manager.database import DatabaseManager


class SteamInventoryHistoryData:
    """Steam库存历史数据类 - 提供列表查询"""

    @staticmethod
    def get_list():
        """获取Steam交易历史记录列表（分页、筛选、搜索）"""
        try:
            # 获取查询参数
            page = int(request.args.get('page', 1))
            page_size = int(request.args.get('page_size', 20))
            trade_type = request.args.get('trade_type', None)
            search = request.args.get('search', None)
            start_date = request.args.get('start_date', None)
            end_date = request.args.get('end_date', None)
            sort_field = request.args.get('sort_field', 'order_time')
            sort_order = request.args.get('sort_order', 'desc')
            need_stats = request.args.get('need_stats', 'true').lower() == 'true'

            # 允许排序的字段白名单
            allowed_sort_fields = {
                'order_time', 'trade_title', 'item_name', 'weapon_name',
                'weapon_type', 'float_range', 'trade_type', 'ID'
            }
            if sort_field not in allowed_sort_fields:
                sort_field = 'order_time'

            # 构建 WHERE 条件
            where_conditions = []

            if trade_type and trade_type in ['+', '-']:
                where_conditions.append(f"trade_type = '{trade_type}'")

            if search:
                safe_search = search.replace("'", "''")
                where_conditions.append(
                    f"(trade_title LIKE '%{safe_search}%' "
                    f"OR item_name LIKE '%{safe_search}%' "
                    f"OR weapon_name LIKE '%{safe_search}%')"
                )

            if start_date and end_date:
                safe_start = start_date.replace("'", "''")
                safe_end = end_date.replace("'", "''")
                where_conditions.append(
                    f"DATE(order_time) BETWEEN '{safe_start}' AND '{safe_end}'"
                )

            where_clause = ' AND '.join(where_conditions) if where_conditions else '1=1'

            sort_direction = 'DESC' if sort_order.lower() == 'desc' else 'ASC'
            offset = (page - 1) * page_size

            db = DatabaseManager()

            # 主查询
            data_sql = f"""
            SELECT instanceid, classid, ID, order_time, trade_title,
                   appid, item_name, weapon_name, weapon_type, float_range, trade_type
            FROM steam_inventoryhistory
            WHERE {where_clause}
            ORDER BY {sort_field} {sort_direction}
            LIMIT {page_size} OFFSET {offset}
            """

            results = db.execute_query(data_sql, ())

            records = []
            if results:
                for row in results:
                    records.append({
                        'instanceid': row[0],
                        'classid': row[1],
                        'ID': row[2],
                        'order_time': row[3],
                        'trade_title': row[4],
                        'appid': row[5],
                        'item_name': row[6],
                        'weapon_name': row[7],
                        'weapon_type': row[8],
                        'float_range': row[9],
                        'trade_type': row[10]
                    })

            # 总数查询
            count_sql = f"""
            SELECT COUNT(*) FROM steam_inventoryhistory
            WHERE {where_clause}
            """
            count_result = db.execute_query(count_sql, ())
            total_count = count_result[0][0] if count_result else 0

            # 可选统计
            gain_count = 0
            loss_count = 0

            if need_stats:
                gain_sql = f"""
                SELECT COUNT(*) FROM steam_inventoryhistory
                WHERE {where_clause} AND trade_type = '+'
                """
                loss_sql = f"""
                SELECT COUNT(*) FROM steam_inventoryhistory
                WHERE {where_clause} AND trade_type = '-'
                """

                gain_result = db.execute_query(gain_sql, ())
                loss_result = db.execute_query(loss_sql, ())

                gain_count = gain_result[0][0] if gain_success and gain_result else 0
                loss_count = loss_result[0][0] if loss_success and loss_result else 0

            return jsonify({
                'success': True,
                'data': {
                    'records': records,
                    'total': total_count,
                    'page': page,
                    'page_size': page_size,
                    'gain_count': gain_count,
                    'loss_count': loss_count
                }
            }), 200

        except Exception as e:
            Log().write_log(f"查询Steam交易历史列表失败: {str(e)}", 'error')
            return jsonify({
                'success': False,
                'error': str(e),
                'data': {
                    'records': [],
                    'total': 0,
                    'page': 1,
                    'page_size': 20,
                    'gain_count': 0,
                    'loss_count': 0
                }
            }), 500
