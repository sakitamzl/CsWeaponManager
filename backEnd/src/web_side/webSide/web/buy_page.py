from flask import jsonify, request, Blueprint
from src.log import Log
from src.execution_db import Date_base
from src.now_time import today
from src.db_manager.index.model.buy import BuyModel
import requests

webBuyV1 = Blueprint('webBuyV1', __name__)

@webBuyV1.route('/countBuyNumber', methods=['get'])
def countBuyNumber():
    try:
        records = BuyModel.find_all()
        count = len(records)
        return jsonify({"count": count}), 200
    except Exception as e:
        print(f"查询购买数量失败: {e}")
        return jsonify({"count": 0}), 500

@webBuyV1.route('/selectBuyWeaponName/<itemName>', methods=['get'])
def selectBuyWeaponName(itemName):
    sql = f"SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, \"from\", order_time, status, status_sub, steam_hash_name, sticker, pendant, rename FROM buy WHERE item_name LIKE '%{itemName}%' OR weapon_name LIKE '%{itemName}%' ORDER BY order_time DESC;"
    result = Date_base().select(sql)
    if result and len(result) == 2:
        flag, data = result
        if flag:
            return jsonify(data), 200
    return "查询失败", 500

@webBuyV1.route('/getSourceList', methods=['GET'])
def get_source_list():
    """获取购买数据来源平台列表"""
    # 固定来源列表，不再从数据库去重
    sources = ['yyyp', 'buff', 'CsFloat', 'SMK', 'ING']
    return jsonify(sources), 200


@webBuyV1.route('/searchBuyByTimeRange/<start_date>/<end_date>', methods=['GET'])
def search_buy_by_time_range(start_date, end_date):
    """按时间范围搜索 buy 记录"""
    try:
        sql = """
        SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, `from`, order_time, status, status_sub, steam_hash_name, sticker, pendant, rename
        FROM buy
        WHERE order_time BETWEEN ? AND ?
        ORDER BY order_time DESC
        """
        params = (f"{start_date} 00:00:00", f"{end_date} 23:59:59")
        db = Date_base()
        result = db.execute_query(sql, params)
        return jsonify(result or []), 200
    except Exception as e:
        print(f"按时间范围查询购入失败: {e}")
        return jsonify([]), 500


@webBuyV1.route('/getBuyStatsByTimeRange/<start_date>/<end_date>', methods=['GET'])
def get_buy_stats_by_time_range(start_date, end_date):
    """按时间范围获取 buy 统计"""
    try:
        sql = """
        SELECT 
            COUNT(*) as total_count,
            COALESCE(SUM(CASE WHEN status != '已取消' THEN price ELSE 0 END), 0) as total_amount,
            COALESCE(AVG(CASE WHEN status != '已取消' THEN price ELSE NULL END), 0) as avg_price,
            COUNT(CASE WHEN status = '已完成' THEN 1 END) as completed_count,
            COUNT(CASE WHEN status = '已取消' THEN 1 END) as cancelled_count,
            COUNT(CASE WHEN status = '待收货' THEN 1 END) as pending_count
        FROM buy
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
        print(f"获取购入时间范围统计失败: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


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

@webBuyV1.route('/getBuyDataFiltered', methods=['POST'])
def get_buy_data_filtered():
    """组合查询接口：支持所有过滤条件的分页数据获取"""
    try:
        data = request.get_json() or {}
        filters = data.get('filters', {})
        min_offset = data.get('min', 0)
        max_limit = data.get('max', 20)

        where_clause, params = _build_filter_clauses(filters)

        sql = f"""
        SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, `from`, order_time, status, status_sub, steam_hash_name, sticker, pendant, rename
        FROM buy
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
        print(f"获取购入筛选数据失败: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@webBuyV1.route('/getBuyStatsFiltered', methods=['POST'])
def get_buy_stats_filtered():
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
        FROM buy
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
        print(f"获取购入筛选统计失败: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@webBuyV1.route('/getBuyStats', methods=['get'])
def getBuyStats():
    sql = """
    SELECT 
        COUNT(*) as total_count,
        COALESCE(SUM(CASE WHEN status != '已取消' THEN price ELSE 0 END), 0) as total_amount,
        COALESCE(AVG(CASE WHEN status != '已取消' THEN price ELSE NULL END), 0) as avg_price,
        COUNT(CASE WHEN status = '已完成' THEN 1 END) as completed_count,
        COUNT(CASE WHEN status = '已取消' THEN 1 END) as cancelled_count,
        COUNT(CASE WHEN status = '待收货' THEN 1 END) as pending_count
    FROM buy
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

@webBuyV1.route('/getBuyTotalStats', methods=['POST'])
def getBuyTotalStats():
    sql = """
    SELECT COUNT(*) as total_count, COALESCE(SUM(price), 0) as total_amount
    FROM buy
    """
    result = Date_base().select(sql)
    if result and len(result) == 2:
        flag, data = result
        if flag and len(data) > 0:
            stats = data[0]
            return jsonify([stats[0], round(float(stats[1]), 2)]), 200
    return jsonify([0, 0]), 500

@webBuyV1.route('/getDataUserList', methods=['GET'])
def get_data_user_list():
    """获取 buy 表中 data_user 去重列表"""
    sql = """
    SELECT DISTINCT data_user
    FROM buy
    WHERE data_user IS NOT NULL AND data_user != ''
    ORDER BY data_user
    """
    result = Date_base().select(sql)
    if result and len(result) == 2:
        flag, data = result
        if flag:
            # data 为[(value,), ...]
            users = [row[0] for row in data if row and row[0]]
            return jsonify(users), 200
    return jsonify([]), 500

@webBuyV1.route('/insertIngameBuy', methods=['POST'])
def insert_ingame_buy():
    """插入游戏内购买记录到 buy 表（from='ING'）"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '无效的JSON数据'}), 400
        
        ID = data.get('ID')
        print(f"收到游戏内购买数据 - ID: {ID}, 物品: {data.get('item_name')}, 价格: {data.get('price')}")
        weapon_name = data.get('weapon_name')
        weapon_type = data.get('weapon_type')
        item_name = data.get('item_name')
        weapon_float = data.get('weapon_float')
        float_range = data.get('float_range')
        price = data.get('price')
        order_time = data.get('order_time')
        steam_id = data.get('steam_id')
        data_user = data.get('data_user')
        
        if not ID or not price:
            return jsonify({'success': False, 'error': '缺少必要参数（ID或price）'}), 400
        
        # 插入到 buy 表
        buy_record = BuyModel()
        buy_record.ID = ID
        buy_record.weapon_name = weapon_name
        buy_record.weapon_type = weapon_type
        buy_record.item_name = item_name
        buy_record.weapon_float = weapon_float
        buy_record.float_range = float_range
        buy_record.price = price
        buy_record.seller_name = None  # 游戏内购买没有卖家
        buy_record.status = '已完成'  # 游戏内购买通常是即时完成的
        buy_record.status_sub = None
        buy_record.steam_id = steam_id
        buy_record.order_time = order_time
        buy_record.data_user = data_user
        setattr(buy_record, 'from', 'ING')
        
        # 检查是否已存在相同ID的记录
        existing_record = BuyModel.find_by_id(ID=ID)
        if existing_record:
            print(f"警告：ID {ID} 已存在于buy表中，跳过重复插入")
            return jsonify({
                'success': True,
                'message': '记录已存在，跳过重复插入',
                'data': {
                    'id': ID,
                    'weapon_name': weapon_name,
                    'item_name': item_name,
                    'price': price
                }
            }), 200
        
        buy_saved = buy_record.save()
        
        if buy_saved:
            return jsonify({
                'success': True,
                'message': '游戏内购买数据插入成功',
                'data': {
                    'id': ID,
                    'weapon_name': weapon_name,
                    'item_name': item_name,
                    'price': price
                }
            }), 200
        else:
            print(f"数据插入失败 - ID: {ID}, 物品: {item_name}, 价格: {price}")
            return jsonify({'success': False, 'error': '数据插入失败'}), 500
            
    except Exception as e:
        print(f"游戏内购买数据插入错误: {str(e)}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500


@webBuyV1.route('/getYyypPriceInfo/<steam_hash_name>', methods=['GET'])
def get_yyyp_price_info(steam_hash_name):
    """
    根据 steam_hash_name 查询 weapon_classID 表中的价格信息（包括悠悠有品和BUFF）
    """
    try:
        from src.db_manager.index.model.weapon_classID import WeaponClassIDModel

        # 查询 weapon_classID 表
        results = WeaponClassIDModel.find_by_steam_hash_name(steam_hash_name)

        if results and len(results) > 0:
            weapon_info = results[0]
            return jsonify({
                'success': True,
                'data': {
                    'yyyp_price': weapon_info.yyyp_Price if weapon_info.yyyp_Price else None,
                    'yyyp_on_sale_count': weapon_info.yyyp_OnSaleCount if weapon_info.yyyp_OnSaleCount else None,
                    'buff_price': weapon_info.buff_Price if weapon_info.buff_Price else None,
                    'buff_on_sale_count': weapon_info.buff_OnSaleCount if weapon_info.buff_OnSaleCount else None,
                    'market_listing_item_name': weapon_info.market_listing_item_name if weapon_info.market_listing_item_name else None
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '未找到该武器的价格信息',
                'data': {
                    'yyyp_price': None,
                    'yyyp_on_sale_count': None,
                    'buff_price': None,
                    'buff_on_sale_count': None,
                    'market_listing_item_name': None
                }
            }), 404

    except Exception as e:
        print(f"查询价格信息失败: {str(e)}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}',
            'data': {
                'yyyp_price': None,
                'yyyp_on_sale_count': None,
                'buff_price': None,
                'buff_on_sale_count': None
            }
        }), 500
