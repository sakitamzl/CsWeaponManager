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


@webStockComponentsV1.route('/auto_fill_prices/<steam_id>', methods=['POST'])
def auto_fill_prices(steam_id):
    """
    自动填充组件的购入价格

    参数:
        steam_id: Steam用户ID (对应data_user字段)

    逻辑:
        1. 优先通过 goods_assetid 匹配 steam_inventory 表的 assetid 获取 buy_price（不管有没有磨损值）
        2. 如果匹配不到，对于有 float 值的组件，使用 steam_hash_name + weapon_float 精确匹配 buy 表
        3. 对于没有 float 值的组件，使用 steam_hash_name 批量查询 buy 表的平均价格

    返回:
    {
        "success": True,
        "data": {
            "total_count": 总数,
            "filled_count": 成功填充的数量,
            "already_filled_count": 已有价格的数量,
            "not_found_count": 未找到价格的数量,
            "from_inventory_count": 从库存表匹配的数量
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
                    'not_found_count': 0,
                    'from_inventory_count': 0
                },
                'message': '该用户没有组件记录'
            }), 200

        # 统计数据
        total_count = len(components)
        filled_count = 0
        already_filled_count = 0
        not_found_count = 0
        from_inventory_count = 0  # 从库存表匹配的数量

        # 第一步：优先从 steam_inventory 表中获取价格（不管有没有磨损值，不管是否已有价格）
        # 批量查询所有 goods_assetid 对应的 buy_price
        assetids = [comp[0] for comp in components]  # 获取所有 goods_assetid
        inventory_price_map = {}

        if assetids:
            placeholders = ','.join(['?' for _ in assetids])
            inventory_price_sql = f"""
            SELECT assetid, buy_price
            FROM steam_inventory
            WHERE assetid IN ({placeholders})
              AND buy_price IS NOT NULL
              AND buy_price != ''
              AND buy_price != 'None'
              AND CAST(buy_price AS REAL) > 0
            """
            inventory_results = db.execute_query(inventory_price_sql, tuple(assetids))

            if inventory_results:
                for row in inventory_results:
                    assetid = row[0]
                    buy_price = row[1]
                    inventory_price_map[assetid] = buy_price

                print(f"📦 从库存表查询完成 - 找到 {len(inventory_price_map)} 个 assetid 的价格")

        # 第二步：处理所有组件
        float_components = []
        no_float_components = []

        for component in components:
            goods_assetid = component[0]
            item_name = component[1]
            weapon_float = component[2]
            current_buy_price = component[3]
            steam_hash_name = component[4]

            # 优先从库存表获取价格（不管是否已有价格）
            if goods_assetid in inventory_price_map:
                buy_price = inventory_price_map[goods_assetid]

                # 检查是否需要更新（价格不同才更新）
                current_price_str = '' if current_buy_price is None else str(current_buy_price)
                new_price_str = str(buy_price)

                if current_price_str == new_price_str:
                    # 价格相同，不需要更新
                    already_filled_count += 1
                    from_inventory_count += 1
                    print(f"ℹ️  价格已是最新 - goods_assetid: {goods_assetid}, item_name: {item_name}, price: {buy_price}")
                else:
                    # 价格不同，需要更新
                    update_sql = """
                    UPDATE steam_stockComponents
                    SET buy_price = ?
                    WHERE goods_assetid = ? AND data_user = ?
                    """
                    affected_rows = db.execute_update(update_sql, (str(buy_price), goods_assetid, steam_id))
                    if affected_rows > 0:
                        filled_count += 1
                        from_inventory_count += 1
                        print(f"✅ 从库存表匹配 - goods_assetid: {goods_assetid}, item_name: {item_name}, old_price: {current_buy_price}, new_price: {buy_price}")
                continue

            # 如果已有价格且库存表没有匹配到，跳过
            if current_buy_price not in [None, '', 'None', '0', '0.0', '0.00']:
                already_filled_count += 1
                continue

            # 如果库存表没有，分类到 float 或 no_float 组件
            if weapon_float and weapon_float not in ['', '0', '0.0', 'None']:
                float_components.append((goods_assetid, item_name, weapon_float, steam_hash_name))
            else:
                no_float_components.append((goods_assetid, item_name, steam_hash_name))

        # 第三步：处理有 float 值的组件（逐个精确匹配 buy 表，仅使用 steam_hash_name）
        for goods_assetid, item_name, weapon_float, steam_hash_name in float_components:
            buy_price = None
            try:
                float_value = float(weapon_float)
                # 精确匹配：steam_hash_name + weapon_float
                if steam_hash_name and steam_hash_name not in ['', 'None']:
                    exact_price_sql = """
                    SELECT price
                    FROM buy
                    WHERE steam_hash_name = ? AND ABS(CAST(weapon_float AS REAL) - ?) < 0.0001
                    ORDER BY order_time DESC
                    LIMIT 1
                    """
                    exact_result = db.execute_query(exact_price_sql, (steam_hash_name, float_value))

                    if exact_result and exact_result[0][0] is not None:
                        buy_price = exact_result[0][0]
                        print(f"✅ 精确匹配（磨损值） - goods_assetid: {goods_assetid}, hash_name: {steam_hash_name}, float: {weapon_float}, price: {buy_price}")
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

        # 第四步：批量处理没有 float 值的组件（使用 steam_hash_name 查询 buy 表）
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

        print(f"📊 自动填充价格完成 - steamId: {steam_id}, 总数: {total_count}, 成功填充: {filled_count} (库存表: {from_inventory_count}), 已有价格: {already_filled_count}, 未找到: {not_found_count}")

        return jsonify({
            'success': True,
            'data': {
                'total_count': total_count,
                'filled_count': filled_count,
                'already_filled_count': already_filled_count,
                'not_found_count': not_found_count,
                'from_inventory_count': from_inventory_count
            },
            'message': f'价格自动填充完成！总计: {total_count}, 成功填充: {filled_count} (库存表: {from_inventory_count}), 已有价格: {already_filled_count}, 未找到: {not_found_count}'
        }), 200

    except Exception as e:
        print(f"❌ 自动填充价格失败 - steam_id: {steam_id}")
        print(f"错误详情: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'自动填充价格失败: {str(e)}'
        }), 500


@webStockComponentsV1.route('/verify_component/<steam_id>/<assetid>', methods=['GET'])
def verify_component(steam_id, assetid):
    """
    验证库存组件的实际数量是否与下拉框显示的数量一致

    Args:
        steam_id: Steam 用户 ID
        assetid: 库存组件的 assetid

    返回:
    {
        "success": True,
        "data": {
            "assetid": "组件assetid",
            "item_name": "组件名称",
            "display_count": 显示的数量（来自steam_inventory的weapon_float字段）,
            "actual_count": 实际的数量（来自steam_stockComponents表的记录数）,
            "is_match": 是否匹配,
            "difference": 差值（实际数量 - 显示数量）
        }
    }
    """
    try:
        db = DatabaseManager()

        # 1. 从 steam_inventory 表查询组件信息（获取显示的数量）
        inventory_sql = """
        SELECT item_name, weapon_float
        FROM steam_inventory
        WHERE assetid = ? AND data_user = ?
        """
        inventory_result = db.execute_query(inventory_sql, (assetid, steam_id))

        if not inventory_result or len(inventory_result) == 0:
            return jsonify({
                'success': False,
                'message': '未找到该库存组件'
            }), 404

        item_name = inventory_result[0][0]
        weapon_float = inventory_result[0][1]

        # 将 weapon_float 转换为数字（作为显示的数量）
        try:
            display_count = int(float(weapon_float)) if weapon_float not in [None, '', 'None'] else 0
        except (ValueError, TypeError):
            display_count = 0

        # 2. 从 steam_stockComponents 表查询该组件实际的记录数
        count_sql = """
        SELECT COUNT(*) FROM steam_stockComponents
        WHERE assetid = ? AND data_user = ?
        """
        count_result = db.execute_query(count_sql, (assetid, steam_id))
        actual_count = count_result[0][0] if count_result else 0

        # 3. 比对数量
        is_match = (display_count == actual_count)
        difference = actual_count - display_count

        return jsonify({
            'success': True,
            'data': {
                'assetid': assetid,
                'item_name': item_name,
                'display_count': display_count,
                'actual_count': actual_count,
                'is_match': is_match,
                'difference': difference
            }
        }), 200

    except Exception as e:
        print(f"❌ 验证组件数量失败 - assetid: {assetid}, steam_id: {steam_id}")
        print(f"错误详情: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'验证失败: {str(e)}'
        }), 500
