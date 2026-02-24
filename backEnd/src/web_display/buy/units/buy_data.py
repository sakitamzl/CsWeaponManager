"""
Buy 页面数据查询模块
提供购入记录的分页查询、时间范围搜索、类型磨损搜索、总数统计
"""
from flask import jsonify, request
from src.execution_db import Date_base
from src.db_manager.index.model.buy import BuyModel


class BuyData:

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
    def get_buy_data_filtered():
        """组合查询接口：支持所有过滤条件的分页数据获取"""
        try:
            data = request.get_json() or {}
            filters = data.get('filters', {})
            min_offset = data.get('min', 0)
            max_limit = data.get('max', 20)

            where_clause, params = BuyData._build_filter_clauses(filters)

            sql = f"""
            SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, `from`, order_time, status, status_sub, steam_hash_name, sticker, pendant, rename
            FROM buy
            {where_clause}
            ORDER BY order_time DESC
            LIMIT {max_limit} OFFSET {min_offset}
            """

            db = Date_base()
            result = db.execute_query(sql, params)

            if result:
                return jsonify(result), 200
            return jsonify([]), 200
        except Exception as e:
            print(f"获取购入筛选数据失败: {e}")
            return jsonify({"success": False, "message": str(e)}), 500

    @staticmethod
    def count_buy_number():
        """获取购买记录总数"""
        try:
            records = BuyModel.find_all()
            count = len(records)
            return jsonify({"count": count}), 200
        except Exception as e:
            print(f"查询购买数量失败: {e}")
            return jsonify({"count": 0}), 500

    @staticmethod
    def search_buy_by_time_range(start_date, end_date):
        """按时间范围搜索 buy 记录"""
        try:
            sql = """
            SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, `from`, order_time, status, status_sub, steam_hash_name, sticker, pendant, rename
            FROM buy
            WHERE order_time BETWEEN ? AND ?
            ORDER BY order_time DESC
            """
            params = (f"{start_date} 00:00:00", f"{end_date} 23:59:59")
            db = Date_base()
            result = db.execute_query(sql, params)
            return jsonify(result or []), 200
        except Exception as e:
            print(f"按时间范围查询购入失败: {e}")
            return jsonify([]), 500

    @staticmethod
    def search_by_type_and_wear():
        """根据类型和磨损等级搜索购买记录（支持多选）"""
        try:
            data = request.get_json()
            weapon_types = data.get('weapon_types', [])
            float_ranges = data.get('float_ranges', [])
            page = data.get('page', 1)
            page_size = data.get('page_size', 20)

            conditions = []

            if weapon_types and len(weapon_types) > 0:
                weapon_type_conditions = "', '".join(weapon_types)
                conditions.append(f"weapon_type IN ('{weapon_type_conditions}')")

            if float_ranges and len(float_ranges) > 0:
                float_range_conditions = "', '".join(float_ranges)
                conditions.append(f"float_range IN ('{float_range_conditions}')")

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

            db = Date_base()

            count_sql = f"SELECT COUNT(*) FROM buy WHERE {where_clause}"
            success, count_result = db.select(count_sql)
            total = count_result[0][0] if success and count_result else 0

            data_sql = f"""
            SELECT ID, weapon_name, weapon_type, item_name, weapon_float, float_range,
                   price, seller_name, status, status_sub, `from`, order_time,
                   steam_id, buy_number, sell_of, st, sou, payment, trade_type, data_user
            FROM buy
            WHERE {where_clause}
            ORDER BY order_time DESC
            LIMIT {page_size} OFFSET {offset}
            """
            success2, data_result = db.select(data_sql)

            records = []
            if success2 and data_result:
                for row in data_result:
                    records.append([
                        row[0], row[1], row[2], row[3], row[4], row[5],
                        row[6], row[7], row[8], row[9], row[10], row[11],
                        row[12], row[13], row[14], row[15], row[16], row[17],
                        row[18], row[19]
                    ])

            return jsonify({
                'success': True,
                'data': records,
                'total': total,
                'page': page,
                'page_size': page_size
            }), 200

        except Exception as e:
            print(f"按类型和磨损等级搜索失败: {e}")
            return jsonify({
                'success': False,
                'message': str(e),
                'data': [],
                'total': 0
            }), 500
