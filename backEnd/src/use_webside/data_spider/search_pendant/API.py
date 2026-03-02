"""
search_pendant API 模块
对应前端页面：SearchPendant
层级路径：/backENDV2/src/use_webside/data_spider/search_pendant/...
"""
from flask import Blueprint
from .units.search_pendant_handler import SearchPendantHandler

search_pendant_blueprint = Blueprint('search_pendant_v2', __name__)

search_pendant_blueprint.add_url_rule('/search_pendant/config/save', view_func=SearchPendantHandler.save_config, methods=['POST'])
search_pendant_blueprint.add_url_rule('/search_pendant/item/add', view_func=SearchPendantHandler.add_item, methods=['POST'])
search_pendant_blueprint.add_url_rule('/search_pendant/items/list', view_func=SearchPendantHandler.get_items_list, methods=['GET'])
search_pendant_blueprint.add_url_rule('/search_pendant/item/update_status', view_func=SearchPendantHandler.update_item_status, methods=['POST'])
search_pendant_blueprint.add_url_rule('/search_pendant/items/clear', view_func=SearchPendantHandler.clear_data, methods=['POST'])
