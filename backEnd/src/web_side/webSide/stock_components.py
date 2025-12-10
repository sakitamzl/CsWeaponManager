from flask import jsonify, request, Blueprint
from src.db_manager.database import DatabaseManager
import traceback

webStockComponentsV1 = Blueprint('webStockComponentsV1', __name__)

# 组件的classid常量
COMPONENT_CLASSID = '3604678661'


@webStockComponentsV1.route('/steam_ids', methods=['GET'])
def get_steam_ids():
    """从 steam_stockComponents 表获取所有不同的Steam ID列表"""
    try:
        db = DatabaseManager()
        
        # 查询所有不同的 data_user (Steam ID)，并统计每个ID的组件数量
        sql = """
        SELECT data_user, COUNT(*) as item_count
        FROM steam_stockComponents
        WHERE data_user IS NOT NULL AND data_user != ''
        GROUP BY data_user
        ORDER BY data_user
        """
        results = db.execute_query(sql)
        
        steam_ids = []
        for row in results:
            steam_ids.append({
                'steam_id': row[0],
                'item_count': row[1]
            })
        
        return jsonify({
            'success': True,
            'data': steam_ids
        }), 200
        
    except Exception as e:
        print(f"获取Steam ID列表失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'查询失败: {str(e)}'
        }), 500


@webStockComponentsV1.route('/components/<steam_id>', methods=['GET'])
def get_components(steam_id):
    """获取指定用户的库存组件列表 - 从 steam_stockComponents 表读取"""
    try:
        # 获取查询参数
        search_text = request.args.get('search', '')
        weapon_type = request.args.get('weapon_type', '')  # 武器类型筛选
        weapon_level = request.args.get('weapon_level', '')  # 武器等级筛选
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        db = DatabaseManager()
        
        # 构建查询条件
        where_conditions = ["data_user = ?"]
        params = [steam_id]
        
        # 关键词搜索 - 搜索武器名称
        if search_text:
            where_conditions.append("weapon_name LIKE ?")
            params.append(f"%{search_text}%")
        
        # 武器类型筛选
        if weapon_type:
            where_conditions.append("weapon_type = ?")
            params.append(weapon_type)
        
        # 武器等级筛选
        if weapon_level:
            where_conditions.append("weapon_level = ?")
            params.append(weapon_level)
        
        where_clause = " AND ".join(where_conditions)
        
        # 查询数据 - 查询所有字段，包含 steam_hash_name, sticker, pendant, rename
        sql = f"""
        SELECT
            assetid, goods_assetid, classid, item_name, weapon_name,
            float_range, weapon_type, weapon_float, weapon_level, data_user,
            buy_price, yyyp_price, buff_price, order_time, steam_price,
            steam_hash_name, sticker, pendant, rename
        FROM steam_stockComponents
        WHERE {where_clause}
        ORDER BY order_time DESC
        LIMIT ? OFFSET ?
        """
        params.extend([page_size, offset])
        results = db.execute_query(sql, tuple(params))

        # 转换为字典列表
        components = []
        if results:
            for row in results:
                # 安全的浮点数转换函数
                def safe_float(value, default=0.0):
                    if value is None or value == '':
                        return default
                    try:
                        return float(value)
                    except (ValueError, TypeError):
                        return default

                component = {
                    # 基本信息
                    'assetid': row[0],  # 组件ID（库存组件的assetid）
                    'goods_assetid': row[1],  # 物品资产ID（主键，物品的itemId）
                    'component_id': row[1],  # 兼容：使用 goods_assetid 作为 component_id
                    'classid': row[2],
                    'item_name': row[3],  # 物品名称
                    'weapon_name': row[4],  # 武器名称
                    'float_range': row[5],  # 磨损值范围
                    'weapon_type': row[6],  # 武器类型
                    'weapon_float': row[7],  # 武器磨损值/数量
                    'weapon_level': row[8],  # 武器等级

                    # 价格信息
                    'buy_price': safe_float(row[10]),  # 购入价格
                    'yyyp_price': safe_float(row[11]),  # 悠悠价格
                    'buff_price': safe_float(row[12]),  # BUFF价格
                    'steam_price': safe_float(row[14]),  # Steam价格

                    # 时间信息
                    'order_time': row[13],  # 入库时间

                    # 图片和装饰信息
                    'steam_hash_name': row[15],  # Steam市场hash名称
                    'sticker': row[16],  # 印花信息
                    'pendant': row[17],  # 挂件信息
                    'rename': row[18],  # 改名信息

                    # 兼容旧字段
                    'component_name': row[3],
                    'component_type': row[6],
                    'quality': row[8],
                    'quantity': row[7],  # weapon_float 作为数量
                    'unit_cost': safe_float(row[10]),
                    'total_cost': safe_float(row[10]),
                    'source': '库存',
                    'purchase_date': row[13],
                    'status': '库存中',
                    'status_desc': ''
                }
                components.append(component)
        
        # 获取总数
        count_params = params[:-2]  # 去掉limit和offset参数
        count_sql = f"SELECT COUNT(*) FROM steam_stockComponents WHERE {where_clause}"
        count_result = db.execute_query(count_sql, tuple(count_params))
        total = count_result[0][0] if count_result else 0
        
        return jsonify({
            'success': True,
            'data': components,
            'total': total,
            'page': page,
            'page_size': page_size
        }), 200
        
    except Exception as e:
        print(f"查询库存组件失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'查询失败: {str(e)}'
        }), 500


@webStockComponentsV1.route('/components/stats/<steam_id>', methods=['GET'])
def get_components_stats(steam_id):
    """获取库存组件统计信息 - 从 steam_stockComponents 表读取"""
    try:
        db = DatabaseManager()
        
        # 统计总数和各种价格总和
        stats_sql = f"""
        SELECT 
            COUNT(*) as total_count,
            SUM(CAST(buy_price AS REAL)) as total_buy_price,
            SUM(CAST(yyyp_price AS REAL)) as total_yyyp_price,
            SUM(CAST(buff_price AS REAL)) as total_buff_price,
            SUM(CAST(steam_price AS REAL)) as total_steam_price
        FROM steam_stockComponents
        WHERE data_user = ?
        """
        stats_result = db.execute_query(stats_sql, (steam_id,))
        
        total_count = 0
        total_cost = 0
        total_yyyp_price = 0
        total_buff_price = 0
        total_steam_price = 0
        
        if stats_result and stats_result[0][0] is not None:
            total_count = stats_result[0][0] or 0
            total_cost = round(stats_result[0][1] or 0, 2)
            total_yyyp_price = round(stats_result[0][2] or 0, 2)
            total_buff_price = round(stats_result[0][3] or 0, 2)
            total_steam_price = round(stats_result[0][4] or 0, 2)
        
        return jsonify({
            'success': True,
            'data': {
                'totalCount': total_count,
                'totalCost': total_cost,
                'totalYYYPPrice': total_yyyp_price,
                'totalBuffPrice': total_buff_price,
                'totalSteamPrice': total_steam_price
            }
        }), 200
        
    except Exception as e:
        print(f"查询统计信息失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'查询失败: {str(e)}'
        }), 500


@webStockComponentsV1.route('/components/grouped/<steam_id>', methods=['GET'])
def get_components_grouped(steam_id):
    """
    按物品组合统计（聚合）库存组件，例如：
    “2022年里约热内卢锦标赛炙热沙城 II 纪念包 x100”

    支持参数：
    - search: 模糊匹配 item_name
    - page, page_size: 分页
    - order_by: 排序字段，支持 count(默认)、name、buy_price、yyyp_price、buff_price、steam_price
    """
    try:
        search_text = request.args.get('search', '')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        order_by = (request.args.get('order_by') or 'count').lower()

        offset = (page - 1) * page_size

        db = DatabaseManager()

        where_conditions = ["data_user = ?"]
        params = [steam_id]

        if search_text:
            where_conditions.append("item_name LIKE ?")
            params.append(f"%{search_text}%")

        where_clause = " AND ".join(where_conditions)

        # 排序字段映射
        order_map = {
            'count': 'item_count DESC, item_name ASC',
            'name': 'item_name ASC',
            'buy_price': 'total_buy_price DESC',
            'yyyp_price': 'total_yyyp_price DESC',
            'buff_price': 'total_buff_price DESC',
            'steam_price': 'total_steam_price DESC'
        }
        order_clause = order_map.get(order_by, order_map['count'])

        sql = f"""
        SELECT
            item_name,
            steam_hash_name,
            weapon_name,
            weapon_type,
            weapon_level,
            float_range,
            COUNT(*) AS item_count,
            SUM(CAST(weapon_float AS REAL)) AS total_quantity,
            SUM(CAST(buy_price AS REAL)) AS total_buy_price,
            SUM(CAST(yyyp_price AS REAL)) AS total_yyyp_price,
            SUM(CAST(buff_price AS REAL)) AS total_buff_price,
            SUM(CAST(steam_price AS REAL)) AS total_steam_price,
            GROUP_CONCAT(goods_assetid) AS goods_assetids,
            GROUP_CONCAT(weapon_float) AS weapon_floats,
            GROUP_CONCAT(buy_price) AS buy_prices,
            GROUP_CONCAT(yyyp_price) AS yyyp_prices,
            GROUP_CONCAT(buff_price) AS buff_prices,
            GROUP_CONCAT(steam_price) AS steam_prices,
            GROUP_CONCAT(sticker, '|||') AS stickers,
            GROUP_CONCAT(pendant, '|||') AS pendants,
            GROUP_CONCAT(rename, '|||') AS renames
        FROM steam_stockComponents
        WHERE {where_clause}
        GROUP BY item_name, steam_hash_name, weapon_name, weapon_type, weapon_level, float_range
        ORDER BY {order_clause}
        LIMIT ? OFFSET ?
        """
        params_with_limit = params + [page_size, offset]
        rows = db.execute_query(sql, tuple(params_with_limit))

        grouped_list = []
        for row in rows or []:
            # 安全地处理可能为None的字段
            goods_assetids = str(row[12]).split(',') if row[12] and row[12] != 'None' else []
            weapon_floats = str(row[13]).split(',') if row[13] and row[13] != 'None' else []
            buy_prices = str(row[14]).split(',') if row[14] and row[14] != 'None' else []
            yyyp_prices = str(row[15]).split(',') if row[15] and row[15] != 'None' else []
            buff_prices = str(row[16]).split(',') if row[16] and row[16] != 'None' else []
            steam_prices = str(row[17]).split(',') if row[17] and row[17] != 'None' else []
            stickers = str(row[18]).split('|||') if row[18] and row[18] != 'None' else []
            pendants = str(row[19]).split('|||') if row[19] and row[19] != 'None' else []
            renames = str(row[20]).split('|||') if row[20] and row[20] != 'None' else []
            
            grouped_list.append({
                "item_name": row[0],
                "steam_hash_name": row[1],
                "weapon_name": row[2],
                "weapon_type": row[3],
                "weapon_level": row[4],
                "float_range": row[5],
                "item_count": row[6] or 0,
                "total_quantity": round(row[7] or 0, 2),
                "total_buy_price": round(row[8] or 0, 2),
                "total_yyyp_price": round(row[9] or 0, 2),
                "total_buff_price": round(row[10] or 0, 2),
                "total_steam_price": round(row[11] or 0, 2),
                "goods_assetids": goods_assetids,
                "weapon_floats": weapon_floats,
                "buy_prices": buy_prices,
                "yyyp_prices": yyyp_prices,
                "buff_prices": buff_prices,
                "steam_prices": steam_prices,
                "stickers": stickers,
                "pendants": pendants,
                "renames": renames
            })

        # 总记录数
        count_sql = f"""
        SELECT COUNT(*) FROM (
            SELECT 1
            FROM steam_stockComponents
            WHERE {where_clause}
            GROUP BY item_name, steam_hash_name, weapon_name, weapon_type, weapon_level, float_range
        ) AS grouped_items
        """
        total_rows = db.execute_query(count_sql, tuple(params))
        total = total_rows[0][0] if total_rows else 0

        return jsonify({
            "success": True,
            "data": grouped_list,
            "total": total,
            "page": page,
            "page_size": page_size
        })

    except Exception as e:
        import traceback
        print(f"❌ 组合查询失败 - steam_id: {steam_id}, 错误: {str(e)}")
        print(f"错误详情: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": f"组合查询失败: {str(e)}",
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

@webStockComponentsV1.route('/components/time-range/<steam_id>/<start_date>/<end_date>', methods=['GET'])
def get_components_by_time_range(steam_id, start_date, end_date):
    """按时间范围搜索库存组件 - 从 steam_stockComponents 表读取"""
    try:
        db = DatabaseManager()
        
        sql = f"""
        SELECT
            assetid, goods_assetid, classid, item_name, weapon_name,
            float_range, weapon_type, weapon_float, weapon_level, data_user,
            buy_price, yyyp_price, buff_price, order_time, steam_price
        FROM steam_stockComponents
        WHERE data_user = ?
            AND DATE(order_time) BETWEEN ? AND ?
        ORDER BY order_time DESC
        """
        
        results = db.execute_query(sql, (steam_id, start_date, end_date))
        
        # 转换为字典列表
        components = []
        if results:
            for row in results:
                def safe_float(value, default=0.0):
                    if value is None or value == '':
                        return default
                    try:
                        return float(value)
                    except (ValueError, TypeError):
                        return default
                
                component = {
                    'component_id': row[0],
                    'item_name': row[3],
                    'weapon_name': row[4],
                    'float_range': row[5],
                    'weapon_type': row[6],
                    'weapon_float': row[7],
                    'weapon_level': row[8],
                    'buy_price': safe_float(row[10]),
                    'yyyp_price': safe_float(row[11]),
                    'buff_price': safe_float(row[12]),
                    'steam_price': safe_float(row[14]),
                    'order_time': row[13],
                    'component_name': row[3],
                    'component_type': row[6],
                    'quality': row[8],
                    'quantity': row[7],
                    'unit_cost': safe_float(row[10]),
                    'total_cost': safe_float(row[10]),
                    'source': '库存',
                    'purchase_date': row[13],
                    'status': '库存中',
                    'status_desc': ''
                }
                components.append(component)
        
        return jsonify({
            'success': True,
            'data': components,
            'total': len(components)
        }), 200
        
    except Exception as e:
        print(f"按时间范围搜索失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'查询失败: {str(e)}'
        }), 500


@webStockComponentsV1.route('/components/use/<component_id>', methods=['POST'])
def use_component(component_id):
    """使用组件"""
    try:
        # TODO: 实现使用组件的逻辑
        # 可能需要更新if_inventory字段或添加使用记录
        
        return jsonify({
            'success': True,
            'message': f'组件 {component_id} 使用成功'
        }), 200
        
    except Exception as e:
        print(f"使用组件失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'操作失败: {str(e)}'
        }), 500


@webStockComponentsV1.route('/components/sell/<component_id>', methods=['POST'])
def sell_component(component_id):
    """出售组件"""
    try:
        # TODO: 实现出售组件的逻辑
        # 可能需要更新if_inventory字段或添加出售记录
        
        return jsonify({
            'success': True,
            'message': f'组件 {component_id} 出售成功'
        }), 200
        
    except Exception as e:
        print(f"出售组件失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'操作失败: {str(e)}'
        }), 500


@webStockComponentsV1.route('/components/detail/<component_id>', methods=['GET'])
def get_component_detail(component_id):
    """获取组件详细信息 - 从 steam_stockComponents 表读取"""
    try:
        db = DatabaseManager()
        
        sql = f"""
        SELECT
            assetid, goods_assetid, classid, item_name, weapon_name,
            float_range, weapon_type, weapon_float, weapon_level, data_user,
            buy_price, yyyp_price, buff_price, order_time, steam_price
        FROM steam_stockComponents
        WHERE goods_assetid = ?
        """
        
        results = db.execute_query(sql, (component_id,))
        
        if not results or len(results) == 0:
            return jsonify({
                'success': False,
                'error': '组件不存在'
            }), 404
        
        row = results[0]
        
        def safe_float(value, default=0.0):
            if value is None or value == '':
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                return default
        
        component_detail = {
            'component_id': row[0],
            'item_name': row[3],
            'weapon_name': row[4],
            'float_range': row[5],
            'weapon_type': row[6],
            'weapon_float': row[7],
            'weapon_level': row[8],
            'buy_price': safe_float(row[10]),
            'yyyp_price': safe_float(row[11]),
            'buff_price': safe_float(row[12]),
            'steam_price': safe_float(row[14]),
            'order_time': row[13],
            # 兼容旧字段
            'assetid': row[0],
            'instanceid': row[1],
            'classid': row[2],
            'component_name': row[3],
            'component_type': row[6],
            'quality': row[8],
            'quantity': row[7],
            'unit_cost': safe_float(row[10]),
            'total_cost': safe_float(row[10]),
            'source': '库存',
            'purchase_date': row[13],
            'status': '库存中',
            'status_desc': '',
            'data_user': row[9]
        }
        
        return jsonify({
            'success': True,
            'data': component_detail
        }), 200
        
    except Exception as e:
        print(f"查询组件详情失败: {e}")
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'查询失败: {str(e)}'
        }), 500


@webStockComponentsV1.route('/update/buy_price/<steam_id>/<goods_assetid>', methods=['PUT'])
def update_buy_price(steam_id, goods_assetid):
    """
    更新指定组件的购入价格

    参数:
        steam_id: Steam用户ID (对应data_user字段)
        goods_assetid: 物品资产ID（主键）

    请求体:
    {
        "buy_price": "100.50"
    }

    返回:
    {
        "success": True,
        "message": "价格更新成功"
    }
    """
    try:
        data = request.get_json()

        if not data or 'buy_price' not in data:
            return jsonify({
                'success': False,
                'message': '缺少 buy_price 参数'
            }), 400

        buy_price = data.get('buy_price')

        # 验证价格格式
        try:
            price_float = float(buy_price)
            if price_float < 0:
                return jsonify({
                    'success': False,
                    'message': '价格不能为负数'
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'message': '价格格式不正确'
            }), 400

        db = DatabaseManager()

        # 检查记录是否存在
        check_sql = """
        SELECT COUNT(*) FROM steam_stockComponents
        WHERE goods_assetid = ? AND data_user = ?
        """
        check_result = db.execute_query(check_sql, (goods_assetid, steam_id))

        if not check_result or check_result[0][0] == 0:
            return jsonify({
                'success': False,
                'message': '未找到该组件记录'
            }), 404

        # 更新价格
        update_sql = """
        UPDATE steam_stockComponents
        SET buy_price = ?
        WHERE goods_assetid = ? AND data_user = ?
        """

        db.execute_update(update_sql, (str(buy_price), goods_assetid, steam_id))

        print(f"✅ 价格更新成功 - goods_assetid: {goods_assetid}, steam_id: {steam_id}, buy_price: {buy_price}")

        return jsonify({
            'success': True,
            'message': '价格更新成功'
        })

    except Exception as e:
        print(f"❌ 更新价格失败 - goods_assetid: {goods_assetid}, steam_id: {steam_id}")
        print(f"错误详情: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@webStockComponentsV1.route('/auto_fill_prices/<steam_id>', methods=['POST'])
def auto_fill_prices(steam_id):
    """
    自动填充组件的购入价格
    
    参数:
        steam_id: Steam用户ID (对应data_user字段)
    
    返回:
    {
        "success": True,
        "data": {
            "total_count": 总数,
            "filled_count": 成功填充的数量,
            "already_filled_count": 已有价格的数量,
            "not_found_count": 未找到价格的数量
        }
    }
    """
    try:
        db = DatabaseManager()
        
        # 查询该用户的所有组件 - 包含 steam_hash_name
        query_sql = """
        SELECT goods_assetid, item_name, weapon_float, buy_price, steam_hash_name
        FROM steam_stockComponents
        WHERE data_user = ?
        """
        components = db.execute_query(query_sql, (steam_id,))

        if not components:
            return jsonify({
                'success': True,
                'data': {
                    'total_count': 0,
                    'filled_count': 0,
                    'already_filled_count': 0,
                    'not_found_count': 0
                },
                'message': '该用户没有组件记录'
            }), 200

        # 统计数据
        total_count = len(components)
        filled_count = 0
        already_filled_count = 0
        not_found_count = 0

        # 第一步：处理有 float 值的组件（精确匹配）
        float_components = []
        no_float_components = []
        
        for component in components:
            goods_assetid = component[0]
            item_name = component[1]
            weapon_float = component[2]
            current_buy_price = component[3]
            steam_hash_name = component[4]

            # 如果已有价格，跳过
            if current_buy_price not in [None, '', 'None', '0', '0.0', '0.00']:
                already_filled_count += 1
                continue

            # 分类：有 float 值的和没有 float 值的
            if weapon_float and weapon_float not in ['', '0', '0.0', 'None']:
                float_components.append((goods_assetid, item_name, weapon_float, steam_hash_name))
            else:
                no_float_components.append((goods_assetid, item_name, steam_hash_name))

        # 处理有 float 值的组件（逐个精确匹配）
        for goods_assetid, item_name, weapon_float, steam_hash_name in float_components:
            buy_price = None
            try:
                float_value = float(weapon_float)
                # 精确匹配：item_name + weapon_float
                exact_price_sql = """
                SELECT price
                FROM buy
                WHERE item_name = ? AND ABS(CAST(weapon_float AS REAL) - ?) < 0.0001
                ORDER BY order_time DESC
                LIMIT 1
                """
                exact_result = db.execute_query(exact_price_sql, (item_name, float_value))

                if exact_result and exact_result[0][0] is not None:
                    buy_price = exact_result[0][0]
                    print(f"✅ 精确匹配（磨损值） - goods_assetid: {goods_assetid}, item_name: {item_name}, float: {weapon_float}, price: {buy_price}")
            except (ValueError, TypeError):
                pass

            # 如果找到价格，更新
            if buy_price is not None:
                update_sql = """
                UPDATE steam_stockComponents
                SET buy_price = ?
                WHERE goods_assetid = ? AND data_user = ?
                """
                affected_rows = db.execute_update(update_sql, (str(buy_price), goods_assetid, steam_id))
                if affected_rows > 0:
                    filled_count += 1
                else:
                    not_found_count += 1
                    print(f"⚠️  更新失败 - goods_assetid: {goods_assetid}, item_name: {item_name}")
            else:
                not_found_count += 1
                print(f"⚠️  未找到价格（float匹配） - goods_assetid: {goods_assetid}, item_name: {item_name}, float: {weapon_float}")

        # 第二步：批量处理没有 float 值的组件（使用 steam_hash_name）
        if no_float_components:
            # 收集所有唯一的 steam_hash_name
            hash_names = list(set([comp[2] for comp in no_float_components if comp[2] and comp[2] not in ['', 'None']]))
            
            if hash_names:
                # 批量查询：使用 steam_hash_name 获取平均价格
                placeholders = ','.join(['?' for _ in hash_names])
                batch_price_sql = f"""
                SELECT steam_hash_name, AVG(CAST(price AS REAL)) as avg_price
                FROM buy
                WHERE steam_hash_name IN ({placeholders})
                  AND price IS NOT NULL 
                  AND price != ''
                  AND steam_hash_name IS NOT NULL
                  AND steam_hash_name != ''
                GROUP BY steam_hash_name
                """
                price_results = db.execute_query(batch_price_sql, tuple(hash_names))
                
                # 构建 hash_name -> price 的映射
                price_map = {}
                if price_results:
                    for row in price_results:
                        hash_name = row[0]
                        avg_price = round(row[1], 2) if row[1] else None
                        if avg_price:
                            price_map[hash_name] = avg_price
                
                print(f"📦 批量查询完成 - 找到 {len(price_map)} 个 hash_name 的价格")
                
                # 批量更新价格
                for goods_assetid, item_name, steam_hash_name in no_float_components:
                    if steam_hash_name and steam_hash_name in price_map:
                        buy_price = price_map[steam_hash_name]
                        update_sql = """
                        UPDATE steam_stockComponents
                        SET buy_price = ?
                        WHERE goods_assetid = ? AND data_user = ?
                        """
                        affected_rows = db.execute_update(update_sql, (str(buy_price), goods_assetid, steam_id))
                        if affected_rows > 0:
                            filled_count += 1
                            print(f"✅ 批量匹配（hash_name） - goods_assetid: {goods_assetid}, hash_name: {steam_hash_name}, price: {buy_price}")
                        else:
                            not_found_count += 1
                            print(f"⚠️  更新失败 - goods_assetid: {goods_assetid}, hash_name: {steam_hash_name}")
                    else:
                        not_found_count += 1
                        if not steam_hash_name or steam_hash_name in ['', 'None']:
                            print(f"⚠️  缺少 hash_name - goods_assetid: {goods_assetid}, item_name: {item_name}")
                        else:
                            print(f"⚠️  未找到价格（hash_name） - goods_assetid: {goods_assetid}, hash_name: {steam_hash_name}")
        
        print(f"📊 自动填充价格完成 - steamId: {steam_id}, 总数: {total_count}, 成功填充: {filled_count}, 已有价格: {already_filled_count}, 未找到: {not_found_count}")
        
        return jsonify({
            'success': True,
            'data': {
                'total_count': total_count,
                'filled_count': filled_count,
                'already_filled_count': already_filled_count,
                'not_found_count': not_found_count
            },
            'message': f'价格自动填充完成！总计: {total_count}, 成功填充: {filled_count}, 已有价格: {already_filled_count}, 未找到: {not_found_count}'
        }), 200
        
    except Exception as e:
        print(f"❌ 自动填充价格失败 - steam_id: {steam_id}")
        print(f"错误详情: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'自动填充价格失败: {str(e)}'
        }), 500


@webStockComponentsV1.route('/fill_reference_price/<steam_id>/<source>', methods=['POST'])
def fill_reference_price(steam_id, source):
    """
    根据 weapon_classID 表中的价格，填充/更新库存组件的悠悠有品或BUFF参考价。

    Args:
        steam_id: Steam 用户 ID
        source: 价格来源，支持 'yyyp'（悠悠有品）或 'buff'
    """
    source = (source or '').lower()
    if source not in ('yyyp', 'buff'):
        return jsonify({
            'success': False,
            'message': "source 参数只能是 'yyyp' 或 'buff'"
        }), 400

    try:
        db = DatabaseManager()

        component_column = 'yyyp_price' if source == 'yyyp' else 'buff_price'
        weapon_column = 'yyyp_Price' if source == 'yyyp' else 'buff_Price'

        # 取出当前账号下所有带 steam_hash_name 的组件
        component_sql = f"""
        SELECT goods_assetid, steam_hash_name, {component_column}
        FROM steam_stockComponents
        WHERE data_user = ?
          AND steam_hash_name IS NOT NULL
          AND steam_hash_name != ''
        """
        components = db.execute_query(component_sql, (steam_id,))

        if not components:
            return jsonify({
                'success': True,
                'message': '该账号没有可更新的组件或缺少 steam_hash_name',
                'data': {
                    'total': 0,
                    'matched': 0,
                    'updated': 0,
                    'unchanged': 0,
                    'missing_price': 0
                }
            })

        steam_hash_names = list({row[1] for row in components if row[1]})
        if not steam_hash_names:
            return jsonify({
                'success': True,
                'message': '组件缺少 steam_hash_name，无法匹配价格',
                'data': {
                    'total': len(components),
                    'matched': 0,
                    'updated': 0,
                    'unchanged': 0,
                    'missing_price': len(components)
                }
            })

        placeholders = ','.join(['?'] * len(steam_hash_names))
        weapon_sql = f"""
        SELECT steam_hash_name, {weapon_column}
        FROM weapon_classID
        WHERE steam_hash_name IN ({placeholders})
        """
        weapon_rows = db.execute_query(weapon_sql, tuple(steam_hash_names))

        price_map = {}
        for row in weapon_rows or []:
            hash_name = row[0]
            price_value = row[1]
            if hash_name and price_value not in [None, '', 'None']:
                price_map[hash_name] = str(price_value)

        matched = len(price_map)
        updated = 0
        unchanged = 0
        missing_price = 0

        update_sql = f"""
        UPDATE steam_stockComponents
        SET {component_column} = ?
        WHERE goods_assetid = ?
        """

        for goods_assetid, hash_name, current_price in components:
            target_price = price_map.get(hash_name)
            if not target_price:
                missing_price += 1
                continue

            current_price_str = '' if current_price is None else str(current_price)
            if current_price_str == target_price:
                unchanged += 1
                continue

            db.execute_update(update_sql, (target_price, goods_assetid))
            updated += 1

        total = len(components)
        message = f"{'悠悠有品' if source == 'yyyp' else 'BUFF'}价格同步完成：总计 {total}，匹配 {matched}，更新 {updated}，保持不变 {unchanged}，缺少价格 {missing_price}"

        return jsonify({
            'success': True,
            'message': message,
            'data': {
                'total': total,
                'matched': matched,
                'updated': updated,
                'unchanged': unchanged,
                'missing_price': missing_price
            }
        })

    except Exception as e:
        print(f"❌ 同步参考价格失败 - steam_id: {steam_id}, source: {source}, 错误: {str(e)}")
        print(f"错误详情: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f"同步参考价格失败: {str(e)}"
        }), 500