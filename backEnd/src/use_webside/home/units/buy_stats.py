"""
Home 页面购买统计模块
从 webBuyV1/getBuyStats 分离的独立实现
"""
from flask import jsonify
from src.units.execution_db import Date_base


class HomeBuyStats:

    @staticmethod
    def get_buy_stats():
        """获取购买统计数据（总数量、总金额、平均价格等）"""
        sql = """
        SELECT
            COUNT(*) as total_count,
            COALESCE(SUM(CASE WHEN status != '已取消' THEN price ELSE 0 END), 0) as total_amount,
            COALESCE(AVG(CASE WHEN status != '已取消' THEN price ELSE NULL END), 0) as avg_price,
            COUNT(CASE WHEN status = '已完成' THEN 1 END) as completed_count,
            COUNT(CASE WHEN status = '已取消' THEN 1 END) as cancelled_count,
            COUNT(CASE WHEN status = '待收货' THEN 1 END) as pending_count
        FROM buy
        """
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag and len(data) > 0:
                stats = data[0]
                return jsonify({
                    "total_count": stats[0],
                    "total_amount": round(float(stats[1]), 2),
                    "avg_price": round(float(stats[2]), 2),
                    "completed_count": stats[3],
                    "cancelled_count": stats[4],
                    "pending_count": stats[5]
                }), 200
        return "查询失败", 500
