"""
Rental 页面数据查询模块
提供借入数据的分页查询、状态筛选、名称搜索、时间范围搜索
查询 rental 表
"""
from flask import jsonify
from src.execution_db import Date_base


class RentalData:

    @staticmethod
    def get_rental_data(min, max):
        """分页获取借入数据"""
        sql = f"""
        SELECT
            ID, weapon_name, weapon_type, item_name, weapon_float, float_range, price,
            lessor_name, status, last_status, "from", lean_start_time, lean_end_time,
            total_Lease_Days, max_Lease_Days, steam_hash_name, sticker, pendant, rename, data_user
        FROM rental
        ORDER BY lean_start_time DESC
        LIMIT {max} OFFSET {min};
        """
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag:
                return jsonify(data), 200
        return "查询失败", 500

    @staticmethod
    def get_rental_data_by_status(status, min, max):
        """按状态分页获取借入数据"""
        if status == 'all':
            sql = f"""
            SELECT
                ID, weapon_name, weapon_type, item_name, weapon_float, float_range, price,
                lessor_name, status, last_status, "from", lean_start_time, lean_end_time,
                total_Lease_Days, max_Lease_Days, steam_hash_name, sticker, pendant, rename, data_user
            FROM rental
            ORDER BY lean_start_time DESC
            LIMIT {max} OFFSET {min};
            """
        else:
            sql = f"""
            SELECT
                ID, weapon_name, weapon_type, item_name, weapon_float, float_range, price,
                lessor_name, status, last_status, "from", lean_start_time, lean_end_time,
                total_Lease_Days, max_Lease_Days, steam_hash_name, sticker, pendant, rename, data_user
            FROM rental
            WHERE status = '{status}'
            ORDER BY lean_start_time DESC
            LIMIT {max} OFFSET {min};
            """
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag:
                return jsonify(data), 200
        return "查询失败", 500

    @staticmethod
    def get_rental_data_by_status_sub(last_status, min, max):
        """按子状态分页获取借入数据"""
        if last_status == 'all':
            sql = f"""
            SELECT
                ID, weapon_name, weapon_type, item_name, weapon_float, float_range, price,
                lessor_name, status, last_status, "from", lean_start_time, lean_end_time,
                total_Lease_Days, max_Lease_Days, steam_hash_name, sticker, pendant, rename, data_user
            FROM rental
            WHERE last_status IS NOT NULL AND last_status != ''
            ORDER BY lean_start_time DESC
            LIMIT {max} OFFSET {min};
            """
        else:
            safe_sub = last_status.replace("'", "''")
            sql = f"""
            SELECT
                ID, weapon_name, weapon_type, item_name, weapon_float, float_range, price,
                lessor_name, status, last_status, "from", lean_start_time, lean_end_time,
                total_Lease_Days, max_Lease_Days, steam_hash_name, sticker, pendant, rename, data_user
            FROM rental
            WHERE last_status = '{safe_sub}'
            ORDER BY lean_start_time DESC
            LIMIT {max} OFFSET {min};
            """
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag:
                return jsonify(data), 200
        return "查询失败", 500

    @staticmethod
    def select_rental_weapon_name(item_name):
        """按武器名称搜索借入数据"""
        sql = f"""
        SELECT
            ID, weapon_name, weapon_type, item_name, weapon_float, float_range, price,
            lessor_name, status, last_status, "from", lean_start_time, lean_end_time,
            total_Lease_Days, max_Lease_Days, steam_hash_name, sticker, pendant, rename, data_user
        FROM rental
        WHERE item_name LIKE '%{item_name}%' OR weapon_name LIKE '%{item_name}%'
        ORDER BY lean_start_time DESC;
        """
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag:
                return jsonify(data), 200
        return "查询失败", 500

    @staticmethod
    def search_rental_by_time_range(start_date, end_date):
        """按时间范围搜索借入数据（全量返回）"""
        sql = f"""
        SELECT
            ID, weapon_name, weapon_type, item_name, weapon_float, float_range, price,
            lessor_name, status, last_status, "from", lean_start_time, lean_end_time,
            total_Lease_Days, max_Lease_Days, steam_hash_name, sticker, pendant, rename
        FROM rental
        WHERE DATE(lean_start_time) >= '{start_date}' AND DATE(lean_start_time) <= '{end_date}'
        ORDER BY lean_start_time DESC;
        """
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag:
                return jsonify(data), 200
        return "查询失败", 500
