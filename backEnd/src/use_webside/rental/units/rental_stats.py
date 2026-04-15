"""
Rental 页面统计模块
提供借入数据的整体统计和按时间范围统计
查询 rental 表；统一 DatabaseManager + 参数化 SQL
"""
from flask import jsonify
from src.db_manager.database import DatabaseManager


class RentalStats:

    @staticmethod
    def get_rental_stats():
        """获取借入数据整体统计"""
        try:
            sql = """
            SELECT
                COUNT(*) as total_count,
                COALESCE(SUM(price * total_Lease_Days), 0) as total_amount,
                COALESCE(AVG(price), 0) as avg_price,
                COALESCE(SUM(total_Lease_Days), 0) as total_lease_days,
                COALESCE(AVG(total_Lease_Days), 0) as avg_lease_days,
                COUNT(CASE WHEN status = '租赁中' THEN 1 END) as renting_count,
                COUNT(CASE WHEN status = '已完成' THEN 1 END) as completed_count,
                COUNT(CASE WHEN status = '已取消' THEN 1 END) as cancelled_count
            FROM rental
            """
            rows = DatabaseManager().execute_query(sql, ())
            if not rows:
                return jsonify({"success": False, "message": "查询失败"}), 500
            stats = rows[0]
            return jsonify({
                "total_count": stats[0],
                "total_amount": round(float(stats[1]), 2),
                "avg_price": round(float(stats[2]), 2),
                "total_lease_days": stats[3],
                "avg_lease_days": round(float(stats[4]), 1),
                "renting_count": stats[5],
                "completed_count": stats[6],
                "cancelled_count": stats[7]
            }), 200
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    @staticmethod
    def get_rental_stats_by_time_range(start_date, end_date):
        """按时间范围获取借入数据统计"""
        try:
            sql = """
            SELECT
                COUNT(*) as total_count,
                COALESCE(SUM(price * total_Lease_Days), 0) as total_amount,
                COALESCE(AVG(price), 0) as avg_price,
                COALESCE(SUM(total_Lease_Days), 0) as total_lease_days,
                COALESCE(AVG(total_Lease_Days), 0) as avg_lease_days,
                COUNT(CASE WHEN status = '租赁中' THEN 1 END) as renting_count,
                COUNT(CASE WHEN status = '已完成' THEN 1 END) as completed_count,
                COUNT(CASE WHEN status = '已取消' THEN 1 END) as cancelled_count
            FROM rental
            WHERE DATE(lean_start_time) >= ? AND DATE(lean_start_time) <= ?
            """
            rows = DatabaseManager().execute_query(sql, (start_date, end_date))
            if not rows:
                return jsonify({"success": False, "message": "查询失败"}), 500
            stats = rows[0]
            return jsonify({
                "total_count": stats[0],
                "total_amount": round(float(stats[1]), 2),
                "avg_price": round(float(stats[2]), 2),
                "total_lease_days": stats[3],
                "avg_lease_days": round(float(stats[4]), 1),
                "renting_count": stats[5],
                "completed_count": stats[6],
                "cancelled_count": stats[7]
            }), 200
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
