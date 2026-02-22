from flask import jsonify, request, Blueprint
from src.log import Log
from src.execution_db import Date_base
from src.read_conf import read_conf
from src.db_manager.index.model.config import ConfigModel
from src.db_manager.index.model.auto_search_weapon import AutoSearchWeaponModel
import requests
import json


configV1 = Blueprint('configV1', __name__)

def get_database_name():
    conf = read_conf()
    return conf.get_database_name()


@configV1.route('/config_v1/<key1>/<key2>/<value>', methods=['post'])
def updata_config(key1, key2, value):
    database_name = get_database_name()
    sql = f"UPDATE config SET value = '{value}' WHERE key1 = '{key1}' AND key2 = '{key2}';"
    Date_base().update(sql)
    return '更新成功', 200

@configV1.route('/get_config/<key1>/<key2>', methods=['post'])
def get_yyyp_config(key1, key2):
    database_name = get_database_name()
    sql = f"SELECT value FROM config WHERE key1 = '{key1}' and key2 = '{key2}'"
    flag, data = Date_base().select(sql)
    return jsonify(data), 200

@configV1.route('/save', methods=['POST'])
def save_config():
    """保存或更新配置"""
    try:
        data = request.get_json()
        data_name = data.get('dataName')
        key1 = data.get('key1')
        key2 = data.get('key2')
        value = data.get('value')
        
        if not all([data_name, key1, key2, value]):
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400
        
        # 转义单引号，防止 SQL 错误
        data_name_escaped = data_name.replace("'", "''")
        key1_escaped = key1.replace("'", "''")
        key2_escaped = key2.replace("'", "''")
        value_escaped = value.replace("'", "''")
        
        # 检查是否存在同名配置
        sql = f"SELECT dataID, dataName, key1, key2, value FROM config WHERE dataName = '{data_name_escaped}' AND key1 = '{key1_escaped}' AND key2 = '{key2_escaped}'"
        flag, existing = Date_base().select(sql)
        
        if flag and existing and len(existing) > 0:
            # 更新现有配置，existing[0] 是元组，第一个字段是 dataID
            dataID = existing[0][0]
            Log().write_log(f"更新现有配置，dataID: {dataID}", 'info')
            update_sql = f"""
                UPDATE config 
                SET value = '{value_escaped}' 
                WHERE dataID = {dataID}
            """
            Date_base().update(update_sql)
        else:
            # 插入新配置
            insert_sql = f"""
                INSERT INTO config (dataName, key1, key2, value, status) 
                VALUES ('{data_name_escaped}', '{key1_escaped}', '{key2_escaped}', '{value_escaped}', '1')
            """
            Date_base().insert(insert_sql)
        
        return jsonify({
            'success': True,
            'message': '保存成功'
        }), 200
        
    except Exception as e:
        Log().write_log(f"保存配置失败: {str(e)}", 'error')
        return jsonify({
            'success': False,
            'message': f'保存失败: {str(e)}'
        }), 500

@configV1.route('/update', methods=['POST'])
def update_config():
    """更新现有配置"""
    try:
        data = request.get_json() or {}
        config_id = data.get('id')
        data_name = data.get('dataName')
        key1 = data.get('key1')
        key2 = data.get('key2')
        value = data.get('value')

        if not config_id:
            return jsonify({
                'success': False,
                'message': '缺少配置ID'
            }), 400

        try:
            config_id = int(config_id)
        except (TypeError, ValueError):
            return jsonify({
                'success': False,
                'message': '配置ID必须为整数'
            }), 400

        if not all([data_name, key1, key2, value]):
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400

        # 检查配置是否存在
        select_sql = f"SELECT dataID FROM config WHERE dataID = {config_id}"
        flag, existing = Date_base().select(select_sql)
        if not (flag and existing):
            return jsonify({
                'success': False,
                'message': '配置不存在或已被删除'
            }), 404

        # 转义单引号
        data_name_escaped = data_name.replace("'", "''")
        key1_escaped = key1.replace("'", "''")
        key2_escaped = key2.replace("'", "''")
        value_escaped = value.replace("'", "''")

        update_sql = f"""
            UPDATE config
            SET dataName = '{data_name_escaped}',
                key1 = '{key1_escaped}',
                key2 = '{key2_escaped}',
                value = '{value_escaped}'
            WHERE dataID = {config_id}
        """
        Date_base().update(update_sql)

        Log().write_log(f"更新配置成功，dataID: {config_id}", 'info')
        return jsonify({
            'success': True,
            'message': '更新成功',
            'data': {
                'id': config_id
            }
        }), 200

    except Exception as e:
        Log().write_log(f"更新配置失败: {str(e)}", 'error')
        return jsonify({
            'success': False,
            'message': f'更新失败: {str(e)}'
        }), 500

@configV1.route('/list', methods=['GET'])
def list_configs():
    """获取配置列表"""
    try:
        key1 = request.args.get('key1')
        key2 = request.args.get('key2')
        
        # 构建WHERE条件
        where_conditions = []
        if key1:
            where_conditions.append(f"key1 = '{key1}'")
        if key2:
            where_conditions.append(f"key2 = '{key2}'")
        
        if not where_conditions:
            return jsonify({
                'success': False,
                'message': '至少需要提供 key1 或 key2 参数'
            }), 400
        
        where_clause = ' AND '.join(where_conditions)
        
        sql = f"""
            SELECT dataID, dataName, key1, key2, value, status, steamID, 
                   datetime('now') as updated_at
            FROM config 
            WHERE {where_clause}
            ORDER BY dataID DESC
        """
        flag, result = Date_base().select(sql)
        
        # 将元组列表转换为字典列表
        data = []
        if result:
            for row in result:
                data.append({
                    'id': row[0],           # dataID
                    'dataName': row[1],     # dataName
                    'key1': row[2],         # key1
                    'key2': row[3],         # key2
                    'value': row[4],        # value
                    'status': row[5],       # status
                    'steamID': row[6],      # steamID
                    'updated_at': row[7]    # updated_at
                })
        
        return jsonify({
            'success': True,
            'data': data
        }), 200
        
    except Exception as e:
        Log().write_log(f"获取配置列表失败: {str(e)}", 'error')
        return jsonify({
            'success': False,
            'message': f'获取失败: {str(e)}'
        }), 500

@configV1.route('/delete/<int:config_id>', methods=['DELETE'])
def delete_config(config_id):
    """删除配置，同时清理相关的搜索结果数据"""
    try:
        # 先清理 auto_search_weapon 表中相关的数据（硬删除）
        try:
            from src.execution_db import DatabaseManager
            
            db = DatabaseManager()
            table_name = AutoSearchWeaponModel.get_table_name()
            
            # 先统计要删除的记录数
            count_sql = f"SELECT COUNT(*) FROM {table_name} WHERE config_id = ?"
            count_result = db.execute_query(count_sql, (config_id,))
            count = count_result[0][0] if count_result else 0
            
            if count > 0:
                # 硬删除：直接删除记录
                delete_sql = f"DELETE FROM {table_name} WHERE config_id = ?"
                db.execute_update(delete_sql, (config_id,))
                
                Log().write_log(
                    f"删除配置 {config_id} 时，已删除 {count} 条相关搜索结果数据",
                    'info'
                )
            else:
                Log().write_log(
                    f"删除配置 {config_id} 时，未找到相关搜索结果数据",
                    'info'
                )
        except Exception as cleanup_error:
            # 清理数据失败不影响配置删除，只记录日志
            Log().write_log(
                f"清理配置 {config_id} 的搜索结果数据时出错: {str(cleanup_error)}",
                'warning'
            )
        
        # 删除配置
        sql = f"DELETE FROM config WHERE dataID = {config_id}"
        Date_base().delete(sql)
        
        return jsonify({
            'success': True,
            'message': '删除成功'
        }), 200
        
    except Exception as e:
        Log().write_log(f"删除配置失败: {str(e)}", 'error')
        return jsonify({
            'success': False,
            'message': f'删除失败: {str(e)}'
        }), 500
