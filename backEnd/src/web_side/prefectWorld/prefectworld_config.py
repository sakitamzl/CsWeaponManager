from flask import jsonify, request, Blueprint
from src.db_manager.database import DatabaseManager

prefectWorldConfigV1 = Blueprint('prefectWorldConfigV1', __name__)


@prefectWorldConfigV1.route('/configs', methods=['GET'])
def get_all_prefectworld_configs():
    """获取所有完美世界配置列表"""
    try:
        db = DatabaseManager()
        
        # 获取查询参数，判断是否只统计特定classid的物品
        classid_filter = request.args.get('classid', '')
        print(f"[DEBUG] 获取完美世界配置列表，classid过滤: {classid_filter}")
        
        sql = """
        SELECT dataID, dataName, value FROM config 
        WHERE key1 = 'perfectworld'
        ORDER BY dataID
        """
        
        results = db.execute_query(sql)
        print(f"[DEBUG] 查询到 {len(results) if results else 0} 条完美世界配置")
        
        if not results:
            return jsonify({
                'success': True,
                'data': [],
                'message': '未找到完美世界配置'
            }), 200
        
        import json
        config_list = []
        
        for row in results:
            data_id = row[0]
            data_name = row[1] if row[1] else None
            value = row[2]
            
            if value:
                try:
                    # 解析配置数据
                    if isinstance(value, str):
                        config_data = json.loads(value)
                    else:
                        config_data = value
                    
                    steam_id = config_data.get('steamID')
                    if not steam_id:
                        continue
                    
                    # 如果没有dataName，使用配置中的dataName或steamID
                    if not data_name:
                        data_name = config_data.get('dataName', steam_id)
                    
                    # 查询该steamID在库存组件中的物品数量
                    item_count = 0
                    try:
                        if classid_filter:
                            count_sql = """
                            SELECT COUNT(*) 
                            FROM steam_stockComponents 
                            WHERE data_user = ? AND classid = ?
                            """
                            count_result = db.execute_query(count_sql, (steam_id, classid_filter))
                            print(f"[DEBUG] 查询组件数量 - Steam ID: {steam_id}, classid: {classid_filter}, 结果: {count_result}")
                        else:
                            count_sql = """
                            SELECT COUNT(*) 
                            FROM steam_stockComponents 
                            WHERE data_user = ?
                            """
                            count_result = db.execute_query(count_sql, (steam_id,))
                            print(f"[DEBUG] 查询组件数量 - Steam ID: {steam_id}, 结果: {count_result}")
                        
                        if count_result and len(count_result) > 0 and count_result[0]:
                            item_count = count_result[0][0] or 0
                            print(f"[DEBUG] Steam ID {steam_id} 的组件数量: {item_count}")
                    except Exception as count_error:
                        print(f"[ERROR] 查询组件数量失败 - Steam ID: {steam_id}, 错误: {str(count_error)}")
                        item_count = 0
                    
                    config_item = {
                        'dataID': data_id,
                        'dataName': data_name,
                        'steamID': steam_id,
                        'item_count': item_count,
                        'status': config_data.get('status', '1')
                    }
                    config_list.append(config_item)
                    print(f"[DEBUG] 添加配置: {config_item}")
                    
                except Exception as e:
                    print(f"[ERROR] 处理配置数据失败: {str(e)}")
                    import traceback
                    print(f"[ERROR] 详细错误: {traceback.format_exc()}")
                    continue
        
        print(f"[INFO] 返回 {len(config_list)} 条完美世界配置")
        return jsonify({
            'success': True,
            'data': config_list
        }), 200
            
    except Exception as e:
        print(f"[ERROR] 获取完美世界配置列表失败: {e}")
        import traceback
        print(f"[ERROR] 详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'查询失败: {str(e)}'
        }), 500


@prefectWorldConfigV1.route('/config/<steam_id>', methods=['GET'])
def get_prefectworld_config(steam_id):
    try:
        print(f"[DEBUG] 查询完美世界配置，Steam ID: {steam_id}")
        db = DatabaseManager()
        sql = """
        SELECT value FROM config 
        WHERE key1 = 'perfectworld'
        """
        
        results = db.execute_query(sql)
        print(f"[DEBUG] 查询到 {len(results) if results else 0} 条完美世界配置记录")
        
        if not results:
            print("[ERROR] 未找到任何完美世界配置")
            return jsonify({
                'success': False,
                'error': '未找到完美世界配置'
            }), 404
        
        # 遍历所有完美世界配置，找到匹配的steamID
        import json
        for idx, row in enumerate(results):
            value = row[0]
            print(f"[DEBUG] 处理第 {idx + 1} 条配置，value类型: {type(value)}")
            if value:
                try:
                    # 如果value已经是字典，直接使用；否则解析JSON
                    if isinstance(value, str):
                        config_data = json.loads(value)
                    else:
                        config_data = value
                    
                    config_steam_id = config_data.get('steamID')
                    print(f"[DEBUG] 配置中的Steam ID: {config_steam_id}")
                    
                    # 检查steamID是否匹配
                    if config_steam_id == steam_id:
                        print(f"[INFO] 找到匹配的完美世界配置")
                        return jsonify({
                            'success': True,
                            'data': {
                                'steamId': config_steam_id,
                                'appversion': config_data.get('appversion', ''),
                                'device': config_data.get('device', ''),
                                'gameType': config_data.get('gameType', ''),
                                'platform': config_data.get('platform', ''),
                                'token': config_data.get('token', ''),
                                'tdSign': config_data.get('tdSign', ''),
                                'dataName': config_data.get('dataName', ''),
                                'status': config_data.get('status', '1')
                            }
                        }), 200
                except json.JSONDecodeError as je:
                    print(f"[ERROR] JSON解析失败: {str(je)}")
                    continue
                except Exception as e:
                    print(f"[ERROR] 处理配置数据失败: {str(e)}")
                    continue
        
        print(f"[ERROR] 未找到Steam ID为 {steam_id} 的完美世界配置")
        return jsonify({
            'success': False,
            'error': f'未找到Steam ID为 {steam_id} 的完美世界配置'
        }), 404
            
    except Exception as e:
        print(f"[ERROR] 获取完美世界配置失败: {e}")
        import traceback
        print(f"[ERROR] 详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'查询失败: {str(e)}'
        }), 500

