from flask import Blueprint, jsonify, request
from src.execution_db import Date_base
from src.log import Log
import json

autoManagerPage = Blueprint('autoManagerPage', __name__)

@autoManagerPage.route('/api/auto-manager/tasks', methods=['GET'])
def get_auto_manager_tasks():
    """获取所有自动化管理任务配置"""
    try:
        db = Date_base()
        
        # 查询所有 key2 = 'auto_manager' 的配置
        query_sql = """
        SELECT dataID, dataName, key1, value, status 
        FROM config 
        WHERE key2 = 'auto_manager'
        ORDER BY dataID DESC
        """
        
        results = db.select(query_sql)
        
        tasks = []
        if results:
            for row in results:
                try:
                    # 解析 value 字段中的 JSON 配置
                    config = json.loads(row[3]) if row[3] else {}
                    
                    tasks.append({
                        'taskId': row[0],
                        'taskName': row[1],
                        'automateType': row[2],  # key1 存储自动化类型
                        'config': config,
                        'enabled': row[4] == '1'
                    })
                except json.JSONDecodeError as e:
                    Log().write_log(f"解析任务配置失败 (dataID={row[0]}): {e}", 'error')
                    continue
        
        return jsonify({
            'success': True,
            'data': tasks
        }), 200
        
    except Exception as e:
        Log().write_log(f"获取自动化管理任务失败: {str(e)}", 'error')
        return jsonify({
            'success': False,
            'message': f'获取任务失败: {str(e)}'
        }), 500


@autoManagerPage.route('/api/auto-manager/task', methods=['POST'])
def create_auto_manager_task():
    """创建新的自动化管理任务"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        db = Date_base()
        
        # 获取最大的 dataID
        max_id_sql = "SELECT MAX(dataID) FROM config"
        max_id_result = db.select(max_id_sql)
        new_id = (max_id_result[0][0] or 0) + 1 if max_id_result else 1
        
        task_name = data.get('taskName', '').replace("'", "''")
        automate_type = data.get('automateType', '').replace("'", "''")  # auto_update 或 auto_fetch
        config_data = data.get('config', {})
        enabled = '1' if data.get('enabled', True) else '0'
        
        # 将配置转换为 JSON 字符串
        config_json = json.dumps(config_data, ensure_ascii=False)
        config_json_escaped = config_json.replace("'", "''")
        
        # 插入数据
        insert_sql = f"""
        INSERT INTO config (dataID, dataName, key1, key2, value, status) 
        VALUES ({new_id}, '{task_name}', '{automate_type}', 'auto_manager', '{config_json_escaped}', '{enabled}')
        """
        
        result = db.insert(insert_sql)
        
        if result:
            Log().write_log(f"创建自动化任务成功: {task_name}", 'info')
            return jsonify({
                'success': True,
                'message': '任务创建成功',
                'taskId': new_id
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '任务创建失败'
            }), 500
            
    except Exception as e:
        Log().write_log(f"创建自动化任务失败: {str(e)}", 'error')
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@autoManagerPage.route('/api/auto-manager/task/<int:task_id>', methods=['PUT'])
def update_auto_manager_task(task_id):
    """更新自动化管理任务"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        db = Date_base()
        
        task_name = data.get('taskName', '').replace("'", "''")
        automate_type = data.get('automateType', '').replace("'", "''")
        config_data = data.get('config', {})
        enabled = '1' if data.get('enabled', True) else '0'
        
        # 将配置转换为 JSON 字符串
        config_json = json.dumps(config_data, ensure_ascii=False)
        config_json_escaped = config_json.replace("'", "''")
        
        # 更新数据
        update_sql = f"""
        UPDATE config 
        SET dataName = '{task_name}', key1 = '{automate_type}', value = '{config_json_escaped}', status = '{enabled}' 
        WHERE dataID = {task_id} AND key2 = 'auto_manager'
        """
        
        result = db.update(update_sql)
        
        if result:
            Log().write_log(f"更新自动化任务成功: {task_name}", 'info')
            return jsonify({
                'success': True,
                'message': '任务更新成功'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '任务更新失败'
            }), 500
            
    except Exception as e:
        Log().write_log(f"更新自动化任务失败: {str(e)}", 'error')
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@autoManagerPage.route('/api/auto-manager/task/<int:task_id>', methods=['DELETE'])
def delete_auto_manager_task(task_id):
    """删除自动化管理任务"""
    try:
        db = Date_base()
        
        # 删除数据
        delete_sql = f"DELETE FROM config WHERE dataID = {task_id} AND key2 = 'auto_manager'"
        
        result = db.delete(delete_sql)
        
        if result:
            Log().write_log(f"删除自动化任务成功: taskId={task_id}", 'info')
            return jsonify({
                'success': True,
                'message': '任务删除成功'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '任务删除失败'
            }), 500
            
    except Exception as e:
        Log().write_log(f"删除自动化任务失败: {str(e)}", 'error')
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500


@autoManagerPage.route('/api/auto-manager/task/<int:task_id>/toggle', methods=['POST'])
def toggle_auto_manager_task(task_id):
    """切换自动化管理任务的启用状态"""
    try:
        db = Date_base()
        
        # 查询当前状态
        query_sql = f"SELECT status FROM config WHERE dataID = {task_id} AND key2 = 'auto_manager'"
        result = db.select(query_sql)
        
        if not result:
            return jsonify({
                'success': False,
                'message': '任务不存在'
            }), 404
        
        current_status = result[0][0]
        new_status = '0' if current_status == '1' else '1'
        
        # 更新状态
        update_sql = f"UPDATE config SET status = '{new_status}' WHERE dataID = {task_id} AND key2 = 'auto_manager'"
        
        update_result = db.update(update_sql)
        
        if update_result:
            Log().write_log(f"切换自动化任务状态成功: taskId={task_id}, newStatus={new_status}", 'info')
            return jsonify({
                'success': True,
                'message': '状态切换成功',
                'enabled': new_status == '1'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '状态切换失败'
            }), 500
            
    except Exception as e:
        Log().write_log(f"切换自动化任务状态失败: {str(e)}", 'error')
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500

