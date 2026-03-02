"""
buy 查询模块
提供 Spider 所需的购买记录查询接口（时间戳、ID 列表、数量）
"""
from flask import jsonify
from src.db_manager.youpin.model.yyyp_buy import YyypBuyModel


class BuyQuery:

    @staticmethod
    def select_apex_time(data_user=None):
        """获取指定用户最新购买记录时间，供 Spider 判断增量同步起点"""
        try:
            if not data_user:
                return jsonify({'error': 'data_user参数不能为空'}), 400

            records = YyypBuyModel.find_all(
                "data_user = ? ORDER BY order_time DESC",
                (data_user,),
                limit=1
            )
            if records and records[0].order_time:
                return jsonify({
                    "success": True,
                    "order_time": str(records[0].order_time)
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "order_time": None,
                    "message": "未查询到数据"
                }), 200
        except Exception as e:
            print(f"查询最新时间失败: {e}")
            return jsonify({
                "success": False,
                "order_time": None,
                "message": f"查询异常: {str(e)}"
            }), 500

    @staticmethod
    def get_weapon_not_end_status_list(data_user):
        """获取未完成/未取消的购买订单 ID 列表，供 Spider 更新状态"""
        try:
            records = YyypBuyModel.find_all(
                "status NOT IN ('已完成', '已取消') AND data_user = ?",
                (data_user,)
            )
            data = [[record.ID] for record in records]
            return jsonify(data), 200
        except Exception as e:
            print(f"查询未完成状态列表失败: {e}")
            return jsonify([]), 500

    @staticmethod
    def select_not_end_id(data_user):
        """获取状态非已完成/已取消的购买订单 ID 列表"""
        try:
            records = YyypBuyModel.find_all(
                "status <> '已完成' AND status <> '已取消' AND data_user = ?",
                (data_user,)
            )
            data = [[record.ID] for record in records]
            return jsonify(data), 200
        except Exception as e:
            print(f"查询未完成ID列表失败: {e}")
            return jsonify([]), 500

    @staticmethod
    def get_count(data_user):
        """获取指定用户购买记录总数，供 Spider 计算分页起点"""
        try:
            records = YyypBuyModel.find_all("data_user = ?", (data_user,))
            data = str(len(records))
            return data, 200
        except Exception as e:
            print(f"查询记录数量失败: {e}")
            return "0", 500
