"""
lent 写入模块
提供 Spider 所需的租赁记录插入与状态更新接口
"""
from flask import jsonify, request
from src.db_manager.youpin.model.yyyp_lent import YyypLentModel
from src.db_manager.index.model.lent import LentModel


class LentInsert:

    @staticmethod
    def insert_webside_lentdata():
        """插入租赁订单数据（写入 yyyp_lent 源表）"""
        try:
            data = request.get_json()

            ID = data['ID']
            weapon_name = data['weapon_name']
            weapon_type = data['weapon_type']
            item_name = data['item_name']
            weapon_float = data.get('weapon_float')
            float_range = data['float_range']
            price = data['price']
            lent_user_name = data['buyer_user_name']
            lenter_id = data.get('lenter_id', '')
            status = data['status']
            orderSubStatusName = data['orderSubStatusName']
            status_sub = data.get('status_sub', '')
            data_from = data['from']
            lean_start_time = data['lean_start_time']
            lean_end_time = data.get('lean_end_time')
            totalLeaseDays = int(data['totalLeaseDays'])
            max_Lease_Days = int(data.get('leaseMaxDays', totalLeaseDays))
            data_user = data.get('data_user', '')

            existing_record = YyypLentModel.find_by_id(ID=ID)
            if existing_record:
                return '重复数据', 200

            lent_record = YyypLentModel(
                ID=ID,
                weapon_name=weapon_name,
                weapon_type=weapon_type,
                item_name=item_name,
                weapon_float=weapon_float,
                float_range=float_range,
                price=price,
                lenter_name=lent_user_name,
                lenter_id=lenter_id,
                status=status,
                status_sub=status_sub,
                last_status=orderSubStatusName,
                **{'from': data_from},
                lean_start_time=lean_start_time,
                lean_end_time=lean_end_time,
                total_Lease_Days=totalLeaseDays,
                max_Lease_Days=max_Lease_Days,
                data_user=data_user
            )

            if lent_record.save():
                return '写入成功', 200
            else:
                return '写入失败', 500

        except Exception as e:
            print(f"插入租赁数据失败: {e}")
            import traceback
            traceback.print_exc()
            return '写入失败', 500

    @staticmethod
    def insert_main_lentdata():
        """插入租赁主表数据（写入 lent 主表）"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': '无效的JSON数据'}), 400

            ID = data['ID']

            existing = LentModel.find_by_id(ID=ID)
            if existing:
                return jsonify({'success': True, 'message': '记录已存在'}), 200

            weapon_name = data.get('weapon_name')
            weapon_type = data.get('weapon_type')
            item_name = data.get('item_name')
            weapon_float = data.get('weapon_float')
            float_range = data.get('float_range')
            price = data.get('price')
            lenter_name = data.get('buyer_user_name') or data.get('lenter_name')
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

            lent_main = LentModel()
            lent_main.ID = ID
            lent_main.weapon_name = weapon_name
            lent_main.weapon_type = weapon_type
            lent_main.item_name = item_name
            lent_main.weapon_float = weapon_float
            lent_main.float_range = float_range
            lent_main.price = price
            lent_main.total_Lease_Days = total_lease_days
            lent_main.max_Lease_Days = max_lease_days
            lent_main.lean_start_time = lean_start_time
            lent_main.lean_end_time = lean_end_time
            lent_main.lenter_name = lenter_name
            lent_main.status = status
            lent_main.status_sub = status_sub
            lent_main.last_status = last_status
            lent_main.data_user = data_user
            lent_main.steam_hash_name = steam_hash_name
            lent_main.sticker = sticker
            lent_main.pendant = pendant
            lent_main.rename = rename
            setattr(lent_main, 'from', data_from)

            saved = lent_main.save()

            if saved:
                return jsonify({
                    'success': True,
                    'message': '租赁主表数据插入成功',
                    'data': {'id': ID, 'weapon_name': weapon_name, 'item_name': item_name, 'price': price}
                }), 200
            else:
                return jsonify({'success': False, 'error': '数据插入失败'}), 500

        except Exception as e:
            print(f"租赁主表数据插入错误: {str(e)}")
            import traceback
            print(f"详细错误信息: {traceback.format_exc()}")
            return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500

    @staticmethod
    def update_lent_data():
        """更新租赁订单状态（更新 yyyp_lent 源表）"""
        try:
            data = request.get_json()
            ID = data['ID']

            lent_record = YyypLentModel.find_by_id(ID=ID)
            if not lent_record:
                return 'update_error', 404

            # 仅传 status 时做简单状态更新
            if 'orderSubStatusName' not in data and 'lean_end_time' not in data:
                status = data.get('status')
                if status:
                    lent_record.status = status
                    if lent_record.save():
                        return 'update_info', 200
                    else:
                        return 'update_error', 500
                else:
                    return 'update_error', 400

            # 完整更新
            status = data['status']
            status_sub = data.get('status_sub', '')
            orderSubStatusName = data['orderSubStatusName']
            lean_end_time = data['lean_end_time']
            totalLeaseDays = data['totalLeaseDays']
            leaseMaxDays = data.get('leaseMaxDays')

            if lent_record.status in ('已转租', '已归还'):
                return 'skip_final_status', 200

            lent_record.status = status
            lent_record.status_sub = status_sub
            lent_record.last_status = orderSubStatusName
            lent_record.lean_end_time = lean_end_time
            lent_record.total_Lease_Days = totalLeaseDays

            if leaseMaxDays is not None:
                lent_record.max_Lease_Days = leaseMaxDays

            if lent_record.save():
                return 'update_info', 200
            else:
                return 'update_error', 500

        except Exception as e:
            print(f"更新租赁数据失败: {e}")
            import traceback
            traceback.print_exc()
            return 'update_error', 500

    @staticmethod
    def update_main_lent_data():
        """更新租赁主表数据（更新 lent 主表）"""
        try:
            data = request.get_json()
            ID = data['ID']

            lent_main = LentModel.find_by_id(ID=ID)
            if not lent_main:
                return jsonify({'success': False, 'message': '主表记录不存在'}), 404

            # 仅传 status 时做简单状态更新
            if 'orderSubStatusName' not in data and 'lean_end_time' not in data:
                status = data.get('status')
                if status:
                    lent_main.status = status
                    if lent_main.save():
                        return jsonify({'success': True, 'message': 'update_info'}), 200
                    else:
                        return jsonify({'success': False, 'message': 'update_error'}), 500
                else:
                    return jsonify({'success': False, 'message': '缺少status字段'}), 400

            # 完整更新
            status = data['status']
            status_sub = data.get('status_sub', '')
            orderSubStatusName = data['orderSubStatusName']
            lean_end_time = data.get('lean_end_time')
            totalLeaseDays = data.get('totalLeaseDays')
            leaseMaxDays = data.get('leaseMaxDays')

            if lent_main.status in ('已转租', '已归还'):
                return jsonify({'success': True, 'message': 'skip_final_status'}), 200

            lent_main.status = status
            lent_main.status_sub = status_sub
            lent_main.last_status = orderSubStatusName
            lent_main.lean_end_time = lean_end_time
            lent_main.total_Lease_Days = totalLeaseDays

            if leaseMaxDays is not None:
                lent_main.max_Lease_Days = leaseMaxDays

            if lent_main.save():
                return jsonify({'success': True, 'message': 'update_info'}), 200
            else:
                return jsonify({'success': False, 'message': 'update_error'}), 500

        except Exception as e:
            print(f"更新租赁主表数据失败: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'message': 'update_error', 'error': str(e)}), 500
