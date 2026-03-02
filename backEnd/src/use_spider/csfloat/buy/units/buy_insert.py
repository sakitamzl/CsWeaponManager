"""
CSFloat buy 写入模块
提供 Spider 所需的购买记录插入、状态更新与数据清理接口
"""
import json
import sys
from pathlib import Path
from flask import jsonify, request
from src.db_manager.csfloat.model import CsFloatBuyModel
from src.db_manager.index.model.buy import BuyModel
from src.db_manager.index.model.weapon_classID import WeaponClassIDModel

# 导入状态映射模块
spider_path = Path(__file__).parent.parent.parent.parent.parent.parent / "Spider" / "src"
if str(spider_path) not in sys.path:
    sys.path.insert(0, str(spider_path))

try:
    from model.csfloat_state import get_status_mapping
except ImportError:
    def get_status_mapping(csfloat_state):
        return {"status": csfloat_state, "status_sub": None}


class BuyInsert:

    @staticmethod
    def resolve_weapon():
        """根据 market_hash_name 解析武器信息（weapon_type, weapon_name, item_name, float_range）"""
        try:
            data = request.get_json(force=True) or {}
            market_hash_name = data.get("market_hash_name") or data.get("steam_hash_name")
            if not market_hash_name:
                return jsonify({"success": False, "message": "缺少 market_hash_name"}), 400

            records = WeaponClassIDModel.find_by_steam_hash_name(market_hash_name)
            if not records:
                return jsonify({"success": False, "message": "未找到匹配数据"}), 200

            weapon = records[0]
            return jsonify({
                "success": True,
                "data": {
                    "weapon_type": getattr(weapon, "weapon_type", None),
                    "weapon_name": getattr(weapon, "weapon_name", None),
                    "item_name": getattr(weapon, "item_name", None),
                    "float_range": getattr(weapon, "float_range", None),
                },
            }), 200
        except Exception as exc:
            print(f"解析 CSFloat 武器信息失败: {exc}")
            return jsonify({"success": False, "error": str(exc)}), 500

    @staticmethod
    def resolve_accessory():
        """解析饰品信息（印花/挂件），查询 steam_hash_name 和 market_listing_item_name"""
        try:
            data = request.get_json(force=True) or {}
            name = data.get("name")
            if not name:
                return jsonify({"success": False, "message": "缺少 name"}), 400

            if name.startswith("印花 | ") or name.startswith("挂件 | "):
                records = WeaponClassIDModel.find_by_market_listing_item_name(name)
            else:
                records = WeaponClassIDModel.find_by_steam_hash_name(name)

            if not records:
                return jsonify({"success": False, "message": "未找到匹配数据"}), 200

            accessory = records[0]
            return jsonify({
                "success": True,
                "data": {
                    "market_listing_item_name": getattr(accessory, "market_listing_item_name", None),
                    "steam_hash_name": getattr(accessory, "steam_hash_name", None),
                },
            }), 200
        except Exception as exc:
            print(f"解析 CSFloat 饰品信息失败: {exc}")
            return jsonify({"success": False, "error": str(exc)}), 500

    @staticmethod
    def insert_db():
        """插入 CSFloat 购买记录（同时写入 csfloat_buy 表和 buy 主表）"""
        try:
            data = request.get_json(force=True)
            if not data:
                return jsonify({"success": False, "error": "无效的 JSON 数据"}), 400

            trade_id = data.get("trade_id")
            if not trade_id:
                return jsonify({"success": False, "error": "缺少 trade_id"}), 400

            original_state = data.get("state")
            status_mapping = get_status_mapping(original_state)

            csfloat_record = CsFloatBuyModel()
            csfloat_record.ID = trade_id
            csfloat_record.contract_id = data.get("contract_id")
            csfloat_record.weapon_name = data.get("weaponitem_name")
            csfloat_record.weapon_type = data.get("weapon_type")
            csfloat_record.item_name = data.get("item_name")
            csfloat_record.weapon_float = data.get("weapon_float")
            csfloat_record.float_range = data.get("float_range")
            csfloat_record.price = data.get("price")
            csfloat_record.us_price = data.get("price_usd")
            csfloat_record.price_original = data.get("price_original")
            csfloat_record.seller_name = data.get("seller_name")
            csfloat_record.seller_id = data.get("seller_id")
            csfloat_record.buyer_name = data.get("buyer_name")
            csfloat_record.buyer_id = data.get("buyer_id")
            csfloat_record.state = status_mapping["status"]
            csfloat_record.state_sub = status_mapping["status_sub"]
            csfloat_record.created_at = data.get("created_at")
            csfloat_record.accepted_at = data.get("accepted_at")
            csfloat_record.inventory_check_status = data.get("inventory_check_status")
            csfloat_record.market_hash_name = data.get("market_hash_name")
            csfloat_record.data_user = data.get("data_user")
            csfloat_record.save()

            buy_record = BuyModel()
            buy_record.ID = trade_id
            buy_record.weapon_name = data.get("weaponitem_name")
            buy_record.weapon_type = data.get("weapon_type")
            buy_record.item_name = data.get("item_name")
            buy_record.weapon_float = data.get("weapon_float")
            buy_record.float_range = data.get("float_range")
            buy_record.price = data.get("price")
            buy_record.seller_name = data.get("seller_name")
            buy_record.status = status_mapping["status"]
            buy_record.status_sub = status_mapping["status_sub"]
            buy_record.order_time = data.get("created_at")
            buy_record.payment = None
            buy_record.trade_type = None
            buy_record.data_user = data.get("data_user")
            buy_record.steam_id = data.get("steam_id")
            buy_record.steam_hash_name = data.get("market_hash_name")
            stickers = data.get("stickers")
            buy_record.sticker = json.dumps(stickers, ensure_ascii=False) if stickers else None
            keychains = data.get("keychains")
            buy_record.pendant = json.dumps(keychains, ensure_ascii=False) if keychains else None
            setattr(buy_record, "from", "csfloat")
            buy_record.save()

            return jsonify({"success": True, "message": "CSFloat 购买数据插入成功"}), 200
        except Exception as exc:
            print(f"CSFloat 购买数据插入失败: {exc}")
            return jsonify({"success": False, "error": str(exc)}), 500

    @staticmethod
    def update_order_status():
        """更新 CSFloat 购买订单状态（同时更新 csfloat_buy 和 buy 主表）"""
        try:
            data = request.get_json(force=True)
            trade_id = data.get("trade_id")
            original_state = data.get("state")
            state_sub = data.get("state_sub")
            verified_at = data.get("verified_at")

            if not trade_id:
                return jsonify({"success": False, "error": "缺少 trade_id"}), 400

            status_mapping = get_status_mapping(original_state)
            state = status_mapping["status"]
            if not state_sub:
                state_sub = status_mapping["status_sub"]

            record = CsFloatBuyModel.find_by_id(ID=trade_id)
            if record:
                record.state = state
                record.state_sub = state_sub
                record.save()

            buy_record = BuyModel.find_by_id(ID=trade_id)
            if buy_record:
                buy_record.status = state
                buy_record.status_sub = state_sub
                if verified_at:
                    buy_record.order_time = verified_at
                buy_record.save()

            return jsonify({"success": True, "message": "更新成功"}), 200
        except Exception as exc:
            print(f"更新 CSFloat 购买订单状态失败: {exc}")
            return jsonify({"success": False, "error": str(exc)}), 500

    @staticmethod
    def delete_recent_days(user_id, days):
        """删除指定用户最近 N 天的购买数据（csfloat_buy 和 buy 表）"""
        try:
            from datetime import datetime, timedelta
            cutoff_time = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
            deleted_csfloat = CsFloatBuyModel.delete_all("data_user = ? AND created_at >= ?", (user_id, cutoff_time))
            deleted_buy = BuyModel.delete_all(
                "data_user = ? AND order_time >= ? AND `from` = 'csfloat'", (user_id, cutoff_time)
            )
            return jsonify({
                "success": True, "message": "删除成功",
                "deleted_csfloat_count": deleted_csfloat, "deleted_buy_count": deleted_buy
            }), 200
        except Exception as exc:
            print(f"删除最近 {days} 天购买数据失败: {exc}")
            return jsonify({"success": False, "error": str(exc)}), 500

    @staticmethod
    def delete_from_time(user_id):
        """删除指定用户从某时间点之后的所有购买数据"""
        try:
            data = request.get_json(force=True) or {}
            from_time = data.get("from_time")
            if not from_time:
                return jsonify({"success": False, "error": "缺少 from_time 参数"}), 400
            deleted_csfloat = CsFloatBuyModel.delete_all("data_user = ? AND created_at >= ?", (user_id, from_time))
            deleted_buy = BuyModel.delete_all(
                "data_user = ? AND order_time >= ? AND `from` = 'csfloat'", (user_id, from_time)
            )
            return jsonify({
                "success": True, "message": "删除成功",
                "deleted_csfloat_count": deleted_csfloat, "deleted_buy_count": deleted_buy
            }), 200
        except Exception as exc:
            print(f"删除指定时间之后的购买数据失败: {exc}")
            return jsonify({"success": False, "error": str(exc)}), 500
