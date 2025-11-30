import json
import sys
from pathlib import Path
from flask import Blueprint, jsonify, request

from src.db_manager.csfloat import CsFloatSellModel
from src.db_manager.index.sell import SellModel

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
        # 使用状态映射转换状态（与 csfloat_record 使用相同的映射）
        sell_record.status = status_mapping["status"]
        sell_record.status_sub = status_mapping["status_sub"]
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


@csfloatSellV1.route("/deleteRecentDays/<user_id>/<int:days>", methods=["DELETE"])
def delete_recent_days(user_id, days):
    """
    删除指定用户最近N天的销售数据（包括 sell 和 csfloat_sell 表）
    
    Args:
        user_id: 用户ID
        days: 天数
    """
    try:
        from datetime import datetime, timedelta
        from src.db_manager.index.sell import SellModel
        
        # 计算N天前的时间
        cutoff_time = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
        
        # 删除 csfloat_sell 表中最近N天的数据
        deleted_csfloat = CsFloatSellModel.delete_all(
            "data_user = ? AND created_at >= ?", (user_id, cutoff_time)
        )
        
        # 删除 sell 表中最近N天的数据（只删除来源为 csfloat 的）
        deleted_sell = SellModel.delete_all(
            "data_user = ? AND order_time >= ? AND `from` = 'csfloat'", 
            (user_id, cutoff_time)
        )
        
        return jsonify({
            "success": True, 
            "message": f"删除成功",
            "deleted_csfloat_count": deleted_csfloat,
            "deleted_sell_count": deleted_sell
        }), 200
    except Exception as exc:
        print(f"删除最近 {days} 天销售数据失败: {exc}")
        return jsonify({"success": False, "error": str(exc)}), 500

