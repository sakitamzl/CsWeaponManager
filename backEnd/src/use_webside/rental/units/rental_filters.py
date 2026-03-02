"""
Rental 页面筛选选项模块
提供下拉框数据：武器类型、磨损等级、状态、子状态、平台、用户列表
查询 rental 表
"""
from flask import jsonify
from src.execution_db import Date_base


class RentalFilters:

    @staticmethod
    def get_rental_weapon_types():
        """获取所有武器类型列表"""
        try:
            sql = """
            SELECT DISTINCT weapon_type
            FROM rental
            WHERE weapon_type IS NOT NULL AND weapon_type != ''
            ORDER BY weapon_type
            """
            result = Date_base().select(sql)
            if result and len(result) == 2:
                flag, data = result
                if flag:
                    weapon_types = [row[0] for row in data if row[0]]
                    return jsonify({"success": True, "data": weapon_types}), 200
            return jsonify({"success": True, "data": []}), 200
        except Exception as e:
            print(f"获取武器类型失败: {e}")
            return jsonify({"success": False, "message": str(e)}), 500

    @staticmethod
    def get_rental_float_ranges():
        """获取所有磨损等级列表"""
        try:
            sql = """
            SELECT DISTINCT float_range
            FROM rental
            WHERE float_range IS NOT NULL AND float_range != ''
            ORDER BY
                CASE float_range
                    WHEN '崭新出厂' THEN 1
                    WHEN '略有磨损' THEN 2
                    WHEN '久经沙场' THEN 3
                    WHEN '破损不堪' THEN 4
                    WHEN '战痕累累' THEN 5
                    ELSE 6
                END
            """
            result = Date_base().select(sql)
            if result and len(result) == 2:
                flag, data = result
                if flag:
                    float_ranges = [row[0] for row in data if row[0]]
                    return jsonify({"success": True, "data": float_ranges}), 200
            return jsonify({"success": True, "data": []}), 200
        except Exception as e:
            print(f"获取磨损等级失败: {e}")
            return jsonify({"success": False, "message": str(e)}), 500

    @staticmethod
    def get_rental_status_list():
        """获取所有状态列表"""
        try:
            sql = """
            SELECT DISTINCT status
            FROM rental
            WHERE status IS NOT NULL AND status != ''
            ORDER BY status
            """
            result = Date_base().select(sql)
            if result and len(result) == 2:
                flag, data = result
                if flag:
                    status_list = [row[0] for row in data if row[0]]
                    return jsonify({"success": True, "data": status_list}), 200
            return jsonify({"success": True, "data": []}), 200
        except Exception as e:
            print(f"获取状态列表失败: {e}")
            return jsonify({"success": False, "message": str(e)}), 500

    @staticmethod
    def get_rental_status_sub_list(status='all'):
        """获取子状态列表，可选按主状态筛选"""
        try:
            if status == 'all' or not status:
                sql = """
                SELECT DISTINCT last_status
                FROM rental
                WHERE last_status IS NOT NULL AND last_status != ''
                ORDER BY last_status
                """
            else:
                safe_status = status.replace("'", "''")
                sql = f"""
                SELECT DISTINCT last_status
                FROM rental
                WHERE status = '{safe_status}'
                    AND last_status IS NOT NULL
                    AND last_status != ''
                ORDER BY last_status
                """
            result = Date_base().select(sql)
            if result and len(result) == 2:
                flag, data = result
                if flag:
                    status_sub_list = [row[0] for row in data if row[0]]
                    return jsonify({"success": True, "data": status_sub_list}), 200
            return jsonify({"success": True, "data": []}), 200
        except Exception as e:
            print(f"获取子状态列表失败: {e}")
            return jsonify({"success": False, "message": str(e)}), 500

    @staticmethod
    def get_rental_platform_list():
        """获取所有平台列表"""
        try:
            sql = """
            SELECT DISTINCT "from"
            FROM rental
            WHERE "from" IS NOT NULL AND "from" != ''
            ORDER BY "from"
            """
            result = Date_base().select(sql)
            if result and len(result) == 2:
                flag, data = result
                if flag:
                    platform_list = [row[0] for row in data if row[0]]
                    return jsonify({"success": True, "data": platform_list}), 200
            return jsonify({"success": True, "data": []}), 200
        except Exception as e:
            print(f"获取平台列表失败: {e}")
            return jsonify({"success": False, "message": str(e)}), 500

    @staticmethod
    def get_rental_user_list():
        """获取所有用户列表（data_user字段）"""
        try:
            sql = """
            SELECT DISTINCT data_user
            FROM rental
            WHERE data_user IS NOT NULL AND data_user != ''
            ORDER BY data_user
            """
            result = Date_base().select(sql)
            if result and len(result) == 2:
                flag, data = result
                if flag:
                    user_list = [row[0] for row in data if row[0]]
                    return jsonify({"success": True, "data": user_list}), 200
            return jsonify({"success": True, "data": []}), 200
        except Exception as e:
            print(f"获取用户列表失败: {e}")
            return jsonify({"success": False, "message": str(e)}), 500
