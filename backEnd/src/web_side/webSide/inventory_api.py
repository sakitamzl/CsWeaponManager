from flask import jsonify, request, Blueprint
from src.db_manager.steam.model.steam_inventory import SteamInventoryModel
from src.db_manager.database import DatabaseManager

webInventoryV1 = Blueprint('webInventoryV1', __name__)


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
