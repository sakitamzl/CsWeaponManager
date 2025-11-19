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

@webSellV1.route('/getSourceList', methods=['GET'])
def get_source_list():
    """获取销售数据来源平台列表"""
    # 固定来源列表，不再从数据库去重
    sources = ['yyyp', 'buff', 'csfloat', 'SMK']
    return jsonify(sources), 200


@webSellV1.route('/selectSellWeaponName/<itemName>', methods=['get'])
def selectSellWeaponName(itemName):
    sql = f"SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, \"from\", order_time, status, status_sub FROM sell WHERE item_name LIKE '%{itemName}%' OR weapon_name LIKE '%{itemName}%' ORDER BY order_time DESC;"
    result = Date_base().select(sql)
    if result and len(result) == 2:
        flag, data = result
        if flag:
            return jsonify(data), 200
    return "查询失败", 500


@webSellV1.route('/searchSellByTimeRange/<start_date>/<end_date>', methods=['GET'])
def search_sell_by_time_range(start_date, end_date):
    """按时间范围搜索 sell 记录"""
    try:
        sql = """
        SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, `from`, order_time, status, status_sub
        FROM sell
        WHERE order_time BETWEEN ? AND ?
        ORDER BY order_time DESC
        """
        params = (f"{start_date} 00:00:00", f"{end_date} 23:59:59")
        db = Date_base()
        result = db.execute_query(sql, params)
        return jsonify(result or []), 200
    except Exception as e:
        print(f"按时间范围查询出售失败: {e}")
        return jsonify([]), 500


@webSellV1.route('/getSellStatsByTimeRange/<start_date>/<end_date>', methods=['GET'])
def get_sell_stats_by_time_range(start_date, end_date):
    """按时间范围获取 sell 统计"""
    try:
        sql = """
        SELECT 
            COUNT(*) as total_count,
            COALESCE(SUM(CASE WHEN status != '已取消' THEN price ELSE 0 END), 0) as total_amount,
            COALESCE(AVG(CASE WHEN status != '已取消' THEN price ELSE NULL END), 0) as avg_price,
            COUNT(CASE WHEN status = '已完成' THEN 1 END) as completed_count,
            COUNT(CASE WHEN status = '已取消' THEN 1 END) as cancelled_count,
            COUNT(CASE WHEN status = '待收货' THEN 1 END) as pending_count
        FROM sell
        WHERE order_time BETWEEN ? AND ?
        """
        params = (f"{start_date} 00:00:00", f"{end_date} 23:59:59")
        db = Date_base()
        result = db.execute_query(sql, params)

        if result and len(result) > 0:
            stats = result[0]
            return jsonify({
                "total_count": stats[0],
                "total_amount": round(float(stats[1]), 2),
                "avg_price": round(float(stats[2]), 2),
                "completed_count": stats[3],
                "cancelled_count": stats[4],
                "pending_count": stats[5]
            }), 200

        return jsonify({
            "total_count": 0,
            "total_amount": 0.0,
            "avg_price": 0.0,
            "completed_count": 0,
            "cancelled_count": 0,
            "pending_count": 0
        }), 200
    except Exception as e:
        print(f"获取出售时间范围统计失败: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


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



def _build_filter_clauses(filters):
    """构建过滤条件的SQL子句和参数"""
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

    return where_clause, tuple(params)

@webSellV1.route('/getSellDataFiltered', methods=['POST'])
def get_sell_data_filtered():
    """组合查询接口：支持所有过滤条件的分页数据获取"""
    try:
        data = request.get_json() or {}
        filters = data.get('filters', {})
        min_offset = data.get('min', 0)
        max_limit = data.get('max', 20)

        where_clause, params = _build_filter_clauses(filters)

        sql = f"""
        SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, `from`, order_time, status, status_sub
        FROM sell
        {where_clause}
        ORDER BY order_time DESC
        LIMIT {max_limit} OFFSET {min_offset}
        """

        db = Date_base()
        result = db.execute_query(sql, params)

        if result:
            return jsonify(result), 200
        return jsonify([]), 200
    except Exception as e:
        print(f"获取出售筛选数据失败: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@webSellV1.route('/getSellStatsFiltered', methods=['POST'])
def get_sell_stats_filtered():
    """组合查询接口：支持所有过滤条件的统计信息获取"""
    try:
        filters = request.get_json() or {}
        where_clause, params = _build_filter_clauses(filters)

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
        result = db.execute_query(sql, params)

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
