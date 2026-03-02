"""
search_weapon_rename API 模块
对应前端页面：SearchWeaponRename
层级路径：/backENDV2/src/use_webside/data_spider/search_weapon_rename/...
"""
from flask import Blueprint
from .units.search_rename_handler import SearchRenameHandler

search_weapon_rename_blueprint = Blueprint('search_weapon_rename_v2', __name__)

search_weapon_rename_blueprint.add_url_rule('/search_weapon_rename/item/add', view_func=SearchRenameHandler.add_item, methods=['POST'])
search_weapon_rename_blueprint.add_url_rule('/search_weapon_rename/item/get/<int:item_id>', view_func=SearchRenameHandler.get_item, methods=['GET'])
search_weapon_rename_blueprint.add_url_rule('/search_weapon_rename/item/update_status', view_func=SearchRenameHandler.update_item_status, methods=['POST'])
search_weapon_rename_blueprint.add_url_rule('/search_weapon_rename/items/batch', view_func=SearchRenameHandler.add_items_batch, methods=['POST'])
search_weapon_rename_blueprint.add_url_rule('/search_weapon_rename/items/list', view_func=SearchRenameHandler.get_items_list, methods=['GET'])
search_weapon_rename_blueprint.add_url_rule('/search_weapon_rename/items/count', view_func=SearchRenameHandler.get_items_count, methods=['GET'])
search_weapon_rename_blueprint.add_url_rule('/search_weapon_rename/items/latest', view_func=SearchRenameHandler.get_latest_items, methods=['GET'])
search_weapon_rename_blueprint.add_url_rule('/search_weapon_rename/items/clear', view_func=SearchRenameHandler.clear_data, methods=['POST'])
search_weapon_rename_blueprint.add_url_rule('/search_weapon_rename/items/cleanup', view_func=SearchRenameHandler.cleanup_old_data, methods=['POST'])
search_weapon_rename_blueprint.add_url_rule('/search_weapon_rename/stats', view_func=SearchRenameHandler.get_stats, methods=['GET'])
