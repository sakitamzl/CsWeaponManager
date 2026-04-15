"""
Rental 页面数据查询模块
提供借入数据的分页查询、状态筛选、名称搜索、时间范围搜索
查询 rental 表；统一 DatabaseManager + 参数化 SQL
"""
from flask import jsonify
from src.db_manager.database import DatabaseManager

_RENTAL_SELECT = """
        SELECT
            ID, weapon_name, weapon_type, item_name, weapon_float, float_range, price,
            lessor_name, status, last_status, "from", lean_start_time, lean_end_time,
            total_Lease_Days, max_Lease_Days, steam_hash_name, sticker, pendant, rename, data_user
        FROM rental
"""


class RentalData:

    @staticmethod
    def get_rental_data(min, max):
        """分页获取借入数据（max=limit, min=offset）"""
        try:
            sql = f"""
            {_RENTAL_SELECT.strip()}
            ORDER BY lean_start_time DESC
            LIMIT ? OFFSET ?
            """
            rows = DatabaseManager().execute_query(sql, (max, min))
            return jsonify(rows or []), 200
        except Exception as e:
            print(f"查询借入数据失败: {e}")
            return jsonify({"success": False, "message": str(e)}), 500

    @staticmethod
    def get_rental_data_by_status(status, min, max):
        """按状态分页获取借入数据"""
        try:
            db = DatabaseManager()
            if status == 'all':
                sql = f"""
                {_RENTAL_SELECT.strip()}
                ORDER BY lean_start_time DESC
                LIMIT ? OFFSET ?
                """
                rows = db.execute_query(sql, (max, min))
            else:
                sql = f"""
                {_RENTAL_SELECT.strip()}
                WHERE status = ?
                ORDER BY lean_start_time DESC
                LIMIT ? OFFSET ?
                """
                rows = db.execute_query(sql, (status, max, min))
            return jsonify(rows or []), 200
        except Exception as e:
            print(f"按状态查询借入数据失败: {e}")
            return jsonify({"success": False, "message": str(e)}), 500

    @staticmethod
    def get_rental_data_by_status_sub(last_status, min, max):
        """按子状态分页获取借入数据"""
        try:
            db = DatabaseManager()
            if last_status == 'all':
                sql = f"""
                {_RENTAL_SELECT.strip()}
                WHERE last_status IS NOT NULL AND last_status != ''
                ORDER BY lean_start_time DESC
                LIMIT ? OFFSET ?
                """
                rows = db.execute_query(sql, (max, min))
            else:
                sql = f"""
                {_RENTAL_SELECT.strip()}
                WHERE last_status = ?
                ORDER BY lean_start_time DESC
                LIMIT ? OFFSET ?
                """
                rows = db.execute_query(sql, (last_status, max, min))
            return jsonify(rows or []), 200
        except Exception as e:
            print(f"按子状态查询借入数据失败: {e}")
            return jsonify({"success": False, "message": str(e)}), 500

    @staticmethod
    def select_rental_weapon_name(item_name):
        """按武器名称搜索借入数据"""
        try:
            like = f"%{item_name}%"
            sql = f"""
            {_RENTAL_SELECT.strip()}
            WHERE item_name LIKE ? OR weapon_name LIKE ?
            ORDER BY lean_start_time DESC
            """
            rows = DatabaseManager().execute_query(sql, (like, like))
            return jsonify(rows or []), 200
        except Exception as e:
            print(f"按名称搜索借入失败: {e}")
            return jsonify({"success": False, "message": str(e)}), 500

    @staticmethod
    def search_rental_by_time_range(start_date, end_date):
        """按时间范围搜索借入数据（全量返回）"""
        try:
            sql = """
            SELECT
                ID, weapon_name, weapon_type, item_name, weapon_float, float_range, price,
                lessor_name, status, last_status, "from", lean_start_time, lean_end_time,
                total_Lease_Days, max_Lease_Days, steam_hash_name, sticker, pendant, rename
            FROM rental
            WHERE DATE(lean_start_time) >= ? AND DATE(lean_start_time) <= ?
            ORDER BY lean_start_time DESC
            """
            rows = DatabaseManager().execute_query(sql, (start_date, end_date))
            return jsonify(rows or []), 200
        except Exception as e:
            print(f"按时间范围查询借入失败: {e}")
            return jsonify({"success": False, "message": str(e)}), 500
