"""
C5GAME buy 查询模块
提供 Spider 所需的购买记录查询接口
"""
from flask import jsonify
from src.db_manager.index.model.buy import BuyModel


class BuyQuery:
    @staticmethod
    def get_latest_data(user_id):
        """获取指定用户 C5GAME 平台最新一条购买记录（ID 和订单时间）"""
        try:
            records = BuyModel.find_all(
                "data_user = ? AND \"from\" IN ('c5game', 'C5', 'C5game') ORDER BY order_time DESC",
                (user_id,),
                limit=1
            )
            if records and len(records) > 0:
                latest_record = records[0]
                return jsonify({"ID": latest_record.ID, "order_time": latest_record.order_time}), 200
            return jsonify({"ID": None, "order_time": None}), 200
        except Exception as exc:
            print(f"获取最新 C5GAME 购买数据失败: {exc}")
            return jsonify({"ID": None, "order_time": None}), 500

