"""
数据源 CRUD 操作模块
提供数据源的增删改查功能
"""
from flask import jsonify, request
from src.units.log import Log
from src.units.execution_db import Date_base
import json
from datetime import datetime


class DataSourceData:
    """数据源数据管理类 - 提供 CRUD 操作"""

    @staticmethod
    def get_data_source_list():
        """获取所有数据源"""
        try:
            db = Date_base()

            # 只查询key2='config'的配置记录，过滤掉其他配置项
            try:
                success, result = db.select(
                    "SELECT dataID, dataName, key1, key2, value, status, steamID "
                    "FROM config WHERE key2 = 'config' ORDER BY dataID"
                )
                has_steam_id_column = True
            except Exception as e:
                print(f"[WARNING] steamID列可能不存在，使用备用查询: {e}")
                success, result = db.select(
                    "SELECT dataID, dataName, key1, key2, value, status "
                    "FROM config WHERE key2 = 'config' ORDER BY dataID"
                )
                has_steam_id_column = False

            if success:
                # 按dataID和dataName分组数据
                datasource_groups = {}
                for row in result:
                    if has_steam_id_column:
                        data_id, data_name, key1, key2, value, status, steam_id = row
                    else:
                        data_id, data_name, key1, key2, value, status = row
                        steam_id = None

                    # 创建唯一键
                    key = f"{data_id}_{data_name}"

                    if key not in datasource_groups:
                        data_source_type = key1 if key1 else 'unknown'
                        datasource_groups[key] = {
                            'dataID': data_id,
                            'dataName': data_name,
                            'type': data_source_type,
                            'config': {},
                            'status': status,
                            'enabled': status == '1',
                            'lastUpdate': None,
                            'updateFreq': '15min',
                            'steamID': ''
                        }

                    # 如果steamID字段有值，直接使用
                    if steam_id:
                        datasource_groups[key]['steamID'] = steam_id

                    # 确保每次都更新数据源类型
                    if key1:
                        datasource_groups[key]['type'] = key1

                    # 如果key2是'config'，说明value存储的是JSON配置
                    if key2 == 'config' and value:
                        try:
                            config_json = json.loads(value)
                            if isinstance(config_json, dict):
                                # 如果steamID字段为空，尝试从config中提取
                                if not datasource_groups[key]['steamID']:
                                    extracted_steam_id = (
                                        config_json.get('steamID') or
                                        config_json.get('steamId') or
                                        config_json.get('yyyp_steamId') or ''
                                    )
                                    if extracted_steam_id:
                                        datasource_groups[key]['steamID'] = extracted_steam_id

                                # 提取lastUpdate时间
                                if 'lastUpdate' in config_json and config_json['lastUpdate']:
                                    datasource_groups[key]['lastUpdate'] = config_json['lastUpdate']
                                else:
                                    # 如果旧数据没有lastUpdate，自动添加并更新到数据库
                                    current_time = datetime.now().isoformat()
                                    datasource_groups[key]['lastUpdate'] = current_time
                                    config_json['lastUpdate'] = current_time

                                    try:
                                        updated_value = json.dumps(config_json).replace("'", "''")
                                        update_sql = (
                                            f"UPDATE config SET value = '{updated_value}' "
                                            f"WHERE dataID = {data_id} AND key2 = 'config'"
                                        )
                                        db.update(update_sql)
                                        print(f"[自动迁移] 为 dataID={data_id} ({data_name}) 添加 lastUpdate: {current_time}")
                                    except Exception as update_error:
                                        print(f"[自动迁移] 更新 lastUpdate 失败: {update_error}")

                                # 为悠悠有品配置添加yyyp_前缀保持前端兼容性
                                if key1 == 'youpin':
                                    for config_key, config_value in config_json.items():
                                        if config_key == 'lastUpdate':
                                            continue
                                        if config_key.startswith('yyyp_'):
                                            datasource_groups[key]['config'][config_key] = config_value
                                        else:
                                            datasource_groups[key]['config'][f"yyyp_{config_key}"] = config_value
                                else:
                                    for config_key, config_value in config_json.items():
                                        if config_key != 'lastUpdate':
                                            datasource_groups[key]['config'][config_key] = config_value
                        except json.JSONDecodeError:
                            pass
                    # 兼容旧的存储格式
                    elif key1 and key2 and key2 != 'config':
                        if key1 == 'youpin':
                            datasource_groups[key]['config'][f"yyyp_{key2}"] = value
                        else:
                            datasource_groups[key]['config'][key2] = value

                        if key2 == 'sleep_time' and value:
                            try:
                                sleep_seconds = int(value)
                                if sleep_seconds <= 300:
                                    datasource_groups[key]['updateFreq'] = f"{sleep_seconds}s"
                                elif sleep_seconds <= 3600:
                                    minutes = sleep_seconds // 60
                                    datasource_groups[key]['updateFreq'] = f"{minutes}min"
                                elif sleep_seconds <= 86400:
                                    hours = sleep_seconds // 3600
                                    datasource_groups[key]['updateFreq'] = f"{hours}hour"
                                else:
                                    days = sleep_seconds // 86400
                                    datasource_groups[key]['updateFreq'] = f"{days}day"
                            except (ValueError, TypeError):
                                datasource_groups[key]['updateFreq'] = '15min'
                    elif key1 and not key2:
                        datasource_groups[key]['config'][key1] = value
                    elif not key1 and not key2 and value:
                        try:
                            json_config = json.loads(value)
                            if isinstance(json_config, dict):
                                datasource_groups[key]['config'].update(json_config)
                        except:
                            pass

                    # 更新状态信息
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

    @staticmethod
    def create_data_source():
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

            data_type = data.get('type', '')
            data_name = data['dataName'].replace("'", "''")
            status = '1' if data.get('enabled', True) else '0'

            config_json = data.get('configJson', '{}')
            config_json_escaped = config_json.replace("'", "''")

            # 从配置JSON中提取steamID
            steam_id = ''
            try:
                config_data = json.loads(config_json)
                steam_id = (
                    config_data.get('steamID') or
                    config_data.get('steamId') or
                    config_data.get('yyyp_steamId') or ''
                )
            except:
                pass
            steam_id_escaped = steam_id.replace("'", "''") if steam_id else ''

            insert_sql = (
                f"INSERT INTO config (dataID, dataName, key1, key2, value, status, steamID) "
                f"VALUES ({new_id}, '{data_name}', '{data_type}', 'config', "
                f"'{config_json_escaped}', '{status}', '{steam_id_escaped}')"
            )

            db = Date_base()
            result = db.insert(insert_sql)

            if not result:
                return jsonify({
                    'success': False,
                    'message': '添加数据源失败'
                }), 500

            return jsonify({
                'success': True,
                'message': '数据源添加成功',
                'data': {
                    'dataID': new_id,
                    'dataName': data['dataName'],
                    'type': data_type,
                    'configJson': config_json,
                    'status': status,
                    'enabled': data.get('enabled', True)
                }
            }), 201

        except Exception as e:
            Log().write_log(f"添加数据源失败: {str(e)}", 'error')
            return jsonify({
                'success': False,
                'message': f'服务器错误: {str(e)}'
            }), 500

    @staticmethod
    def get_data_source_by_id(data_id):
        """获取单个数据源详细信息"""
        try:
            db = Date_base()

            select_sql = (
                f"SELECT dataID, dataName, key1, key2, value, status, steamID "
                f"FROM config WHERE dataID = {data_id} AND key2 = 'config'"
            )
            success, result = db.select(select_sql)

            if not success or not result:
                return jsonify({
                    'success': False,
                    'message': f'未找到 dataID={data_id} 的数据源'
                }), 404

            data_id, data_name, data_type, key2, value, status, steam_id = result[0]

            config_json = {}
            try:
                config_json = json.loads(value) if value else {}
            except:
                pass

            datasource = {
                'dataID': data_id,
                'dataName': data_name,
                'type': data_type,
                'enabled': status == '1',
                'steamID': steam_id or '',
                'config': config_json
            }

            return jsonify({
                'success': True,
                'data': datasource
            }), 200

        except Exception as e:
            Log().write_log(f"获取数据源失败: {str(e)}", 'error')
            return jsonify({
                'success': False,
                'message': f'服务器错误: {str(e)}'
            }), 500

    @staticmethod
    def update_data_source(data_id):
        """更新数据源"""
        try:
            data = request.get_json()

            if not data:
                return jsonify({
                    'success': False,
                    'message': '请求数据不能为空'
                }), 400

            db = Date_base()
            data_name = data.get('dataName', '').replace("'", "''")
            data_type = data.get('type', '')
            status = '1' if data.get('enabled', True) else '0'

            config_json = data.get('configJson', '{}')
            config_json_escaped = config_json.replace("'", "''")

            # 从配置JSON中提取steamID
            steam_id = ''
            try:
                config_data = json.loads(config_json)
                steam_id = (
                    config_data.get('steamID') or
                    config_data.get('steamId') or
                    config_data.get('yyyp_steamId') or ''
                )
            except:
                pass
            steam_id_escaped = steam_id.replace("'", "''") if steam_id else ''

            update_sql = (
                f"UPDATE config "
                f"SET dataName = '{data_name}', key1 = '{data_type}', "
                f"value = '{config_json_escaped}', status = '{status}', "
                f"steamID = '{steam_id_escaped}' "
                f"WHERE dataID = {data_id} AND key2 = 'config'"
            )

            result = db.update(update_sql)

            if not result:
                return jsonify({
                    'success': False,
                    'message': '更新数据源失败'
                }), 500

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

    @staticmethod
    def delete_data_source(data_id):
        """删除数据源"""
        try:
            check_sql = f"SELECT COUNT(*) FROM config WHERE dataID = {data_id}"

            db = Date_base()
            success, result = db.select(check_sql)

            if not success or not result or result[0][0] == 0:
                return jsonify({
                    'success': False,
                    'message': '数据源不存在'
                }), 404

            # 使用update方法执行DELETE语句
            delete_sql = f"DELETE FROM config WHERE dataID = {data_id}"

            db = Date_base()
            result = db.update(delete_sql)

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
