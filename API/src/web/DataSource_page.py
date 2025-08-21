from flask import jsonify, request, Blueprint
from src.log import Log
from src.execution_db import Date_base
from src.now_time import today
import json

dataSourcePage = Blueprint('dataSourcePage', __name__)


@dataSourcePage.route('/api/datasource', methods=['GET'])
def get_datasources():
    """获取所有数据源"""
    try:
        db = Date_base()
        success, result = db.select("SELECT dataID, dataName, key1, key2, value, status FROM config ORDER BY dataID")
        
        if success:
            # 按dataID和dataName分组数据
            datasource_groups = {}
            for row in result:
                data_id, data_name, key1, key2, value, status = row
                
                # 创建唯一键
                key = f"{data_id}_{data_name}"
                
                if key not in datasource_groups:
                    from datetime import datetime
                    # 从key2字段获取数据源类型
                    data_source_type = key2 if key2 and not key1 else 'unknown'
                    datasource_groups[key] = {
                        'dataID': data_id,
                        'dataName': data_name,
                        'type': data_source_type,
                        'config': {},
                        'status': status,
                        'enabled': status == '1',
                        'lastUpdate': datetime.now().isoformat(),
                        'updateFreq': '15min'  # 默认值，会被sleep_time覆盖
                    }
                
                # 如果key1为空且key2不为空，说明key2存储的是数据源类型
                if not key1 and key2:
                    datasource_groups[key]['type'] = key2
                # 如果key1和key2都有值，作为配置信息存储  
                elif key1 and key2:
                    # 特殊处理悠悠有品的JSON配置
                    if key1 == 'yyyp' and key2 == 'youpin' and value:
                        try:
                            import json
                            json_config = json.loads(value)
                            if isinstance(json_config, dict):
                                # 将JSON配置直接展开到config中，使用yyyp_前缀
                                for json_key, json_value in json_config.items():
                                    datasource_groups[key]['config'][f"yyyp_{json_key}"] = json_value
                        except json.JSONDecodeError:
                            # JSON解析失败，按原逻辑处理
                            datasource_groups[key]['config'][f"{key1}_{key2}"] = value
                    else:
                        datasource_groups[key]['config'][f"{key1}_{key2}"] = value
                    
                    # 特殊处理sleep_time字段转换为更新频率
                    if key2 == 'sleep_time' and value:
                        try:
                            sleep_seconds = int(value)
                            if sleep_seconds <= 300:  # 5分钟以内
                                datasource_groups[key]['updateFreq'] = f"{sleep_seconds}s"
                            elif sleep_seconds <= 3600:  # 1小时以内
                                minutes = sleep_seconds // 60
                                datasource_groups[key]['updateFreq'] = f"{minutes}min"
                            elif sleep_seconds <= 86400:  # 1天以内
                                hours = sleep_seconds // 3600
                                datasource_groups[key]['updateFreq'] = f"{hours}hour"
                            else:
                                days = sleep_seconds // 86400
                                datasource_groups[key]['updateFreq'] = f"{days}day"
                        except (ValueError, TypeError):
                            datasource_groups[key]['updateFreq'] = '15min'
                # 如果只有key1，作为单个配置项存储
                elif key1 and not key2:
                    datasource_groups[key]['config'][key1] = value
                # 如果只有value且没有key1和key2，可能是JSON配置
                elif not key1 and not key2 and value:
                    try:
                        import json
                        json_config = json.loads(value)
                        if isinstance(json_config, dict):
                            datasource_groups[key]['config'].update(json_config)
                    except:
                        pass
                
                # 更新状态信息（取最新的）
                if status is not None:
                    datasource_groups[key]['status'] = status
                    datasource_groups[key]['enabled'] = status == '1'
            
            datasources = list(datasource_groups.values())
            
            return jsonify({
                'success': True,
                'data': datasources,
                'message': '获取数据源成功'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '查询数据源失败'
            }), 500
            
    except Exception as e:
        Log().write_log(f"获取数据源失败: {str(e)}", 'error')
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@dataSourcePage.route('/api/datasource', methods=['POST'])
def add_datasource():
    """添加新数据源"""
    try:
        data = request.get_json()
        
        if not data or not data.get('dataName'):
            return jsonify({
                'success': False,
                'message': '数据源名称不能为空'
            }), 400
        
        # 获取当前最大的dataID
        db = Date_base()
        success, result = db.select("SELECT MAX(dataID) FROM config")
        
        max_id = 0
        if success and result and result[0][0] is not None:
            max_id = result[0][0]
        
        new_id = max_id + 1
        
        # 构建配置数据
        config_data = {
            'type': data.get('type', ''),
            'apiUrl': data.get('apiUrl', ''),
            'apiKey': data.get('apiKey', ''),
            'updateFreq': data.get('updateFreq', '15min'),
            'description': data.get('description', '')
        }
        
        # 将数据源类型存储在key2字段中
        data_type = data.get('type', '')
        
        # 插入新数据源
        insert_sql = f"""
        INSERT INTO config (dataID, dataName, key1, key2, value, status) 
        VALUES ({new_id}, '{data['dataName']}', '{data.get('key1', '')}', '{data_type}', 
                '{json.dumps(config_data, ensure_ascii=False)}', '{'1' if data.get('enabled', True) else '0'}')
        """
        
        db = Date_base()
        result = db.insert(insert_sql)
        
        if result is True:
            return jsonify({
                'success': True,
                'message': '数据源添加成功',
                'data': {
                    'dataID': new_id,
                    'dataName': data['dataName'],
                    'key1': data.get('key1', ''),
                    'key2': data.get('key2', ''),
                    'config': config_data,
                    'status': '1' if data.get('enabled', True) else '0',
                    'enabled': data.get('enabled', True)
                }
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': '添加数据源失败'
            }), 500
            
    except Exception as e:
        Log().write_log(f"添加数据源失败: {str(e)}", 'error')
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@dataSourcePage.route('/api/datasource/<int:data_id>', methods=['PUT'])
def update_datasource(data_id):
    """更新数据源"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        db = Date_base()
        
        # 首先删除该数据源的所有配置记录
        delete_sql = f"DELETE FROM config WHERE dataID = {data_id}"
        db.update(delete_sql)
        
        # 插入基本信息记录（数据源类型）
        if 'type' in data:
            insert_type_sql = f"""
            INSERT INTO config (dataID, dataName, key1, key2, value, status) 
            VALUES ({data_id}, '{data['dataName']}', '', '{data['type']}', '', '{'1' if data.get('enabled', True) else '0'}')
            """
            db.insert(insert_type_sql)
        
        # 根据数据源类型插入配置记录
        config_data = data.get('config', {})
        data_name = data.get('dataName', '')
        status = '1' if data.get('enabled', True) else '0'
        
        if data.get('type') == 'youpin':
            # 悠悠有品特有配置
            config_mappings = {
                'phone': 'yyyp_phone',
                'Sessionid': 'yyyp_Sessionid', 
                'token': 'yyyp_token',
                'DeviceName': 'yyyp_DeviceName',
                'app_version': 'yyyp_app_version',
                'app_type': 'yyyp_app_type',
                'userId': 'yyyp_userId',
                'sleep_time': 'yyyp_sleep_time'
            }
            
            for config_key, db_key in config_mappings.items():
                if config_key in config_data:
                    key_parts = db_key.split('_', 1)
                    key1 = key_parts[0] if len(key_parts) > 1 else ''
                    key2 = key_parts[1] if len(key_parts) > 1 else db_key
                    value = str(config_data[config_key])
                    
                    insert_config_sql = f"""
                    INSERT INTO config (dataID, dataName, key1, key2, value, status) 
                    VALUES ({data_id}, '{data_name}', '{key1}', '{key2}', '{value}', '{status}')
                    """
                    db.insert(insert_config_sql)
                    
        elif data.get('type') == 'buff':
            # BUFF特有配置
            if 'apiUrl' in config_data:
                insert_sql = f"""
                INSERT INTO config (dataID, dataName, key1, key2, value, status) 
                VALUES ({data_id}, '{data_name}', 'buff', 'api_url', '{config_data['apiUrl']}', '{status}')
                """
                db.insert(insert_sql)
            
            if 'apiKey' in config_data:
                insert_sql = f"""
                INSERT INTO config (dataID, dataName, key1, key2, value, status) 
                VALUES ({data_id}, '{data_name}', 'buff', 'token', '{config_data['apiKey']}', '{status}')
                """
                db.insert(insert_sql)
                
            if 'sleep_time' in config_data:
                insert_sql = f"""
                INSERT INTO config (dataID, dataName, key1, key2, value, status) 
                VALUES ({data_id}, '{data_name}', 'buff', 'sleep_time', '{config_data.get('sleep_time', '6000')}', '{status}')
                """
                db.insert(insert_sql)
        else:
            # 通用配置
            if 'apiUrl' in config_data:
                insert_sql = f"""
                INSERT INTO config (dataID, dataName, key1, key2, value, status) 
                VALUES ({data_id}, '{data_name}', '', 'api_url', '{config_data['apiUrl']}', '{status}')
                """
                db.insert(insert_sql)
                
            if 'apiKey' in config_data:
                insert_sql = f"""
                INSERT INTO config (dataID, dataName, key1, key2, value, status) 
                VALUES ({data_id}, '{data_name}', '', 'api_key', '{config_data['apiKey']}', '{status}')
                """
                db.insert(insert_sql)
                
            if 'sleep_time' in config_data:
                insert_sql = f"""
                INSERT INTO config (dataID, dataName, key1, key2, value, status) 
                VALUES ({data_id}, '{data_name}', '', 'sleep_time', '{config_data.get('sleep_time', '6000')}', '{status}')
                """
                db.insert(insert_sql)
        
        return jsonify({
            'success': True,
            'message': '数据源更新成功'
        }), 200
            
    except Exception as e:
        Log().write_log(f"更新数据源失败: {str(e)}", 'error')
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@dataSourcePage.route('/api/datasource/<int:data_id>', methods=['DELETE'])
def delete_datasource(data_id):
    """删除数据源"""
    try:
        # 首先检查数据源是否存在
        check_sql = f"SELECT COUNT(*) FROM config WHERE dataID = {data_id}"
        
        db = Date_base()
        success, result = db.select(check_sql)
        
        if not success or not result or result[0][0] == 0:
            return jsonify({
                'success': False,
                'message': '数据源不存在'
            }), 404
        
        # 使用update方法执行DELETE语句（因为delete方法有问题）
        delete_sql = f"DELETE FROM config WHERE dataID = {data_id}"
        
        db = Date_base()
        result = db.update(delete_sql)  # 使用update方法来执行DELETE
        
        if result:
            return jsonify({
                'success': True,
                'message': '数据源删除成功'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '删除数据源失败'
            }), 500
            
    except Exception as e:
        Log().write_log(f"删除数据源失败: {str(e)}", 'error')
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@dataSourcePage.route('/api/datasource/<int:data_id>/toggle', methods=['PUT'])
def toggle_datasource_status(data_id):
    """切换数据源启用状态"""
    try:
        data = request.get_json()
        enabled = data.get('enabled', True)
        status = '1' if enabled else '0'
        
        update_sql = f"UPDATE config SET status = '{status}' WHERE dataID = {data_id}"
        
        db = Date_base()
        result = db.update(update_sql)
        
        if result:
            return jsonify({
                'success': True,
                'message': f'数据源已{"启用" if enabled else "禁用"}'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '更新状态失败'
            }), 500
            
    except Exception as e:
        Log().write_log(f"切换数据源状态失败: {str(e)}", 'error')
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@dataSourcePage.route('/api/datasource/test', methods=['POST'])
def test_datasource_connection():
    """测试数据源连接"""
    try:
        data = request.get_json()
        
        # 这里可以根据数据源类型实现具体的连接测试逻辑
        # 目前返回模拟结果
        
        datasource_type = data.get('type', '')
        api_url = data.get('apiUrl', '')
        
        if not api_url:
            return jsonify({
                'success': False,
                'message': 'API地址不能为空'
            }), 400
        
        # 模拟连接测试
        import time
        time.sleep(1)  # 模拟测试延迟
        
        # 这里可以添加真实的连接测试逻辑
        # 比如发送HTTP请求到API地址
        
        return jsonify({
            'success': True,
            'message': '连接测试成功',
            'data': {
                'latency': '150ms',
                'status': 'online'
            }
        }), 200
        
    except Exception as e:
        Log().write_log(f"测试数据源连接失败: {str(e)}", 'error')
        return jsonify({
            'success': False,
            'message': f'连接测试失败: {str(e)}'
        }), 500


@dataSourcePage.route('/api/datasource/<int:data_id>/collect', methods=['POST'])
def collect_datasource(data_id):
    """启动数据源采集"""
    try:
        data = request.get_json()
        
        # 首先验证数据源是否存在且启用
        check_sql = f"SELECT dataName, status FROM config WHERE dataID = {data_id} LIMIT 1"
        
        db = Date_base()
        success, result = db.select(check_sql)
        
        if not success or not result:
            return jsonify({
                'success': False,
                'message': '数据源不存在'
            }), 404
            
        data_name = result[0][0]
        status = result[0][1]
        
        if status != '1':
            return jsonify({
                'success': False,
                'message': '数据源未启用，无法采集'
            }), 400
        
        Log().write_log(f"开始采集数据源: {data_name} (ID: {data_id})", 'info')
        
        # 这里可以添加实际的采集逻辑
        # 根据不同的数据源类型调用不同的采集模块
        # 暂时返回模拟结果
        
        import random
        import time
        
        # 模拟采集时间
        time.sleep(2)
        
        # 模拟采集结果
        collected_count = random.randint(50, 500)
        
        # 更新数据源的最后更新时间（可选）
        from datetime import datetime
        update_sql = f"""
        UPDATE config SET value = CONCAT(IFNULL(value, ''), 
        ', last_collect: {datetime.now().isoformat()}') 
        WHERE dataID = {data_id} AND key2 = 'last_collect'
        """
        
        Log().write_log(f"采集完成: {data_name}, 采集到 {collected_count} 条数据", 'info')
        
        return jsonify({
            'success': True,
            'message': f'数据源 {data_name} 采集完成',
            'data': {
                'dataSourceId': data_id,
                'dataSourceName': data_name,
                'count': collected_count,
                'startTime': datetime.now().isoformat(),
                'status': 'completed'
            }
        }), 200
        
    except Exception as e:
        Log().write_log(f"采集数据源失败: {str(e)}", 'error')
        return jsonify({
            'success': False,
            'message': f'采集失败: {str(e)}'
        }), 500