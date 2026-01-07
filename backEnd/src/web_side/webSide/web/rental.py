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
