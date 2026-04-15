"""
Steam市场数据处理器
迁移自 web_side/webSide/steamMarket.py
统一使用 DatabaseManager + 参数化 SQL
"""
from flask import jsonify
from src.db_manager.database import DatabaseManager

STEAM_BUY = "steam_buy"
STEAM_SELL = "steam_sell"

_BUY_ROW_SQL = (
    f"SELECT [ID], item_name, weapon_name, weapon_type, weapon_float, float_range, "
    f"price, trade_date, game_name FROM {STEAM_BUY}"
)
_SELL_ROW_SQL = (
    f"SELECT [ID], item_name, weapon_name, weapon_type, weapon_float, float_range, "
    f"price, trade_date, game_name FROM {STEAM_SELL}"
)


def _row_to_array(row):
    """与原先 record_to_array 一致的 11 列数组"""
    return [
        row[0], row[1], row[2], row[3], row[4], row[5],
        row[6], "Steam", row[7], "已完成", row[8],
    ]


def _distinct_game_names(table: str):
    db = DatabaseManager()
    sql = f"""
    SELECT DISTINCT game_name FROM {table}
    WHERE game_name IS NOT NULL AND TRIM(game_name) != ''
    ORDER BY game_name
    """
    rows = db.execute_query(sql, ())
    names = sorted({r[0] for r in rows if r and r[0]})
    if "Counter-Strike 2" in names:
        names.remove("Counter-Strike 2")
        names.insert(0, "Counter-Strike 2")
    return names


def _stats_from_sql(where_sql: str, params: tuple, table: str):
    db = DatabaseManager()
    sql = f"""
    SELECT COUNT(*),
           COALESCE(SUM(CASE WHEN price IS NOT NULL THEN price ELSE 0 END), 0)
    FROM {table}
    {where_sql}
    """
    rows = db.execute_query(sql, params)
    if not rows:
        return _empty_stats
    total_count, total_amount = rows[0]
    total_count = int(total_count or 0)
    total_amount = float(total_amount or 0)
    avg_price = total_amount / total_count if total_count else 0
    return {
        "total_count": total_count,
        "total_amount": round(total_amount, 2),
        "avg_price": round(avg_price, 2),
        "completed_count": total_count,
        "cancelled_count": 0,
        "pending_count": 0,
    }


_empty_stats = {
    "total_count": 0,
    "total_amount": 0,
    "avg_price": 0,
    "completed_count": 0,
    "cancelled_count": 0,
    "pending_count": 0,
}


class SteamMarketBuy:

    @staticmethod
    def get_buy_game_names():
        try:
            return jsonify(_distinct_game_names(STEAM_BUY)), 200
        except Exception as e:
            print(f"获取购买游戏名称失败: {e}")
            return jsonify([]), 500

    @staticmethod
    def get_buy_data(min, max):
        try:
            sql = f"{_BUY_ROW_SQL} ORDER BY trade_date DESC LIMIT ? OFFSET ?"
            rows = DatabaseManager().execute_query(sql, (max, min))
            return jsonify([_row_to_array(r) for r in rows]), 200
        except Exception as e:
            print(f"查询Steam购买数据失败: {e}")
            return jsonify([]), 500

    @staticmethod
    def search_buy_by_name(itemName):
        try:
            like = f"%{itemName}%"
            sql = f"{_BUY_ROW_SQL} WHERE item_name LIKE ? OR weapon_name LIKE ? ORDER BY trade_date DESC"
            rows = DatabaseManager().execute_query(sql, (like, like))
            return jsonify([_row_to_array(r) for r in rows]), 200
        except Exception as e:
            print(f"搜索Steam购买记录失败: {e}")
            return jsonify([]), 500

    @staticmethod
    def get_buy_data_by_game_name(gameName, min, max):
        try:
            sql = f"{_BUY_ROW_SQL} WHERE game_name = ? ORDER BY trade_date DESC LIMIT ? OFFSET ?"
            rows = DatabaseManager().execute_query(sql, (gameName, max, min))
            return jsonify([_row_to_array(r) for r in rows]), 200
        except Exception as e:
            print(f"根据游戏名称查询Steam购买数据失败: {e}")
            return jsonify([]), 500

    @staticmethod
    def get_buy_stats():
        try:
            return jsonify(_stats_from_sql("", (), STEAM_BUY)), 200
        except Exception as e:
            print(f"获取Steam购买统计失败: {e}")
            return jsonify(_empty_stats), 500

    @staticmethod
    def get_buy_stats_by_search(itemName):
        try:
            like = f"%{itemName}%"
            w = "WHERE item_name LIKE ? OR weapon_name LIKE ?"
            return jsonify(_stats_from_sql(w, (like, like), STEAM_BUY)), 200
        except Exception as e:
            print(f"根据搜索获取Steam购买统计失败: {e}")
            return jsonify(_empty_stats), 500

    @staticmethod
    def get_buy_stats_by_game_name(gameName):
        try:
            return jsonify(_stats_from_sql("WHERE game_name = ?", (gameName,), STEAM_BUY)), 200
        except Exception as e:
            print(f"根据游戏名称获取Steam购买统计失败: {e}")
            return jsonify(_empty_stats), 500

    @staticmethod
    def search_buy_by_time_range(startDate, endDate):
        try:
            sql = f"{_BUY_ROW_SQL} WHERE DATE(trade_date) BETWEEN ? AND ? ORDER BY trade_date DESC"
            rows = DatabaseManager().execute_query(sql, (startDate, endDate))
            return jsonify([_row_to_array(r) for r in rows]), 200
        except Exception as e:
            print(f"根据时间范围搜索Steam购买记录失败: {e}")
            return jsonify([]), 500

    @staticmethod
    def get_buy_stats_by_time_range(startDate, endDate):
        try:
            w = "WHERE DATE(trade_date) BETWEEN ? AND ?"
            return jsonify(_stats_from_sql(w, (startDate, endDate), STEAM_BUY)), 200
        except Exception as e:
            print(f"根据时间范围获取Steam购买统计失败: {e}")
            return jsonify(_empty_stats), 500


class SteamMarketSell:

    @staticmethod
    def get_sell_game_names():
        try:
            return jsonify(_distinct_game_names(STEAM_SELL)), 200
        except Exception as e:
            print(f"获取销售游戏名称失败: {e}")
            return jsonify([]), 500

    @staticmethod
    def get_sell_data(min, max):
        try:
            sql = f"{_SELL_ROW_SQL} ORDER BY trade_date DESC LIMIT ? OFFSET ?"
            rows = DatabaseManager().execute_query(sql, (max, min))
            return jsonify([_row_to_array(r) for r in rows]), 200
        except Exception as e:
            print(f"查询Steam销售数据失败: {e}")
            return jsonify([]), 500

    @staticmethod
    def search_sell_by_name(itemName):
        try:
            like = f"%{itemName}%"
            sql = f"{_SELL_ROW_SQL} WHERE item_name LIKE ? OR weapon_name LIKE ? ORDER BY trade_date DESC"
            rows = DatabaseManager().execute_query(sql, (like, like))
            return jsonify([_row_to_array(r) for r in rows]), 200
        except Exception as e:
            print(f"搜索Steam销售记录失败: {e}")
            return jsonify([]), 500

    @staticmethod
    def get_sell_data_by_game_name(gameName, min, max):
        try:
            sql = f"{_SELL_ROW_SQL} WHERE game_name = ? ORDER BY trade_date DESC LIMIT ? OFFSET ?"
            rows = DatabaseManager().execute_query(sql, (gameName, max, min))
            return jsonify([_row_to_array(r) for r in rows]), 200
        except Exception as e:
            print(f"根据游戏名称查询Steam销售数据失败: {e}")
            return jsonify([]), 500

    @staticmethod
    def get_sell_stats():
        try:
            return jsonify(_stats_from_sql("", (), STEAM_SELL)), 200
        except Exception as e:
            print(f"获取Steam销售统计失败: {e}")
            return jsonify(_empty_stats), 500

    @staticmethod
    def get_sell_stats_by_search(itemName):
        try:
            like = f"%{itemName}%"
            w = "WHERE item_name LIKE ? OR weapon_name LIKE ?"
            return jsonify(_stats_from_sql(w, (like, like), STEAM_SELL)), 200
        except Exception as e:
            print(f"根据搜索获取Steam销售统计失败: {e}")
            return jsonify(_empty_stats), 500

    @staticmethod
    def get_sell_stats_by_game_name(gameName):
        try:
            return jsonify(_stats_from_sql("WHERE game_name = ?", (gameName,), STEAM_SELL)), 200
        except Exception as e:
            print(f"根据游戏名称获取Steam销售统计失败: {e}")
            return jsonify(_empty_stats), 500

    @staticmethod
    def search_sell_by_time_range(startDate, endDate):
        try:
            sql = f"{_SELL_ROW_SQL} WHERE DATE(trade_date) BETWEEN ? AND ? ORDER BY trade_date DESC"
            rows = DatabaseManager().execute_query(sql, (startDate, endDate))
            return jsonify([_row_to_array(r) for r in rows]), 200
        except Exception as e:
            print(f"根据时间范围搜索Steam销售记录失败: {e}")
            return jsonify([]), 500

    @staticmethod
    def get_sell_stats_by_time_range(startDate, endDate):
        try:
            w = "WHERE DATE(trade_date) BETWEEN ? AND ?"
            return jsonify(_stats_from_sql(w, (startDate, endDate), STEAM_SELL)), 200
        except Exception as e:
            print(f"根据时间范围获取Steam销售统计失败: {e}")
            return jsonify(_empty_stats), 500


class SteamMarketCombined:

    @staticmethod
    def get_steam_market_stats():
        try:
            db = DatabaseManager()
            buy_rows = db.execute_query(
                f"SELECT COUNT(*), COALESCE(SUM(price),0) FROM {STEAM_BUY}", ()
            )
            sell_rows = db.execute_query(
                f"SELECT COUNT(*), COALESCE(SUM(price),0) FROM {STEAM_SELL}", ()
            )
            buy_count = int(buy_rows[0][0]) if buy_rows else 0
            buy_total = float(buy_rows[0][1]) if buy_rows else 0.0
            sell_count = int(sell_rows[0][0]) if sell_rows else 0
            sell_total = float(sell_rows[0][1]) if sell_rows else 0.0
            buy_avg = buy_total / buy_count if buy_count else 0
            sell_avg = sell_total / sell_count if sell_count else 0

            return jsonify({
                "buy_count": buy_count,
                "buy_total": round(buy_total, 2),
                "buy_avg": round(buy_avg, 2),
                "sell_count": sell_count,
                "sell_total": round(sell_total, 2),
                "sell_avg": round(sell_avg, 2),
                "net_profit": round(sell_total - buy_total, 2),
                "total_transactions": buy_count + sell_count,
            }), 200
        except Exception as e:
            print(f"获取Steam市场综合统计失败: {e}")
            return jsonify({
                "buy_count": 0, "buy_total": 0, "buy_avg": 0,
                "sell_count": 0, "sell_total": 0, "sell_avg": 0,
                "net_profit": 0, "total_transactions": 0,
            }), 500
