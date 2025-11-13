from flask import Blueprint, jsonify, request

from src.db_manager.csfloat import CsFloatBuyModel
from src.db_manager.index.buy import BuyModel

csfloatBuyV1 = Blueprint("csfloatBuyV1", __name__)


@csfloatBuyV1.route("/selectNotEnd/<user_id>", methods=["GET"])
def select_not_end(user_id):
    try:
        records = CsFloatBuyModel.find_not_end_status(user_id)
        ids = [record.ID for record in records]
        return jsonify({"not_end_orders": ids}), 200
    except Exception as exc:
        print(f"查询 CSFloat 购买未完成订单失败: {exc}")
        return jsonify({"not_end_orders": []}), 500


@csfloatBuyV1.route("/getLatestData/<user_id>", methods=["GET"])
def get_latest_data(user_id):
    try:
        record = CsFloatBuyModel.get_latest_order(user_id)
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
        print(f"获取最新 CSFloat 购买数据失败: {exc}")
        return jsonify({"ID": None, "order_time": None}), 500


@csfloatBuyV1.route("/updateOrderStatus", methods=["POST"])
def update_order_status():
    try:
        data = request.get_json(force=True)
        trade_id = data.get("trade_id")
        state = data.get("state")
        state_sub = data.get("state_sub")
        verified_at = data.get("verified_at")

        if not trade_id:
            return jsonify({"success": False, "error": "缺少 trade_id"}), 400

        record = CsFloatBuyModel.find_by_id(ID=trade_id)
        if record:
            record.state = state
            record.state_sub = state_sub
            if verified_at:
                record.verified_at = verified_at
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


@csfloatBuyV1.route("/insert_db", methods=["POST"])
def insert_db():
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"success": False, "error": "无效的 JSON 数据"}), 400

        trade_id = data.get("trade_id")
        if not trade_id:
            return jsonify({"success": False, "error": "缺少 trade_id"}), 400

        csfloat_record = CsFloatBuyModel()
        csfloat_record.ID = trade_id
        csfloat_record.contract_id = data.get("contract_id")
        csfloat_record.weapon_name = data.get("weaponitem_name")
        csfloat_record.weapon_type = data.get("weapon_type")
        csfloat_record.item_name = data.get("item_name")
        csfloat_record.weapon_float = data.get("weapon_float")
        csfloat_record.float_range = data.get("float_range")
        csfloat_record.price = data.get("price")
        csfloat_record.price_raw = data.get("price_raw")
        csfloat_record.price_original = data.get("price_original")
        csfloat_record.currency = data.get("currency")
        csfloat_record.seller_name = data.get("seller_name")
        csfloat_record.seller_id = data.get("seller_id")
        csfloat_record.buyer_name = data.get("buyer_name")
        csfloat_record.buyer_id = data.get("buyer_id")
        csfloat_record.state = data.get("state")
        csfloat_record.state_sub = data.get("state_sub")
        csfloat_record.created_at = data.get("created_at")
        csfloat_record.accepted_at = data.get("accepted_at")
        csfloat_record.verified_at = data.get("verified_at")
        csfloat_record.trade_url = data.get("trade_url")
        csfloat_record.trade_token = data.get("trade_token")
        csfloat_record.steam_offer_id = data.get("steam_offer_id")
        csfloat_record.steam_offer_state = data.get("steam_offer_state")
        csfloat_record.verification_mode = data.get("verification_mode")
        csfloat_record.inventory_check_status = data.get("inventory_check_status")
        csfloat_record.icon_url = data.get("icon_url")
        csfloat_record.market_hash_name = data.get("market_hash_name")
        csfloat_record.data_user = data.get("data_user")
        csfloat_record.role = data.get("role", "buyer")
        setattr(csfloat_record, "from", "csfloat")
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
        buy_record.status = data.get("state")
        buy_record.status_sub = data.get("state_sub")
        buy_record.order_time = data.get("created_at")
        buy_record.payment = None
        buy_record.trade_type = None
        buy_record.data_user = data.get("data_user")
        buy_record.steam_id = data.get("steam_id")
        setattr(buy_record, "from", "csfloat")
        buy_record.save()

        return jsonify({"success": True, "message": "CSFloat 购买数据插入成功"}), 200
    except Exception as exc:
        print(f"CSFloat 购买数据插入失败: {exc}")
        return jsonify({"success": False, "error": str(exc)}), 500


@csfloatBuyV1.route("/countData/<user_id>", methods=["GET"])
def count_data(user_id):
    try:
        records = CsFloatBuyModel.find_all("data_user = ?", (user_id,))
        return jsonify({"count": len(records)}), 200
    except Exception as exc:
        print(f"统计 CSFloat 购买数据失败: {exc}")
        return jsonify({"count": 0}), 500

