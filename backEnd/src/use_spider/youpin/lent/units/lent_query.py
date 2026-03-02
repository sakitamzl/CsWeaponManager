"""
lent 查询模块
提供 Spider 所需的出租记录查询接口
"""
from flask import jsonify
from src.now_time import today
from src.db_manager.youpin.model.yyyp_lent import YyypLentModel
from src.db_manager.index.model.lent import LentModel


class LentQuery:

    @staticmethod
    def select_apex_time(steamId):
        """获取指定用户最新租赁订单时间，供 Spider 判断增量同步起点"""
        try:
            from src.db_manager.database import DatabaseManager
            db = DatabaseManager()

            sql = """
                SELECT lean_start_time
                FROM yyyp_lent
                WHERE data_user = ?
                ORDER BY lean_start_time DESC
                LIMIT 1
            """
            result = db.execute_query(sql, (steamId,))

            if result and len(result) > 0 and result[0][0]:
                apex_time = result[0][0]
                return jsonify({"success": True, "order_time": apex_time}), 200
            else:
                return jsonify({"success": False, "order_time": None, "message": "未查询到数据"}), 200
        except Exception as e:
            print(f"查询最新租赁时间失败: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"success": False, "order_time": None, "message": f"查询异常: {str(e)}"}), 500

    @staticmethod
    def get_count(steamId):
        """获取指定用户租赁订单总数，供 Spider 计算分页起点"""
        try:
            count = YyypLentModel.count(where="data_user = ?", params=(steamId,))
            return jsonify(count), 200
        except Exception as e:
            print(f"查询租赁订单数量失败: {e}")
            import traceback
            traceback.print_exc()
            return jsonify(0), 500

    @staticmethod
    def get_now_lenting_list():
        """获取当前需要更新状态的租赁订单列表（未完成且已到达或超过结束时间）"""
        try:
            current_time = today()
            records = YyypLentModel.find_all(
                where=" status IN ('租赁中', '转租中') AND lean_end_time <= ? or lean_end_time is null and status != '已取消'",
                params=(current_time,)
            )
            data = [[record.ID] for record in records]
            return jsonify(data), 200
        except Exception as e:
            print(f"查询租借列表失败: {e}")
            import traceback
            traceback.print_exc()
            return jsonify([]), 500

    @staticmethod
    def get_time_out_lent():
        """获取超时的租赁订单"""
        try:
            records = YyypLentModel.find_all(
                where="lean_end_time < ? AND status IN ('白玩中', '归还中', '租赁中')",
                params=(today(),)
            )
            data = [[record.ID] for record in records]
            return jsonify(data), 200
        except Exception as e:
            print(f"查询超时租赁订单失败: {e}")
            import traceback
            traceback.print_exc()
            return jsonify([]), 500

    @staticmethod
    def get_buyout_lent_list(steamId):
        """获取状态为"被买断"且未同步到 sell 表的租赁订单列表"""
        try:
            records = LentModel.find_all(
                where="status in ('被买断', '已买断') AND data_user = ?",
                params=(steamId,)
            )
            data = [
                [
                    record.ID, record.weapon_name, record.weapon_type, record.item_name,
                    record.weapon_float, record.float_range, record.lenter_name,
                    record.lean_start_time, record.steam_hash_name,
                    record.sticker, record.pendant, record.rename
                ]
                for record in records
            ]
            return jsonify(data), 200
        except Exception as e:
            print(f"查询被买断订单列表失败: {e}")
            import traceback
            traceback.print_exc()
            return jsonify([]), 500
