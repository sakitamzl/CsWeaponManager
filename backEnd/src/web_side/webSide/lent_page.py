from flask import jsonify, request, Blueprint
from src.execution_db import Date_base
from src.db_manager.index.lease import LeaseModel

webLentPageV1 = Blueprint('webLentPageV1', __name__)

@webLentPageV1.route('/getWeaponTypes', methods=['GET'])
def getWeaponTypes():
    """获取租赁武器类型唯一值（优先 lent，补充 yyyp_lent）"""
    try:
        db = Date_base()
        sql = """
        SELECT DISTINCT weapon_type
        FROM lent
        WHERE weapon_type IS NOT NULL AND weapon_type != ''
        UNION
        SELECT DISTINCT weapon_type
        FROM yyyp_lent
        WHERE weapon_type IS NOT NULL AND weapon_type != ''
        ORDER BY 
            CASE weapon_type
                WHEN '匕首' THEN 1
                WHEN '手套' THEN 2
                WHEN '手枪' THEN 3
                WHEN '步枪' THEN 4
                WHEN '狙击步枪' THEN 5
                WHEN '微型冲锋枪' THEN 6
                WHEN '霰弹枪' THEN 7
                WHEN '机枪' THEN 8
                WHEN '印花' THEN 9
                ELSE 999
            END,
            weapon_type
        """
        result = db.execute_query(sql)
        
        weapon_types = []
        if result:
            for row in result:
                if row[0]:  # 确保不是空值
                    weapon_types.append(row[0])
        
        print(f"获取到的武器类型: {weapon_types}")
        
        return jsonify({
            'success': True,
            'data': weapon_types
        }), 200
        
    except Exception as e:
        print(f"获取武器类型失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e),
            'data': []
        }), 500

@webLentPageV1.route('/getStatusList', methods=['GET'])
def getStatusList():
    """获取租赁状态唯一值（优先 lent，补充 yyyp_lent）"""
    try:
        db = Date_base()
        sql = """
        SELECT DISTINCT status FROM lent WHERE status IS NOT NULL AND status != ''
        UNION
        SELECT DISTINCT status FROM yyyp_lent WHERE status IS NOT NULL AND status != ''
        """
        result = db.execute_query(sql)
        
        status_list = []
        if result:
            for row in result:
                if row[0]:  # 确保不是空值
                    status_list.append(row[0])
        
        # 排序：核心状态优先，其余按字典序
        def sort_key(val):
            order_map = {'租赁中': 1, '已完成': 2, '已取消': 3}
            return (order_map.get(val, 999), val)
        status_list = sorted(set(status_list), key=sort_key)
        print(f"获取到的状态列表(含租赁/yyyp): {status_list}")
        
        return jsonify({
            'success': True,
            'data': status_list
        }), 200
        
    except Exception as e:
        print(f"获取状态列表失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e),
            'data': []
        }), 500

@webLentPageV1.route('/getStatusSubList', methods=['GET'])
def getStatusSubList():
    """获取租赁子状态：
    - lent: 优先 last_status，回退 status
    - yyyp_lent: 优先 status_sub，回退 last_status，再回退 status
    按主状态筛选；status 为空/ALL 时返回全部
    """
    try:
        status = request.args.get('status', '').strip()
        db = Date_base()
        params = []
        if not status or status.lower() == 'all':
            sql = """
            SELECT DISTINCT COALESCE(last_status, status) AS status_sub
            FROM lent
            WHERE COALESCE(last_status, status) IS NOT NULL AND COALESCE(last_status, status) != ''
            UNION
            SELECT DISTINCT COALESCE(status_sub, last_status, status) AS status_sub
            FROM yyyp_lent
            WHERE COALESCE(status_sub, last_status, status) IS NOT NULL
              AND COALESCE(status_sub, last_status, status) != ''
            """
        else:
            sql = """
            SELECT DISTINCT COALESCE(last_status, status) AS status_sub
            FROM lent
            WHERE status = ?
              AND COALESCE(last_status, status) IS NOT NULL AND COALESCE(last_status, status) != ''
            UNION
            SELECT DISTINCT COALESCE(status_sub, last_status, status) AS status_sub
            FROM yyyp_lent
            WHERE status = ?
              AND COALESCE(status_sub, last_status, status) IS NOT NULL
              AND COALESCE(status_sub, last_status, status) != ''
            """
            params.extend([status, status])

        if params:
            result = db.execute_query(sql, tuple(params))
        else:
            result = db.execute_query(sql)
        sub_list = []
        if result:
            for row in result:
                if row[0]:
                    sub_list.append(row[0])
        sub_list = sorted(set(sub_list))
        print(f"获取到的子状态列表 status={status or 'all'}: {sub_list}")
        return jsonify({'success': True, 'data': sub_list}), 200
    except Exception as e:
        print(f"获取租赁子状态失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e), 'data': []}), 500
@webLentPageV1.route('/getFloatRanges', methods=['GET'])
def getFloatRanges():
    """获取磨损等级唯一值（优先 lent，补充 yyyp_lent；优先显示主要磨损）"""
    try:
        db = Date_base()
        sql = """
        SELECT DISTINCT float_range
        FROM lent
        WHERE float_range IS NOT NULL AND float_range != ''
        UNION
        SELECT DISTINCT float_range
        FROM yyyp_lent
        WHERE float_range IS NOT NULL AND float_range != ''
        ORDER BY 
            CASE float_range
                WHEN '崭新出厂' THEN 1
                WHEN '略有磨损' THEN 2
                WHEN '久经沙场' THEN 3
                WHEN '破损不堪' THEN 4
                WHEN '战痕累累' THEN 5
                ELSE 999
            END,
            float_range
        """
        result = db.execute_query(sql)
        
        float_ranges = []
        if result:
            for row in result:
                if row[0]:  # 确保不是空值
                    float_ranges.append(row[0])
        
        print(f"获取到的磨损等级: {float_ranges}")
        
        return jsonify({
            'success': True,
            'data': float_ranges
        }), 200
        
    except Exception as e:
        print(f"获取磨损等级失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e),
            'data': []
        }), 500

def _build_lent_filter_clauses(filters):
    """构建租赁过滤条件的SQL子句和参数"""
    clauses = []
    params = []

    def add_clause(clause, *values):
        clauses.append(clause)
        params.extend(values)

    status = filters.get('status')
    if status and status != 'all':
        add_clause("status = ?", status)

    status_sub = filters.get('status_sub')
    if status_sub and status_sub != 'all':
        add_clause("last_status = ?", status_sub)

    platform = filters.get('platform')
    if platform and platform != 'all':
        add_clause('"from" = ?', platform)

    lenter_name = filters.get('lenter_name')
    if lenter_name:
        add_clause("lenter_name = ?", lenter_name)

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
        clauses.append("lean_start_time BETWEEN ? AND ?")
        params.extend([f"{start_date} 00:00:00", f"{end_date} 23:59:59"])

    where_clause = ""
    if clauses:
        where_clause = " WHERE " + " AND ".join(clauses)

    return where_clause, tuple(params)

@webLentPageV1.route('/getLentDataFiltered', methods=['POST'])
def get_lent_data_filtered():
    """组合查询接口：支持所有过滤条件的分页数据获取"""
    try:
        data = request.get_json() or {}
        filters = data.get('filters', {})
        min_offset = data.get('min', 0)
        max_limit = data.get('max', 20)

        where_clause, params = _build_lent_filter_clauses(filters)

        sql = f"""
        SELECT ID, weapon_name, weapon_type, item_name, weapon_float, float_range,
               price, lenter_name, status, last_status, "from",
               lean_start_time, lean_end_time, total_Lease_Days, max_Lease_Days
        FROM yyyp_lent
        {where_clause}
        ORDER BY lean_start_time DESC
        LIMIT {max_limit} OFFSET {min_offset}
        """

        db = Date_base()
        result = db.execute_query(sql, params)

        if result:
            # 格式化数据为数组格式
            records = []
            for row in result:
                records.append([
                    row[0],   # ID
                    row[1],   # weapon_name
                    row[2],   # weapon_type
                    row[3],   # item_name
                    row[4],   # weapon_float
                    row[5],   # float_range
                    row[6],   # price
                    row[7],   # lenter_name
                    row[8],   # status
                    row[9],   # last_status
                    row[10],  # from
                    row[11],  # lean_start_time
                    row[12],  # lean_end_time
                    row[13],  # total_Lease_Days
                    row[14]   # max_Lease_Days
                ])
            return jsonify(records), 200
        return jsonify([]), 200
    except Exception as e:
        print(f"获取租赁筛选数据失败: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@webLentPageV1.route('/getLentStatsFiltered', methods=['POST'])
def get_lent_stats_filtered():
    """组合查询接口：支持所有过滤条件的统计信息获取"""
    try:
        filters = request.get_json() or {}
        where_clause, params = _build_lent_filter_clauses(filters)

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
        FROM yyyp_lent
        {where_clause}
        """

        db = Date_base()
        result = db.execute_query(sql, params)

        if result and len(result) > 0:
            stats = result[0]
            return jsonify({
                "success": True,
                "totalCount": stats[0],
                "totalAmount": round(float(stats[1]), 2),
                "avgPrice": round(float(stats[2]), 2),
                "totalLeaseDays": stats[3],
                "avgLeaseDays": round(float(stats[4]), 2),
                "rentingCount": stats[5],
                "completedCount": stats[6],
                "cancelledCount": stats[7]
            }), 200

        return jsonify({
            "success": True,
            "totalCount": 0,
            "totalAmount": 0.0,
            "avgPrice": 0.0,
            "totalLeaseDays": 0,
            "avgLeaseDays": 0.0,
            "rentingCount": 0,
            "completedCount": 0,
            "cancelledCount": 0
        }), 200
    except Exception as e:
        print(f"获取租赁筛选统计失败: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@webLentPageV1.route('/searchByTypeAndWear', methods=['POST'])
def searchByTypeAndWear():
    """根据类型和磨损等级搜索租赁记录（支持多选）"""
    try:
        data = request.get_json()
        weapon_types = data.get('weapon_type', [])  # 现在接收数组
        float_ranges = data.get('float_range', [])  # 现在接收数组
        page = data.get('page', 1)
        page_size = data.get('page_size', 20)
        
        # 构建查询条件
        conditions = []
        params = []
        
        # 处理武器类型（多选）
        if weapon_types and len(weapon_types) > 0:
            placeholders = ','.join(['?' for _ in weapon_types])
            conditions.append(f"weapon_type IN ({placeholders})")
            params.extend(weapon_types)
            
        # 处理磨损等级（多选）
        if float_ranges and len(float_ranges) > 0:
            placeholders = ','.join(['?' for _ in float_ranges])
            conditions.append(f"float_range IN ({placeholders})")
            params.extend(float_ranges)
        
        # 如果没有条件，返回空结果
        if not conditions:
            return jsonify({
                'success': True,
                'data': [],
                'total': 0,
                'page': page,
                'page_size': page_size
            }), 200
        
        where_clause = " AND ".join(conditions)
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 查询数据
        db = Date_base()
        
        # 获取总数
        count_sql = f"SELECT COUNT(*) FROM lent WHERE {where_clause}"
        count_result = db.execute_query(count_sql, tuple(params))
        total = count_result[0][0] if count_result else 0
        
        # 获取分页数据
        data_sql = f"""
        SELECT ID, weapon_name, weapon_type, item_name, weapon_float, float_range,
               price, lenter_name, status, last_status, "from", data_user,
               lean_start_time, lean_end_time, total_Lease_Days, max_Lease_Days
        FROM lent
        WHERE {where_clause}
        ORDER BY lean_start_time DESC
        LIMIT ? OFFSET ?
        """
        params.extend([page_size, offset])
        data_result = db.execute_query(data_sql, tuple(params))
        
        # 格式化数据
        records = []
        for row in data_result:
            records.append([
                row[0],   # ID
                row[1],   # weapon_name
                row[2],   # weapon_type
                row[3],   # item_name
                row[4],   # weapon_float
                row[5],   # float_range
                row[6],   # price
                row[7],   # lenter_name
                row[8],   # status
                row[9],   # last_status
                row[10],  # from
                row[11],  # lean_start_time
                row[12],  # lean_end_time
                row[13],  # total_Lease_Days
                row[14]   # max_Lease_Days
            ])
        
        return jsonify({
            'success': True,
            'data': records,
            'total': total,
            'page': page,
            'page_size': page_size
        }), 200
        
    except Exception as e:
        print(f"按类型和磨损等级搜索失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e),
            'data': [],
            'total': 0
        }), 500

@webLentPageV1.route('/getStatsByTypeAndWear', methods=['POST'])
def getStatsByTypeAndWear():
    """获取按类型和磨损等级筛选的统计数据（支持多选）"""
    try:
        data = request.get_json()
        weapon_types = data.get('weapon_type', [])  # 现在接收数组
        float_ranges = data.get('float_range', [])  # 现在接收数组
        
        # 构建查询条件
        conditions = []
        params = []
        
        # 处理武器类型（多选）
        if weapon_types and len(weapon_types) > 0:
            placeholders = ','.join(['?' for _ in weapon_types])
            conditions.append(f"weapon_type IN ({placeholders})")
            params.extend(weapon_types)
            
        # 处理磨损等级（多选）
        if float_ranges and len(float_ranges) > 0:
            placeholders = ','.join(['?' for _ in float_ranges])
            conditions.append(f"float_range IN ({placeholders})")
            params.extend(float_ranges)
        
        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)
        
        db = Date_base()
        
        # 获取统计数据
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
        FROM yyyp_lent 
        {where_clause}
        """
        
        result = db.execute_query(sql, tuple(params))
        
        if result:
            row = result[0]
            stats = {
                'totalCount': row[0],
                'totalAmount': round(row[1], 2),
                'avgPrice': round(row[2], 2),
                'totalLeaseDays': row[3],
                'avgLeaseDays': round(row[4], 2),
                'rentingCount': row[5],
                'completedCount': row[6],
                'cancelledCount': row[7]
            }
        else:
            stats = {
                'totalCount': 0,
                'totalAmount': 0,
                'avgPrice': 0,
                'totalLeaseDays': 0,
                'avgLeaseDays': 0,
                'rentingCount': 0,
                'completedCount': 0,
                'cancelledCount': 0
            }
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        print(f"获取统计数据失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e),
            'data': {}
        }), 500


@webLentPageV1.route('/getPlatformList', methods=['GET'])
def getPlatformList():
    """获取平台来源（from）唯一值，优先 lent，补充 yyyp_lent"""
    try:
        db = Date_base()
        sql = """
        SELECT DISTINCT "from" AS platform
        FROM lent
        WHERE "from" IS NOT NULL AND "from" != ''
        UNION
        SELECT DISTINCT "from" AS platform
        FROM yyyp_lent
        WHERE "from" IS NOT NULL AND "from" != ''
        ORDER BY platform
        """
        result = db.execute_query(sql)
        platforms = [row[0] for row in result or [] if row[0]]
        return jsonify({'success': True, 'data': platforms}), 200
    except Exception as e:
        print(f"获取平台列表失败: {e}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': str(e), 'data': []}), 500


@webLentPageV1.route('/getLenterList', methods=['GET'])
def getLenterList():
    """获取出租用户（lenter_name）唯一值，优先 lent，补充 yyyp_lent"""
    try:
        db = Date_base()
        sql = """
        SELECT DISTINCT lenter_name
        FROM lent
        WHERE lenter_name IS NOT NULL AND lenter_name != ''
        UNION
        SELECT DISTINCT lenter_name
        FROM yyyp_lent
        WHERE lenter_name IS NOT NULL AND lenter_name != ''
        ORDER BY lenter_name
        """
        result = db.execute_query(sql)
        users = [row[0] for row in result or [] if row[0]]
        return jsonify({'success': True, 'data': users}), 200
    except Exception as e:
        print(f"获取用户列表失败: {e}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': str(e), 'data': []}), 500
