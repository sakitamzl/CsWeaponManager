"""
Unites API 模块
层级蓝图注册：
- 从 src/API.py 接收前缀 /backENDV2/src
- 向下传递给各公共单元子模块，添加 /unites 路径段
最终路径示例：
  /backENDV2/src/unites/search_config/get/<key1>/<key2>
  /backENDV2/src/unites/search_config/save
  /backENDV2/src/unites/search_config/list
"""
from flask import Blueprint
from .search_config.API import search_config_blueprint

unites_blueprint = Blueprint('unites_v2', __name__)
unites_blueprint.register_blueprint(search_config_blueprint, url_prefix='/unites')
