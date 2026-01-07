from flask import jsonify, request, Blueprint
from src.log import Log
from src.execution_db import Date_base
from src.now_time import today
import requests

webRentalV1 = Blueprint('webRentalV1', __name__)

@webRentalV1.route('/countRentalNumber', methods=['get'])
def countRentalNumber():
    """
    快速统计总数：仅计数，不加载其他列
    """
    try:
        sql = "SELECT COUNT(*) FROM rental"
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag:
                return jsonify({"count": data[0][0]}), 200
        return jsonify({"count": 0}), 200
    except Exception as e:
        print(f"统计借入总数失败: {e}")
        import traceback
        print(traceback.format_exc())
        return "查询失败", 500

@webRentalV1.route('/getRentalData/<int:min>/<int:max>', methods=['get'])
def getRentalData(min, max):
    sql = f"""
    SELECT 
        ID, weapon_name, weapon_type, item_name, weapon_float, float_range, price,
        lessor_name, status, last_status, "from", lean_start_time, lean_end_time,
        total_Lease_Days, max_Lease_Days, steam_hash_name, sticker, pendant, rename, data_user
    FROM rental
    ORDER BY lean_start_time DESC
    LIMIT {max} OFFSET {min};
    """
    result = Date_base().select(sql)
    if result and len(result) == 2:
        flag, data = result
        if flag:
            return jsonify(data), 200
    return "查询失败", 500

@webRentalV1.route('/selectRentalWeaponName/<itemName>', methods=['get'])
def selectRentalWeaponName(itemName):
    sql = f"""
    SELECT 
        ID, weapon_name, weapon_type, item_name, weapon_float, float_range, price,
        lessor_name, status, last_status, "from", lean_start_time, lean_end_time,
        total_Lease_Days, max_Lease_Days, steam_hash_name, sticker, pendant, rename, data_user
    FROM rental
    WHERE item_name LIKE '%{itemName}%' OR weapon_name LIKE '%{itemName}%'
    ORDER BY lean_start_time DESC;
    """
    result = Date_base().select(sql)
    if result and len(result) == 2:
        flag, data = result
        if flag:
            return jsonify(data), 200
    return "查询失败", 500

@webRentalV1.route('/getRentalDataByStatus/<status>/<int:min>/<int:max>', methods=['get'])
def getRentalDataByStatus(status, min, max):
    if status == 'all':
        sql = f"""
        SELECT 
            ID, weapon_name, weapon_type, item_name, weapon_float, float_range, price,
            lessor_name, status, last_status, "from", lean_start_time, lean_end_time,
            total_Lease_Days, max_Lease_Days, steam_hash_name, sticker, pendant, rename, data_user
        FROM rental
        ORDER BY lean_start_time DESC
        LIMIT {max} OFFSET {min};
        """
    else:
        sql = f"""
        SELECT 
            ID, weapon_name, weapon_type, item_name, weapon_float, float_range, price,
            lessor_name, status, last_status, "from", lean_start_time, lean_end_time,
            total_Lease_Days, max_Lease_Days, steam_hash_name, sticker, pendant, rename, data_user
        FROM rental
        WHERE status = '{status}'
        ORDER BY lean_start_time DESC
        LIMIT {max} OFFSET {min};
        """
    result = Date_base().select(sql)
    if result and len(result) == 2:
        flag, data = result
        if flag:
            return jsonify(data), 200
    return "查询失败", 500

@webRentalV1.route('/getRentalDataByStatusSub/<path:last_status>/<int:min>/<int:max>', methods=['GET'])
def getRentalDataByStatusSub(last_status, min, max):
    if last_status == 'all':
        sql = f"""
        SELECT 
            ID, weapon_name, weapon_type, item_name, weapon_float, float_range, price,
            lessor_name, status, last_status, "from", lean_start_time, lean_end_time,
            total_Lease_Days, max_Lease_Days, steam_hash_name, sticker, pendant, rename, data_user
        FROM rental
        WHERE last_status IS NOT NULL AND last_status != ''
        ORDER BY lean_start_time DESC
        LIMIT {max} OFFSET {min};
        """
    else:
        safe_sub = last_status.replace("'", "''")
        sql = f"""
        SELECT 
            ID, weapon_name, weapon_type, item_name, weapon_float, float_range, price,
            lessor_name, status, last_status, "from", lean_start_time, lean_end_time,
            total_Lease_Days, max_Lease_Days, steam_hash_name, sticker, pendant, rename, data_user
        FROM rental
        WHERE last_status = '{safe_sub}'
        ORDER BY lean_start_time DESC
        LIMIT {max} OFFSET {min};
        """
    result = Date_base().select(sql)
    if result and len(result) == 2:
        flag, data = result
        if flag:
            return jsonify(data), 200
    return "查询失败", 500

@webRentalV1.route('/getRentalStatsByStatusSub/<path:last_status>', methods=['GET'])
def getRentalStatsByStatusSub(last_status):
    if last_status == 'all':
        where = "last_status IS NOT NULL AND last_status != ''"
    else:
        safe_sub = last_status.replace("'", "''")
        where = f"last_status = '{safe_sub}'"
    sql = f"""
    SELECT 
        COUNT(*) as total_count,
        COALESCE(SUM(price * total_Lease_Days), 0) as total_amount,
        COALESCE(AVG(price), 0) as avg_price,
        COALESCE(SUM(total_Lease_Days), 0) as total_lease_days,
        COALESCE(AVG(total_Lease_Days), 0) as avg_lease_days,
        COUNT(CASE WHEN status = '租赁中' THEN 1 END) as renting_count,
        COUNT(CASE WHEN status = '已完成' THEN 1 END) as completed_count,
        COUNT(CASE WHEN status = '已取消' THEN 1 END) as cancelled_count
    FROM rental
    WHERE {where}
    """
    result = Date_base().select(sql)
    if result and len(result) == 2:
        flag, data = result
        if flag and len(data) > 0:
            stats = data[0]
            return jsonify({
                "total_count": stats[0],
                "total_amount": round(float(stats[1]), 2),
                "avg_price": round(float(stats[2]), 2),
                "total_lease_days": stats[3],
                "avg_lease_days": round(float(stats[4]), 1),
                "renting_count": stats[5],
                "completed_count": stats[6],
                "cancelled_count": stats[7]
            }), 200
    return "查询失败", 500

@webRentalV1.route('/getRentalStats', methods=['get'])
def getRentalStats():
    sql = """
    SELECT 
        COUNT(*) as total_count,
        COALESCE(SUM(price * total_Lease_Days), 0) as total_amount,
        COALESCE(AVG(price), 0) as avg_price,
        COALESCE(SUM(total_Lease_Days), 0) as total_lease_days,
        COALESCE(AVG(total_Lease_Days), 0) as avg_lease_days,
        COUNT(CASE WHEN status = '租赁中' THEN 1 END) as renting_count,
        COUNT(CASE WHEN status = '已完成' THEN 1 END) as completed_count,
        COUNT(CASE WHEN status = '已取消' THEN 1 END) as cancelled_count
    FROM rental
    """
    result = Date_base().select(sql)
    if result and len(result) == 2:
        flag, data = result
        if flag and len(data) > 0:
            stats = data[0]
            return jsonify({
                "total_count": stats[0],
                "total_amount": round(float(stats[1]), 2),
                "avg_price": round(float(stats[2]), 2),
                "total_lease_days": stats[3],
                "avg_lease_days": round(float(stats[4]), 1),
                "renting_count": stats[5],
                "completed_count": stats[6],
                "cancelled_count": stats[7]
            }), 200
    return "查询失败", 500

@webRentalV1.route('/getRentalDataByTimeRange/<start_date>/<end_date>/<int:min>/<int:max>', methods=['GET'])
def getRentalDataByTimeRange(start_date, end_date, min, max):
    sql = f"""
    SELECT 
        ID, weapon_name, weapon_type, item_name, weapon_float, float_range, price,
        lessor_name, status, last_status, "from", lean_start_time, lean_end_time,
        total_Lease_Days, max_Lease_Days, steam_hash_name, sticker, pendant, rename
    FROM rental
    WHERE DATE(lean_start_time) >= '{start_date}' AND DATE(lean_start_time) <= '{end_date}'
    ORDER BY lean_start_time DESC 
    LIMIT {max} OFFSET {min};
    """
    result = Date_base().select(sql)
    if result and len(result) == 2:
        flag, data = result
        if flag:
            return jsonify(data), 200
    return "查询失败", 500

@webRentalV1.route('/getRentalStatsByTimeRange/<start_date>/<end_date>', methods=['GET'])
def getRentalStatsByTimeRange(start_date, end_date):
    sql = f"""
    SELECT 
        COUNT(*) as total_count,
        COALESCE(SUM(price * total_Lease_Days), 0) as total_amount,
        COALESCE(AVG(price), 0) as avg_price,
        COALESCE(SUM(total_Lease_Days), 0) as total_lease_days,
        COALESCE(AVG(total_Lease_Days), 0) as avg_lease_days,
        COUNT(CASE WHEN status = '租赁中' THEN 1 END) as renting_count,
        COUNT(CASE WHEN status = '已完成' THEN 1 END) as completed_count,
        COUNT(CASE WHEN status = '已取消' THEN 1 END) as cancelled_count
    FROM rental
    WHERE DATE(lean_start_time) >= '{start_date}' AND DATE(lean_start_time) <= '{end_date}'
    """
    result = Date_base().select(sql)
    if result and len(result) == 2:
        flag, data = result
        if flag and len(data) > 0:
            stats = data[0]
            return jsonify({
                "total_count": stats[0],
                "total_amount": round(float(stats[1]), 2),
                "avg_price": round(float(stats[2]), 2),
                "total_lease_days": stats[3],
                "avg_lease_days": round(float(stats[4]), 1),
                "renting_count": stats[5],
                "completed_count": stats[6],
                "cancelled_count": stats[7]
            }), 200
    return "查询失败", 500

@webRentalV1.route('/searchRentalByTimeRange/<start_date>/<end_date>', methods=['GET'])
def searchRentalByTimeRange(start_date, end_date):
    sql = f"""
    SELECT 
        ID, weapon_name, weapon_type, item_name, weapon_float, float_range, price,
        lessor_name, status, last_status, "from", lean_start_time, lean_end_time,
        total_Lease_Days, max_Lease_Days, steam_hash_name, sticker, pendant, rename
    FROM rental 
    WHERE DATE(lean_start_time) >= '{start_date}' AND DATE(lean_start_time) <= '{end_date}'
    ORDER BY lean_start_time DESC;
    """
    result = Date_base().select(sql)
    if result and len(result) == 2:
        flag, data = result
        if flag:
            return jsonify(data), 200
    return "查询失败", 500

@webRentalV1.route('/getRentalWeaponTypes', methods=['GET'])
def getRentalWeaponTypes():
    """获取所有武器类型列表"""
    try:
        sql = """
        SELECT DISTINCT weapon_type 
        FROM rental 
        WHERE weapon_type IS NOT NULL AND weapon_type != ''
        ORDER BY weapon_type
        """
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag:
                weapon_types = [row[0] for row in data if row[0]]
                return jsonify({"success": True, "data": weapon_types}), 200
        return jsonify({"success": True, "data": []}), 200
    except Exception as e:
        print(f"获取武器类型失败: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@webRentalV1.route('/getRentalFloatRanges', methods=['GET'])
def getRentalFloatRanges():
    """获取所有磨损等级列表"""
    try:
        sql = """
        SELECT DISTINCT float_range 
        FROM rental 
        WHERE float_range IS NOT NULL AND float_range != ''
        ORDER BY 
            CASE float_range
                WHEN '崭新出厂' THEN 1
                WHEN '略有磨损' THEN 2
                WHEN '久经沙场' THEN 3
                WHEN '破损不堪' THEN 4
                WHEN '战痕累累' THEN 5
                ELSE 6
            END
        """
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag:
                float_ranges = [row[0] for row in data if row[0]]
                return jsonify({"success": True, "data": float_ranges}), 200
        return jsonify({"success": True, "data": []}), 200
    except Exception as e:
        print(f"获取磨损等级失败: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@webRentalV1.route('/getRentalStatusList', methods=['GET'])
def getRentalStatusList():
    """获取所有状态列表"""
    try:
        sql = """
        SELECT DISTINCT status 
        FROM rental 
        WHERE status IS NOT NULL AND status != ''
        ORDER BY status
        """
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag:
                status_list = [row[0] for row in data if row[0]]
                return jsonify({"success": True, "data": status_list}), 200
        return jsonify({"success": True, "data": []}), 200
    except Exception as e:
        print(f"获取状态列表失败: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@webRentalV1.route('/getRentalStatusSubList', methods=['GET'])
@webRentalV1.route('/getRentalStatusSubList/<status>', methods=['GET'])
def getRentalStatusSubList(status='all'):
    """获取子状态列表，可选按主状态筛选"""
    try:
        if status == 'all' or not status:
            sql = """
            SELECT DISTINCT last_status 
            FROM rental 
            WHERE last_status IS NOT NULL AND last_status != ''
            ORDER BY last_status
            """
        else:
            safe_status = status.replace("'", "''")
            sql = f"""
            SELECT DISTINCT last_status 
            FROM rental 
            WHERE status = '{safe_status}' 
                AND last_status IS NOT NULL 
                AND last_status != ''
            ORDER BY last_status
            """
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag:
                status_sub_list = [row[0] for row in data if row[0]]
                return jsonify({"success": True, "data": status_sub_list}), 200
        return jsonify({"success": True, "data": []}), 200
    except Exception as e:
        print(f"获取子状态列表失败: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@webRentalV1.route('/getRentalPlatformList', methods=['GET'])
def getRentalPlatformList():
    """获取所有平台列表"""
    try:
        sql = """
        SELECT DISTINCT "from" 
        FROM rental 
        WHERE "from" IS NOT NULL AND "from" != ''
        ORDER BY "from"
        """
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag:
                platform_list = [row[0] for row in data if row[0]]
                return jsonify({"success": True, "data": platform_list}), 200
        return jsonify({"success": True, "data": []}), 200
    except Exception as e:
        print(f"获取平台列表失败: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@webRentalV1.route('/getRentalLessorList', methods=['GET'])
def getRentalLessorList():
    """获取所有出租人列表"""
    try:
        sql = """
        SELECT DISTINCT lessor_name 
        FROM rental 
        WHERE lessor_name IS NOT NULL AND lessor_name != ''
        ORDER BY lessor_name
        """
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag:
                lessor_list = [row[0] for row in data if row[0]]
                return jsonify({"success": True, "data": lessor_list}), 200
        return jsonify({"success": True, "data": []}), 200
    except Exception as e:
        print(f"获取出租人列表失败: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@webRentalV1.route('/getRentalUserList', methods=['GET'])
def getRentalUserList():
    """获取所有用户列表（data_user字段）"""
    try:
        sql = """
        SELECT DISTINCT data_user 
        FROM rental 
        WHERE data_user IS NOT NULL AND data_user != ''
        ORDER BY data_user
        """
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag:
                user_list = [row[0] for row in data if row[0]]
                return jsonify({"success": True, "data": user_list}), 200
        return jsonify({"success": True, "data": []}), 200
    except Exception as e:
        print(f"获取用户列表失败: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
