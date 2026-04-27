"""
Sell 页面数据查询模块
提供出售记录的筛选查询、时间范围搜索、类型磨损搜索
统一使用 DatabaseManager + 参数化 SQL
"""
from flask import jsonify, request
from src.db_manager.database import DatabaseManager


class SellData:

    @staticmethod
    def _build_filter_clauses(filters):
        """构建过滤条件的SQL子句和参数"""
        clauses = []
        params = []

        def add_clause(clause, *values):
            clauses.append(clause)
            params.extend(values)

        source = filters.get('source')
        if source:
            s = str(source).strip().lower()
            if s in ("c5", "c5game"):
                add_clause("LOWER(`from`) IN ('c5', 'c5game')")
            else:
                add_clause("LOWER(`from`) = LOWER(?)", source)

        status = filters.get('status')
        if status:
            add_clause("status = ?", status)

        status_sub = filters.get('status_sub')
        if status_sub:
            add_clause("status_sub = ?", status_sub)

        data_user = filters.get('data_user')
        if data_user:
            add_clause("data_user = ?", data_user)

        weapon_types = filters.get('weapon_types') or []
        if isinstance(weapon_types, list) and len(weapon_types) > 0:
            placeholders = ",".join(["?"] * len(weapon_types))
            clauses.append(f"weapon_type IN ({placeholders})")
            params.extend(weapon_types)

        float_ranges = filters.get('float_ranges') or []
        if isinstance(float_ranges, list) and len(float_ranges) > 0:
            placeholders = ",".join(["?"] * len(float_ranges))
            clauses.append(f"float_range IN ({placeholders})")
            params.extend(float_ranges)

        search_keyword = filters.get('search')
        if search_keyword:
            like = f"%{search_keyword}%"
            clauses.append("(item_name LIKE ? OR weapon_name LIKE ?)")
            params.extend([like, like])

        start_date = filters.get('start_date')
        end_date = filters.get('end_date')
        if start_date and end_date:
            clauses.append("order_time BETWEEN ? AND ?")
            params.extend([f"{start_date} 00:00:00", f"{end_date} 23:59:59"])

        where_clause = ""
        if clauses:
            where_clause = " WHERE " + " AND ".join(clauses)

        return where_clause, tuple(params)

    @staticmethod
    def get_sell_data_filtered():
        """组合查询接口：支持所有过滤条件的分页数据获取"""
        try:
            data = request.get_json() or {}
            filters = data.get('filters', {})
            min_offset = data.get('min', 0)
            max_limit = data.get('max', 20)

            where_clause, params = SellData._build_filter_clauses(filters)

            sql = f"""
            SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, `from`, order_time, status, status_sub, steam_hash_name, sticker, pendant, rename
            FROM sell
            {where_clause}
            ORDER BY order_time DESC
            LIMIT {max_limit} OFFSET {min_offset}
            """

            db = DatabaseManager()
            result = db.execute_query(sql, params)

            if result:
                return jsonify(result), 200
            return jsonify([]), 200
        except Exception as e:
            print(f"获取出售筛选数据失败: {e}")
            return jsonify({"success": False, "message": str(e)}), 500

    @staticmethod
    def search_sell_by_time_range(start_date, end_date):
        """按时间范围搜索 sell 记录"""
        try:
            sql = """
            SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, `from`, order_time, status, status_sub, steam_hash_name, sticker, pendant, rename
            FROM sell
            WHERE order_time BETWEEN ? AND ?
            ORDER BY order_time DESC
            """
            params = (f"{start_date} 00:00:00", f"{end_date} 23:59:59")
            db = DatabaseManager()
            result = db.execute_query(sql, params)
            return jsonify(result or []), 200
        except Exception as e:
            print(f"按时间范围查询出售失败: {e}")
            return jsonify([]), 500

    @staticmethod
    def search_by_type_and_wear():
        """根据类型和磨损等级搜索销售记录（支持多选）"""
        try:
            data = request.get_json() or {}
            weapon_types = data.get('weapon_type', [])
            float_ranges = data.get('float_range', [])
            page = max(int(data.get('page', 1)), 1)
            page_size = max(int(data.get('page_size', 20)), 1)

            if isinstance(weapon_types, str):
                weapon_types = [weapon_types]
            if isinstance(float_ranges, str):
                float_ranges = [float_ranges]

            conditions = []
            params = []

            if weapon_types:
                placeholders = ','.join(['?' for _ in weapon_types])
                conditions.append(f"weapon_type IN ({placeholders})")
                params.extend(weapon_types)

            if float_ranges:
                placeholders = ','.join(['?' for _ in float_ranges])
                conditions.append(f"float_range IN ({placeholders})")
                params.extend(float_ranges)

            if not conditions:
                return jsonify({
                    'success': True,
                    'data': [],
                    'total': 0,
                    'page': page,
                    'page_size': page_size
                }), 200

            where_clause = " AND ".join(conditions)
            offset = (page - 1) * page_size

            db = DatabaseManager()

            count_sql = f"SELECT COUNT(*) FROM sell WHERE {where_clause}"
            count_result = db.execute_query(count_sql, tuple(params))
            total = int(count_result[0][0]) if count_result else 0

            data_sql = f"""
            SELECT [ID], weapon_name, weapon_type, item_name, weapon_float, float_range,
                   price, price_original, buyer_name, status, status_sub, [from], order_time,
                   steam_id, st, sou
            FROM sell
            WHERE {where_clause}
            ORDER BY order_time DESC
            LIMIT ? OFFSET ?
            """
            data_result = db.execute_query(
                data_sql, tuple(params) + (page_size, offset)
            )

            records = []
            if data_result:
                for row in data_result:
                    records.append(list(row))

            return jsonify({
                'success': True,
                'data': records,
                'total': total,
                'page': page,
                'page_size': page_size
            }), 200

        except Exception as e:
            print(f"按类型和磨损等级搜索失败: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': str(e),
                'data': [],
                'total': 0
            }), 500
