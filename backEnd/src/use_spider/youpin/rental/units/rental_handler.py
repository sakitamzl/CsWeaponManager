"""
rental 处理模块
提供 Spider 所需的借入记录查询、插入与状态更新接口
"""
from flask import jsonify, request
from src.units.now_time import today
from src.db_manager.index.model.rental import RentalModel


class RentalHandler:

    @staticmethod
    def select_apex_time(steamId, data_from=None):
        """获取指定用户最新借入订单时间，供 Spider 判断增量同步起点"""
        try:
            from src.db_manager.database import DatabaseManager
            db = DatabaseManager()

            if data_from:
                sql = """
                    SELECT lean_start_time
                    FROM rental
                    WHERE data_user = ? AND `from` = ?
                    ORDER BY lean_start_time DESC
                    LIMIT 1
                """
                result = db.execute_query(sql, (steamId, data_from))
            else:
                sql = """
                    SELECT lean_start_time
                    FROM rental
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
            print(f"查询最新借入时间失败: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"success": False, "order_time": None, "message": f"查询异常: {str(e)}"}), 500

    @staticmethod
    def get_count(steamId, data_from=None):
        """获取指定用户借入订单总数，供 Spider 计算分页起点"""
        try:
            if data_from:
                count = RentalModel.count(
                    where="data_user = ? AND `from` = ?",
                    params=(steamId, data_from)
                )
            else:
                count = RentalModel.count(where="data_user = ?", params=(steamId,))
            return jsonify(count), 200
        except Exception as e:
            print(f"查询借入订单数量失败: {e}")
            import traceback
            traceback.print_exc()
            return jsonify(0), 500

    @staticmethod
    def get_now_rental_list(data_from=None):
        """获取当前需要更新状态的借入订单列表（已到期且 last_status 不是"完成"）"""
        try:
            current_time = today()
            if data_from:
                where_clause = "lean_end_time <= ? AND last_status != '完成' AND `from` = ?"
                params = (current_time, data_from)
            else:
                where_clause = "lean_end_time <= ? AND last_status != '完成'"
                params = (current_time,)

            records = RentalModel.find_all(where=where_clause, params=params)
            data = [[record.ID] for record in records]
            return jsonify(data), 200
        except Exception as e:
            print(f"查询借入列表失败: {e}")
            import traceback
            traceback.print_exc()
            return jsonify([]), 500

    @staticmethod
    def get_time_out_rental():
        """获取超时的借入订单"""
        try:
            records = RentalModel.find_all(
                where="lean_end_time < ? AND status IN ('白玩中', '归还中', '租赁中')",
                params=(today(),)
            )
            data = [[record.ID] for record in records]
            return jsonify(data), 200
        except Exception as e:
            print(f"查询超时借入订单失败: {e}")
            import traceback
            traceback.print_exc()
            return jsonify([]), 500

    @staticmethod
    def insert_rental_data():
        """插入借入主表数据（写入 rental 表）"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': '无效的JSON数据'}), 400

            ID = data['ID']

            existing = RentalModel.find_by_id(ID=ID)
            if existing:
                return jsonify({'success': True, 'message': '记录已存在'}), 200

            weapon_name = data.get('weapon_name')
            weapon_type = data.get('weapon_type')
            item_name = data.get('item_name')
            weapon_float = data.get('weapon_float')
            float_range = data.get('float_range')
            price = data.get('price')
            lessor_name = data.get('lessor_name')
            lessor_id = data.get('lessor_id')
            status = data.get('status')
            status_sub = data.get('status_sub')
            last_status = data.get('orderSubStatusName')
            data_from = data.get('from')
            lean_start_time = data.get('lean_start_time')
            lean_end_time = data.get('lean_end_time')

            try:
                total_lease_days = int(data.get('totalLeaseDays')) if data.get('totalLeaseDays') is not None else None
            except (TypeError, ValueError):
                total_lease_days = None

            try:
                max_lease_days = int(data.get('leaseMaxDays')) if data.get('leaseMaxDays') is not None else total_lease_days
            except (TypeError, ValueError):
                max_lease_days = total_lease_days

            data_user = data.get('data_user')
            steam_hash_name = data.get('steam_hash_name')
            sticker = data.get('sticker')
            pendant = data.get('pendant')
            rename = data.get('rename')

            rental_main = RentalModel()
            rental_main.ID = ID
            rental_main.weapon_name = weapon_name
            rental_main.weapon_type = weapon_type
            rental_main.item_name = item_name
            rental_main.weapon_float = weapon_float
            rental_main.float_range = float_range
            rental_main.price = price
            rental_main.total_Lease_Days = total_lease_days
            rental_main.max_Lease_Days = max_lease_days
            rental_main.lean_start_time = lean_start_time
            rental_main.lean_end_time = lean_end_time
            rental_main.lessor_name = lessor_name
            rental_main.lessor_id = lessor_id
            rental_main.status = status
            rental_main.status_sub = status_sub
            rental_main.last_status = last_status
            rental_main.data_user = data_user
            rental_main.steam_hash_name = steam_hash_name
            rental_main.sticker = sticker
            rental_main.pendant = pendant
            rental_main.rename = rename
            setattr(rental_main, 'from', data_from)

            saved = rental_main.save()

            if saved:
                return jsonify({
                    'success': True,
                    'message': '借入主表数据插入成功',
                    'data': {'id': ID, 'weapon_name': weapon_name, 'item_name': item_name, 'price': price}
                }), 200
            else:
                return jsonify({'success': False, 'error': '数据插入失败'}), 500

        except Exception as e:
            print(f"借入主表数据插入错误: {str(e)}")
            import traceback
            print(f"详细错误信息: {traceback.format_exc()}")
            return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500

    @staticmethod
    def _do_update_rental(rental_record, data):
        """通用更新逻辑（同时用于 updateRentalData 和 updateMainRentalData）"""
        if 'last_status' not in data and 'lean_end_time' not in data:
            status = data.get('status')
            if status:
                rental_record.status = status
                if rental_record.save():
                    return 'update_info', 200
                else:
                    return 'update_error', 500
            else:
                return 'update_error', 400

        status = data['status']
        status_sub = data.get('status_sub', '')
        last_status = data.get('last_status')
        lean_end_time = data.get('lean_end_time')
        totalLeaseDays = data.get('totalLeaseDays')
        leaseMaxDays = data.get('leaseMaxDays')
        steam_hash_name = data.get('steam_hash_name')
        sticker = data.get('sticker')
        pendant = data.get('pendant')
        rename = data.get('rename')

        if rental_record.status in ('已归还', '已取消'):
            return 'skip_final_status', 200

        rental_record.status = status
        rental_record.status_sub = status_sub
        if last_status:
            rental_record.last_status = last_status
        if lean_end_time:
            rental_record.lean_end_time = lean_end_time
        if totalLeaseDays is not None:
            rental_record.total_Lease_Days = totalLeaseDays
        if leaseMaxDays is not None:
            rental_record.max_Lease_Days = leaseMaxDays
        if steam_hash_name:
            rental_record.steam_hash_name = steam_hash_name
        if sticker:
            rental_record.sticker = sticker
        if pendant:
            rental_record.pendant = pendant
        if rename is not None:
            rental_record.rename = rename

        if rental_record.save():
            return 'update_info', 200
        else:
            return 'update_error', 500

    @staticmethod
    def update_rental_data():
        """更新借入订单状态（更新 rental 表）"""
        try:
            data = request.get_json()
            ID = data['ID']

            rental_record = RentalModel.find_by_id(ID=ID)
            if not rental_record:
                return 'update_error', 404

            return RentalHandler._do_update_rental(rental_record, data)

        except Exception as e:
            print(f"更新借入数据失败: {e}")
            import traceback
            traceback.print_exc()
            return 'update_error', 500

    @staticmethod
    def update_main_rental_data():
        """更新借入主表数据（与 update_rental_data 逻辑相同，保持兼容性）"""
        try:
            data = request.get_json()
            ID = data['ID']

            rental_record = RentalModel.find_by_id(ID=ID)
            if not rental_record:
                return 'update_error', 404

            return RentalHandler._do_update_rental(rental_record, data)

        except Exception as e:
            print(f"更新借入主表数据失败: {e}")
            import traceback
            traceback.print_exc()
            return 'update_error', 500
