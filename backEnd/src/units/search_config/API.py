"""
SearchConfig API 模块
层级蓝图注册：
- 从 Unites/API.py 接收前缀 /backENDV2/src/unites
- 注册所有公共配置路由，添加 /search_config 路径段
最终路径示例：
  GET    /backENDV2/src/unites/search_config/get/<key1>/<key2>
  POST   /backENDV2/src/unites/search_config/save
  POST   /backENDV2/src/unites/search_config/update
  GET    /backENDV2/src/unites/search_config/list
  DELETE /backENDV2/src/unites/search_config/delete/<config_id>
"""
from flask import Blueprint
from .config_handler import SearchConfig

search_config_blueprint = Blueprint('search_config_v2', __name__)

search_config_blueprint.route('/search_config/get/<key1>/<key2>', methods=['POST'])(SearchConfig.get_config)
search_config_blueprint.route('/search_config/save', methods=['POST'])(SearchConfig.save_config)
search_config_blueprint.route('/search_config/update', methods=['POST'])(SearchConfig.update_config)
search_config_blueprint.route('/search_config/list', methods=['GET'])(SearchConfig.list_configs)
search_config_blueprint.route('/search_config/delete/<int:config_id>', methods=['DELETE'])(SearchConfig.delete_config)
