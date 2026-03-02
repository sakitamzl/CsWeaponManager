"""
select_weapon Spider V2 API 模块
层级蓝图注册：
- 从 use_spider/youpin/API.py 接收前缀 /backENDV2/src/use_spider/youpin
- 定义所有 selectWeapon 路由，添加 /selectWeapon/ 路径段
完整 URL 格式: /backENDV2/src/use_spider/youpin/selectWeapon/<endpoint>
"""
from flask import Blueprint
from .units.weapon_insert import WeaponInsert
from .units.weapon_query import WeaponQuery

select_weapon_spider_blueprint = Blueprint('select_weapon_spider', __name__)

# 查询类路由
select_weapon_spider_blueprint.route('/selectWeapon/fetchWeaponIcons',              methods=['POST'])(WeaponQuery.fetch_weapon_icons)
select_weapon_spider_blueprint.route('/selectWeapon/getYyypIdBySteamHashName',      methods=['POST'])(WeaponQuery.get_yyyp_id_by_steam_hash_name)
select_weapon_spider_blueprint.route('/selectWeapon/pendingWeaponIconsCount',       methods=['GET'])(WeaponQuery.pending_weapon_icons_count)

# 写入/更新类路由
select_weapon_spider_blueprint.route('/selectWeapon/batchInsertOrUpdate',           methods=['POST'])(WeaponInsert.batch_insert_or_update)
select_weapon_spider_blueprint.route('/selectWeapon/insertWeapon',                  methods=['POST'])(WeaponInsert.insert_weapon)
select_weapon_spider_blueprint.route('/selectWeapon/updateWeaponByYyypId/<int:yyyp_id>', methods=['PUT'])(WeaponInsert.update_weapon_by_yyyp_id)
select_weapon_spider_blueprint.route('/selectWeapon/updateIconStatus',              methods=['POST'])(WeaponInsert.update_icon_status)
select_weapon_spider_blueprint.route('/selectWeapon/recordPriceHistory',            methods=['POST'])(WeaponInsert.record_price_history)
