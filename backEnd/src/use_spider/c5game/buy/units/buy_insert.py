"""
C5GAME buy 写入模块
仅写入 buy 表。
"""
import json
from flask import jsonify, request
from src.db_manager.index.model.buy import BuyModel


def _normalize_json_text(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, ensure_ascii=False)
    except Exception:
        return None


class BuyInsert:
    @staticmethod
    def insert_db():
        try:
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "无效的JSON数据"}), 400

            item_id = str(data.get("item_id") or "").strip()
            if not item_id:
                return jsonify({"success": False, "error": "缺少 item_id"}), 400

            buy_record = BuyModel()
            buy_record.ID = item_id
            buy_record.ID_sub = str(data.get("item_id_sub") or "").strip() or None
            buy_record.weapon_name = data.get("weaponitem_name")
            buy_record.weapon_type = data.get("weapon_type")
            buy_record.item_name = data.get("item_name")
            buy_record.weapon_float = data.get("weapon_float")
            buy_record.float_range = data.get("float_range")
            buy_record.price = data.get("price")
            buy_record.seller_name = data.get("seller_id")
            buy_record.status = data.get("state")
            buy_record.order_time = data.get("created_at")
            buy_record.data_user = data.get("data_user")
            buy_record.status_sub = data.get("state_sub")
            buy_record.sticker = _normalize_json_text(data.get("sticker"))
            buy_record.pendant = _normalize_json_text(data.get("pendant"))
            buy_record.rename = data.get("rename")
            buy_record.steam_hash_name = data.get("market_hash_name") or data.get("img_url")
            buy_record.steam_id = data.get("seller_id")
            setattr(buy_record, "from", "c5game")

            saved = buy_record.save()
            if not saved:
                return jsonify({"success": False, "error": "数据插入失败"}), 500

            return jsonify(
                {
                    "success": True,
                    "message": "C5GAME购买数据插入成功",
                    "data": {"id": buy_record.ID, "id_sub": buy_record.ID_sub},
                }
            ), 200
        except Exception as e:
            print(f"C5GAME购买数据插入错误: {e}")
            import traceback
            print(traceback.format_exc())
            return jsonify({"success": False, "error": f"服务器错误: {str(e)}"}), 500

