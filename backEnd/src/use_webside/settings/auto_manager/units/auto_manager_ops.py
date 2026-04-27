"""
自动化管理操作模块
提供任务的启停切换和执行状态查询功能
"""
from flask import jsonify
from src.units.log import Log
from src.db_manager.database import DatabaseManager
from src.units.execution_db import Date_base
from src.units.auto_process.task_scheduler import get_scheduler
import json
from datetime import datetime


class AutoManagerOps:
    """自动化管理操作类 - 提供 toggle + 执行状态查询"""
    
    @staticmethod
    def _get_config_status(data_id):
        """获取配置状态（config.status）"""
        if not data_id:
            return None
        db = DatabaseManager()
        query_sql = f"SELECT status FROM config WHERE dataID = {int(data_id)}"
        result = db.execute_query(query_sql, ())
        if not result:
            return None
        return str(result[0][0])
    
    @staticmethod
    def _validate_task_source_enabled(automate_type, config):
        """
        校验任务依赖的数据源/账号是否启用
        返回: (is_valid: bool, message: str)
        """
        if not config:
            return False, '任务配置为空,请重新编辑后再启动'
        
        # 更新类/认证类任务依赖 Steam/BUFF/悠悠有品配置
        if automate_type in ['auto_update', 'auto_refresh_auth']:
            source_id = config.get('selectedSteamConfig')
            if not source_id:
                return False, '任务缺少账号配置,请先完善任务配置'
            status = AutoManagerOps._get_config_status(source_id)
            if status != '1':
                return False, '账号数据源未启用，请先开启数据源后再启动任务'
            return True, ''
        
        # 数据采集/平台价格任务依赖数据源配置
        if automate_type in ['auto_fetch', 'auto_platform_price']:
            source_ids = config.get('selectedDataSources') if isinstance(config.get('selectedDataSources'), list) else []
            if not source_ids:
                single_id = config.get('selectedDataSource')
                source_ids = [single_id] if single_id else []
            
            if not source_ids:
                return False, '任务缺少数据源配置,请先完善任务配置'
            
            for source_id in source_ids:
                status = AutoManagerOps._get_config_status(source_id)
                if status != '1':
                    return False, '存在未启用的数据源，请先开启数据源后再启动任务'
            return True, ''
        
        # 自动搜索任务依赖搜索配置
        if automate_type == 'auto_search_weapon':
            source_id = config.get('selectedSearchConfig')
            if not source_id:
                return False, '任务缺少搜索配置,请先完善任务配置'
            status = AutoManagerOps._get_config_status(source_id)
            if status != '1':
                return False, '搜索配置未启用，请先开启数据源后再启动任务'
            return True, ''
        
        return True, ''

    @staticmethod
    def toggle_task(task_id):
        """切换自动化管理任务的启用状态"""
        try:
            db = DatabaseManager()

            # 查询当前状态和配置
            query_sql = f"SELECT status, key1, value FROM config WHERE dataID = {task_id} AND key2 = 'auto_manager'"
            result = db.execute_query(query_sql, ())

            if not result:
                return jsonify({
                    'success': False,
                    'message': '任务不存在'
                }), 404

            current_status = result[0][0]
            automate_type = result[0][1]
            new_status = '0' if current_status == '1' else '1'

            # 如果是启动任务,需要设置下次执行时间
            if new_status == '1':
                try:
                    config = json.loads(result[0][2]) if result[0][2] else {}
                    
                    # 启动前校验依赖数据源状态
                    valid, reason = AutoManagerOps._validate_task_source_enabled(automate_type, config)
                    if not valid:
                        return jsonify({
                            'success': False,
                            'message': reason
                        }), 400
                    
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

            update_result = Date_base().update(update_sql)

            if update_result is True:
                # 重新查询任务以获取最新的执行时间
                query_sql = f"SELECT value FROM config WHERE dataID = {task_id} AND key2 = 'auto_manager'"
                result = db.execute_query(query_sql, ())

                next_run = None
                last_run = None
                if result and result[0][0]:
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
