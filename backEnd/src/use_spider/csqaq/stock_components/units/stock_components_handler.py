# -*- coding: utf-8 -*-
"""
CSQAQ stock_components 处理模块（供 Spider 调用）
- getHashNames: 获取某账号下 steam_stockComponents 的 steam_hash_name 列表，供 Spider 调 CSQAQ 查价
- writePrices: 将 CSQAQ 返回的价格写入 steam_stockComponents（yyyp_price / buff_price / steam_price）
"""
import traceback
from flask import request, jsonify
from src.db_manager.database import DatabaseManager


class CsqaqStockComponentsHandler:

    @staticmethod
    def get_hash_names(steam_id):
        """
        GET 获取指定账号下 steam_stockComponents 中所有不重复的 steam_hash_name。
        供 Spider 调用，用于向 CSQAQ 批量查价。
        """
        try:
            if not steam_id or not steam_id.strip():
                return jsonify({"success": False, "message": "steam_id 不能为空", "data": None}), 400
            db = DatabaseManager()
            sql = """
            SELECT DISTINCT steam_hash_name
            FROM steam_stockComponents
            WHERE data_user = ?
              AND steam_hash_name IS NOT NULL
              AND steam_hash_name != ''
            """
            rows = db.execute_query(sql, (steam_id.strip(),))
            names = [row[0] for row in (rows or []) if row[0]]
            return jsonify({"success": True, "message": "ok", "data": names}), 200
        except Exception as e:
            traceback.print_exc()
            return jsonify({"success": False, "message": str(e), "data": None}), 500

    @staticmethod
    def write_prices():
        """
        POST 将 CSQAQ 返回的价格写入 steam_stockComponents。
        请求体: { "steam_id": "...", "prices": { "marketHashName": { "yyypSellPrice", "buffSellPrice", "steamSellPrice" }, ... } }
        按 steam_hash_name + data_user 更新 yyyp_price、buff_price、steam_price。
        """
        try:
            data = request.get_json(silent=True) or {}
            steam_id = (data.get("steam_id") or "").strip()
            prices = data.get("prices")
            if not steam_id:
                return jsonify({"success": False, "message": "steam_id 不能为空", "data": None}), 400
            if not prices or not isinstance(prices, dict):
                return jsonify({"success": False, "message": "prices 必须为非空对象", "data": None}), 400

            db = DatabaseManager()
            updated = 0
            for market_hash_name, info in prices.items():
                if not market_hash_name or not isinstance(info, dict):
                    continue
                yyyp = info.get("yyypSellPrice")
                buff = info.get("buffSellPrice")
                steam = info.get("steamSellPrice")
                yyyp_str = str(yyyp) if yyyp is not None else None
                buff_str = str(buff) if buff is not None else None
                steam_str = str(steam) if steam is not None else None
                update_sql = """
                UPDATE steam_stockComponents
                SET yyyp_price = COALESCE(?, yyyp_price),
                    buff_price = COALESCE(?, buff_price),
                    steam_price = COALESCE(?, steam_price)
                WHERE data_user = ? AND steam_hash_name = ?
                """
                n = db.execute_update(
                    update_sql,
                    (yyyp_str, buff_str, steam_str, steam_id, market_hash_name),
                )
                updated += n

            return jsonify({
                "success": True,
                "message": "ok",
                "data": {"updated": updated},
            }), 200
        except Exception as e:
            traceback.print_exc()
            return jsonify({"success": False, "message": str(e), "data": None}), 500
