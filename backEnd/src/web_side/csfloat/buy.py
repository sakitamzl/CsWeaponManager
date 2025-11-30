import json
from flask import Blueprint, jsonify, request

from src.db_manager.csfloat import CsFloatBuyModel
from src.db_manager.index.buy import BuyModel
from src.db_manager.index.weapon_classID import WeaponClassIDModel

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


@csfloatBuyV1.route("/resolveWeapon", methods=["POST"])
def resolve_weapon():
    try:
        data = request.get_json(force=True) or {}
        market_hash_name = data.get("market_hash_name") or data.get("steam_hash_name")
        if not market_hash_name:
            return jsonify({"success": False, "message": "缺少 market_hash_name"}), 400

        records = WeaponClassIDModel.find_by_steam_hash_name(market_hash_name)
        if not records:
            return jsonify({"success": False, "message": "未找到匹配数据"}), 200

        weapon = records[0]
        return jsonify(
            {
                "success": True,
                "data": {
                    "weapon_type": getattr(weapon, "weapon_type", None),
                    "weapon_name": getattr(weapon, "weapon_name", None),
                    "item_name": getattr(weapon, "item_name", None),
                    "float_range": getattr(weapon, "float_range", None),
                },
            }
        ), 200
    except Exception as exc:
        print(f"解析 CSFloat 武器信息失败: {exc}")
        return jsonify({"success": False, "error": str(exc)}), 500


@csfloatBuyV1.route("/resolveAccessory", methods=["POST"])
def resolve_accessory():
    """解析饰品信息（印花/挂件），使用name查询steam_hash_name，返回market_listing_item_name"""
    try:
        data = request.get_json(force=True) or {}
        name = data.get("name")
        if not name:
            return jsonify({"success": False, "message": "缺少 name"}), 400

        # 使用name查询steam_hash_name字段
        records = WeaponClassIDModel.find_by_steam_hash_name(name)
        if not records:
            return jsonify({"success": False, "message": "未找到匹配数据"}), 200

        accessory = records[0]
        return jsonify(
            {
                "success": True,
                "data": {
                    "market_listing_item_name": getattr(accessory, "market_listing_item_name", None),
                    "steam_hash_name": getattr(accessory, "steam_hash_name", None),
                },
            }
        ), 200
    except Exception as exc:
        print(f"解析 CSFloat 饰品信息失败: {exc}")
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
        price_cny = data.get("price")  # 人民币价格(CNY)
        price_usd = data.get("price_usd")  # 美元价格(USD)
        csfloat_record.price = price_cny
        csfloat_record.us_price = price_usd
        csfloat_record.price_original = data.get("price_original")
        csfloat_record.seller_name = data.get("seller_name")
        csfloat_record.seller_id = data.get("seller_id")
        csfloat_record.buyer_name = data.get("buyer_name")
        csfloat_record.buyer_id = data.get("buyer_id")
        csfloat_record.state = data.get("state")
        csfloat_record.state_sub = data.get("state_sub")
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
        buy_record.status = data.get("state")
        buy_record.status_sub = data.get("state_sub")
        buy_record.order_time = data.get("created_at")
        buy_record.payment = None
        buy_record.trade_type = None
        buy_record.data_user = data.get("data_user")
        buy_record.steam_id = data.get("steam_id")
        buy_record.steam_hash_name = data.get("market_hash_name")  # 将market_hash_name存入steam_hash_name字段
        # 处理stickers和keychains数据，转换为JSON字符串存储到buy表
        stickers = data.get("stickers")
        if stickers:
            buy_record.sticker = json.dumps(stickers, ensure_ascii=False)
        else:
            buy_record.sticker = None
        
        keychains = data.get("keychains")
        if keychains:
            buy_record.pendant = json.dumps(keychains, ensure_ascii=False)
        else:
            buy_record.pendant = None
        
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

