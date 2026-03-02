"""
BUFF rental 处理模块
提供 Spider 所需的租入记录查询、插入与状态更新接口
"""
from flask import jsonify, request
from src.units.execution_db import Date_base
from src.units.now_time import today
from src.db_manager.manager import RentalModel


class RentalHandler:

    @staticmethod
    def count_data(data_user):
        """统计指定用户的 BUFF 租入订单数量"""
        try:
            sql = f"SELECT COUNT(*) FROM rental WHERE data_user = '{data_user}' AND \"from\" = 'buff'"
            result = Date_base().select(sql)
            if result and len(result) == 2:
                flag, data = result
                if flag and len(data) > 0:
                    count = data[0][0]
                    return jsonify({"count": count}), 200
            return jsonify({"count": 0}), 200
        except Exception as e:
            print(f"统计BUFF租入订单数量失败: {e}")
            import traceback
            print(traceback.format_exc())
            return jsonify({"error": "统计失败"}), 500

    @staticmethod
    def insert_db():
        """插入 BUFF 租入订单数据到 rental 表"""
        try:
            data = request.get_json()

            order_id = data.get('order_id', '')
            item_id = data.get('item_id', '')
            assetid = data.get('assetid', '')
            classid = data.get('classid', '')
            weapon_type = data.get('weapon_type', '')
            item_name = data.get('item_name', '')
            weapon_name = data.get('weaponitem_name', '')
            float_range = data.get('float_range', '')
            weapon_float = data.get('weapon_float', None)
            rent_unit_price = data.get('rent_unit_price', '')
            security_price = data.get('security_price', '')
            total_rent_price = data.get('total_rent_price', '')
            state = data.get('state', '')
            state_sub = data.get('state_sub', '')
            created_at = data.get('created_at', '')
            rent_start_time = data.get('rent_start_time', '')
            rent_end_time = data.get('rent_end_time', '')
            pay_method_text = data.get('pay_method_text', '')
            steam_price_cny = data.get('steam_price_cny', '')
            seller_id = data.get('seller_id', '')
            rent_in_day = data.get('rent_in_day', 0)
            rented_day = data.get('rented_day', 0)
            min_rent_out_day = data.get('min_rent_out_day', 0)
            max_rent_out_day = data.get('max_rent_out_day', 0)
            data_user = data.get('data_user', '')
            sticker = data.get('sticker', None)
            pendant = data.get('pendant', None)
            rename = data.get('rename', None)
            market_hash_name = data.get('market_hash_name', '')
            img_url = data.get('img_url', '')

            # 使用 market_hash_name 作为 steam_hash_name
            steam_hash_name = market_hash_name if market_hash_name else img_url if img_url else None

            rental_data = {
                'ID': order_id,
                'item_id': item_id,
                'assetid': assetid,
                'classid': classid,
                'weapon_name': weapon_name,
                'weapon_type': weapon_type,
                'item_name': item_name,
                'weapon_float': weapon_float,
                'float_range': float_range,
                'price': rent_unit_price,
                'security_price': security_price,
                'lessor_name': seller_id,
                'status': state,
                'last_status': state_sub,
                'from': 'buff',
                'lean_start_time': rent_start_time,
                'lean_end_time': rent_end_time,
                'total_Lease_Days': max_rent_out_day,
                'max_Lease_Days': max_rent_out_day,
                'steam_hash_name': steam_hash_name,
                'sticker': sticker,
                'pendant': pendant,
                'rename': rename,
                'data_user': data_user,
            }

            rental_model = RentalModel(**rental_data)
            result = rental_model.save()

            if result:
                return jsonify({"success": True, "message": "数据插入成功"}), 200
            else:
                return jsonify({"success": False, "message": "数据插入失败"}), 500

        except Exception as e:
            print(f"插入BUFF租入数据失败: {e}")
            import traceback
            print(traceback.format_exc())
            return jsonify({"success": False, "error": str(e)}), 500

    @staticmethod
    def get_latest_data(data_user):
        """获取指定用户最新的 BUFF 租入订单数据"""
        try:
            sql = f"""
            SELECT ID, lean_start_time
            FROM rental
            WHERE data_user = '{data_user}' AND \"from\" = 'buff'
            ORDER BY lean_start_time DESC
            LIMIT 1
            """
            result = Date_base().select(sql)

            if result and len(result) == 2:
                flag, data = result
                if flag and len(data) > 0:
                    return jsonify({"ID": data[0][0], "order_time": data[0][1]}), 200

            return jsonify({"message": "数据库为空，请先执行全量采集"}), 200

        except Exception as e:
            print(f"获取最新BUFF租入数据失败: {e}")
            import traceback
            print(traceback.format_exc())
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def select_not_end(data_user):
        """查询指定用户需要更新状态的 BUFF 租入订单"""
        try:
            current_time = today()
            sql = f"""
            SELECT ID
            FROM rental
            WHERE data_user = '{data_user}'
                AND \"from\" = 'buff'
                AND status NOT IN ('已完成', '已取消', '已归还')
                AND (
                    (lean_end_time <= '{current_time}' AND status = '租赁中')
                    OR
                    status NOT IN ('租赁中')
                )
            ORDER BY lean_start_time DESC
            """
            result = Date_base().select(sql)

            if result and len(result) == 2:
                flag, data = result
                if flag:
                    order_ids = [row[0] for row in data]
                    return jsonify({"not_end_orders": order_ids}), 200

            return jsonify({"not_end_orders": []}), 200

        except Exception as e:
            print(f"查询未结束BUFF租入订单失败: {e}")
            import traceback
            print(traceback.format_exc())
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def update_order_status():
        """更新 BUFF 租入订单状态"""
        try:
            data = request.get_json()
            order_id = data.get('order_id', '')
            state = data.get('state', '')
            state_sub = data.get('state_sub', None)

            if not order_id:
                return jsonify({"success": False, "error": "订单ID不能为空"}), 400

            if state_sub is not None:
                sql = f"""
                UPDATE rental
                SET status = '{state}', last_status = '{state_sub}'
                WHERE ID = '{order_id}' AND \"from\" = 'buff'
                """
            else:
                sql = f"""
                UPDATE rental
                SET status = '{state}'
                WHERE ID = '{order_id}' AND \"from\" = 'buff'
                """

            result = Date_base().update(sql)

            if result:
                return jsonify({"success": True, "message": "状态更新成功"}), 200
            else:
                return jsonify({"success": False, "error": "状态更新失败"}), 500

        except Exception as e:
            print(f"更新BUFF租入订单状态失败: {e}")
            import traceback
            print(traceback.format_exc())
            return jsonify({"success": False, "error": str(e)}), 500
