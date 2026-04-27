"""
C5GAME sell 写入模块
仅写入 sell 表，使用 ID_sub 记录主订单号（子订单归并）。
"""
import json
from flask import jsonify, request
from src.db_manager.index.model.sell import SellModel


def _normalize_json_text(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, ensure_ascii=False)
    except Exception:
        return None


class SellInsert:
    @staticmethod
    def insert_db():
        try:
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "无效的JSON数据"}), 400

            item_id = str(data.get("item_id") or "").strip()
            if not item_id:
                return jsonify({"success": False, "error": "缺少 item_id"}), 400

            sell_record = SellModel()
            sell_record.ID = item_id
            sell_record.ID_sub = str(data.get("item_id_sub") or "").strip() or None
            sell_record.weapon_name = data.get("weaponitem_name")
            sell_record.weapon_type = data.get("weapon_type")
            sell_record.item_name = data.get("item_name")
            sell_record.weapon_float = data.get("weapon_float")
            sell_record.float_range = data.get("float_range")
            sell_record.price = data.get("price")
            sell_record.price_original = data.get("price_original")
            sell_record.buyer_name = data.get("seller_id")
            sell_record.status = data.get("state")
            sell_record.order_time = data.get("created_at")
            sell_record.data_user = data.get("data_user")
            sell_record.status_sub = data.get("state_sub")
            sell_record.sticker = _normalize_json_text(data.get("sticker"))
            sell_record.pendant = _normalize_json_text(data.get("pendant"))
            sell_record.rename = data.get("rename")
            sell_record.steam_hash_name = data.get("market_hash_name") or data.get("img_url")
            sell_record.steam_id = data.get("seller_id")
            setattr(sell_record, "from", "c5")

            saved = sell_record.save()
            if not saved:
                return jsonify({"success": False, "error": "数据插入失败"}), 500

            return jsonify(
                {
                    "success": True,
                    "message": "C5GAME销售数据插入成功",
                    "data": {"id": sell_record.ID, "id_sub": sell_record.ID_sub},
                }
            ), 200
        except Exception as e:
            print(f"C5GAME销售数据插入错误: {e}")
            import traceback
            print(traceback.format_exc())
            return jsonify({"success": False, "error": f"服务器错误: {str(e)}"}), 500

