"""
自动化任务调度器
负责在后台执行定时任务,即使前端关闭也能继续运行
"""
import threading
import time
import json
import requests
from datetime import datetime
from src.execution_db import Date_base
from src.log import Log

class TaskScheduler:
    """任务调度器类"""
    
    def __init__(self):
        self.running = False
        self.tasks = {}  # {task_id: {'timer': threading.Timer, 'config': {...}}}
        self.lock = threading.Lock()
        self.log = Log()
        
    def start(self):
        """启动调度器"""
        if self.running:
            self.log.write_log("任务调度器已经在运行中", 'warning')
            return
            
        self.running = True
        self.log.write_log("任务调度器启动", 'info')
        
        # 加载并启动所有已启用的任务
        self.load_and_start_tasks()
        
    def stop(self):
        """停止调度器"""
        self.running = False
        
        with self.lock:
            # 取消所有定时器
            for task_id, task_info in self.tasks.items():
                if task_info.get('timer'):
                    task_info['timer'].cancel()
            
            self.tasks.clear()
        
        self.log.write_log("任务调度器已停止", 'info')
        
    def load_and_start_tasks(self):
        """从数据库加载并启动所有已启用的任务"""
        try:
            db = Date_base()
            
            # 查询所有启用的任务
            query_sql = """
            SELECT dataID, dataName, key1, value 
            FROM config 
            WHERE key2 = 'auto_manager' AND status = '1'
            """
            
            success, results = db.select(query_sql)
            
            if success and results:
                for row in results:
                    task_id = row[0]
                    task_name = row[1]
                    automate_type = row[2]
                    
                    try:
                        config = json.loads(row[3]) if row[3] else {}
                        
                        # 启动任务
                        self.start_task(task_id, task_name, automate_type, config)
                        
                    except json.JSONDecodeError as e:
                        self.log.write_log(f"解析任务配置失败 (taskId={task_id}): {e}", 'error')
                        continue
                
                self.log.write_log(f"已加载 {len(self.tasks)} 个定时任务", 'info')
            else:
                self.log.write_log("没有找到启用的定时任务", 'info')
                
        except Exception as e:
            self.log.write_log(f"加载定时任务失败: {str(e)}", 'error')
    
    def start_task(self, task_id, task_name, automate_type, config, delay_seconds=30):
        """启动单个任务
        
        Args:
            task_id: 任务ID
            task_name: 任务名称
            automate_type: 自动化类型
            config: 任务配置
            delay_seconds: 延迟执行秒数(默认30秒,等待程序完全启动)
        """
        with self.lock:
            # 如果任务已存在,先停止
            if task_id in self.tasks:
                self.stop_task(task_id)
            
            # 创建任务信息
            task_info = {
                'task_id': task_id,
                'task_name': task_name,
                'automate_type': automate_type,
                'config': config,
                'timer': None
            }
            
            self.tasks[task_id] = task_info
            
            # 延迟执行任务
            timer = threading.Timer(delay_seconds, lambda: self._schedule_task(task_id))
            timer.daemon = True
            timer.start()
            
            self.tasks[task_id]['timer'] = timer
            
            self.log.write_log(f"任务已启动: {task_name} (ID: {task_id}), 将在 {delay_seconds} 秒后开始执行", 'info')
    
    
    def stop_task(self, task_id):
        """停止单个任务"""
        with self.lock:
            if task_id in self.tasks:
                task_info = self.tasks[task_id]
                
                # 取消定时器
                if task_info.get('timer'):
                    try:
                        task_info['timer'].cancel()
                    except Exception as e:
                        self.log.write_log(f"取消定时器失败 (taskId={task_id}): {str(e)}", 'warning')
                
                task_name = task_info.get('task_name', 'Unknown')
                del self.tasks[task_id]
                
                self.log.write_log(f"任务已停止: {task_name} (ID: {task_id})", 'info')
            else:
                self.log.write_log(f"任务不存在或已停止 (taskId={task_id})", 'info')
    
    def reload_task(self, task_id):
        """重新加载单个任务(用于更新任务配置)"""
        try:
            db = Date_base()
            
            query_sql = f"""
            SELECT dataName, key1, value, status 
            FROM config 
            WHERE dataID = {task_id} AND key2 = 'auto_manager'
            """
            
            success, result = db.select(query_sql)
            
            if success and result:
                row = result[0]
                task_name = row[0]
                automate_type = row[1]
                config = json.loads(row[2]) if row[2] else {}
                enabled = row[3] == '1'
                
                # 先停止任务
                self.stop_task(task_id)
                
                # 如果启用,重新启动
                if enabled:
                    self.start_task(task_id, task_name, automate_type, config)
                    
        except Exception as e:
            self.log.write_log(f"重新加载任务失败 (taskId={task_id}): {str(e)}", 'error')
    
    def _schedule_task(self, task_id):
        """调度任务执行"""
        if task_id not in self.tasks:
            return
        
        task_info = self.tasks[task_id]
        
        # 执行任务
        try:
            self._execute_task(task_info)
            
            # 更新最后执行时间
            self._update_task_execution_time(task_id)
        except Exception as e:
            self.log.write_log(f"执行任务失败 ({task_info['task_name']}): {str(e)}", 'error')
        
        # 设置下次执行
        if task_id in self.tasks:  # 确保任务没有被停止
            interval = task_info['config'].get('interval', 30) * 60  # 转换为秒
            
            timer = threading.Timer(interval, lambda: self._schedule_task(task_id))
            timer.daemon = True
            timer.start()
            
            self.tasks[task_id]['timer'] = timer
    
    def _update_task_execution_time(self, task_id):
        """更新任务执行时间到数据库(存储在value JSON中)"""
        try:
            from datetime import datetime, timedelta
            
            db = Date_base()
            
            # 获取任务配置
            if task_id not in self.tasks:
                return
            
            task_info = self.tasks[task_id]
            interval = task_info['config'].get('interval', 30)
            
            # 计算时间
            now = datetime.now()
            last_run = now.strftime('%Y-%m-%d %H:%M:%S')
            next_run = (now + timedelta(minutes=interval)).strftime('%Y-%m-%d %H:%M:%S')
            
            # 获取当前配置
            query_sql = f"SELECT value FROM config WHERE dataID = {task_id} AND key2 = 'auto_manager'"
            success, result = db.select(query_sql)
            
            if success and result:
                # 解析现有配置
                current_config = json.loads(result[0][0]) if result[0][0] else {}
                
                # 更新执行时间
                current_config['lastRun'] = last_run
                current_config['nextRun'] = next_run
                
                # 保存回数据库
                config_json = json.dumps(current_config, ensure_ascii=False).replace("'", "''")
                update_sql = f"""
                UPDATE config 
                SET value = '{config_json}' 
                WHERE dataID = {task_id} AND key2 = 'auto_manager'
                """
                
                db.update(update_sql)
                
                # 同步更新内存中的配置
                task_info['config']['lastRun'] = last_run
                task_info['config']['nextRun'] = next_run
            
        except Exception as e:
            self.log.write_log(f"更新任务执行时间失败 (taskId={task_id}): {str(e)}", 'error')
    
    def _execute_task(self, task_info):
        """执行具体任务"""
        task_id = task_info['task_id']
        task_name = task_info['task_name']
        automate_type = task_info['automate_type']
        config = task_info['config']
        
        self.log.write_log(f"开始执行任务: {task_name} (ID: {task_id})", 'info')
        
        try:
            if automate_type == 'auto_update':
                # 自动更新数据任务
                self._execute_update_task(task_info)
            elif automate_type == 'auto_fetch':
                # 自动获取数据任务
                self._execute_fetch_task(task_info)
            else:
                self.log.write_log(f"未知的任务类型: {automate_type}", 'error')
                
        except Exception as e:
            self.log.write_log(f"任务执行异常 ({task_name}): {str(e)}", 'error')
    
    def _execute_update_task(self, task_info):
        """执行更新类任务"""
        config = task_info['config']
        selected_task = config.get('selectedTask')
        steam_id = config.get('selectedSteamId')
        
        if not steam_id:
            self.log.write_log(f"任务 {task_info['task_name']} 缺少 Steam ID", 'error')
            return
        
        # 根据任务类型调用相应的API
        spider_base_url = "http://127.0.0.1:9002"  # Spider服务地址
        
        try:
            if selected_task == 'update_steam_inventory':
                # 更新Steam库存
                response = requests.post(
                    f"{spider_base_url}/steamSpiderV1/getInventory",
                    json={'steamId': steam_id},
                    timeout=300  # 5分钟超时
                )
                self.log.write_log(f"更新Steam库存完成: {steam_id}, 状态: {response.status_code}", 'info')
                
            elif selected_task == 'fetch_yyyp_price':
                # 获取悠悠有品价格
                response = requests.post(
                    f"{spider_base_url}/youping898SpiderV1/getYYYPPrice",
                    json={'steamId': steam_id},
                    timeout=300
                )
                self.log.write_log(f"获取悠悠有品价格完成: {steam_id}, 状态: {response.status_code}", 'info')
                
            elif selected_task == 'fetch_buff_price':
                # 获取BUFF价格
                response = requests.post(
                    f"{spider_base_url}/buffSpiderV1/getBUFFPrice",
                    json={'steamId': steam_id},
                    timeout=300
                )
                self.log.write_log(f"获取BUFF价格完成: {steam_id}, 状态: {response.status_code}", 'info')
                
        except requests.exceptions.Timeout:
            self.log.write_log(f"任务执行超时: {task_info['task_name']}", 'error')
        except requests.exceptions.RequestException as e:
            self.log.write_log(f"API请求失败: {str(e)}", 'error')
    
    def _execute_fetch_task(self, task_info):
        """执行数据采集类任务"""
        config = task_info['config']
        selected_task = config.get('selectedTask')
        data_source_id = config.get('selectedDataSource')
        
        if not data_source_id:
            self.log.write_log(f"任务 {task_info['task_name']} 没有选择数据源", 'error')
            return
        
        # 获取数据源配置
        db = Date_base()
        
        try:
            # 查询数据源配置
            query_sql = f"""
            SELECT dataName, key1, value, steamID 
            FROM config 
            WHERE dataID = {data_source_id} AND key2 = 'config'
            """
            
            success, result = db.select(query_sql)
            
            if not success or not result:
                self.log.write_log(f"数据源不存在: ID={data_source_id}", 'error')
                return
            
            data_name = result[0][0]
            data_type = result[0][1]
            config_json = json.loads(result[0][2]) if result[0][2] else {}
            steam_id = result[0][3]
            
            # 根据任务类型和数据源类型执行采集
            spider_base_url = "http://127.0.0.1:9002"  # Spider服务地址
            
            if selected_task == 'collect_buff' and data_type == 'buff':
                # 采集BUFF数据
                response = requests.post(
                    f"{spider_base_url}/buffSpiderV1/NewData",
                    json={'steamID': steam_id},
                    timeout=600  # 10分钟超时
                )
                self.log.write_log(f"BUFF数据采集完成: {data_name}, 状态: {response.status_code}", 'info')
                
            elif selected_task == 'collect_youpin' and data_type == 'youpin':
                # 采集悠悠有品数据
                spider_data = {
                    'phone': config_json.get('phone', ''),
                    'sessionid': config_json.get('Sessionid', ''),
                    'token': config_json.get('token', ''),
                    'app_version': config_json.get('app_version', ''),
                    'app_type': config_json.get('app_type', ''),
                    'userId': config_json.get('userId', ''),
                    'steamId': config_json.get('steamId', '')
                }
                
                response = requests.post(
                    f"{spider_base_url}/youpin898SpiderV1/NewData",
                    json=spider_data,
                    timeout=600
                )
                self.log.write_log(f"悠悠有品数据采集完成: {data_name}, 状态: {response.status_code}", 'info')
                
        except requests.exceptions.Timeout:
            self.log.write_log(f"数据采集超时", 'error')
        except requests.exceptions.RequestException as e:
            self.log.write_log(f"数据采集失败: {str(e)}", 'error')
        except Exception as e:
            self.log.write_log(f"处理数据源失败 (ID={data_source_id}): {str(e)}", 'error')


# 全局调度器实例
_scheduler = None

def get_scheduler():
    """获取全局调度器实例"""
    global _scheduler
    if _scheduler is None:
        _scheduler = TaskScheduler()
    return _scheduler

