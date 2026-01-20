from flask import jsonify, request, Blueprint
from src.db_manager.steam.steam_inventory import SteamInventoryModel
from src.db_manager.database import DatabaseManager

webInventoryV1 = Blueprint('webInventoryV1', __name__)


def get_auto_price(item_name):
    """
    根据物品名称自动填充价格
    返回: float 价格，或 None（需要从buy表查询）
    """
    if not item_name:
        return None
    
    # 价格为0的物品关键词
    zero_price_keywords = ['赛季奖牌', '奖牌', '勋章', '徽章', '布章', '硬币']
    for keyword in zero_price_keywords:
        if keyword in item_name:
            return 0
    
    # 库存存储组件价格为14
    if '库存存储组件' in item_name:
        return 14
    
    # 其他物品返回None，需要从buy表查询
    return None


def get_price_from_buy_table(item_name, weapon_float=None, order_time=None, steam_hash_name=None):
    """
    从buy表查询价格
    
    参数:
        item_name: 物品名称
        weapon_float: 磨损值
        order_time: 订单时间（用于时间范围查询）
        steam_hash_name: Steam市场hash名称（用于更精确的匹配）
    
    逻辑:
        1. 优先使用steam_hash_name + weapon_float进行精确匹配
        2. 如果失败，使用item_name + weapon_float进行精确匹配
        3. 如果精确匹配失败且有order_time，使用前后24小时时间范围查询平均价（优先使用steam_hash_name）
        4. 如果没有order_time，查询最新的一条数据（优先使用steam_hash_name）
        5. 如果都失败，返回None
    """
    db = DatabaseManager()
    
    if weapon_float:
        # 第一步：优先使用steam_hash_name + weapon_float进行精确匹配
        if steam_hash_name:
            price_sql = "SELECT price FROM buy WHERE steam_hash_name = ? AND weapon_float = ? LIMIT 1"
            price_result = db.execute_query(price_sql, (steam_hash_name, weapon_float))
            if price_result and len(price_result) > 0:
                print(f"✅ 精确匹配成功（steam_hash_name + float）- {steam_hash_name}, float: {weapon_float}, price: {price_result[0][0]}")
                return price_result[0][0]
        
        # 第二步：使用item_name + weapon_float进行精确匹配
        price_sql = "SELECT price FROM buy WHERE item_name = ? AND weapon_float = ? LIMIT 1"
        price_result = db.execute_query(price_sql, (item_name, weapon_float))
        if price_result and len(price_result) > 0:
            print(f"✅ 精确匹配成功（item_name + float）- {item_name}, float: {weapon_float}, price: {price_result[0][0]}")
            return price_result[0][0]
        
        # 第三步：精确匹配失败，尝试使用时间范围或最新数据
        if order_time:
            # 使用order_time前后24小时时间范围查询平均价
            try:
                from datetime import datetime, timedelta
                
                # 尝试解析order_time
                if isinstance(order_time, str):
                    # 尝试多种日期格式
                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y/%m/%d %H:%M:%S', '%Y/%m/%d']:
                        try:
                            order_dt = datetime.strptime(order_time, fmt)
                            break
                        except ValueError:
                            continue
                    else:
                        # 如果所有格式都失败，尝试作为时间戳
                        try:
                            order_dt = datetime.fromtimestamp(float(order_time))
                        except:
                            order_dt = None
                elif isinstance(order_time, (int, float)):
                    order_dt = datetime.fromtimestamp(order_time)
                else:
                    order_dt = order_time
                
                if order_dt:
                    # 计算前后24小时的时间范围
                    start_time = order_dt - timedelta(hours=24)
                    end_time = order_dt + timedelta(hours=24)
                    
                    # 转换为字符串格式用于SQL查询
                    start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
                    end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 优先使用steam_hash_name查询时间范围内的平均价格
                    if steam_hash_name:
                        time_range_sql = """
                        SELECT AVG(CAST(price AS REAL)) 
                        FROM buy 
                        WHERE steam_hash_name = ? 
                        AND order_time >= ? 
                        AND order_time <= ?
                        """
                        avg_result = db.execute_query(time_range_sql, (steam_hash_name, start_time_str, end_time_str))
                        if avg_result and len(avg_result) > 0 and avg_result[0][0] is not None:
                            print(f"✅ 时间范围匹配成功（steam_hash_name）- {steam_hash_name}, 时间: {start_time_str} ~ {end_time_str}, price: {round(avg_result[0][0], 2)}")
                            return round(avg_result[0][0], 2)
                    
                    # 使用item_name查询时间范围内的平均价格
                    time_range_sql = """
                    SELECT AVG(CAST(price AS REAL)) 
                    FROM buy 
                    WHERE item_name = ? 
                    AND order_time >= ? 
                    AND order_time <= ?
                    """
                    avg_result = db.execute_query(time_range_sql, (item_name, start_time_str, end_time_str))
                    if avg_result and len(avg_result) > 0 and avg_result[0][0] is not None:
                        print(f"✅ 时间范围匹配成功（item_name）- {item_name}, 时间: {start_time_str} ~ {end_time_str}, price: {round(avg_result[0][0], 2)}")
                        return round(avg_result[0][0], 2)
            except Exception as e:
                print(f"使用时间范围查询价格失败: {str(e)}")
        
        # 第四步：如果没有order_time或时间范围查询失败，查询最新的一条数据
        # 优先使用steam_hash_name
        if steam_hash_name:
            latest_sql = """
            SELECT price 
            FROM buy 
            WHERE steam_hash_name = ? 
            ORDER BY order_time DESC 
            LIMIT 1
            """
            latest_result = db.execute_query(latest_sql, (steam_hash_name,))
            if latest_result and len(latest_result) > 0:
                print(f"✅ 最新数据匹配成功（steam_hash_name）- {steam_hash_name}, price: {latest_result[0][0]}")
                return latest_result[0][0]
        
        # 使用item_name查询最新的一条数据
        latest_sql = """
        SELECT price 
        FROM buy 
        WHERE item_name = ? 
        ORDER BY order_time DESC 
        LIMIT 1
        """
        latest_result = db.execute_query(latest_sql, (item_name,))
        if latest_result and len(latest_result) > 0:
            print(f"✅ 最新数据匹配成功（item_name）- {item_name}, price: {latest_result[0][0]}")
            return latest_result[0][0]
    else:
        # 没有磨损值的情况
        # 第一步：如果有order_time，使用时间范围查询平均价
        if order_time:
            try:
                from datetime import datetime, timedelta
                
                # 尝试解析order_time
                if isinstance(order_time, str):
                    # 尝试多种日期格式
                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y/%m/%d %H:%M:%S', '%Y/%m/%d']:
                        try:
                            order_dt = datetime.strptime(order_time, fmt)
                            break
                        except ValueError:
                            continue
                    else:
                        # 如果所有格式都失败，尝试作为时间戳
                        try:
                            order_dt = datetime.fromtimestamp(float(order_time))
                        except:
                            order_dt = None
                elif isinstance(order_time, (int, float)):
                    order_dt = datetime.fromtimestamp(order_time)
                else:
                    order_dt = order_time
                
                if order_dt:
                    # 计算前后24小时的时间范围
                    start_time = order_dt - timedelta(hours=24)
                    end_time = order_dt + timedelta(hours=24)
                    
                    # 转换为字符串格式用于SQL查询
                    start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
                    end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 优先使用steam_hash_name查询时间范围内的平均价格
                    if steam_hash_name:
                        time_range_sql = """
                        SELECT AVG(CAST(price AS REAL)) 
                        FROM buy 
                        WHERE steam_hash_name = ? 
                        AND order_time >= ? 
                        AND order_time <= ?
                        """
                        avg_result = db.execute_query(time_range_sql, (steam_hash_name, start_time_str, end_time_str))
                        if avg_result and len(avg_result) > 0 and avg_result[0][0] is not None:
                            print(f"✅ 时间范围平均价匹配成功（steam_hash_name，无float）- {steam_hash_name}, 时间: {start_time_str} ~ {end_time_str}, price: {round(avg_result[0][0], 2)}")
                            return round(avg_result[0][0], 2)
                    
                    # 使用item_name查询时间范围内的平均价格
                    time_range_sql = """
                    SELECT AVG(CAST(price AS REAL)) 
                    FROM buy 
                    WHERE item_name = ? 
                    AND order_time >= ? 
                    AND order_time <= ?
                    """
                    avg_result = db.execute_query(time_range_sql, (item_name, start_time_str, end_time_str))
                    if avg_result and len(avg_result) > 0 and avg_result[0][0] is not None:
                        print(f"✅ 时间范围平均价匹配成功（item_name，无float）- {item_name}, 时间: {start_time_str} ~ {end_time_str}, price: {round(avg_result[0][0], 2)}")
                        return round(avg_result[0][0], 2)
                    
                    # 如果24小时内没有找到记录，返回None（留空）
                    print(f"⚠️  24小时内无记录（无float）- item_name: {item_name}, steam_hash_name: {steam_hash_name}, 时间: {start_time_str} ~ {end_time_str}")
                    return None
            except Exception as e:
                print(f"使用时间范围查询价格失败（无float）: {str(e)}")
        
        # 第二步：如果没有order_time，查询最新的一条数据
        # 优先使用steam_hash_name
        if steam_hash_name:
            latest_sql = """
            SELECT price 
            FROM buy 
            WHERE steam_hash_name = ? 
            ORDER BY order_time DESC 
            LIMIT 1
            """
            latest_result = db.execute_query(latest_sql, (steam_hash_name,))
            if latest_result and len(latest_result) > 0:
                print(f"✅ 最新数据匹配成功（steam_hash_name，无float）- {steam_hash_name}, price: {latest_result[0][0]}")
                return latest_result[0][0]
        
        # 使用item_name查询最新的一条数据
        latest_sql = """
        SELECT price 
        FROM buy 
        WHERE item_name = ? 
        ORDER BY order_time DESC 
        LIMIT 1
        """
        latest_result = db.execute_query(latest_sql, (item_name,))
        if latest_result and len(latest_result) > 0:
            print(f"✅ 最新数据匹配成功（item_name，无float）- {item_name}, price: {latest_result[0][0]}")
            return latest_result[0][0]
        
        # 第三步：如果以上都失败，返回None（不再使用全局平均价格）
        print(f"❌ 未找到价格（无float）- item_name: {item_name}, steam_hash_name: {steam_hash_name}")
        return None
    
    print(f"❌ 未找到价格 - item_name: {item_name}, steam_hash_name: {steam_hash_name}, weapon_float: {weapon_float}")
    return None

@webInventoryV1.route('/steam_ids', methods=['GET'])
def get_steam_ids():
    """从config表获取所有Steam配置（key1='steam' AND key2='config'）"""
    try:
        # 获取查询参数，判断是否只统计特定classid的物品
        classid_filter = request.args.get('classid', '')
        
        db = DatabaseManager()
        
        # 只查询 key1='steam' AND key2='config' 的记录，包含 dataID
        steam_config_sql = """
        SELECT dataID, dataName, value, steamID
        FROM config 
        WHERE key1 = 'steam' AND key2 = 'config'
        ORDER BY dataID
        """
        steam_config_results = db.execute_query(steam_config_sql)
        
        steam_ids = []
        
        for row in steam_config_results:
            data_id = row[0]
            data_name = row[1] if row[1] else None
            value_json = row[2] if len(row) > 2 else None
            steam_id_from_field = row[3] if len(row) > 3 else None
            
            # 尝试从value JSON中解析steamID
            steam_id = steam_id_from_field
            if not steam_id and value_json:
                try:
                    import json
                    config_data = json.loads(value_json)
                    steam_id = config_data.get('steamID')
                except:
                    pass
            
            # 如果没有steamID，跳过这条记录
            if not steam_id:
                continue
            
            # 如果没有dataName，使用steamID作为名称
            if not data_name:
                data_name = steam_id
            
            # 查询该steamID在库存中的物品数量
            if classid_filter:
                count_sql = """
                SELECT COUNT(*) 
                FROM steam_inventory 
                WHERE data_user = ? AND if_inventory = '1' AND classid = ?
                """
                count_result = db.execute_query(count_sql, (steam_id, classid_filter))
            else:
                count_sql = """
                SELECT COUNT(*) 
                FROM steam_inventory 
                WHERE data_user = ? AND if_inventory = '1'
                """
                count_result = db.execute_query(count_sql, (steam_id,))
            
            item_count = count_result[0][0] if count_result else 0
            
            steam_ids.append({
                'dataID': data_id,  # 添加 dataID
                'dataName': data_name,  # 改为 dataName 保持一致
                'steamID': steam_id,  # 改为 steamID 保持一致
                'item_count': item_count
            })
        
        return jsonify({
            'success': True,
            'data': steam_ids
        }), 200
        
    except Exception as e:
        print(f"查询Steam ID列表失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'查询失败: {str(e)}'
        }), 500


@webInventoryV1.route('/steam_config', methods=['POST'])
def save_steam_config():
    """
    保存 / 更新 Steam 配置（Cookie 等）

    该接口主要供 Spider 服务调用：
    - URL: /webInventoryV1/steam_config
    - 方法: POST
    - 请求体示例（SteamCookieManager.save_to_database）:
      {
          "steamID": "7656...",
          "cookies": "...",
          "baseCookies": "...",
          "inventoryCookies": "...",
          "dataName": "Steam配置",
          "status": "1"
      }

    行为：
    - 如果 config 表中已存在 key1='steam' AND key2='config' 且 steamID=steamID 的记录，则执行 UPDATE
    - 否则插入一条新的配置记录
    """
    try:
        data = request.get_json() or {}

        # 1. 基本参数校验
        steam_id = (
            data.get('steamID')
            or data.get('steamId')
            or data.get('steam_id')
        )

        if not steam_id:
            return jsonify({
                'success': False,
                'message': 'steamID 不能为空'
            }), 400

        data_name = data.get('dataName') or steam_id
        status = data.get('status', '1')

        # 2. 处理 Cookie 字段，兼容多种字段名
        cookies = (
            data.get('inventoryCookies')
            or data.get('cookies')
            or data.get('cookie')
            or ''
        )
        base_cookies = (
            data.get('baseCookies')
            or data.get('baseCookie')
            or cookies
            or ''
        )
        inventory_cookies = (
            data.get('inventoryCookies')
            or cookies
            or ''
        )

        # 3. 组装需要存入 value 字段的 JSON
        config_payload = {
            'steamID': steam_id,
            'cookies': cookies,
            'baseCookies': base_cookies,
            'inventoryCookies': inventory_cookies,
            'dataName': data_name,
            'status': status
        }

        import json
        config_json = json.dumps(config_payload, ensure_ascii=False)

        db = DatabaseManager()

        # 4. 判断是更新还是新增
        select_sql = """
        SELECT dataID
        FROM config
        WHERE key1 = 'steam' AND key2 = 'config' AND steamID = ?
        """
        rows = db.execute_query(select_sql, (steam_id,))

        if rows:
            # 已存在配置，执行更新
            data_id = rows[0][0]
            update_sql = """
            UPDATE config
            SET dataName = ?, value = ?, status = ?, steamID = ?
            WHERE dataID = ?
            """
            affected = db.execute_update(
                update_sql,
                (data_name, config_json, status, steam_id, data_id)
            )

            if affected > 0:
                return jsonify({
                    'success': True,
                    'message': 'Steam 配置更新成功',
                    'data': {
                        'dataID': data_id,
                        'steamID': steam_id,
                        'dataName': data_name,
                        'status': status
                    }
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'Steam 配置更新失败，未找到对应记录'
                }), 404

        # 4.b 不存在配置，插入新记录
        max_id_rows = db.execute_query("SELECT MAX(dataID) FROM config")
        max_id = max_id_rows[0][0] if max_id_rows and max_id_rows[0][0] is not None else 0
        new_id = max_id + 1

        insert_sql = """
        INSERT INTO config (dataID, dataName, key1, key2, value, status, steamID)
        VALUES (?, ?, 'steam', 'config', ?, ?, ?)
        """
        inserted_id = db.execute_insert(
            insert_sql,
            (new_id, data_name, config_json, status, steam_id)
        )

        if inserted_id is not None:
            return jsonify({
                'success': True,
                'message': 'Steam 配置保存成功',
                'data': {
                    'dataID': new_id,
                    'steamID': steam_id,
                    'dataName': data_name,
                    'status': status
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Steam 配置保存失败'
            }), 500

    except Exception as e:
        print(f"[ERROR] 保存 Steam 配置失败: {e}")
        import traceback
        print(f"[ERROR] 详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'保存失败: {str(e)}'
        }), 500

@webInventoryV1.route('/inventory/<steam_id>', methods=['GET'])
def get_inventory(steam_id):
    """获取指定用户的库存列表"""
    try:
        # 获取查询参数
        search_text = request.args.get('search', '')
        weapon_type = request.args.get('weapon_type', '')
        float_range = request.args.get('float_range', '')
        classid = request.args.get('classid', '')  # 新增：classid筛选参数
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # 构建查询条件
        where_conditions = ["data_user = ?", "if_inventory = '1'"]  # 只查询在库存中的物品
        params = [steam_id]
        
        if search_text:
            where_conditions.append("(item_name LIKE ? OR weapon_name LIKE ?)")
            search_pattern = f"%{search_text}%"
            params.extend([search_pattern, search_pattern])
        
        if weapon_type:
            where_conditions.append("weapon_type = ?")
            params.append(weapon_type)
        
        if float_range:
            where_conditions.append("float_range = ?")
            params.append(float_range)
        
        if classid:
            where_conditions.append("classid = ?")
            params.append(classid)
        
        where_clause = " AND ".join(where_conditions)
        
        # 查询数据，使用自定义排序：未知物品放在最后
        from src.db_manager.database import DatabaseManager
        db = DatabaseManager()
        
        sql = f"""
        SELECT
            si.assetid, si.instanceid, si.classid, si.item_name, si.weapon_name, si.float_range,
            si.weapon_type, si.weapon_float, si.remark, si.data_user, si.buy_price, si.yyyp_price, si.buff_price, si.steam_price, si.order_time, si.steam_hash_name,
            si.sticker, si.pendant, si.rename
        FROM {SteamInventoryModel.get_table_name()} si
        WHERE {where_clause.replace('data_user', 'si.data_user').replace('weapon_type', 'si.weapon_type').replace('float_range', 'si.float_range').replace('item_name', 'si.item_name').replace('weapon_name', 'si.weapon_name')}
        ORDER BY
            CASE
                WHEN si.weapon_type = '未知物品' THEN 1
                ELSE 0
            END,
            CAST(si.buy_price AS REAL) DESC NULLS LAST,
            si.ROWID
        LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        results = db.execute_query(sql, tuple(params))
        
        # 将结果转换为模型对象和字典
        records = []
        if results:
            for row in results:
                # 优先读取steam_inventory表中的buy_price字段
                # 使用 is None 判断，因为 buy_price 可能为 "0"（字符串）
                buy_price_raw = row[10] if len(row) > 10 else None
                buy_price = buy_price_raw if buy_price_raw not in [None, '', 'None'] else None
                item_name = row[3]  # item_name
                
                # 只有当buy_price为空（None或空字符串）时，才进行后续处理
                if buy_price is None:
                    # 自动填充特殊物品价格
                    auto_price = get_auto_price(item_name)
                    
                    if auto_price is not None:
                        # 特殊物品，使用自动价格
                        buy_price = auto_price
                    else:
                        # 普通物品，从buy表查询
                        weapon_float = row[7]  # weapon_float
                        order_time = row[14] if len(row) > 14 else None  # order_time
                        steam_hash_name = row[15] if len(row) > 15 else None  # steam_hash_name
                        
                        # 使用新的价格查询函数
                        buy_price = get_price_from_buy_table(item_name, weapon_float, order_time, steam_hash_name)
                    
                    # 如果有价格（自动填充或从buy表查到），更新到steam_inventory数据库
                    # 注意：buy_price可能为0（如勋章、硬币等），所以用 is not None 判断
                    if buy_price is not None:
                        update_sql = "UPDATE steam_inventory SET buy_price = ? WHERE assetid = ?"
                        affected = db.execute_update(update_sql, (buy_price, row[0]))
                        if affected > 0:
                            print(f"自动填充价格: {item_name} -> ¥{buy_price}")
                
                # 如果是库存组件（classid = '3604678661'），查询实际数量
                actual_count = None
                if row[2] == '3604678661':  # classid
                    try:
                        count_sql = """
                        SELECT COUNT(*) FROM steam_stockComponents
                        WHERE assetid = ? AND data_user = ?
                        """
                        count_result = db.execute_query(count_sql, (row[0], steam_id))  # row[0] is assetid
                        actual_count = count_result[0][0] if count_result else 0
                    except Exception as e:
                        print(f"查询组件实际数量失败 - assetid: {row[0]}, 错误: {e}")
                        actual_count = 0

                record = {
                    'assetid': row[0],
                    'instanceid': row[1],
                    'classid': row[2],
                    'item_name': row[3],
                    'weapon_name': row[4],
                    'float_range': row[5],
                    'weapon_type': row[6],
                    'weapon_float': row[7],
                    'remark': row[8],
                    'data_user': row[9],
                    'buy_price': buy_price,
                    'yyyp_price': row[11] if len(row) > 11 else None,
                    'buff_price': row[12] if len(row) > 12 else None,
                    'steam_price': row[13] if len(row) > 13 else None,
                    'order_time': row[14] if len(row) > 14 else None,
                    'steam_hash_name': row[15] if len(row) > 15 else None,
                    'sticker': row[16] if len(row) > 16 else None,
                    'pendant': row[17] if len(row) > 17 else None,
                    'rename': row[18] if len(row) > 18 else None,
                    'actual_count': actual_count  # 实际数量（仅库存组件有值）
                }
                records.append(record)
        
        # records 已经是字典列表了
        inventory_list = records
        
        # 获取总数 - 需要使用相同的where条件和参数，但排除limit和offset
        # 因为params在后面添加了limit和offset，所以需要去掉最后两个参数
        count_params = params[:-2] if len(params) >= 2 else params
        total = SteamInventoryModel.count(where_clause, tuple(count_params))
        
        return jsonify({
            'success': True,
            'data': inventory_list,
            'total': total
        }), 200
        
    except Exception as e:
        print(f"查询库存失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'查询失败: {str(e)}'
        }), 500


@webInventoryV1.route('/inventory/grouped/<steam_id>', methods=['GET'])
def get_grouped_inventory(steam_id):
    """获取按item_name分组的库存列表"""
    try:
        from src.db_manager.database import DatabaseManager
        
        db = DatabaseManager()
        
        # 查询分组数据，只查询在库存中的物品（if_inventory = '1'）
        sql = """
        SELECT 
            si.item_name,
            si.weapon_name,
            si.weapon_type,
            si.float_range,
            si.steam_hash_name,
            COUNT(*) as count,
            GROUP_CONCAT(si.assetid) as assetids,
            GROUP_CONCAT(si.weapon_float) as weapon_floats,
            GROUP_CONCAT(si.remark, '|||') as remarks,
            GROUP_CONCAT(si.buy_price) as buy_prices,
            GROUP_CONCAT(si.yyyp_price) as yyyp_prices,
            GROUP_CONCAT(si.buff_price) as buff_prices,
            GROUP_CONCAT(si.steam_price) as steam_prices,
            GROUP_CONCAT(si.order_time) as order_times,
            GROUP_CONCAT(si.sticker, '|||') as stickers,
            GROUP_CONCAT(si.pendant, '|||') as pendants,
            GROUP_CONCAT(si.rename, '|||') as renames
        FROM steam_inventory si
        WHERE si.data_user = ? AND si.if_inventory = '1'
        GROUP BY si.item_name, si.weapon_name, si.weapon_type, si.float_range, si.steam_hash_name
        ORDER BY 
            CASE 
                WHEN si.weapon_type = '未知物品' THEN 1
                ELSE 0
            END,
            si.item_name
        """
        
        results = db.execute_query(sql, (steam_id,))
        
        # 转换为字典列表
        grouped_list = []
        for row in results:
            item_name, weapon_name, weapon_type, float_range, steam_hash_name, count, assetids, weapon_floats, remarks, buy_prices, yyyp_prices, buff_prices, steam_prices, order_times, stickers, pendants, renames = row
            
            # 分割字符串为列表
            assetid_list = assetids.split(',') if assetids else []
            float_list = weapon_floats.split(',') if weapon_floats else []
            remark_list = remarks.split('|||') if remarks else []
            price_list = buy_prices.split(',') if buy_prices else []
            yyyp_price_list = yyyp_prices.split(',') if yyyp_prices else []
            buff_price_list = buff_prices.split(',') if buff_prices else []
            steam_price_list = steam_prices.split(',') if steam_prices else []
            order_time_list = order_times.split(',') if order_times else []
            sticker_list = stickers.split('|||') if stickers else []
            pendant_list = pendants.split('|||') if pendants else []
            rename_list = renames.split('|||') if renames else []
            
            grouped_list.append({
                'item_name': item_name,
                'weapon_name': weapon_name,
                'weapon_type': weapon_type,
                'float_range': float_range,
                'steam_hash_name': steam_hash_name,
                'count': count,
                'assetids': assetid_list,
                'weapon_floats': float_list,
                'remarks': remark_list,
                'buy_prices': price_list,
                'yyyp_prices': yyyp_price_list,
                'buff_prices': buff_price_list,
                'steam_prices': steam_price_list,
                'order_times': order_time_list,
                'stickers': sticker_list,
                'pendants': pendant_list,
                'renames': rename_list
            })
        
        return jsonify({
            'success': True,
            'data': grouped_list,
            'total': len(grouped_list)
        }), 200
        
    except Exception as e:
        print(f"查询分组库存失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'查询失败: {str(e)}'
        }), 500


@webInventoryV1.route('/inventory/stats/<steam_id>', methods=['GET'])
def get_inventory_stats(steam_id):
    """获取库存统计信息（支持筛选参数）"""
    try:
        from src.db_manager.database import DatabaseManager

        db = DatabaseManager()
        
        # 获取查询参数（与get_inventory接口保持一致）
        search_text = request.args.get('search', '')
        weapon_type = request.args.get('weapon_type', '')
        float_range = request.args.get('float_range', '')
        classid = request.args.get('classid', '')
        
        # 构建查询条件
        where_conditions = ["data_user = ?", "if_inventory = '1'"]
        params = [steam_id]
        
        if search_text:
            where_conditions.append("(item_name LIKE ? OR weapon_name LIKE ?)")
            search_pattern = f"%{search_text}%"
            params.extend([search_pattern, search_pattern])
        
        if weapon_type:
            where_conditions.append("weapon_type = ?")
            params.append(weapon_type)
        
        if float_range:
            where_conditions.append("float_range = ?")
            params.append(float_range)
        
        if classid:
            where_conditions.append("classid = ?")
            params.append(classid)
        
        where_clause = " AND ".join(where_conditions)

        # 统计总数
        total_sql = f"SELECT COUNT(*) FROM steam_inventory WHERE {where_clause}"
        total_result = db.execute_query(total_sql, tuple(params))
        total_count = total_result[0][0] if total_result else 0

        # 按武器类型统计
        type_sql = f"""
        SELECT weapon_type, COUNT(*) as count 
        FROM steam_inventory 
        WHERE {where_clause} AND weapon_type IS NOT NULL AND weapon_type != ''
        GROUP BY weapon_type
        ORDER BY count DESC
        """
        type_results = db.execute_query(type_sql, tuple(params))
        
        type_stats = []
        for row in type_results:
            weapon_type_val, count = row
            type_stats.append({
                'weapon_type': weapon_type_val,
                'count': count
            })
        
        # 按磨损等级统计
        wear_sql = f"""
        SELECT float_range, COUNT(*) as count 
        FROM steam_inventory 
        WHERE {where_clause} AND float_range IS NOT NULL AND float_range != ''
        GROUP BY float_range
        ORDER BY count DESC
        """
        wear_results = db.execute_query(wear_sql, tuple(params))

        wear_stats = []
        for row in wear_results:
            float_range_val, count = row
            wear_stats.append({
                'float_range': float_range_val,
                'count': count
            })

        # 统计购入价格总和
        price_sql = f"""
        SELECT 
            COUNT(CASE WHEN CAST(buy_price AS REAL) > 0 THEN 1 END) as priced_count,
            SUM(CAST(buy_price AS REAL)) as total_price,
            AVG(CAST(buy_price AS REAL)) as avg_price,
            MIN(CAST(buy_price AS REAL)) as min_price,
            MAX(CAST(buy_price AS REAL)) as max_price
        FROM steam_inventory
        WHERE {where_clause}
        """
        price_result = db.execute_query(price_sql, tuple(params))

        price_stats = {
            'priced_count': 0,
            'total_price': 0,
            'avg_price': 0,
            'min_price': 0,
            'max_price': 0
        }

        if price_result and len(price_result) > 0:
            priced_count, total_price, avg_price, min_price, max_price = price_result[0]
            price_stats = {
                'priced_count': priced_count if priced_count else 0,
                'total_price': round(total_price, 2) if total_price else 0,
                'avg_price': round(avg_price, 2) if avg_price else 0,
                'min_price': round(min_price, 2) if min_price else 0,
                'max_price': round(max_price, 2) if max_price else 0
            }

        # 统计悠悠有品价格总和
        yyyp_price_sql = f"""
        SELECT 
            COUNT(CASE WHEN CAST(yyyp_price AS REAL) > 0 THEN 1 END) as priced_count,
            SUM(CAST(yyyp_price AS REAL)) as total_price,
            AVG(CAST(yyyp_price AS REAL)) as avg_price
        FROM steam_inventory
        WHERE {where_clause}
        """
        yyyp_price_result = db.execute_query(yyyp_price_sql, tuple(params))

        yyyp_price_stats = {
            'priced_count': 0,
            'total_price': 0,
            'avg_price': 0
        }

        if yyyp_price_result and len(yyyp_price_result) > 0:
            priced_count, total_price, avg_price = yyyp_price_result[0]
            yyyp_price_stats = {
                'priced_count': priced_count if priced_count else 0,
                'total_price': round(total_price, 2) if total_price else 0,
                'avg_price': round(avg_price, 2) if avg_price else 0
            }

        # 统计BUFF价格总和
        buff_price_sql = f"""
        SELECT 
            COUNT(CASE WHEN CAST(buff_price AS REAL) > 0 THEN 1 END) as priced_count,
            SUM(CAST(buff_price AS REAL)) as total_price,
            AVG(CAST(buff_price AS REAL)) as avg_price
        FROM steam_inventory
        WHERE {where_clause}
        """
        buff_price_result = db.execute_query(buff_price_sql, tuple(params))

        buff_price_stats = {
            'priced_count': 0,
            'total_price': 0,
            'avg_price': 0
        }

        if buff_price_result and len(buff_price_result) > 0:
            priced_count, total_price, avg_price = buff_price_result[0]
            buff_price_stats = {
                'priced_count': priced_count if priced_count else 0,
                'total_price': round(total_price, 2) if total_price else 0,
                'avg_price': round(avg_price, 2) if avg_price else 0
            }

        # 统计 Steam 参考价总和
        steam_price_sql = f"""
        SELECT 
            COUNT(CASE WHEN CAST(steam_price AS REAL) > 0 THEN 1 END) as priced_count,
            SUM(CAST(steam_price AS REAL)) as total_price,
            AVG(CAST(steam_price AS REAL)) as avg_price
        FROM steam_inventory
        WHERE {where_clause}
        """
        steam_price_result = db.execute_query(steam_price_sql, tuple(params))

        steam_price_stats = {
            'priced_count': 0,
            'total_price': 0,
            'avg_price': 0
        }

        if steam_price_result and len(steam_price_result) > 0:
            priced_count, total_price, avg_price = steam_price_result[0]
            steam_price_stats = {
                'priced_count': priced_count if priced_count else 0,
                'total_price': round(total_price, 2) if total_price else 0,
                'avg_price': round(avg_price, 2) if avg_price else 0
            }

        return jsonify({
            'success': True,
            'data': {
                'total_count': total_count,
                'by_type': type_stats,
                'by_wear': wear_stats,
                'price_stats': price_stats,
                'yyyp_price_stats': yyyp_price_stats,
                'buff_price_stats': buff_price_stats,
                'steam_price_stats': steam_price_stats
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


@webInventoryV1.route('/inventory/buy_price/<steam_id>/<assetid>', methods=['PUT'])
def update_buy_price(steam_id, assetid):
    """更新库存物品的购入价格"""
    try:
        data = request.get_json()
        buy_price = data.get('buy_price', '')
        
        from src.db_manager.database import DatabaseManager
        db = DatabaseManager()
        
        sql = """
        UPDATE steam_inventory 
        SET buy_price = ? 
        WHERE data_user = ? AND assetid = ?
        """
        
        affected_rows = db.execute_update(sql, (buy_price, steam_id, assetid))
        
        if affected_rows > 0:
            return jsonify({
                'success': True,
                'message': '更新成功'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '未找到对应记录'
            }), 404
            
    except Exception as e:
        print(f"更新buy_price失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'更新失败: {str(e)}'
        }), 500


@webInventoryV1.route('/steam_config/<steam_id>', methods=['GET'])
def get_steam_config(steam_id):
    """根据Steam ID获取Steam配置（cookie等）"""
    try:
        print(f"[DEBUG] 查询Steam配置，Steam ID: {steam_id}")
        from src.db_manager.database import DatabaseManager
        db = DatabaseManager()
        
        # 查询config表，获取key1='steam'且key2='config'的记录
        sql = """
        SELECT value FROM config 
        WHERE key1 = 'steam' AND key2 = 'config'
        """
        
        results = db.execute_query(sql)
        print(f"[DEBUG] 查询到 {len(results) if results else 0} 条Steam配置记录")
        
        if not results:
            print("[ERROR] 未找到任何Steam配置")
            return jsonify({
                'success': False,
                'error': '未找到Steam配置'
            }), 404
        
        # 遍历所有steam配置，找到匹配的steamID
        import json
        for idx, row in enumerate(results):
            value = row[0]
            print(f"[DEBUG] 处理第 {idx + 1} 条配置...")
            if value:
                try:
                    config_data = json.loads(value)
                    config_steam_id = config_data.get('steamID')
                    print(f"[DEBUG] 配置中的Steam ID: {config_steam_id}")
                    
                    # 检查steamID是否匹配
                    if config_steam_id == steam_id:
                        print(f"[INFO] 找到匹配的Steam配置")
                        # Steam配置中使用 inventoryCookies/baseCookies 字段
                        base_cookie = config_data.get('baseCookies') or config_data.get('baseCookie') or config_data.get('cookie', '')
                        inventory_cookie = config_data.get('inventoryCookies') or config_data.get('cookies') or config_data.get('cookie', '')
                        print(f"[DEBUG] Cookie长度: {len(inventory_cookie)}")
                        return jsonify({
                            'success': True,
                            'data': {
                                'steamId': config_steam_id,
                                'cookie': inventory_cookie,
                                'inventoryCookie': inventory_cookie,
                                'baseCookie': base_cookie,
                                'baseCookies': base_cookie,
                                'inventoryCookies': inventory_cookie,
                                'dataName': config_data.get('dataName', ''),
                                'status': config_data.get('status', '1')
                            }
                        }), 200
                except json.JSONDecodeError as je:
                    print(f"[ERROR] JSON解析失败: {str(je)}")
                    continue
        
        print(f"[ERROR] 未找到Steam ID为 {steam_id} 的配置")
        return jsonify({
            'success': False,
            'error': f'未找到Steam ID为 {steam_id} 的配置'
        }), 404
            
    except Exception as e:
        print(f"[ERROR] 获取Steam配置失败: {e}")
        import traceback
        print(f"[ERROR] 详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'查询失败: {str(e)}'
        }), 500


@webInventoryV1.route('/inventory/batch_update_yyyp_price', methods=['POST'])
def batch_update_yyyp_price():
    """批量更新悠悠有品价格"""
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data or 'weapon_list' not in data:
            return jsonify({
                'success': False,
                'error': '缺少必要参数 weapon_list'
            }), 400
        
        weapon_list = data['weapon_list']
        
        if not isinstance(weapon_list, list):
            return jsonify({
                'success': False,
                'error': 'weapon_list 必须是数组'
            }), 400
        
        # 统计信息
        success_count = 0
        failed_count = 0
        error_messages = []
        
        # 遍历列表，更新每个武器的价格
        for weapon in weapon_list:
            try:
                # 获取必要字段
                steam_asset_id = weapon.get('SteamAssetId')
                asset_add_time = weapon.get('AssetAddTime')
                show_mark_price = weapon.get('ShowMarkPrice')
                
                if not steam_asset_id:
                    failed_count += 1
                    error_messages.append(f"缺少 SteamAssetId")
                    continue
                
                # 查找库存记录
                inventory = SteamInventoryModel.find_by_assetid(steam_asset_id)
                
                if inventory:
                    # 更新已存在的记录
                    if asset_add_time:
                        inventory.order_time = asset_add_time
                    if show_mark_price:
                        # 提取价格数字部分（去掉 ￥ 符号）
                        if isinstance(show_mark_price, str) and show_mark_price.startswith('￥'):
                            price_value = show_mark_price.replace('￥', '').strip()
                        else:
                            price_value = str(show_mark_price)
                        inventory.yyyp_price = price_value
                    
                    if inventory.save():
                        success_count += 1
                    else:
                        failed_count += 1
                        error_messages.append(f"SteamAssetId {steam_asset_id} 更新失败")
                else:
                    # 记录不存在
                    failed_count += 1
                    error_messages.append(f"SteamAssetId {steam_asset_id} 在数据库中不存在")
                    
            except Exception as e:
                failed_count += 1
                error_messages.append(f"处理 SteamAssetId {weapon.get('SteamAssetId', 'Unknown')} 时出错: {str(e)}")
                print(f"批量更新时出错: {e}")
                import traceback
                print(traceback.format_exc())
        
        # 返回结果
        return jsonify({
            'success': True,
            'data': {
                'total': len(weapon_list),
                'success_count': success_count,
                'failed_count': failed_count,
                'error_messages': error_messages[:10]  # 只返回前10条错误信息
            }
        }), 200
        
    except Exception as e:
        print(f"批量更新悠悠有品价格失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'更新失败: {str(e)}'
        }), 500


@webInventoryV1.route('/inventory/batch_update_buff_price', methods=['POST'])
def batch_update_buff_price():
    """批量更新BUFF价格"""
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data or 'weapon_list' not in data:
            return jsonify({
                'success': False,
                'error': '缺少必要参数 weapon_list'
            }), 400
        
        weapon_list = data['weapon_list']
        
        if not isinstance(weapon_list, list):
            return jsonify({
                'success': False,
                'error': 'weapon_list 必须是数组'
            }), 400
        
        # 统计信息
        success_count = 0
        failed_count = 0
        error_messages = []
        
        # 遍历列表，更新每个武器的价格
        for weapon in weapon_list:
            try:
                # 获取必要字段
                assetid = weapon.get('assetid')
                instanceid = weapon.get('instanceid')
                steam_price = weapon.get('steam_price')
                buff_price = weapon.get('buff_price')
                
                if not assetid:
                    failed_count += 1
                    error_messages.append(f"缺少 assetid")
                    continue
                
                # 查找库存记录
                inventory = SteamInventoryModel.find_by_assetid(assetid)
                
                if inventory:
                    # 更新已存在的记录
                    if instanceid:
                        inventory.instanceid = instanceid
                    
                    if steam_price:
                        # 确保价格是字符串格式
                        inventory.steam_price = str(steam_price)
                    
                    if buff_price:
                        # 确保价格是字符串格式
                        inventory.buff_price = str(buff_price)
                    
                    if inventory.save():
                        success_count += 1
                    else:
                        failed_count += 1
                        error_messages.append(f"assetid {assetid} 更新失败")
                else:
                    # 记录不存在
                    failed_count += 1
                    error_messages.append(f"assetid {assetid} 在数据库中不存在")
                    
            except Exception as e:
                failed_count += 1
                error_messages.append(f"处理 assetid {weapon.get('assetid', 'Unknown')} 时出错: {str(e)}")
                print(f"批量更新时出错: {e}")
                import traceback
                print(traceback.format_exc())
        
        # 返回结果
        return jsonify({
            'success': True,
            'data': {
                'total': len(weapon_list),
                'success_count': success_count,
                'failed_count': failed_count,
                'error_messages': error_messages[:10]  # 只返回前10条错误信息
            }
        }), 200
        
    except Exception as e:
        print(f"批量更新BUFF价格失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'更新失败: {str(e)}'
        }), 500


@webInventoryV1.route('/steam_account_name/<steam_id>', methods=['PUT'])
def update_steam_account_name(steam_id):
    """更新或创建Steam账号名称配置"""
    try:
        data = request.get_json()
        account_name = data.get('accountName', '').replace("'", "''")
        
        if not account_name:
            return jsonify({
                'success': False,
                'message': '账号名称不能为空'
            }), 400
        
        from src.db_manager.database import DatabaseManager
        db = DatabaseManager()
        
        # 先检查是否已存在该steamID的账号名称配置
        check_sql = """
        SELECT dataID FROM config 
        WHERE steamID = ? AND key2 = 'steam_account'
        LIMIT 1
        """
        check_result = db.execute_query(check_sql, (steam_id,))
        
        if check_result:
            # 如果存在，更新
            update_sql = f"""
            UPDATE config 
            SET dataName = '{account_name}' 
            WHERE steamID = ? AND key2 = 'steam_account'
            """
            db.execute_update(update_sql, (steam_id,))
            message = '账号名称更新成功'
        else:
            # 如果不存在，创建新记录
            insert_sql = f"""
            INSERT INTO config (dataName, key1, key2, steamID, status) 
            VALUES ('{account_name}', 'steam', 'steam_account', '{steam_id.replace("'", "''")}', '1')
            """
            db.execute_update(insert_sql)
            message = '账号名称创建成功'
        
        return jsonify({
            'success': True,
            'message': message
        }), 200
        
    except Exception as e:
        print(f"更新Steam账号名称失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'更新失败: {str(e)}'
        }), 500


@webInventoryV1.route('/getAvailableComponents', methods=['POST'])
def get_available_components():
    """
    获取可用的库存组件列表（classID为3604678661，且有剩余空位）
    """
    try:
        data = request.get_json()
        steam_id = data.get('steamId')
        
        if not steam_id:
            return jsonify({
                'success': False,
                'message': '缺少steamId参数'
            }), 400
        
        print(f"获取可用库存组件 - steamId: {steam_id}")
        
        db = DatabaseManager()
        
        # 1. 从 steam_inventory 表获取该用户的所有库存组件（classid=3604678661）
        # weapon_float 字段存储的是组件已存储的数量
        query_components = """
            SELECT 
                assetid,
                item_name,
                steam_hash_name,
                weapon_float
            FROM steam_inventory
            WHERE data_user = ? 
            AND classid = '3604678661'
            AND if_inventory = '1'
        """
        
        components = db.execute_query(query_components, (steam_id,))
        
        if not components:
            print(f"未找到库存组件 - steamId: {steam_id}")
            return jsonify({
                'success': True,
                'message': '未找到库存组件',
                'components': [],
                'total_count': 0
            }), 200
        
        print(f"找到 {len(components)} 个库存组件")
        
        # 2. 计算每个组件的剩余空位
        available_components = []
        max_capacity = 1000  # 每个组件最多存储1000件物品
        
        for component in components:
            assetid = component[0]  # assetid
            item_name = component[1] if len(component) > 1 else '库存组件'
            steam_hash_name = component[2] if len(component) > 2 else ''
            weapon_float = component[3] if len(component) > 3 else '0'
            
            # weapon_float 存储的是已存储的数量
            try:
                stored_count = int(float(weapon_float)) if weapon_float else 0
            except (ValueError, TypeError):
                stored_count = 0
            
            # 计算剩余空位
            remaining_slots = max_capacity - stored_count
            
            # 只返回有剩余空位的组件（剩余空位 > 0）
            if remaining_slots > 0:
                available_components.append({
                    'assetid': assetid,
                    'name': item_name or '库存组件',
                    'market_hash_name': steam_hash_name,
                    'stored_count': stored_count,
                    'remaining_slots': remaining_slots,
                    'max_capacity': max_capacity,
                    'icon_url': ''
                })
        
        # 按剩余空位从大到小排序（剩余空位多的排在前面）
        available_components.sort(key=lambda x: x['remaining_slots'], reverse=True)
        
        print(f"可用组件数量: {len(available_components)}")
        
        return jsonify({
            'success': True,
            'message': f'找到 {len(available_components)} 个可用组件',
            'components': available_components,
            'total_count': len(available_components)
        }), 200
        
    except Exception as e:
        import traceback
        error_msg = f'获取可用组件失败: {str(e)}'
        print(error_msg)
        print(f"详细错误: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': error_msg
        }), 500
