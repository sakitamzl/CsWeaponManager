"""
Steam inventory_history 处理模块
提供 Spider 所需的库存历史记录查询、插入与解析接口
"""
import json
import traceback
from flask import jsonify, request
from src.db_manager.steam.model.steam_inventory_history import SteamInventoryHistoryModel
from src.db_manager.steam.model.steam_inventory_history_index import SteamInventoryHistoryIndexModel
from src.db_manager.index.model.weapon_classID import WeaponClassIDModel


class InventoryHistoryHandler:

    @staticmethod
    def select_max_time(steam_ID):
        """查询指定用户的最新一条历史记录"""
        try:
            if not steam_ID:
                return jsonify({'success': False, 'error': '缺少steam_ID参数'}), 400
            records = SteamInventoryHistoryIndexModel.find_all("data_user = ? ORDER BY order_time DESC", (steam_ID,), limit=1)
            if records:
                r = records[0]
                return jsonify({'success': True, 'data': {'ID': r.ID, 'order_time': r.order_time, 'trade_type': r.trade_type, 'data_user': r.data_user}}), 200
            return jsonify({'success': True, 'data': None, 'message': '未找到相关记录'}), 200
        except Exception as e:
            print(f"查询最新记录失败: {e}\n{traceback.format_exc()}")
            return jsonify({'success': False, 'error': f'查询失败: {str(e)}'}), 500

    @staticmethod
    def select_min_time(steam_ID):
        """查询指定用户的最早一条历史记录"""
        try:
            if not steam_ID:
                return jsonify({'success': False, 'error': '缺少steam_ID参数'}), 400
            records = SteamInventoryHistoryIndexModel.find_all("data_user = ? ORDER BY order_time ASC", (steam_ID,), limit=1)
            if records:
                r = records[0]
                return jsonify({'success': True, 'data': {'ID': r.ID, 'order_time': r.order_time, 'trade_type': r.trade_type, 'data_user': r.data_user}}), 200
            return jsonify({'success': True, 'data': None, 'message': '未找到相关记录'}), 200
        except Exception as e:
            print(f"查询最早记录失败: {e}\n{traceback.format_exc()}")
            return jsonify({'success': False, 'error': f'查询失败: {str(e)}'}), 500

    @staticmethod
    def insert_inventory_history():
        """插入 Steam 库存历史记录（使用索引表防止重复）"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': '无效的JSON数据'}), 400

            item_ID = data.get('ID')
            trade_title = data.get('trade_title')
            items = data.get('items')
            order_time = data.get('order_time')
            trade_type = data.get('trade_type')
            data_user = data.get('data_user')

            if not item_ID:
                return jsonify({'success': False, 'error': '缺少ID参数'}), 400
            if items is None or not isinstance(items, list):
                return jsonify({'success': False, 'error': '无效的items数据'}), 400

            # 检查索引表是否已存在
            existing_index = SteamInventoryHistoryIndexModel.find_by_id(ID=item_ID)
            if existing_index:
                print(f"[跳过] ID {item_ID} 已存在于索引表中")
                return jsonify({'success': True, 'message': '记录已存在，跳过重复入库', 'data': {'already_exists': True, 'ID': item_ID, 'skip_count': len(items)}}), 200

            success_count = 0
            failed_count = 0

            for i in items:
                try:
                    inventory_record = SteamInventoryHistoryModel()
                    inventory_record.instanceid = i.get('instanceid')
                    inventory_record.classid = i.get('classid')
                    inventory_record.ID = item_ID
                    inventory_record.order_time = order_time
                    inventory_record.trade_title = trade_title
                    inventory_record.appid = i.get('appid')
                    inventory_record.item_name = i.get('item_name')
                    inventory_record.weapon_name = i.get('weapon_name')
                    inventory_record.weapon_type = i.get('weapon_type')
                    inventory_record.float_range = i.get('float_range')
                    inventory_record.trade_type = trade_type
                    inventory_record.data_user = data_user
                    inventory_record.market_hash_name = i.get('market_hash_name')
                    inventory_record.rename = i.get('rename')
                    inventory_record.sticker = i.get('sticker')
                    inventory_record.pendant = i.get('pendant')
                    if inventory_record.save():
                        success_count += 1
                    else:
                        failed_count += 1
                except Exception as item_error:
                    failed_count += 1
                    print(f"处理单条记录异常: {item_error}\n{traceback.format_exc()}")

            if success_count > 0 or len(items) == 0:
                try:
                    index_record = SteamInventoryHistoryIndexModel()
                    index_record.ID = item_ID
                    index_record.order_time = order_time
                    index_record.trade_type = trade_type
                    index_record.data_user = data_user
                    index_record.save()
                except Exception as index_error:
                    print(f"创建索引记录异常: {index_error}\n{traceback.format_exc()}")

                message = '空交易记录已保存' if len(items) == 0 else f'成功插入{success_count}条记录'
                return jsonify({'success': True, 'message': message, 'data': {'ID': item_ID, 'success_count': success_count, 'failed_count': failed_count, 'total_count': len(items), 'is_empty': len(items) == 0}}), 200
            else:
                return jsonify({'success': False, 'error': f'所有记录插入失败，共{failed_count}条', 'data': {'ID': item_ID, 'success_count': success_count, 'failed_count': failed_count, 'total_count': len(items)}}), 500

        except Exception as e:
            print(f"服务器未捕获异常: {e}\n{traceback.format_exc()}")
            return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500

    @staticmethod
    def resolve_sticker():
        """解析印花名称，查询对应的 steam_hash_name"""
        try:
            data = request.get_json(force=True) or {}
            sticker_name = data.get("name")
            if not sticker_name:
                return jsonify({"success": False, "message": "缺少 name 参数"}), 400

            search_name = f"印花 | {sticker_name}"
            records = WeaponClassIDModel.find_by_market_listing_item_name(search_name)
            if not records:
                return jsonify({"success": False, "message": "未找到匹配的印花数据", "data": {"name": sticker_name, "steam_hash_name": ""}}), 200

            steam_hash_name = getattr(records[0], "steam_hash_name", "")
            if steam_hash_name.startswith('Sticker | '):
                steam_hash_name = steam_hash_name[10:]
            return jsonify({"success": True, "data": {"name": sticker_name, "steam_hash_name": steam_hash_name}}), 200
        except Exception as exc:
            print(f"解析印花信息失败: {exc}\n{traceback.format_exc()}")
            return jsonify({"success": False, "error": str(exc)}), 500

    @staticmethod
    def resolve_pendant():
        """解析挂件名称，查询对应的 steam_hash_name"""
        try:
            data = request.get_json(force=True) or {}
            pendant_name = data.get("name")
            if not pendant_name:
                return jsonify({"success": False, "message": "缺少 name 参数"}), 400

            search_name = f"挂件 | {pendant_name}"
            records = WeaponClassIDModel.find_by_market_listing_item_name(search_name)
            if not records:
                return jsonify({"success": False, "message": "未找到匹配的挂件数据", "data": {"name": pendant_name, "steam_hash_name": ""}}), 200

            steam_hash_name = getattr(records[0], "steam_hash_name", "")
            return jsonify({"success": True, "data": {"name": pendant_name, "steam_hash_name": steam_hash_name}}), 200
        except Exception as exc:
            print(f"解析挂件信息失败: {exc}\n{traceback.format_exc()}")
            return jsonify({"success": False, "error": str(exc)}), 500

    @staticmethod
    def resolve_market_item():
        """根据 market_listing_item_name 查询 steam_hash_name 等武器信息"""
        try:
            data = request.get_json(force=True) or {}
            market_name = data.get("market_listing_item_name") or data.get("name")
            if not market_name:
                return jsonify({"success": False, "message": "缺少 market_listing_item_name 参数"}), 400

            records = WeaponClassIDModel.find_by_market_listing_item_name(market_name)
            if not records:
                return jsonify({"success": False, "message": "未找到匹配的数据", "data": {"market_listing_item_name": market_name, "steam_hash_name": ""}}), 200

            weapon = records[0]
            return jsonify({"success": True, "data": {"market_listing_item_name": market_name, "steam_hash_name": getattr(weapon, "steam_hash_name", "") or "", "weapon_name": getattr(weapon, "weapon_name", "") or "", "item_name": getattr(weapon, "item_name", "") or "", "weapon_type": getattr(weapon, "weapon_type", "") or ""}}), 200
        except Exception as exc:
            print(f"解析 market_listing_item_name 失败: {exc}\n{traceback.format_exc()}")
            return jsonify({"success": False, "error": str(exc)}), 500
