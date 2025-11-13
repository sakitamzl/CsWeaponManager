from flask import jsonify, request, Blueprint
from src.log import Log
from src.execution_db import Date_base
from src.now_time import today
from src.db_manager.index.sell import SellModel
import requests

webSellV1 = Blueprint('webSellV1', __name__)

@webSellV1.route('/countSellNumber', methods=['get'])
def countSellNumber():
    try:
        records = SellModel.find_all()
        count = len(records)
        return jsonify({"count": count}), 200
    except Exception as e:
        print(f"查询销售数量失败: {e}")
        return jsonify({"count": 0}), 500

@webSellV1.route('/getSellData/<int:min>/<int:max>', methods=['get'])
def getSellData(min, max):
    try:
        records = SellModel.find_all(
            "1=1 ORDER BY order_time DESC", 
            (), 
            limit=max, 
            offset=min
        )
        data = []
        for record in records:
            data.append([
                record.ID, record.item_name, record.weapon_name, 
                record.weapon_type, record.weapon_float, record.float_range, 
                record.price, getattr(record, 'from', ''), record.order_time, record.status,
                record.status_sub
            ])
        return jsonify(data), 200
    except Exception as e:
        print(f"查询销售数据失败: {e}")
        return jsonify([]), 500
    

@webSellV1.route('/selectSellWeaponName/<itemName>', methods=['get'])
def selectSellWeaponName(itemName):
    sql = f"SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, \"from\", order_time, status, status_sub FROM sell WHERE item_name LIKE '%{itemName}%' OR weapon_name LIKE '%{itemName}%' ORDER BY order_time DESC;"
    result = Date_base().select(sql)
    if result and len(result) == 2:
        flag, data = result
        if flag:
            return jsonify(data), 200
    return "查询失败", 500

@webSellV1.route('/getDataUserList', methods=['GET'])
def get_sell_data_user_list():
    """获取 sell 表中 data_user 去重列表"""
    sql = """
    SELECT DISTINCT data_user
    FROM sell
    WHERE data_user IS NOT NULL AND data_user != ''
    ORDER BY data_user
    """
    result = Date_base().select(sql)
    if result and len(result) == 2:
        flag, data = result
        if flag:
            users = [row[0] for row in data if row and row[0]]
            return jsonify(users), 200
    return jsonify([]), 500

@webSellV1.route('/getSellDataByDataUser/<path:data_user>/<int:min>/<int:max>', methods=['GET'])
def get_sell_data_by_data_user(data_user, min, max):
    """按 data_user 分页获取 sell 数据"""
    if data_user == 'all':
        return getSellData(min, max)
    safe_user = data_user.replace("'", "''")
    sql = f"""
    SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, `from`, order_time, status, status_sub
    FROM sell
    WHERE data_user = '{safe_user}'
    ORDER BY order_time DESC
    LIMIT {max} OFFSET {min};
    """
    result = Date_base().select(sql)
    if result and len(result) == 2:
        flag, data = result
        if flag:
            return jsonify(data), 200
    return "查询失败", 500

@webSellV1.route('/getSellStatsByDataUser/<path:data_user>', methods=['GET'])
def get_sell_stats_by_data_user(data_user):
    """按 data_user 获取 sell 统计"""
    if data_user == 'all':
        return getSellStats()
    safe_user = data_user.replace("'", "''")
    sql = f"""
    SELECT 
        COUNT(*) as total_count,
        COALESCE(SUM(CASE WHEN status != '已取消' THEN price ELSE 0 END), 0) as total_amount,
        COALESCE(AVG(CASE WHEN status != '已取消' THEN price ELSE NULL END), 0) as avg_price,
        COUNT(CASE WHEN status = '已完成' THEN 1 END) as completed_count,
        COUNT(CASE WHEN status = '已取消' THEN 1 END) as cancelled_count,
        COUNT(CASE WHEN status = '待收货' THEN 1 END) as pending_count
    FROM sell
    WHERE data_user = '{safe_user}'
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
                "completed_count": stats[3],
                "cancelled_count": stats[4],
                "pending_count": stats[5]
            }), 200
    return "查询失败", 500

@webSellV1.route('/getSellDataByStatus/<status>/<int:min>/<int:max>', methods=['get'])
def getSellDataByStatus(status, min, max):
    if status == 'all':
        sql = f"SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, \"from\", order_time, status, status_sub FROM sell ORDER BY order_time DESC LIMIT {max} OFFSET {min};"
    else:
        sql = f"SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, \"from\", order_time, status, status_sub FROM sell WHERE status = '{status}' ORDER BY order_time DESC LIMIT {max} OFFSET {min};"
    result = Date_base().select(sql)
    if result and len(result) == 2:
        flag, data = result
        if flag:
            return jsonify(data), 200
    return "查询失败", 500

@webSellV1.route('/getSellStats', methods=['get'])
def getSellStats():
    sql = """
    SELECT 
        COUNT(*) as total_count,
        COALESCE(SUM(CASE WHEN status != '已取消' THEN price ELSE 0 END), 0) as total_amount,
        COALESCE(AVG(CASE WHEN status != '已取消' THEN price ELSE NULL END), 0) as avg_price,
        COUNT(CASE WHEN status = '已完成' THEN 1 END) as completed_count,
        COUNT(CASE WHEN status = '已取消' THEN 1 END) as cancelled_count,
        COUNT(CASE WHEN status = '待收货' THEN 1 END) as pending_count
    FROM sell
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
                "completed_count": stats[3],
                "cancelled_count": stats[4],
                "pending_count": stats[5]
            }), 200
    return "查询失败", 500

@webSellV1.route('/getSellStatsBySearch/<itemName>', methods=['GET'])
def getSellStatsBySearch(itemName):
    search_pattern = f"%{itemName}%"
    sql = f"""
    SELECT 
        COUNT(*) as total_count,
        COALESCE(SUM(CASE WHEN status != '已取消' THEN price ELSE 0 END), 0) as total_amount,
        COALESCE(AVG(CASE WHEN status != '已取消' THEN price ELSE NULL END), 0) as avg_price,
        COUNT(CASE WHEN status = '已完成' THEN 1 END) as completed_count,
        COUNT(CASE WHEN status = '已取消' THEN 1 END) as cancelled_count,
        COUNT(CASE WHEN status = '待收货' THEN 1 END) as pending_count
    FROM sell
    WHERE item_name LIKE '{search_pattern}' OR weapon_name LIKE '{search_pattern}'
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
                "completed_count": stats[3],
                "cancelled_count": stats[4],
                "pending_count": stats[5]
            }), 200
    return "查询失败", 500

@webSellV1.route('/getSellStatsByStatus/<status>', methods=['GET'])
def getSellStatsByStatus(status):
    if status == 'all':
        return getSellStats()
    
    sql = f"""
    SELECT 
        COUNT(*) as total_count,
        COALESCE(SUM(CASE WHEN status != '已取消' THEN price ELSE 0 END), 0) as total_amount,
        COALESCE(AVG(CASE WHEN status != '已取消' THEN price ELSE NULL END), 0) as avg_price,
        COUNT(CASE WHEN status = '已完成' THEN 1 END) as completed_count,
        COUNT(CASE WHEN status = '已取消' THEN 1 END) as cancelled_count,
        COUNT(CASE WHEN status = '待收货' THEN 1 END) as pending_count
    FROM sell
    WHERE status = '{status}'
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
                "completed_count": stats[3],
                "cancelled_count": stats[4],
                "pending_count": stats[5]
            }), 200
    return "查询失败", 500

@webSellV1.route('/getSellDataByStatusSub/<path:status_sub>/<int:min>/<int:max>', methods=['GET'])
def getSellDataByStatusSub(status_sub, min, max):
    if status_sub == 'all':
        sql = f"""
        SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, "from", order_time, status, status_sub
        FROM sell
        WHERE status_sub IS NOT NULL AND status_sub != ''
        ORDER BY order_time DESC
        LIMIT {max} OFFSET {min};
        """
    else:
        safe_sub = status_sub.replace("'", "''")
        sql = f"""
        SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, "from", order_time, status, status_sub
        FROM sell
        WHERE status_sub = '{safe_sub}'
        ORDER BY order_time DESC
        LIMIT {max} OFFSET {min};
        """
    result = Date_base().select(sql)
    if result and len(result) == 2:
        flag, data = result
        if flag:
            return jsonify(data), 200
    return "查询失败", 500

@webSellV1.route('/getSellStatsByStatusSub/<path:status_sub>', methods=['GET'])
def getSellStatsByStatusSub(status_sub):
    if status_sub == 'all':
        sql = """
        SELECT 
            COUNT(*) as total_count,
            COALESCE(SUM(CASE WHEN status != '已取消' THEN price ELSE 0 END), 0) as total_amount,
            COALESCE(AVG(CASE WHEN status != '已取消' THEN price ELSE NULL END), 0) as avg_price,
            COUNT(CASE WHEN status = '已完成' THEN 1 END) as completed_count,
            COUNT(CASE WHEN status = '已取消' THEN 1 END) as cancelled_count,
            COUNT(CASE WHEN status = '待收货' THEN 1 END) as pending_count
        FROM sell
        WHERE status_sub IS NOT NULL AND status_sub != ''
        """
    else:
        safe_sub = status_sub.replace("'", "''")
        sql = f"""
        SELECT 
            COUNT(*) as total_count,
            COALESCE(SUM(CASE WHEN status != '已取消' THEN price ELSE 0 END), 0) as total_amount,
            COALESCE(AVG(CASE WHEN status != '已取消' THEN price ELSE NULL END), 0) as avg_price,
            COUNT(CASE WHEN status = '已完成' THEN 1 END) as completed_count,
            COUNT(CASE WHEN status = '已取消' THEN 1 END) as cancelled_count,
            COUNT(CASE WHEN status = '待收货' THEN 1 END) as pending_count
        FROM sell
        WHERE status_sub = '{safe_sub}'
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
                "completed_count": stats[3],
                "cancelled_count": stats[4],
                "pending_count": stats[5]
            }), 200
    return "查询失败", 500

@webSellV1.route('/getSellDataByTimeRange/<start_date>/<end_date>/<int:min>/<int:max>', methods=['GET'])
def getSellDataByTimeRange(start_date, end_date, min, max):
    sql = f"""
    SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, \"from\", order_time, status 
    FROM sell 
    WHERE DATE(order_time) >= '{start_date}' AND DATE(order_time) <= '{end_date}'
    ORDER BY order_time DESC 
    LIMIT {max} OFFSET {min};
    """
    result = Date_base().select(sql)
    if result and len(result) == 2:
        flag, data = result
        if flag:
            return jsonify(data), 200
    return "查询失败", 500

@webSellV1.route('/getSellStatsByTimeRange/<start_date>/<end_date>', methods=['GET'])
def getSellStatsByTimeRange(start_date, end_date):
    sql = f"""
    SELECT 
        COUNT(*) as total_count,
        COALESCE(SUM(CASE WHEN status != '已取消' THEN price ELSE 0 END), 0) as total_amount,
        COALESCE(AVG(CASE WHEN status != '已取消' THEN price ELSE NULL END), 0) as avg_price,
        COUNT(CASE WHEN status = '已完成' THEN 1 END) as completed_count,
        COUNT(CASE WHEN status = '已取消' THEN 1 END) as cancelled_count,
        COUNT(CASE WHEN status = '待收货' THEN 1 END) as pending_count
    FROM sell
    WHERE DATE(order_time) >= '{start_date}' AND DATE(order_time) <= '{end_date}'
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
                "completed_count": stats[3],
                "cancelled_count": stats[4],
                "pending_count": stats[5]
            }), 200
    return "查询失败", 500


@webSellV1.route('/getSellStatsFiltered', methods=['POST'])
def get_sell_stats_filtered():
    try:
        filters = request.get_json() or {}
        clauses = []
        params = []

        def add_clause(clause, *values):
            clauses.append(clause)
            params.extend(values)

        source = filters.get('source')
        if source:
            add_clause("LOWER(`from`) = LOWER(?)", source)

        status = filters.get('status')
        if status:
            add_clause("status = ?", status)

        status_sub = filters.get('status_sub')
        if status_sub:
            add_clause("status_sub = ?", status_sub)

        data_user = filters.get('data_user')
        if data_user:
            add_clause("data_user = ?", data_user)

        weapon_types = filters.get('weapon_types') or []
        if isinstance(weapon_types, list) and len(weapon_types) > 0:
            placeholders = ",".join(["?"] * len(weapon_types))
            clauses.append(f"weapon_type IN ({placeholders})")
            params.extend(weapon_types)

        float_ranges = filters.get('float_ranges') or []
        if isinstance(float_ranges, list) and len(float_ranges) > 0:
            placeholders = ",".join(["?"] * len(float_ranges))
            clauses.append(f"float_range IN ({placeholders})")
            params.extend(float_ranges)

        search_keyword = filters.get('search')
        if search_keyword:
            like = f"%{search_keyword}%"
            clauses.append("(item_name LIKE ? OR weapon_name LIKE ?)")
            params.extend([like, like])

        start_date = filters.get('start_date')
        end_date = filters.get('end_date')
        if start_date and end_date:
            clauses.append("order_time BETWEEN ? AND ?")
            params.extend([f"{start_date} 00:00:00", f"{end_date} 23:59:59"])

        where_clause = ""
        if clauses:
            where_clause = " WHERE " + " AND ".join(clauses)

        sql = f"""
        SELECT 
            COUNT(*) as total_count,
            COALESCE(SUM(CASE WHEN status != '已取消' THEN price ELSE 0 END), 0) as total_amount,
            COALESCE(AVG(CASE WHEN status != '已取消' THEN price ELSE NULL END), 0) as avg_price,
            COUNT(CASE WHEN status = '已完成' THEN 1 END) as completed_count,
            COUNT(CASE WHEN status = '已取消' THEN 1 END) as cancelled_count,
            COUNT(CASE WHEN status = '待收货' THEN 1 END) as pending_count
        FROM sell
        {where_clause}
        """

        db = Date_base()
        result = db.execute_query(sql, tuple(params))

        if result and len(result) > 0:
            stats = result[0]
            return jsonify({
                "success": True,
                "total_count": stats[0],
                "total_amount": round(float(stats[1]), 2),
                "avg_price": round(float(stats[2]), 2),
                "completed_count": stats[3],
                "cancelled_count": stats[4],
                "pending_count": stats[5]
            }), 200

        return jsonify({
            "success": True,
            "total_count": 0,
            "total_amount": 0.0,
            "avg_price": 0.0,
            "completed_count": 0,
            "cancelled_count": 0,
            "pending_count": 0
        }), 200
    except Exception as e:
        print(f"获取出售筛选统计失败: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@webSellV1.route('/searchSellByTimeRange/<start_date>/<end_date>', methods=['GET'])
def searchSellByTimeRange(start_date, end_date):
    sql = f"""
    SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, \"from\", order_time, status 
    FROM sell 
    WHERE DATE(order_time) >= '{start_date}' AND DATE(order_time) <= '{end_date}'
    ORDER BY order_time DESC;
    """
    result = Date_base().select(sql)
    if result and len(result) == 2:
        flag, data = result
        if flag:
            return jsonify(data), 200
    return "查询失败", 500