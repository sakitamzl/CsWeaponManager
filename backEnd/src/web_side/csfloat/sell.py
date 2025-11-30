import json
from flask import Blueprint, jsonify, request

from src.db_manager.csfloat import CsFloatSellModel
from src.db_manager.index.sell import SellModel

csfloatSellV1 = Blueprint("csfloatSellV1", __name__)


@csfloatSellV1.route("/selectNotEnd/<user_id>", methods=["GET"])
def select_not_end(user_id):
    try:
        records = CsFloatSellModel.find_not_end_status(user_id)
        ids = [record.ID for record in records]
        return jsonify({"not_end_orders": ids}), 200
    except Exception as exc:
        print(f"查询 CSFloat 销售未完成订单失败: {exc}")
        return jsonify({"not_end_orders": []}), 500


@csfloatSellV1.route("/getLatestData/<user_id>", methods=["GET"])
def get_latest_data(user_id):
    try:
        record = CsFloatSellModel.get_latest_order(user_id)
        if not record:
            return jsonify({"ID": None, "order_time": None}), 200
        return (
            jsonify(
                {
                    "ID": record.ID,
                    "order_time": record.created_at,
                }
            ),
            200,
        )
    except Exception as exc:
        print(f"获取最新 CSFloat 销售数据失败: {exc}")
        return jsonify({"ID": None, "order_time": None}), 500


@csfloatSellV1.route("/updateOrderStatus", methods=["POST"])
def update_order_status():
    try:
        data = request.get_json(force=True)
        trade_id = data.get("trade_id")
        state = data.get("state")
        state_sub = data.get("state_sub")
        verified_at = data.get("verified_at")

        if not trade_id:
            return jsonify({"success": False, "error": "缺少 trade_id"}), 400

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


@csfloatSellV1.route("/insert_db", methods=["POST"])
def insert_db():
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"success": False, "error": "无效的 JSON 数据"}), 400

        trade_id = data.get("trade_id")
        if not trade_id:
            return jsonify({"success": False, "error": "缺少 trade_id"}), 400

        csfloat_record = CsFloatSellModel()
        csfloat_record.ID = trade_id
        csfloat_record.contract_id = data.get("contract_id")
        csfloat_record.weapon_name = data.get("weaponitem_name")
        csfloat_record.weapon_type = data.get("weapon_type")
        csfloat_record.item_name = data.get("item_name")
        csfloat_record.weapon_float = data.get("weapon_float")
        csfloat_record.float_range = data.get("float_range")
        price_cny = data.get("price")  # 人民币价格(CNY)
        price_usd = data.get("price_usd")  # 美元价格(USD)
        csfloat_record.price = price_cny
        csfloat_record.us_price = price_usd
        csfloat_record.price_original = data.get("price_original")
        csfloat_record.buyer_name = data.get("buyer_name")
        csfloat_record.buyer_id = data.get("buyer_id")
        csfloat_record.seller_name = data.get("seller_name")
        csfloat_record.seller_id = data.get("seller_id")
        csfloat_record.state = data.get("state")
        csfloat_record.state_sub = data.get("state_sub")
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
        sell_record.status = data.get("state")
        sell_record.status_sub = data.get("state_sub")
        sell_record.order_time = data.get("created_at")
        sell_record.data_user = data.get("data_user")
        sell_record.steam_id = data.get("steam_id")
        sell_record.steam_hash_name = data.get("market_hash_name")  # 将market_hash_name存入steam_hash_name字段
        # 处理stickers和keychains数据，转换为JSON字符串存储到sell表
        stickers = data.get("stickers")
        if stickers:
            sell_record.sticker = json.dumps(stickers, ensure_ascii=False)
        else:
            sell_record.sticker = None
        
        keychains = data.get("keychains")
        if keychains:
            sell_record.pendant = json.dumps(keychains, ensure_ascii=False)
        else:
            sell_record.pendant = None
        
        setattr(sell_record, "from", "csfloat")
        sell_record.save()

        return jsonify({"success": True, "message": "CSFloat 销售数据插入成功"}), 200
    except Exception as exc:
        print(f"CSFloat 销售数据插入失败: {exc}")
        return jsonify({"success": False, "error": str(exc)}), 500


@csfloatSellV1.route("/countData/<user_id>", methods=["GET"])
def count_data(user_id):
    try:
        records = CsFloatSellModel.find_all("data_user = ?", (user_id,))
        return jsonify({"count": len(records)}), 200
    except Exception as exc:
        print(f"统计 CSFloat 销售数据失败: {exc}")
        return jsonify({"count": 0}), 500

