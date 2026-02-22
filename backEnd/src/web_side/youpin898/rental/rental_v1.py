from flask import jsonify, request, Blueprint
from src.log import Log
from src.now_time import today
from src.db_manager.index.model.rental import RentalModel
import requests

youpin898RentalV1 = Blueprint('youpin898RentalV1', __name__)

@youpin898RentalV1.route('/getNowRentalList', methods=['get'])
@youpin898RentalV1.route('/getNowRentalList/<data_from>', methods=['get'])
def getNowRentalList(data_from=None):
    """获取当前需要更新状态的借入订单列表（已到期且 last_status 不是"完成"的订单）

    Args:
        data_from: 可选，数据来源过滤（如 'yyyp', 'buff' 等）
    """
    try:
        # 查询已到期且 last_status 不是"完成"的订单
        current_time = today()

        # 构建查询条件：已到期 AND last_status != '完成'
        if data_from:
            # 有 from 参数时，添加来源过滤
            where_clause = "lean_end_time <= ? AND last_status != '完成' AND `from` = ?"
            params = (current_time, data_from)
        else:
            # 没有 from 参数时，查询所有来源
            where_clause = "lean_end_time <= ? AND last_status != '完成'"
            params = (current_time,)

        records = RentalModel.find_all(
            where=where_clause,
            params=params
        )
        data = [[record.ID] for record in records]
        return jsonify(data), 200
    except Exception as e:
        print(f"查询借入列表失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify([]), 500  

@youpin898RentalV1.route('/getTimeOutRental', methods=['get'])
def getTimeOutRental():
    """获取超时的借入订单"""
    try:
        # 使用模型查询超时订单
        records = RentalModel.find_all(
            where="lean_end_time < ? AND status IN ('白玩中', '归还中', '租赁中')",
            params=(today(),)
        )
        # 返回ID列表，格式与原来保持一致
        data = [[record.ID] for record in records]
        return jsonify(data), 200
    except Exception as e:
        print(f"查询超时借入订单失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify([]), 500

@youpin898RentalV1.route('/selectApexTime/<steamId>', methods=['get'])
@youpin898RentalV1.route('/selectApexTime/<steamId>/<data_from>', methods=['get'])
def selectApexTime(steamId, data_from=None):
    """
    获取指定steamId的最新借入订单时间
    用于判断是否有新数据需要同步

    Args:
        steamId: 用户的 Steam ID
        data_from: 可选，数据来源过滤（如 'yyyp', 'buff' 等）
    """
    try:
        # 直接使用 SQL 查询，按 lean_start_time 降序排列，取第一条
        from src.db_manager.database import DatabaseManager
        db = DatabaseManager()

        if data_from:
            # 有 from 参数时，添加来源过滤
            sql = """
                SELECT lean_start_time
                FROM rental
                WHERE data_user = ? AND `from` = ?
                ORDER BY lean_start_time DESC
                LIMIT 1
            """
            result = db.execute_query(sql, (steamId, data_from))
        else:
            # 没有 from 参数时，查询所有来源
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
            return jsonify({
                "success": True,
                "order_time": apex_time
            }), 200
        else:
            return jsonify({
                "success": False,
                "order_time": None,
                "message": "未查询到数据"
            }), 200
    except Exception as e:
        print(f"查询最新借入时间失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "order_time": None,
            "message": f"查询异常: {str(e)}"
        }), 500

@youpin898RentalV1.route('/getCount/<steamId>', methods=['get'])
@youpin898RentalV1.route('/getCount/<steamId>/<data_from>', methods=['get'])
def getCount(steamId, data_from=None):
    """
    获取指定steamId的借入订单总数
    用于分页获取历史数据

    Args:
        steamId: 用户的 Steam ID
        data_from: 可选，数据来源过滤（如 'yyyp', 'buff' 等）
    """
    try:
        if data_from:
            # 有 from 参数时，添加来源过滤
            count = RentalModel.count(
                where="data_user = ? AND `from` = ?",
                params=(steamId, data_from)
            )
        else:
            # 没有 from 参数时，查询所有来源
            count = RentalModel.count(
                where="data_user = ?",
                params=(steamId,)
            )
        return jsonify(count), 200
    except Exception as e:
        print(f"查询借入订单数量失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(0), 500

@youpin898RentalV1.route('/updateRentalData', methods=['post'])
def updateRentalData():
    """更新借入订单状态（完整更新）

    字段映射关系：
    - status: orderSubStatusName（子状态，如"已归还"）
    - status_sub: orderStatusDesc（状态描述）
    - last_status: orderStatusName（主状态，如"完成"）
    """
    try:
        data = request.get_json()
        ID = data['ID']

        # 查找现有记录
        rental_record = RentalModel.find_by_id(ID=ID)
        if not rental_record:
            return 'update_error', 404

        # 如果只传递了 status 和 from，则只更新 status
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

        # 完整更新逻辑
        status = data['status']  # orderSubStatusName -> status
        status_sub = data.get('status_sub', '')  # orderStatusDesc -> status_sub
        last_status = data.get('last_status')  # orderStatusName -> last_status
        lean_end_time = data.get('lean_end_time')
        totalLeaseDays = data.get('totalLeaseDays')
        leaseMaxDays = data.get('leaseMaxDays')  # 可选字段

        # 提取商品信息（如果有）
        steam_hash_name = data.get('steam_hash_name')
        sticker = data.get('sticker')
        pendant = data.get('pendant')
        rename = data.get('rename')

        # 如果当前库状态已是终态，则跳过更新，避免覆盖
        if rental_record.status in ('已归还', '已取消'):
            return 'skip_final_status', 200

        # 更新状态字段
        rental_record.status = status  # orderSubStatusName
        rental_record.status_sub = status_sub  # orderStatusDesc
        if last_status:
            rental_record.last_status = last_status  # orderStatusName

        # 更新时间和天数
        if lean_end_time:
            rental_record.lean_end_time = lean_end_time
        if totalLeaseDays is not None:
            rental_record.total_Lease_Days = totalLeaseDays
        if leaseMaxDays is not None:
            rental_record.max_Lease_Days = leaseMaxDays

        # 更新商品信息（如果提供）
        if steam_hash_name:
            rental_record.steam_hash_name = steam_hash_name
        if sticker:
            rental_record.sticker = sticker
        if pendant:
            rental_record.pendant = pendant
        if rename is not None:
            rental_record.rename = rename

        # 保存更新
        if rental_record.save():
            return 'update_info', 200
        else:
            return 'update_error', 500

    except Exception as e:
        print(f"更新借入数据失败: {e}")
        import traceback
        traceback.print_exc()
        return 'update_error', 500


@youpin898RentalV1.route('/insert_rental_data', methods=['post'])
def insert_rental_data():
    """
    插入借入主表数据（rental）
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '无效的JSON数据'}), 400

        ID = data['ID']

        # 如果主表中已存在，直接忽略
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

        # 创建主表记录
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
                'data': {
                    'id': ID,
                    'weapon_name': weapon_name,
                    'item_name': item_name,
                    'price': price
                }
            }), 200
        else:
            return jsonify({'success': False, 'error': '数据插入失败'}), 500

    except Exception as e:
        print(f"借入主表数据插入错误: {str(e)}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500


@youpin898RentalV1.route('/updateMainRentalData', methods=['post'])
def updateMainRentalData():
    """更新借入主表数据（与 updateRentalData 相同的逻辑，用于保持兼容性）

    字段映射关系：
    - status: orderSubStatusName（子状态，如"已归还"）
    - status_sub: orderStatusDesc（状态描述）
    - last_status: orderStatusName（主状态，如"完成"）
    """
    try:
        data = request.get_json()
        ID = data['ID']

        # 查找现有记录
        rental_record = RentalModel.find_by_id(ID=ID)
        if not rental_record:
            return 'update_error', 404

        # 如果只传递了 status 和 from，则只更新 status
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

        # 完整更新逻辑
        status = data['status']  # orderSubStatusName -> status
        status_sub = data.get('status_sub', '')  # orderStatusDesc -> status_sub
        last_status = data.get('last_status')  # orderStatusName -> last_status
        lean_end_time = data.get('lean_end_time')
        totalLeaseDays = data.get('totalLeaseDays')
        leaseMaxDays = data.get('leaseMaxDays')  # 可选字段

        # 提取商品信息（如果有）
        steam_hash_name = data.get('steam_hash_name')
        sticker = data.get('sticker')
        pendant = data.get('pendant')
        rename = data.get('rename')

        # 如果当前库状态已是终态，则跳过更新，避免覆盖
        if rental_record.status in ('已归还', '已取消'):
            return 'skip_final_status', 200

        # 更新状态字段
        rental_record.status = status  # orderSubStatusName
        rental_record.status_sub = status_sub  # orderStatusDesc
        if last_status:
            rental_record.last_status = last_status  # orderStatusName

        # 更新时间和天数
        if lean_end_time:
            rental_record.lean_end_time = lean_end_time
        if totalLeaseDays is not None:
            rental_record.total_Lease_Days = totalLeaseDays
        if leaseMaxDays is not None:
            rental_record.max_Lease_Days = leaseMaxDays

        # 更新商品信息（如果提供）
        if steam_hash_name:
            rental_record.steam_hash_name = steam_hash_name
        if sticker:
            rental_record.sticker = sticker
        if pendant:
            rental_record.pendant = pendant
        if rename is not None:
            rental_record.rename = rename

        # 保存更新
        if rental_record.save():
            return 'update_info', 200
        else:
            return 'update_error', 500

    except Exception as e:
        print(f"更新借入主表数据失败: {e}")
        import traceback
        traceback.print_exc()
        return 'update_error', 500
