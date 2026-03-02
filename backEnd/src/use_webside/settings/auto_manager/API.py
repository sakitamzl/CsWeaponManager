"""
AutoManager API 模块
层级蓝图注册：
- 从 settings/API.py 接收前缀 /backENDV2/src/use_webside/settings
- 注册所有 AutoManager 路由，添加 /auto_manager/units/xxx 路径段
"""
from flask import Blueprint
from .units.auto_manager_data import AutoManagerData
from .units.auto_manager_ops import AutoManagerOps
from .units.auto_manager_filters import AutoManagerFilters

auto_manager_blueprint = Blueprint('auto_manager_v2', __name__)

# 任务 CRUD
auto_manager_blueprint.route('/auto_manager/units/data/getTaskList', methods=['GET'])(AutoManagerData.get_task_list)
auto_manager_blueprint.route('/auto_manager/units/data/createTask', methods=['POST'])(AutoManagerData.create_task)
auto_manager_blueprint.route('/auto_manager/units/data/updateTask/<int:task_id>', methods=['PUT'])(AutoManagerData.update_task)
auto_manager_blueprint.route('/auto_manager/units/data/deleteTask/<int:task_id>', methods=['DELETE'])(AutoManagerData.delete_task)

# 任务操作
auto_manager_blueprint.route('/auto_manager/units/ops/toggleTask/<int:task_id>', methods=['POST'])(AutoManagerOps.toggle_task)
auto_manager_blueprint.route('/auto_manager/units/ops/getExecutingTasks', methods=['GET'])(AutoManagerOps.get_executing_tasks)

# 筛选/加载数据
auto_manager_blueprint.route('/auto_manager/units/filters/getSteamAccounts', methods=['GET'])(AutoManagerFilters.get_steam_accounts)
auto_manager_blueprint.route('/auto_manager/units/filters/getSearchConfigs', methods=['GET'])(AutoManagerFilters.get_search_configs)
