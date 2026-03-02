"""
Steam market 处理模块
提供 Spider 所需的 Steam 市场交易记录查询与插入接口
"""
import re
from datetime import datetime
from flask import jsonify, request
from src.db_manager.steam.model.steam_market import SteamMarketModel
from src.db_manager.index.model.buy import BuyModel
from src.db_manager.index.model.sell import SellModel


def _parse_trade_date_to_datetime(trade_date_str):
    """将 Steam 交易日期字符串转换为 datetime 对象"""
    if not trade_date_str or trade_date_str == "未知交易日期":
        return None
    try:
        match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', trade_date_str)
        if match:
            return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        for fmt in ('%Y-%m-%d', '%Y/%m/%d'):
            try:
                return datetime.strptime(trade_date_str, fmt)
            except ValueError:
                pass
        return None
    except Exception as e:
        print(f"解析交易日期失败: {e}, 原始字符串: {trade_date_str}")
        return None


class MarketHandler:

    @staticmethod
    def count_data(data_user):
        """统计指定用户的 Steam 市场交易数据（购买 + 销售）"""
        try:
            buy_records = SteamMarketModel.find_all("data_user = ? AND trade_type = 'buy'", (data_user,))
            sell_records = SteamMarketModel.find_all("data_user = ? AND trade_type = 'sell'", (data_user,))
            buy_count = len(buy_records)
            sell_count = len(sell_records)
            return jsonify({
                "success": True,
                "data": {
                    "user_id": data_user,
                    "buy_count": buy_count,
                    "sell_count": sell_count,
                    "count": buy_count + sell_count
                }
            }), 200
        except Exception as e:
            print(f"查询Steam数据统计失败: {e}")
            import traceback
            print(traceback.format_exc())
            return jsonify({"success": False, "error": f"查询失败: {str(e)}", "data": {"user_id": data_user, "buy_count": 0, "sell_count": 0, "total_count": 0}}), 500

    @staticmethod
    def get_latest_data(data_user):
        """获取指定用户最新一条交易记录及总数统计"""
        try:
            buy_count = len(SteamMarketModel.find_all("data_user = ? AND trade_type = 'buy'", (data_user,)))
            sell_count = len(SteamMarketModel.find_all("data_user = ? AND trade_type = 'sell'", (data_user,)))
            latest_records = SteamMarketModel.find_all("data_user = ? ORDER BY trade_date DESC LIMIT 1", (data_user,))
            if latest_records:
                r = latest_records[0]
                return jsonify({"ID": r.ID, "trade_date": r.trade_date, "buy_count": buy_count, "sell_count": sell_count, "total_count": buy_count + sell_count}), 200
            return jsonify({"ID": None, "trade_date": None, "buy_count": buy_count, "sell_count": sell_count, "total_count": buy_count + sell_count}), 200
        except Exception as e:
            print(f"获取最新交易数据失败: {e}")
            return jsonify({"ID": None, "trade_date": None, "buy_count": 0, "sell_count": 0, "total_count": 0}), 500

    @staticmethod
    def get_earliest_data(data_user):
        """获取指定用户最早一条交易记录"""
        try:
            earliest_records = SteamMarketModel.find_all("data_user = ? ORDER BY trade_date ASC LIMIT 1", (data_user,))
            if earliest_records:
                r = earliest_records[0]
                return jsonify({"ID": r.ID, "trade_date": r.trade_date}), 200
            return jsonify({"ID": None, "trade_date": None}), 200
        except Exception as e:
            print(f"获取最早交易数据失败: {e}")
            return jsonify({"ID": None, "trade_date": None}), 500

    @staticmethod
    def insert_new_data():
        """插入新的 Steam 市场交易数据，同时同步到 buy/sell 主表"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': '无效的JSON数据'}), 400

            trade_type_raw = data.get('trade_type')
            steam_id = data.get('steamId')
            trade_date_datetime = _parse_trade_date_to_datetime(data.get('trade_date'))
            listing_date_str = data.get('listing_date')
            listing_date_datetime = _parse_trade_date_to_datetime(listing_date_str) if listing_date_str else None

            if trade_type_raw == '+':
                trade_type, operation_type = 'buy', '购买'
            elif trade_type_raw == '-':
                trade_type, operation_type = 'sell', '销售'
            else:
                return jsonify({'success': False, 'error': '无效的交易类型'}), 400

            SteamMarketModel.ensure_table_exists()
            market_record = SteamMarketModel()
            market_record.ID = data.get('ID')
            market_record.trade_type = trade_type
            market_record.asset_id = data.get('asset_id')
            market_record.price = data.get('price')
            market_record.price_original = data.get('price_original') if trade_type == 'sell' else None
            market_record.trade_date = trade_date_datetime
            market_record.listing_date = listing_date_datetime
            market_record.game_name = data.get('game_name')
            market_record.weapon_type = data.get('weapon_type')
            market_record.weapon_name = data.get('weapon_name')
            market_record.item_name = data.get('item_name')
            market_record.steam_hash_name = data.get('market_hash_name')
            market_record.float_range = data.get('exterior_wear')
            market_record.weapon_float = None
            market_record.inspect_link = data.get('inspect_link')
            market_record.data_user = steam_id
            market_record.sticker = data.get('sticker')
            market_record.pendant = data.get('pendant')
            market_record.rename = data.get('rename')
            steam_saved = market_record.save()

            if trade_type == 'buy':
                BuyModel.ensure_table_exists()
                main_record = BuyModel()
                main_record.ID = data.get('ID')
                setattr(main_record, 'from', 'SMK')
                main_record.weapon_name = data.get('weapon_name')
                main_record.weapon_type = data.get('weapon_type')
                main_record.item_name = data.get('item_name')
                main_record.steam_hash_name = data.get('market_hash_name')
                main_record.sticker = data.get('sticker')
                main_record.pendant = data.get('pendant')
                main_record.rename = data.get('rename')
                main_record.weapon_float = None
                main_record.float_range = data.get('exterior_wear')
                main_record.price = data.get('price')
                main_record.seller_name = None
                main_record.status = '已完成'
                main_record.status_sub = None
                main_record.order_time = trade_date_datetime
                main_record.steam_id = steam_id
                main_record.data_user = steam_id
            else:
                SellModel.ensure_table_exists()
                main_record = SellModel()
                main_record.ID = data.get('ID')
                setattr(main_record, 'from', 'SMK')
                main_record.weapon_name = data.get('weapon_name')
                main_record.weapon_type = data.get('weapon_type')
                main_record.item_name = data.get('item_name')
                main_record.steam_hash_name = data.get('market_hash_name')
                main_record.sticker = data.get('sticker')
                main_record.pendant = data.get('pendant')
                main_record.rename = data.get('rename')
                main_record.weapon_float = None
                main_record.float_range = data.get('exterior_wear')
                main_record.price = data.get('price')
                main_record.price_original = data.get('price_original')
                main_record.buyer_name = None
                main_record.order_time = trade_date_datetime
                main_record.status = '已完成'
                main_record.status_sub = None
                main_record.steam_id = steam_id
                main_record.data_user = steam_id

            main_saved = main_record.save()
            saved = steam_saved and main_saved

            if saved:
                return jsonify({'success': True, 'message': f'{operation_type}数据插入成功（已同步到主表）', 'data': {'id': data.get('ID'), 'trade_type': trade_type, 'weapon_name': data.get('weapon_name'), 'item_name': data.get('item_name'), 'price': data.get('price')}}), 200
            else:
                return jsonify({'success': False, 'error': f'数据插入失败: steam_market={steam_saved}, 主表={main_saved}'}), 500

        except Exception as e:
            print(f"插入数据异常: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500
