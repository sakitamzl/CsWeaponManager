"""
自动化管理操作模块
提供任务的启停切换和执行状态查询功能
"""
from flask import jsonify
from src.log import Log
from src.execution_db import Date_base
from src.Unites.auto_process.task_scheduler import get_scheduler
import json
from datetime import datetime


class AutoManagerOps:
    """自动化管理操作类 - 提供 toggle + 执行状态查询"""

    @staticmethod
    def toggle_task(task_id):
        """切换自动化管理任务的启用状态"""
        try:
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
                    config = json.loads(result[0][1]) if result[0][1] else {}
                    interval = config.get('interval', 30)

                    # 计算下次执行时间(立即执行,设置为当前时间)
                    next_run = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    config['nextRun'] = next_run

                    config_json = json.dumps(config, ensure_ascii=False).replace("'", "''")
                    update_sql = f"""
                    UPDATE config
                    SET status = '{new_status}', value = '{config_json}'
                    WHERE dataID = {task_id} AND key2 = 'auto_manager'
                    """
                except Exception as e:
                    Log().write_log(f"设置下次执行时间失败: {str(e)}", 'error')
                    update_sql = f"UPDATE config SET status = '{new_status}' WHERE dataID = {task_id} AND key2 = 'auto_manager'"
            else:
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

    @staticmethod
    def get_executing_tasks():
        """获取正在执行的任务列表"""
        try:
            scheduler = get_scheduler()
            executing_tasks = scheduler.get_currently_executing_tasks()

            return jsonify({
                'success': True,
                'data': executing_tasks
            }), 200

        except Exception as e:
            Log().write_log(f"获取正在执行的任务失败: {str(e)}", 'error')
            return jsonify({
                'success': False,
                'message': f'获取失败: {str(e)}'
            }), 500
