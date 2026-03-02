"""
StockComponents 页面价格操作模块
提供购入价格更新、自动填充购入价、参考价同步功能
"""
from flask import jsonify, request
from src.db_manager.database import DatabaseManager
import traceback


class StockComponentsPrice:

    @staticmethod
    def update_buy_price(steam_id, goods_assetid):
        """更新指定组件的购入价格"""
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

            return jsonify({
                'success': True,
                'message': '价格更新成功'
            })

        except Exception as e:
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': f'服务器错误: {str(e)}'
            }), 500

    @staticmethod
    def auto_fill_prices(steam_id):
        """
        自动填充组件的购入价格
        三级策略：
        1. goods_assetid 匹配 steam_inventory 表的 assetid 获取 buy_price
        2. steam_hash_name + weapon_float 精确匹配 buy 表
        3. steam_hash_name 批量查询 buy 表的平均价格
        """
        try:
            db = DatabaseManager()

            # 查询该用户的所有组件
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

            total_count = len(components)
            filled_count = 0
            already_filled_count = 0
            not_found_count = 0
            from_inventory_count = 0

            # 第一步：从 steam_inventory 表批量获取价格
            assetids = [comp[0] for comp in components]
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
                        inventory_price_map[row[0]] = row[1]

            # 第二步：处理所有组件
            float_components = []
            no_float_components = []

            for component in components:
                goods_assetid = component[0]
                item_name = component[1]
                weapon_float = component[2]
                current_buy_price = component[3]
                steam_hash_name = component[4]

                # 优先从库存表获取价格
                if goods_assetid in inventory_price_map:
                    buy_price = inventory_price_map[goods_assetid]

                    current_price_str = '' if current_buy_price is None else str(current_buy_price)
                    new_price_str = str(buy_price)

                    if current_price_str == new_price_str:
                        already_filled_count += 1
                        from_inventory_count += 1
                    else:
                        update_sql = """
                        UPDATE steam_stockComponents
                        SET buy_price = ?
                        WHERE goods_assetid = ? AND data_user = ?
                        """
                        affected_rows = db.execute_update(update_sql, (str(buy_price), goods_assetid, steam_id))
                        if affected_rows > 0:
                            filled_count += 1
                            from_inventory_count += 1
                    continue

                # 如果已有价格且库存表没有匹配到，跳过
                if current_buy_price not in [None, '', 'None', '0', '0.0', '0.00']:
                    already_filled_count += 1
                    continue

                # 分类到 float 或 no_float 组件
                if weapon_float and weapon_float not in ['', '0', '0.0', 'None']:
                    float_components.append((goods_assetid, item_name, weapon_float, steam_hash_name))
                else:
                    no_float_components.append((goods_assetid, item_name, steam_hash_name))

            # 第三步：处理有 float 值的组件（精确匹配 buy 表）
            for goods_assetid, item_name, weapon_float, steam_hash_name in float_components:
                buy_price = None
                try:
                    float_value = float(weapon_float)
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
                except (ValueError, TypeError):
                    pass

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
                else:
                    not_found_count += 1

            # 第四步：批量处理没有 float 值的组件
            if no_float_components:
                hash_names = list(set([comp[2] for comp in no_float_components if comp[2] and comp[2] not in ['', 'None']]))

                if hash_names:
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

                    price_map = {}
                    if price_results:
                        for row in price_results:
                            avg_price = round(row[1], 2) if row[1] else None
                            if avg_price:
                                price_map[row[0]] = avg_price

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
                            else:
                                not_found_count += 1
                        else:
                            not_found_count += 1

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
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': f'自动填充价格失败: {str(e)}'
            }), 500

    @staticmethod
    def fill_reference_price(steam_id, source):
        """
        根据 weapon_classID 表中的价格，填充/更新库存组件的悠悠有品或BUFF参考价
        source: 'yyyp' 或 'buff'
        支持 force_update 参数
        """
        source = (source or '').lower()
        if source not in ('yyyp', 'buff'):
            return jsonify({
                'success': False,
                'message': "source 参数只能是 'yyyp' 或 'buff'"
            }), 400

        try:
            request_data = request.get_json() or {}
            force_update = request_data.get('force_update', False)

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

                if not force_update and current_price_str == target_price:
                    unchanged += 1
                    continue

                db.execute_update(update_sql, (target_price, goods_assetid))
                updated += 1

            total = len(components)
            update_mode = "强制更新" if force_update else "增量更新"
            label = '悠悠有品' if source == 'yyyp' else 'BUFF'
            message = f"{label}价格同步完成（{update_mode}）：总计 {total}，匹配 {matched}，更新 {updated}，保持不变 {unchanged}，缺少价格 {missing_price}"

            return jsonify({
                'success': True,
                'message': message,
                'data': {
                    'total': total,
                    'matched': matched,
                    'updated': updated,
                    'unchanged': unchanged,
                    'missing_price': missing_price,
                    'force_update': force_update
                }
            })

        except Exception as e:
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': f"同步参考价格失败: {str(e)}"
            }), 500
