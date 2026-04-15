"""
Home 页面购买统计模块
从 webBuyV1/getBuyStats 分离的独立实现
与 Home 其他接口一致：使用 DatabaseManager + 参数化 SQL
"""
from flask import jsonify
from src.db_manager.database import DatabaseManager


class HomeBuyStats:

    @staticmethod
    def get_buy_stats():
        """获取购买统计数据（总数量、总金额、平均价格等）"""
        sql = """
        SELECT
            COUNT(*) AS total_count,
            COALESCE(SUM(CASE WHEN status != '已取消' THEN price ELSE 0 END), 0) AS total_amount,
            COALESCE(AVG(CASE WHEN status != '已取消' THEN price ELSE NULL END), 0) AS avg_price,
            COUNT(CASE WHEN status = '已完成' THEN 1 END) AS completed_count,
            COUNT(CASE WHEN status = '已取消' THEN 1 END) AS cancelled_count,
            COUNT(CASE WHEN status = '待收货' THEN 1 END) AS pending_count
        FROM buy
        """
        try:
            db = DatabaseManager()
            rows = db.execute_query(sql, ())
            if not rows:
                return jsonify({"success": False, "message": "查询失败"}), 500
            stats = rows[0]
            return jsonify({
                "total_count": stats[0],
                "total_amount": round(float(stats[1]), 2),
                "avg_price": round(float(stats[2]), 2),
                "completed_count": stats[3],
                "cancelled_count": stats[4],
                "pending_count": stats[5],
            }), 200
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
