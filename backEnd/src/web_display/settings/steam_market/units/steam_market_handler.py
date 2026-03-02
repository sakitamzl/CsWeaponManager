"""
Steam市场数据处理器
迁移自 web_side/webSide/steamMarket.py
"""
from flask import jsonify
from src.db_manager.steam.model.steam_buy import SteamBuyModel
from src.db_manager.steam.model.steam_sell import SteamSellModel


# ==================== Helper Functions ====================

def get_distinct_game_names(model_class):
    """获取不重复的游戏名称列表"""
    try:
        records = model_class.find_all("game_name IS NOT NULL")
        game_names = list(set([record.game_name for record in records if record.game_name]))
        game_names.sort()
        if 'Counter-Strike 2' in game_names:
            game_names.remove('Counter-Strike 2')
            game_names.insert(0, 'Counter-Strike 2')
        return game_names
    except Exception as e:
        print(f"获取游戏名称失败: {e}")
        return []


def calculate_stats(records):
    """计算统计数据"""
    if not records:
        return {
            "total_count": 0,
            "total_amount": 0,
            "avg_price": 0,
            "completed_count": 0,
            "cancelled_count": 0,
            "pending_count": 0
        }
    total_count = len(records)
    total_amount = sum([record.price for record in records if record.price])
    avg_price = total_amount / total_count if total_count > 0 else 0
    return {
        "total_count": total_count,
        "total_amount": round(float(total_amount), 2),
        "avg_price": round(float(avg_price), 2),
        "completed_count": total_count,
        "cancelled_count": 0,
        "pending_count": 0
    }


def record_to_array(record):
    """将记录转换为数组格式"""
    return [
        record.ID, record.item_name, record.weapon_name,
        record.weapon_type, record.weapon_float, record.float_range,
        record.price, 'Steam', record.trade_date, '已完成', record.game_name
    ]


_empty_stats = {
    "total_count": 0, "total_amount": 0, "avg_price": 0,
    "completed_count": 0, "cancelled_count": 0, "pending_count": 0
}


# ==================== Steam Buy ====================

class SteamMarketBuy:

    @staticmethod
    def get_buy_game_names():
        try:
            return jsonify(get_distinct_game_names(SteamBuyModel)), 200
        except Exception as e:
            print(f"获取购买游戏名称失败: {e}")
            return jsonify([]), 500

    @staticmethod
    def get_buy_data(min, max):
        try:
            records = SteamBuyModel.find_all(
                "1=1 ORDER BY trade_date DESC", (), limit=max, offset=min
            )
            return jsonify([record_to_array(r) for r in records]), 200
        except Exception as e:
            print(f"查询Steam购买数据失败: {e}")
            return jsonify([]), 500

    @staticmethod
    def search_buy_by_name(itemName):
        try:
            records = SteamBuyModel.find_all(
                "item_name LIKE ? OR weapon_name LIKE ? ORDER BY trade_date DESC",
                (f"%{itemName}%", f"%{itemName}%")
            )
            return jsonify([record_to_array(r) for r in records]), 200
        except Exception as e:
            print(f"搜索Steam购买记录失败: {e}")
            return jsonify([]), 500

    @staticmethod
    def get_buy_data_by_game_name(gameName, min, max):
        try:
            records = SteamBuyModel.find_all(
                "game_name = ? ORDER BY trade_date DESC", (gameName,), limit=max, offset=min
            )
            return jsonify([record_to_array(r) for r in records]), 200
        except Exception as e:
            print(f"根据游戏名称查询Steam购买数据失败: {e}")
            return jsonify([]), 500

    @staticmethod
    def get_buy_stats():
        try:
            records = SteamBuyModel.find_all()
            return jsonify(calculate_stats(records)), 200
        except Exception as e:
            print(f"获取Steam购买统计失败: {e}")
            return jsonify(_empty_stats), 500

    @staticmethod
    def get_buy_stats_by_search(itemName):
        try:
            records = SteamBuyModel.find_all(
                "item_name LIKE ? OR weapon_name LIKE ?",
                (f"%{itemName}%", f"%{itemName}%")
            )
            return jsonify(calculate_stats(records)), 200
        except Exception as e:
            print(f"根据搜索获取Steam购买统计失败: {e}")
            return jsonify(_empty_stats), 500

    @staticmethod
    def get_buy_stats_by_game_name(gameName):
        try:
            records = SteamBuyModel.find_all("game_name = ?", (gameName,))
            return jsonify(calculate_stats(records)), 200
        except Exception as e:
            print(f"根据游戏名称获取Steam购买统计失败: {e}")
            return jsonify(_empty_stats), 500

    @staticmethod
    def search_buy_by_time_range(startDate, endDate):
        try:
            records = SteamBuyModel.find_all(
                "DATE(trade_date) BETWEEN ? AND ? ORDER BY trade_date DESC",
                (startDate, endDate)
            )
            return jsonify([record_to_array(r) for r in records]), 200
        except Exception as e:
            print(f"根据时间范围搜索Steam购买记录失败: {e}")
            return jsonify([]), 500

    @staticmethod
    def get_buy_stats_by_time_range(startDate, endDate):
        try:
            records = SteamBuyModel.find_all(
                "DATE(trade_date) BETWEEN ? AND ?", (startDate, endDate)
            )
            return jsonify(calculate_stats(records)), 200
        except Exception as e:
            print(f"根据时间范围获取Steam购买统计失败: {e}")
            return jsonify(_empty_stats), 500


# ==================== Steam Sell ====================

class SteamMarketSell:

    @staticmethod
    def get_sell_game_names():
        try:
            return jsonify(get_distinct_game_names(SteamSellModel)), 200
        except Exception as e:
            print(f"获取销售游戏名称失败: {e}")
            return jsonify([]), 500

    @staticmethod
    def get_sell_data(min, max):
        try:
            records = SteamSellModel.find_all(
                "1=1 ORDER BY trade_date DESC", (), limit=max, offset=min
            )
            return jsonify([record_to_array(r) for r in records]), 200
        except Exception as e:
            print(f"查询Steam销售数据失败: {e}")
            return jsonify([]), 500

    @staticmethod
    def search_sell_by_name(itemName):
        try:
            records = SteamSellModel.find_all(
                "item_name LIKE ? OR weapon_name LIKE ? ORDER BY trade_date DESC",
                (f"%{itemName}%", f"%{itemName}%")
            )
            return jsonify([record_to_array(r) for r in records]), 200
        except Exception as e:
            print(f"搜索Steam销售记录失败: {e}")
            return jsonify([]), 500

    @staticmethod
    def get_sell_data_by_game_name(gameName, min, max):
        try:
            records = SteamSellModel.find_all(
                "game_name = ? ORDER BY trade_date DESC", (gameName,), limit=max, offset=min
            )
            return jsonify([record_to_array(r) for r in records]), 200
        except Exception as e:
            print(f"根据游戏名称查询Steam销售数据失败: {e}")
            return jsonify([]), 500

    @staticmethod
    def get_sell_stats():
        try:
            records = SteamSellModel.find_all()
            return jsonify(calculate_stats(records)), 200
        except Exception as e:
            print(f"获取Steam销售统计失败: {e}")
            return jsonify(_empty_stats), 500

    @staticmethod
    def get_sell_stats_by_search(itemName):
        try:
            records = SteamSellModel.find_all(
                "item_name LIKE ? OR weapon_name LIKE ?",
                (f"%{itemName}%", f"%{itemName}%")
            )
            return jsonify(calculate_stats(records)), 200
        except Exception as e:
            print(f"根据搜索获取Steam销售统计失败: {e}")
            return jsonify(_empty_stats), 500

    @staticmethod
    def get_sell_stats_by_game_name(gameName):
        try:
            records = SteamSellModel.find_all("game_name = ?", (gameName,))
            return jsonify(calculate_stats(records)), 200
        except Exception as e:
            print(f"根据游戏名称获取Steam销售统计失败: {e}")
            return jsonify(_empty_stats), 500

    @staticmethod
    def search_sell_by_time_range(startDate, endDate):
        try:
            records = SteamSellModel.find_all(
                "DATE(trade_date) BETWEEN ? AND ? ORDER BY trade_date DESC",
                (startDate, endDate)
            )
            return jsonify([record_to_array(r) for r in records]), 200
        except Exception as e:
            print(f"根据时间范围搜索Steam销售记录失败: {e}")
            return jsonify([]), 500

    @staticmethod
    def get_sell_stats_by_time_range(startDate, endDate):
        try:
            records = SteamSellModel.find_all(
                "DATE(trade_date) BETWEEN ? AND ?", (startDate, endDate)
            )
            return jsonify(calculate_stats(records)), 200
        except Exception as e:
            print(f"根据时间范围获取Steam销售统计失败: {e}")
            return jsonify(_empty_stats), 500


# ==================== Combined ====================

class SteamMarketCombined:

    @staticmethod
    def get_steam_market_stats():
        try:
            buy_records = SteamBuyModel.find_all()
            buy_count = len(buy_records)
            buy_total = sum([r.price for r in buy_records if r.price])
            buy_avg = buy_total / buy_count if buy_count > 0 else 0

            sell_records = SteamSellModel.find_all()
            sell_count = len(sell_records)
            sell_total = sum([r.price for r in sell_records if r.price])
            sell_avg = sell_total / sell_count if sell_count > 0 else 0

            return jsonify({
                "buy_count": buy_count,
                "buy_total": round(float(buy_total), 2),
                "buy_avg": round(float(buy_avg), 2),
                "sell_count": sell_count,
                "sell_total": round(float(sell_total), 2),
                "sell_avg": round(float(sell_avg), 2),
                "net_profit": round(float(sell_total - buy_total), 2),
                "total_transactions": buy_count + sell_count
            }), 200
        except Exception as e:
            print(f"获取Steam市场综合统计失败: {e}")
            return jsonify({
                "buy_count": 0, "buy_total": 0, "buy_avg": 0,
                "sell_count": 0, "sell_total": 0, "sell_avg": 0,
                "net_profit": 0, "total_transactions": 0
            }), 500
