"""
Data Source API 模块
层级蓝图注册：
- 从 web_display/API.py 接收前缀 /backENDV2/src/web_display
- 注册所有 Data Source 页面路由，添加 /data_source/units/xxx 路径段
"""
from flask import Blueprint
from .units.data_source_data import DataSourceData
from .units.data_source_ops import DataSourceOps

data_source_blueprint = Blueprint('data_source_v2', __name__)

# 数据源CRUD路由
data_source_blueprint.route('/data_source/units/data/getDataSourceList', methods=['GET'])(DataSourceData.get_data_source_list)
data_source_blueprint.route('/data_source/units/data/createDataSource', methods=['POST'])(DataSourceData.create_data_source)
data_source_blueprint.route('/data_source/units/data/getDataSourceById/<int:data_id>', methods=['GET'])(DataSourceData.get_data_source_by_id)
data_source_blueprint.route('/data_source/units/data/updateDataSource/<int:data_id>', methods=['PUT'])(DataSourceData.update_data_source)
data_source_blueprint.route('/data_source/units/data/deleteDataSource/<int:data_id>', methods=['DELETE'])(DataSourceData.delete_data_source)

# 数据源操作路由
data_source_blueprint.route('/data_source/units/ops/testConnection', methods=['POST'])(DataSourceOps.test_connection)
data_source_blueprint.route('/data_source/units/ops/collectDataSource/<int:data_id>', methods=['POST'])(DataSourceOps.collect_data_source)
data_source_blueprint.route('/data_source/units/ops/toggleDataSource/<int:data_id>', methods=['PUT'])(DataSourceOps.toggle_data_source)
