"""
data_spider API 模块
层级蓝图注册：
- 从 use_webside/API.py 接收前缀 /backENDV2/src/use_webside
- 向下添加 /data_spider 路径段
最终路径示例：
  POST /backENDV2/src/use_webside/data_spider/search_weapon_rename/item/add
  GET  /backENDV2/src/use_webside/data_spider/search_weapon_rename/items/list
  POST /backENDV2/src/use_webside/data_spider/search_pendant/config/save
  GET  /backENDV2/src/use_webside/data_spider/search_pendant/items/list
"""
from flask import Blueprint
from .search_weapon_rename.API import search_weapon_rename_blueprint
from .search_pendant.API import search_pendant_blueprint

data_spider_blueprint = Blueprint('data_spider_v2', __name__)
data_spider_blueprint.register_blueprint(search_weapon_rename_blueprint, url_prefix='/data_spider')
data_spider_blueprint.register_blueprint(search_pendant_blueprint, url_prefix='/data_spider')
