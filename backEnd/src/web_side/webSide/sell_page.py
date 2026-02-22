from flask import jsonify, request, Blueprint
from src.execution_db import Date_base
from src.db_manager.index.model.sell import SellModel

webSellPageV1 = Blueprint('webSellPageV1', __name__)

@webSellPageV1.route('/getWeaponTypes', methods=['GET'])
def getWeaponTypes():
    """获取所有武器类型的唯一值（按优先级排序）"""
    try:
        db = Date_base()
        sql = """
        SELECT DISTINCT weapon_type 
        FROM sell 
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
        success, result = db.select(sql)
        
        weapon_types = []
        if success and result:
            for row in result:
                if row[0]:  # 确保不是空值
                    weapon_types.append(row[0])
        
        return jsonify({
            'success': True,
            'data': weapon_types
        }), 200
        
    except Exception as e:
        print(f"获取武器类型失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e),
            'data': []
        }), 500

@webSellPageV1.route('/getStatusList', methods=['GET'])
def getStatusList():
    """获取所有状态的唯一值"""
    try:
        db = Date_base()
        sql = """
        SELECT DISTINCT status 
        FROM sell 
        WHERE status IS NOT NULL AND status != '' 
        ORDER BY 
            CASE status
                WHEN '已完成' THEN 1
                WHEN '待收货' THEN 2
                WHEN '已取消' THEN 3
                ELSE 999
            END,
            status
        """
        success, result = db.select(sql)
        
        status_list = []
        if success and result:
            for row in result:
                if row[0]:  # 确保不是空值
                    status_list.append(row[0])
        
        return jsonify({
            'success': True,
            'data': status_list
        }), 200
        
    except Exception as e:
        print(f"获取状态列表失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e),
            'data': []
        }), 500

@webSellPageV1.route('/getStatusSubList', methods=['GET'])
def getStatusSubList():
    """根据指定状态获取对应的子状态唯一值列表（销售表 sell.status_sub）"""
    try:
        status = request.args.get('status', '').strip()
        db = Date_base()
        if not status or status == 'all':
            sql = """
            SELECT DISTINCT status_sub
            FROM sell
            WHERE status_sub IS NOT NULL
              AND status_sub != ''
            ORDER BY status_sub
            """
        else:
            safe_status = status.replace("'", "''")
            sql = f"""
            SELECT DISTINCT status_sub
            FROM sell
            WHERE status = '{safe_status}'
              AND status_sub IS NOT NULL
              AND status_sub != ''
            ORDER BY status_sub
            """
        success, result = db.select(sql)
        sub_list = []
        if success and result:
            for row in result:
                if row[0]:
                    sub_list.append(row[0])
        return jsonify({'success': True, 'data': sub_list}), 200
    except Exception as e:
        print(f"获取销售子状态失败: {e}")
        return jsonify({'success': False, 'message': str(e), 'data': []}), 500
@webSellPageV1.route('/getFloatRanges', methods=['GET'])
def getFloatRanges():
    """获取所有磨损等级的唯一值（优先显示主要磨损等级）"""
    try:
        db = Date_base()
        sql = """
        SELECT DISTINCT float_range 
        FROM sell 
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
        success, result = db.select(sql)
        
        float_ranges = []
        if success and result:
            for row in result:
                if row[0]:  # 确保不是空值
                    float_ranges.append(row[0])
        
        return jsonify({
            'success': True,
            'data': float_ranges
        }), 200
        
    except Exception as e:
        print(f"获取磨损等级失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e),
            'data': []
        }), 500

@webSellPageV1.route('/searchByTypeAndWear', methods=['POST'])
def searchByTypeAndWear():
    """根据类型和磨损等级搜索销售记录（支持多选）"""
    try:
        data = request.get_json() or {}
        weapon_types = data.get('weapon_type', [])
        float_ranges = data.get('float_range', [])
        page = max(int(data.get('page', 1)), 1)
        page_size = max(int(data.get('page_size', 20)), 1)

        if isinstance(weapon_types, str):
            weapon_types = [weapon_types]
        if isinstance(float_ranges, str):
            float_ranges = [float_ranges]

        conditions = []
        params = []

        if weapon_types:
            placeholders = ','.join(['?' for _ in weapon_types])
            conditions.append(f"weapon_type IN ({placeholders})")
            params.extend(weapon_types)

        if float_ranges:
            placeholders = ','.join(['?' for _ in float_ranges])
            conditions.append(f"float_range IN ({placeholders})")
            params.extend(float_ranges)

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        offset = (page - 1) * page_size

        db = Date_base()

        where_clause = " AND ".join(conditions) if conditions else ""

        total = SellModel.count(where_clause, tuple(params))

        records = SellModel.find_all(where_clause, tuple(params), limit=page_size, offset=offset)

        data = []
        for record in records:
            data.append([
                record.ID,
                record.weapon_name,
                record.weapon_type,
                record.item_name,
                record.weapon_float,
                record.float_range,
                record.price,
                record.price_original,
                record.buyer_name,
                record.status,
                record.status_sub,
                getattr(record, 'from', None),
                record.order_time,
                record.steam_id,
                getattr(record, 'st', None),
                getattr(record, 'sou', None),
            ])

        return jsonify({
            'success': True,
            'data': data,
            'total': total,
            'page': page,
            'page_size': page_size
        }), 200

    except Exception as e:
        print(f"按类型和磨损等级搜索失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e),
            'data': [],
            'total': 0
        }), 500

@webSellPageV1.route('/getStatsByTypeAndWear', methods=['POST'])
def getStatsByTypeAndWear():
    """获取按类型和磨损等级筛选的统计数据"""
    try:
        data = request.get_json() or {}
        weapon_types = data.get('weapon_type', [])
        float_ranges = data.get('float_range', [])

        if isinstance(weapon_types, str):
            weapon_types = [weapon_types]
        if isinstance(float_ranges, str):
            float_ranges = [float_ranges]

        conditions = []
        params = []

        if weapon_types:
            placeholders = ','.join(['?' for _ in weapon_types])
            conditions.append(f"weapon_type IN ({placeholders})")
            params.extend(weapon_types)

        if float_ranges:
            placeholders = ','.join(['?' for _ in float_ranges])
            conditions.append(f"float_range IN ({placeholders})")
            params.extend(float_ranges)

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        db = Date_base()

        sql = f"""
        SELECT 
            COUNT(*) as total_count,
            COALESCE(SUM(price), 0) as total_amount,
            COALESCE(AVG(price), 0) as avg_price,
            COUNT(CASE WHEN status = '已完成' THEN 1 END) as completed_count,
            COUNT(CASE WHEN status = '已取消' THEN 1 END) as cancelled_count,
            COUNT(CASE WHEN status = '待收货' THEN 1 END) as pending_count
        FROM sell
        {where_clause}
        """

        result = db.execute_query(sql, tuple(params)) or []

        if result:
            row = result[0]
            stats = {
                'totalCount': row[0],
                'totalAmount': round(row[1], 2),
                'avgPrice': round(row[2], 2),
                'completedCount': row[3],
                'cancelledCount': row[4],
                'pendingCount': row[5]
            }
        else:
            stats = {
                'totalCount': 0,
                'totalAmount': 0,
                'avgPrice': 0,
                'completedCount': 0,
                'cancelledCount': 0,
                'pendingCount': 0
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
