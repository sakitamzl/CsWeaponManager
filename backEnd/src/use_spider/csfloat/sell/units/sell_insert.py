"""
CSFloat sell 写入模块
提供 Spider 所需的销售记录插入、状态更新与数据清理接口
"""
import json
import sys
from pathlib import Path
from flask import jsonify, request
from src.db_manager.csfloat.model import CsFloatSellModel
from src.db_manager.index.model.sell import SellModel

# 导入状态映射模块
spider_path = Path(__file__).parent.parent.parent.parent.parent.parent / "Spider" / "src"
if str(spider_path) not in sys.path:
    sys.path.insert(0, str(spider_path))

try:
    from model.csfloat_state import get_status_mapping
except ImportError:
    def get_status_mapping(csfloat_state):
        return {"status": csfloat_state, "status_sub": None}


class SellInsert:

    @staticmethod
    def insert_db():
        """插入 CSFloat 销售记录（同时写入 csfloat_sell 表和 sell 主表）"""
        try:
            data = request.get_json(force=True)
            if not data:
                return jsonify({"success": False, "error": "无效的 JSON 数据"}), 400

            trade_id = data.get("trade_id")
            if not trade_id:
                return jsonify({"success": False, "error": "缺少 trade_id"}), 400

            original_state = data.get("state")
            status_mapping = get_status_mapping(original_state)

            csfloat_record = CsFloatSellModel()
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
            csfloat_record.buyer_name = data.get("buyer_name")
            csfloat_record.buyer_id = data.get("buyer_id")
            csfloat_record.seller_name = data.get("seller_name")
            csfloat_record.seller_id = data.get("seller_id")
            csfloat_record.state = status_mapping["status"]
            csfloat_record.state_sub = status_mapping["status_sub"]
            csfloat_record.created_at = data.get("created_at")
            csfloat_record.accepted_at = data.get("accepted_at")
            csfloat_record.inventory_check_status = data.get("inventory_check_status")
            csfloat_record.market_hash_name = data.get("market_hash_name")
            csfloat_record.data_user = data.get("data_user")
            csfloat_record.save()

            sell_record = SellModel()
            sell_record.ID = trade_id
            sell_record.weapon_name = data.get("weaponitem_name")
            sell_record.weapon_type = data.get("weapon_type")
            sell_record.item_name = data.get("item_name")
            sell_record.weapon_float = data.get("weapon_float")
            sell_record.float_range = data.get("float_range")
            sell_record.price = data.get("price")
            sell_record.price_original = data.get("price_original")
            sell_record.buyer_name = data.get("buyer_name")
            sell_record.status = status_mapping["status"]
            sell_record.status_sub = status_mapping["status_sub"]
            sell_record.order_time = data.get("created_at")
            sell_record.data_user = data.get("data_user")
            sell_record.steam_id = data.get("steam_id")
            sell_record.steam_hash_name = data.get("market_hash_name")
            stickers = data.get("stickers")
            sell_record.sticker = json.dumps(stickers, ensure_ascii=False) if stickers else None
            keychains = data.get("keychains")
            sell_record.pendant = json.dumps(keychains, ensure_ascii=False) if keychains else None
            setattr(sell_record, "from", "csfloat")
            sell_record.save()

            return jsonify({"success": True, "message": "CSFloat 销售数据插入成功"}), 200
        except Exception as exc:
            print(f"CSFloat 销售数据插入失败: {exc}")
            return jsonify({"success": False, "error": str(exc)}), 500

    @staticmethod
    def update_order_status():
        """更新 CSFloat 销售订单状态（同时更新 csfloat_sell 和 sell 主表）"""
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

            record = CsFloatSellModel.find_by_id(ID=trade_id)
            if record:
                record.state = state
                record.state_sub = state_sub
                record.save()

            sell_record = SellModel.find_by_id(ID=trade_id)
            if sell_record:
                sell_record.status = state
                sell_record.status_sub = state_sub
                if verified_at:
                    sell_record.order_time = verified_at
                sell_record.save()

            return jsonify({"success": True, "message": "更新成功"}), 200
        except Exception as exc:
            print(f"更新 CSFloat 销售订单状态失败: {exc}")
            return jsonify({"success": False, "error": str(exc)}), 500

    @staticmethod
    def delete_recent_days(user_id, days):
        """删除指定用户最近 N 天的销售数据（csfloat_sell 和 sell 表）"""
        try:
            from datetime import datetime, timedelta
            cutoff_time = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
            deleted_csfloat = CsFloatSellModel.delete_all("data_user = ? AND created_at >= ?", (user_id, cutoff_time))
            deleted_sell = SellModel.delete_all(
                "data_user = ? AND order_time >= ? AND `from` = 'csfloat'", (user_id, cutoff_time)
            )
            return jsonify({
                "success": True, "message": "删除成功",
                "deleted_csfloat_count": deleted_csfloat, "deleted_sell_count": deleted_sell
            }), 200
        except Exception as exc:
            print(f"删除最近 {days} 天销售数据失败: {exc}")
            return jsonify({"success": False, "error": str(exc)}), 500

    @staticmethod
    def delete_from_time(user_id):
        """删除指定用户从某时间点之后的所有销售数据"""
        try:
            data = request.get_json(force=True) or {}
            from_time = data.get("from_time")
            if not from_time:
                return jsonify({"success": False, "error": "缺少 from_time 参数"}), 400
            deleted_csfloat = CsFloatSellModel.delete_all("data_user = ? AND created_at >= ?", (user_id, from_time))
            deleted_sell = SellModel.delete_all(
                "data_user = ? AND order_time >= ? AND `from` = 'csfloat'", (user_id, from_time)
            )
            return jsonify({
                "success": True, "message": "删除成功",
                "deleted_csfloat_count": deleted_csfloat, "deleted_sell_count": deleted_sell
            }), 200
        except Exception as exc:
            print(f"删除指定时间之后的销售数据失败: {exc}")
            return jsonify({"success": False, "error": str(exc)}), 500
