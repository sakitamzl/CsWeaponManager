"""
CSFloat buy 查询模块
提供 Spider 所需的购买记录查询接口
"""
from flask import jsonify
from src.db_manager.csfloat.model import CsFloatBuyModel


class BuyQuery:

    @staticmethod
    def select_not_end(user_id):
        """查询 CSFloat 未完成购买订单 ID 列表"""
        try:
            records = CsFloatBuyModel.find_not_end_status(user_id)
            ids = [record.ID for record in records]
            return jsonify({"not_end_orders": ids}), 200
        except Exception as exc:
            print(f"查询 CSFloat 购买未完成订单失败: {exc}")
            return jsonify({"not_end_orders": []}), 500

    @staticmethod
    def get_latest_data(user_id):
        """获取指定用户最新一条 CSFloat 购买记录（ID 和订单时间）"""
        try:
            record = CsFloatBuyModel.get_latest_order(user_id)
            if not record:
                return jsonify({"ID": None, "order_time": None}), 200
            return jsonify({"ID": record.ID, "order_time": record.created_at}), 200
        except Exception as exc:
            print(f"获取最新 CSFloat 购买数据失败: {exc}")
            return jsonify({"ID": None, "order_time": None}), 500

    @staticmethod
    def count_data(user_id):
        """统计指定用户 CSFloat 购买记录数量"""
        try:
            records = CsFloatBuyModel.find_all("data_user = ?", (user_id,))
            return jsonify({"count": len(records)}), 200
        except Exception as exc:
            print(f"统计 CSFloat 购买数据失败: {exc}")
            return jsonify({"count": 0}), 500

    @staticmethod
    def get_earliest_not_end(user_id):
        """获取指定用户最早的一条未完成订单的时间"""
        try:
            records = CsFloatBuyModel.find_all(
                "data_user = ? AND state != '已完成' AND state != '已取消' ORDER BY created_at ASC LIMIT 1",
                (user_id,)
            )
            if records:
                return jsonify({"success": True, "earliest_time": records[0].created_at}), 200
            else:
                return jsonify({"success": True, "earliest_time": None}), 200
        except Exception as exc:
            print(f"获取最早未完成订单失败: {exc}")
            return jsonify({"success": False, "error": str(exc)}), 500
