from flask import jsonify, request, Blueprint
from src.log import Log
from src.now_time import today
from src.db_manager.yyyp.yyyp_lent import YyypLentModel
from src.db_manager.index.lent import LentModel
import requests

youpin898LentV1 = Blueprint('youpin898LentV1', __name__)

@youpin898LentV1.route('/getBuyoutLentList/<steamId>', methods=['get'])
def getBuyoutLentList(steamId):
    """获取状态为"被买断"且未同步到sell表的租赁订单列表"""
    try:
        # 从 lent 主表查询状态为"被买断"的订单
        records = LentModel.find_all(
            where="status in ('被买断', '已买断') AND data_user = ?",
            params=(steamId,)
        )
        
        # 返回需要的字段：ID, weapon_name, weapon_type, item_name, weapon_float, 
        # float_range, buyer_user_name, lean_start_time, steam_hash_name, sticker, pendant, rename
        data = [
            [
                record.ID,
                record.weapon_name,
                record.weapon_type,
                record.item_name,
                record.weapon_float,
                record.float_range,
                record.lenter_name,  # buyer_user_name
                record.lean_start_time,
                record.steam_hash_name,
                record.sticker,
                record.pendant,
                record.rename
            ] 
            for record in records
        ]
        return jsonify(data), 200
    except Exception as e:
        print(f"查询被买断订单列表失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify([]), 500

@youpin898LentV1.route('/getNowLentingList', methods=['get'])
def getNowLentingList():
    """获取当前需要更新状态的租赁订单列表（未完成且已到达或超过结束时间的订单）"""
    try:
        # 查询所有未完成、有结束时间且已到达结束时间的订单
        current_time = today()
        # 仅筛选未完成且非“已转租/已归还”的订单
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

@youpin898LentV1.route('/getTimeOutLent', methods=['get'])
def getTimeOutLent():
    """获取超时的租赁订单"""
    try:
        # 使用模型查询超时订单
        records = YyypLentModel.find_all(
            where="lean_end_time < ? AND status IN ('白玩中', '归还中', '租赁中')",
            params=(today(),)
        )
        # 返回ID列表，格式与原来保持一致
        data = [[record.ID] for record in records]
        return jsonify(data), 200
    except Exception as e:
        print(f"查询超时租赁订单失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify([]), 500

@youpin898LentV1.route('/selectApexTime/<steamId>', methods=['get'])
def selectApexTime(steamId):
    """
    获取指定steamId的最新租赁订单时间
    用于判断是否有新数据需要同步
    """
    try:
        # 直接使用 SQL 查询，按 lean_start_time 降序排列，取第一条
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
        print(f"查询最新租赁时间失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "order_time": None,
            "message": f"查询异常: {str(e)}"
        }), 500

@youpin898LentV1.route('/getCount/<steamId>', methods=['get'])
def getCount(steamId):
    """
    获取指定steamId的租赁订单总数
    用于分页获取历史数据
    """
    try:
        # 使用模型的 count 方法
        count = YyypLentModel.count(
            where="data_user = ?",
            params=(steamId,)
        )
        return jsonify(count), 200
    except Exception as e:
        print(f"查询租赁订单数量失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(0), 500

@youpin898LentV1.route('/updateLentData', methods=['post'])
def updateLentData():
    """更新租赁订单状态（完整更新）"""
    try:
        data = request.get_json()
        ID = data['ID']
        
        # 查找现有记录
        lent_record = YyypLentModel.find_by_id(ID=ID)
        if not lent_record:
            return 'update_error', 404
        
        # 如果只传递了 status 和 from，则只更新 status（用于被买断同步）
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
        
        # 完整更新逻辑
        status = data['status']  # orderStatusName -> status
        status_sub = data.get('status_sub', '')  # orderStatusDesc -> status_sub
        orderSubStatusName = data['orderSubStatusName']  # orderSubStatusName -> last_status
        lean_end_time = data['lean_end_time']
        totalLeaseDays = data['totalLeaseDays']
        leaseMaxDays = data.get('leaseMaxDays')  # 可选字段
        
        # 如果当前库状态已是终态，则跳过更新，避免覆盖
        if lent_record.status in ('已转租', '已归还'):
            return 'skip_final_status', 200

        # 更新字段
        lent_record.status = status  # orderStatusName
        lent_record.status_sub = status_sub  # orderStatusDesc
        lent_record.last_status = orderSubStatusName  # orderSubStatusName
        lent_record.lean_end_time = lean_end_time
        lent_record.total_Lease_Days = totalLeaseDays
        
        # 如果提供了 leaseMaxDays，则更新
        if leaseMaxDays is not None:
            lent_record.max_Lease_Days = leaseMaxDays
        
        # 保存更新
        if lent_record.save():
            return 'update_info', 200
        else:
            return 'update_error', 500
            
    except Exception as e:
        print(f"更新租赁数据失败: {e}")
        import traceback
        traceback.print_exc()
        return 'update_error', 500


@youpin898LentV1.route('/insert_webside_lentdata', methods=['post'])
def insert_webside_lentdata():
    """插入租赁订单数据"""
    try:
        data = request.get_json()
        
        # 提取数据
        ID = data['ID']
        weapon_name = data['weapon_name']
        weapon_type = data['weapon_type']
        item_name = data['item_name']
        weapon_float = data.get('weapon_float')
        float_range = data['float_range']
        price = data['price']
        lent_user_name = data['buyer_user_name']
        lenter_id = data.get('lenter_id', '')  # 租客ID
        status = data['status']
        orderSubStatusName = data['orderSubStatusName']
        status_sub = data.get('status_sub', '')  # 订单状态描述
        data_from = data['from']
        lean_start_time = data['lean_start_time']
        lean_end_time = data.get('lean_end_time')
        totalLeaseDays = int(data['totalLeaseDays'])
        # leaseMaxDays 字段可选，如果没有提供则使用 totalLeaseDays 作为默认值
        max_Lease_Days = int(data.get('leaseMaxDays', totalLeaseDays))
        data_user = data.get('data_user', '')
        
        # 检查记录是否已存在（yyyp 源表）
        existing_record = YyypLentModel.find_by_id(ID=ID)
        if existing_record:
            return '重复数据', 200
        
        # 使用模型创建源表记录
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
            **{'from': data_from},  # 'from' 是保留字，需要用字典解包
            lean_start_time=lean_start_time,
            lean_end_time=lean_end_time,
            total_Lease_Days=totalLeaseDays,
            max_Lease_Days=max_Lease_Days,
            data_user=data_user
        )
        
        # 保存到数据库
        if lent_record.save():
            return '写入成功', 200
        else:
            return '写入失败', 500

    except Exception as e:
        print(f"插入租赁数据失败: {e}")
        import traceback
        traceback.print_exc()
        return '写入失败', 500


@youpin898LentV1.route('/updateMainLentData', methods=['post'])
def updateMainLentData():
    """更新租赁主表数据（支持完整更新和简化状态更新）"""
    try:
        data = request.get_json()
        ID = data['ID']
        
        # 查找主表记录
        lent_main = LentModel.find_by_id(ID=ID)
        if not lent_main:
            return jsonify({'success': False, 'message': '主表记录不存在'}), 404
        
        # 如果只传递了 status 和 from，则只更新 status（用于被买断同步）
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
        
        # 完整更新逻辑
        status = data['status']
        status_sub = data.get('status_sub', '')
        orderSubStatusName = data['orderSubStatusName']
        lean_end_time = data.get('lean_end_time')
        totalLeaseDays = data.get('totalLeaseDays')
        leaseMaxDays = data.get('leaseMaxDays')
        
        # 如果当前状态已是终态，则跳过更新
        if lent_main.status in ('已转租', '已归还'):
            return jsonify({'success': True, 'message': 'skip_final_status'}), 200
        
        # 更新字段
        lent_main.status = status
        lent_main.status_sub = status_sub
        lent_main.last_status = orderSubStatusName
        lent_main.lean_end_time = lean_end_time
        lent_main.total_Lease_Days = totalLeaseDays
        
        if leaseMaxDays is not None:
            lent_main.max_Lease_Days = leaseMaxDays
        
        # 保存更新
        if lent_main.save():
            return jsonify({'success': True, 'message': 'update_info'}), 200
        else:
            return jsonify({'success': False, 'message': 'update_error'}), 500
            
    except Exception as e:
        print(f"更新租赁主表数据失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'update_error', 'error': str(e)}), 500


@youpin898LentV1.route('/insert_main_lentdata', methods=['post'])
def insert_main_lentdata():
    """
    插入租赁主表数据（lent），结构参考 buy_v1.insert_main_buydata
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '无效的JSON数据'}), 400

        ID = data['ID']

        # 如果主表中已存在，直接忽略
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

        # 创建主表记录
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
        print(f"租赁主表数据插入错误: {str(e)}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500
            
    except Exception as e:
        print(f"插入租赁数据失败: {e}")
        import traceback
        traceback.print_exc()
        return '写入失败', 500
