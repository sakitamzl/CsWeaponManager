from flask import Blueprint, jsonify, request
from src.execution_db import Date_base
from src.log import Log
from src.Unites.auto_process.task_scheduler import get_scheduler
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
        
        success, results = db.select(query_sql)
        
        tasks = []
        if success and results:
            for row in results:
                try:
                    # 解析 value 字段中的 JSON 配置
                    config = json.loads(row[3]) if row[3] else {}
                    
                    # 从配置中提取执行时间
                    last_run = config.get('lastRun', None)
                    next_run = config.get('nextRun', None)
                    
                    tasks.append({
                        'taskId': row[0],
                        'taskName': row[1],
                        'automateType': row[2],  # key1 存储自动化类型
                        'config': config,
                        'enabled': row[4] == '1',
                        'lastRun': last_run,
                        'nextRun': next_run
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
        
        task_name = data.get('taskName', '').replace("'", "''")
        automate_type = data.get('automateType', '').replace("'", "''")  # auto_update 或 auto_fetch
        config_data = data.get('config', {})
        enabled = '1' if data.get('enabled', True) else '0'
        
        # 将配置转换为 JSON 字符串
        config_json = json.dumps(config_data, ensure_ascii=False)
        config_json_escaped = config_json.replace("'", "''")
        
        # 插入数据 (dataID自增,不需要手动指定)
        insert_sql = f"""
        INSERT INTO config (dataName, key1, key2, value, status) 
        VALUES ('{task_name}', '{automate_type}', 'auto_manager', '{config_json_escaped}', '{enabled}')
        """
        
        result = db.insert(insert_sql)
        
        if result:
            # 获取刚插入的ID
            success, last_id_result = db.select("SELECT last_insert_rowid()")
            new_id = last_id_result[0][0] if success and last_id_result else None
            
            # 如果任务启用,立即启动后台调度
            if enabled == '1':
                scheduler = get_scheduler()
                scheduler.start_task(new_id, task_name, automate_type, config_data)
            
            Log().write_log(f"创建自动化任务成功: {task_name}, ID: {new_id}", 'info')
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
            # 重新加载任务(会根据状态决定是否启动)
            scheduler = get_scheduler()
            scheduler.reload_task(task_id)
            
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
        
        # 先停止后台任务(在删除数据库记录之前)
        try:
            scheduler = get_scheduler()
            scheduler.stop_task(task_id)
        except Exception as e:
            Log().write_log(f"停止任务失败 (taskId={task_id}): {str(e)}", 'warning')
        
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
                'message': '任务删除失败,可能任务不存在'
            }), 404
            
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
        from datetime import datetime, timedelta
        
        db = Date_base()
        
        # 查询当前状态和配置
        query_sql = f"SELECT status, value FROM config WHERE dataID = {task_id} AND key2 = 'auto_manager'"
        success, result = db.select(query_sql)
        
        if not success or not result:
            return jsonify({
                'success': False,
                'message': '任务不存在'
            }), 404
        
        current_status = result[0][0]
        new_status = '0' if current_status == '1' else '1'
        
        # 如果是启动任务,需要设置下次执行时间
        if new_status == '1':
            try:
                # 解析配置获取执行间隔
                config = json.loads(result[0][1]) if result[0][1] else {}
                interval = config.get('interval', 30)  # 分钟
                
                # 计算下次执行时间(立即执行,设置为当前时间)
                next_run = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                config['nextRun'] = next_run
                
                # 更新配置
                config_json = json.dumps(config, ensure_ascii=False).replace("'", "''")
                update_sql = f"""
                UPDATE config 
                SET status = '{new_status}', value = '{config_json}' 
                WHERE dataID = {task_id} AND key2 = 'auto_manager'
                """
            except Exception as e:
                Log().write_log(f"设置下次执行时间失败: {str(e)}", 'error')
                # 如果失败,仍然更新状态
                update_sql = f"UPDATE config SET status = '{new_status}' WHERE dataID = {task_id} AND key2 = 'auto_manager'"
        else:
            # 停止任务,只更新状态
            update_sql = f"UPDATE config SET status = '{new_status}' WHERE dataID = {task_id} AND key2 = 'auto_manager'"
        
        update_result = db.update(update_sql)
        
        if update_result:
            # 重新查询任务以获取最新的执行时间
            query_sql = f"SELECT value FROM config WHERE dataID = {task_id} AND key2 = 'auto_manager'"
            success, result = db.select(query_sql)
            
            next_run = None
            last_run = None
            if success and result and result[0][0]:
                try:
                    config = json.loads(result[0][0])
                    next_run = config.get('nextRun')
                    last_run = config.get('lastRun')
                except:
                    pass
            
            Log().write_log(f"切换自动化任务状态成功: taskId={task_id}, newStatus={new_status}", 'info')
            
            # 重新加载调度器中的任务
            try:
                from src.Unites.auto_process.task_scheduler import get_scheduler
                scheduler = get_scheduler()
                scheduler.reload_task(task_id)
            except Exception as e:
                Log().write_log(f"重新加载调度器任务失败: {str(e)}", 'warning')
            
            return jsonify({
                'success': True,
                'message': '状态切换成功',
                'enabled': new_status == '1',
                'nextRun': next_run,
                'lastRun': last_run
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

