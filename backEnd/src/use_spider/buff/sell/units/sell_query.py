"""
BUFF sell 查询模块
提供 Spider 所需的销售记录查询接口
"""
from flask import jsonify
from src.db_manager.index.model.sell import SellModel


class SellQuery:

    @staticmethod
    def select_not_end(user_id):
        """查询 BUFF 平台未完成的销售订单 ID 列表"""
        try:
            records = SellModel.find_all(
                "status NOT IN ('已完成', '已取消') AND data_user = ? AND \"from\" = 'buff'",
                (user_id,)
            )
            not_end_orders = [record.ID for record in records]
            return jsonify({"not_end_orders": not_end_orders}), 200
        except Exception as e:
            print(f"查询未完成订单失败: {e}")
            return jsonify({"not_end_orders": []}), 500

    @staticmethod
    def apex_time_url(user_id):
        """获取 BUFF 平台最新销售订单时间，供 Spider 判断增量同步起点"""
        try:
            records = SellModel.find_all(
                "data_user = ? AND \"from\" = 'buff' ORDER BY order_time DESC",
                (user_id,),
                limit=1
            )
            last_order_time = records[0].order_time if records else None
            return jsonify({"last_order_time": last_order_time}), 200
        except Exception as e:
            print(f"查询最新订单时间失败: {e}")
            return jsonify({"last_order_time": None}), 500

    @staticmethod
    def get_latest_data(user_id):
        """获取指定用户 BUFF 平台的最新一条销售记录（ID 和订单时间）"""
        try:
            records = SellModel.find_all(
                "data_user = ? AND \"from\" = 'buff' ORDER BY order_time DESC",
                (user_id,),
                limit=1
            )
            if records and len(records) > 0:
                latest_record = records[0]
                return jsonify({"ID": latest_record.ID, "order_time": latest_record.order_time}), 200
            else:
                return jsonify({"ID": None, "order_time": None}), 200
        except Exception as e:
            print(f"获取最新销售数据失败: {e}")
            import traceback
            print(f"详细错误信息: {traceback.format_exc()}")
            return jsonify({"ID": None, "order_time": None}), 500

    @staticmethod
    def count_data(user_id):
        """统计指定用户 BUFF 平台的销售记录数量"""
        try:
            records = SellModel.find_all("data_user = ? AND \"from\" = 'buff'", (user_id,))
            count = len(records)
            print(f"BUFF销售记录数量: {count}")
            return jsonify({"count": count}), 200
        except Exception as e:
            print(f"查询数据数量失败: {e}")
            return jsonify({"count": 0}), 500
