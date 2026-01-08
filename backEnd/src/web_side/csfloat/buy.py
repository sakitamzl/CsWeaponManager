import json
import sys
from pathlib import Path
from flask import Blueprint, jsonify, request

from src.db_manager.csfloat import CsFloatBuyModel
from src.db_manager.index.buy import BuyModel
from src.db_manager.index.weapon_classID import WeaponClassIDModel

# 导入状态映射模块
# 添加 Spider 目录到路径以便导入
spider_path = Path(__file__).parent.parent.parent.parent.parent / "Spider" / "src"
if str(spider_path) not in sys.path:
    sys.path.insert(0, str(spider_path))

try:
    from model.csfloat_state import get_status_mapping
except ImportError:
    # 如果导入失败，定义一个默认函数
    def get_status_mapping(csfloat_state):
        return {"status": csfloat_state, "status_sub": None}

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
        original_state = data.get("state")
        state_sub = data.get("state_sub")
        verified_at = data.get("verified_at")

        if not trade_id:
            return jsonify({"success": False, "error": "缺少 trade_id"}), 400

        # 使用状态映射转换状态
        status_mapping = get_status_mapping(original_state)
        state = status_mapping["status"]
        # 如果提供了 state_sub，优先使用；否则使用映射的子状态
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
    """解析饰品信息（印花/挂件），使用name查询steam_hash_name，返回market_listing_item_name
    支持三种查询方式：
    1. 如果name以"印花 | "开头，使用market_listing_item_name字段查询
    2. 如果name以"挂件 | "开头，使用market_listing_item_name字段查询
    3. 否则，使用steam_hash_name字段查询
    """
    try:
        data = request.get_json(force=True) or {}
        name = data.get("name")
        if not name:
            return jsonify({"success": False, "message": "缺少 name"}), 400

        records = None
        
        # 如果name以"印花 | "或"挂件 | "开头，使用market_listing_item_name字段查询
        if name.startswith("印花 | ") or name.startswith("挂件 | "):
            records = WeaponClassIDModel.find_by_market_listing_item_name(name)
        else:
            # 否则，使用steam_hash_name字段查询
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
        # 使用状态映射转换状态
        original_state = data.get("state")
        status_mapping = get_status_mapping(original_state)
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
        # 使用状态映射转换状态（与 csfloat_record 使用相同的映射）
        buy_record.status = status_mapping["status"]
        buy_record.status_sub = status_mapping["status_sub"]
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


@csfloatBuyV1.route("/deleteRecentDays/<user_id>/<int:days>", methods=["DELETE"])
def delete_recent_days(user_id, days):
    """
    删除指定用户最近N天的购买数据（包括 buy 和 csfloat_buy 表）
    
    Args:
        user_id: 用户ID
        days: 天数
    """
    try:
        from datetime import datetime, timedelta
        
        # 计算N天前的时间
        cutoff_time = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
        
        # 删除 csfloat_buy 表中最近N天的数据
        deleted_csfloat = CsFloatBuyModel.delete_all(
            "data_user = ? AND created_at >= ?", (user_id, cutoff_time)
        )
        
        # 删除 buy 表中最近N天的数据（只删除来源为 csfloat 的）
        deleted_buy = BuyModel.delete_all(
            "data_user = ? AND order_time >= ? AND `from` = 'csfloat'", 
            (user_id, cutoff_time)
        )
        
        return jsonify({
            "success": True, 
            "message": f"删除成功",
            "deleted_csfloat_count": deleted_csfloat,
            "deleted_buy_count": deleted_buy
        }), 200
    except Exception as exc:
        print(f"删除最近 {days} 天购买数据失败: {exc}")
        return jsonify({"success": False, "error": str(exc)}), 500


@csfloatBuyV1.route("/getEarliestNotEnd/<user_id>", methods=["GET"])
def get_earliest_not_end(user_id):
    """
    获取指定用户最早的一条未完成订单的时间（状态不等于"已完成"和"已取消"）
    
    Args:
        user_id: 用户ID
    
    Returns:
        earliest_time: 最早未完成订单的创建时间，如果没有则返回None
    """
    try:
        # 查询状态不等于"已完成"和"已取消"的订单，按创建时间升序排序，取第一条
        records = CsFloatBuyModel.find_all(
            "data_user = ? AND state != '已完成' AND state != '已取消' ORDER BY created_at ASC LIMIT 1",
            (user_id,)
        )
        
        if records:
            earliest_time = records[0].created_at
            return jsonify({
                "success": True,
                "earliest_time": earliest_time
            }), 200
        else:
            return jsonify({
                "success": True,
                "earliest_time": None
            }), 200
    except Exception as exc:
        print(f"获取最早未完成订单失败: {exc}")
        return jsonify({"success": False, "error": str(exc)}), 500


@csfloatBuyV1.route("/deleteFromTime/<user_id>", methods=["POST"])
def delete_from_time(user_id):
    """
    删除指定用户从某个时间点之后的所有购买数据（包括 buy 和 csfloat_buy 表）
    
    Args:
        user_id: 用户ID
        from_time: 起始时间（从请求体JSON中获取）
    """
    try:
        data = request.get_json(force=True) or {}
        from_time = data.get("from_time")
        
        if not from_time:
            return jsonify({"success": False, "error": "缺少 from_time 参数"}), 400
        
        # 删除 csfloat_buy 表中该时间之后的数据
        deleted_csfloat = CsFloatBuyModel.delete_all(
            "data_user = ? AND created_at >= ?", (user_id, from_time)
        )
        
        # 删除 buy 表中该时间之后的数据（只删除来源为 csfloat 的）
        deleted_buy = BuyModel.delete_all(
            "data_user = ? AND order_time >= ? AND `from` = 'csfloat'", 
            (user_id, from_time)
        )
        
        return jsonify({
            "success": True, 
            "message": f"删除成功",
            "deleted_csfloat_count": deleted_csfloat,
            "deleted_buy_count": deleted_buy
        }), 200
    except Exception as exc:
        print(f"删除指定时间之后的购买数据失败: {exc}")
        return jsonify({"success": False, "error": str(exc)}), 500

