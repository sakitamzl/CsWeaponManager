"""
自动化管理数据模块
提供任务的 CRUD 操作
"""
from flask import jsonify, request
from src.units.log import Log
from src.db_manager.database import DatabaseManager
from src.units.execution_db import Date_base
from src.units.auto_process.task_scheduler import get_scheduler
import json


class AutoManagerData:
    """自动化管理数据类 - 提供任务 CRUD 操作"""

    @staticmethod
    def get_task_list():
        """获取所有自动化管理任务配置"""
        try:
            db = DatabaseManager()

            query_sql = """
            SELECT dataID, dataName, key1, value, status
            FROM config
            WHERE key2 = 'auto_manager'
            ORDER BY dataID DESC
            """

            results = db.execute_query(query_sql, ())

            tasks = []
            if results:
                for row in results:
                    try:
                        config = json.loads(row[3]) if row[3] else {}

                        last_run = config.get('lastRun', None)
                        next_run = config.get('nextRun', None)

                        tasks.append({
                            'taskId': row[0],
                            'taskName': row[1],
                            'automateType': row[2],
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

    @staticmethod
    def create_task():
        """创建新的自动化管理任务"""
        try:
            data = request.get_json()

            if not data:
                return jsonify({
                    'success': False,
                    'message': '请求数据不能为空'
                }), 400

            db = DatabaseManager()

            task_name = data.get('taskName', '').replace("'", "''")
            automate_type = data.get('automateType', '').replace("'", "''")
            config_data = data.get('config', {})
            enabled = '1' if data.get('enabled', True) else '0'

            config_json = json.dumps(config_data, ensure_ascii=False)
            config_json_escaped = config_json.replace("'", "''")

            insert_sql = f"""
            INSERT INTO config (dataName, key1, key2, value, status)
            VALUES ('{task_name}', '{automate_type}', 'auto_manager', '{config_json_escaped}', '{enabled}')
            """

            ok = Date_base().insert(insert_sql)

            if ok is True:
                last_id_result = db.execute_query("SELECT last_insert_rowid()", ())
                new_id = last_id_result[0][0] if last_id_result else None

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

    @staticmethod
    def update_task(task_id):
        """更新自动化管理任务"""
        try:
            data = request.get_json()

            if not data:
                return jsonify({
                    'success': False,
                    'message': '请求数据不能为空'
                }), 400

            db = DatabaseManager()

            task_name = data.get('taskName', '').replace("'", "''")
            automate_type = data.get('automateType', '').replace("'", "''")
            config_data = data.get('config', {})
            enabled = '1' if data.get('enabled', True) else '0'

            config_json = json.dumps(config_data, ensure_ascii=False)
            config_json_escaped = config_json.replace("'", "''")

            update_sql = f"""
            UPDATE config
            SET dataName = '{task_name}', key1 = '{automate_type}', value = '{config_json_escaped}', status = '{enabled}'
            WHERE dataID = {task_id} AND key2 = 'auto_manager'
            """

            ok = Date_base().update(update_sql)

            if ok is True:
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

    @staticmethod
    def delete_task(task_id):
        """删除自动化管理任务"""
        try:
            db = DatabaseManager()

            # 先停止后台任务
            try:
                scheduler = get_scheduler()
                scheduler.stop_task(task_id)
            except Exception as e:
                Log().write_log(f"停止任务失败 (taskId={task_id}): {str(e)}", 'warning')

            delete_sql = f"DELETE FROM config WHERE dataID = {task_id} AND key2 = 'auto_manager'"

            ok = Date_base().update(delete_sql)

            if ok is True:
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
