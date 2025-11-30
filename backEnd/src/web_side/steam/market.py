from flask import jsonify, request, Blueprint
from src.db_manager.steam.steam_buy import SteamBuyModel
from src.db_manager.steam.steam_sell import SteamSellModel
from src.db_manager.steam.steam_market import SteamMarketModel
from src.db_manager.index.buy import BuyModel
from src.db_manager.index.sell import SellModel
from src.execution_db import Date_base
from datetime import datetime
import re

steamMarketV1 = Blueprint('steamMarketV1', __name__)

@steamMarketV1.route('/countData/<data_user>', methods=['get'])
def countData(data_user):
    try:
        # 使用对象化方式查询购买记录数量
        buy_records = SteamBuyModel.find_all("data_user = ?", (data_user,))
        buy_count = len(buy_records)
        
        # 使用对象化方式查询销售记录数量
        sell_records = SteamSellModel.find_all("data_user = ?", (data_user,))
        sell_count = len(sell_records)
        
        # 计算总数量
        total_count = buy_count + sell_count
        
        print(f"Steam用户 {data_user} 的数据统计: 购买{buy_count}条, 销售{sell_count}条, 总计{total_count}条")
        
        return jsonify({
            "success": True,
            "data": {
                "user_id": data_user,
                "buy_count": buy_count,
                "sell_count": sell_count,
                "count": total_count
            }
        }), 200
        
    except Exception as e:
        print(f"查询Steam数据统计失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "error": f"查询失败: {str(e)}",
            "data": {
                "user_id": data_user,
                "buy_count": 0,
                "sell_count": 0,
                "total_count": 0
            }
        }), 500

@steamMarketV1.route('/getLatestData/<data_user>', methods=['GET'])
def getLatestData(data_user):
    """获取指定用户的最新一条交易记录（购买或销售）并返回总数统计"""
    try:
        # 查询购买记录总数
        buy_count_sql = f"""
        SELECT COUNT(*) FROM steam_buy WHERE data_user = '{data_user}'
        """
        buy_count_result = Date_base().select(buy_count_sql)
        buy_count = buy_count_result[1][0][0] if buy_count_result and buy_count_result[0] else 0

        # 查询销售记录总数
        sell_count_sql = f"""
        SELECT COUNT(*) FROM steam_sell WHERE data_user = '{data_user}'
        """
        sell_count_result = Date_base().select(sell_count_sql)
        sell_count = sell_count_result[1][0][0] if sell_count_result and sell_count_result[0] else 0

        # 计算总数
        total_count = buy_count + sell_count

        # 查询最新购买记录
        buy_sql = f"""
        SELECT ID, trade_date, 'buy' as type
        FROM steam_buy
        WHERE data_user = '{data_user}'
        ORDER BY trade_date DESC
        LIMIT 1
        """
        buy_result = Date_base().select(buy_sql)

        # 查询最新销售记录
        sell_sql = f"""
        SELECT ID, trade_date, 'sell' as type
        FROM steam_sell
        WHERE data_user = '{data_user}'
        ORDER BY trade_date DESC
        LIMIT 1
        """
        sell_result = Date_base().select(sell_sql)

        latest_buy = None
        latest_sell = None

        if buy_result and len(buy_result) == 2 and buy_result[0] and len(buy_result[1]) > 0:
            latest_buy = buy_result[1][0]

        if sell_result and len(sell_result) == 2 and sell_result[0] and len(sell_result[1]) > 0:
            latest_sell = sell_result[1][0]

        # 比较两者的交易时间，返回最新的那条
        if latest_buy and latest_sell:
            if latest_buy[1] > latest_sell[1]:
                return jsonify({
                    "ID": latest_buy[0],
                    "trade_date": latest_buy[1],
                    "buy_count": buy_count,
                    "sell_count": sell_count,
                    "total_count": total_count
                }), 200
            else:
                return jsonify({
                    "ID": latest_sell[0],
                    "trade_date": latest_sell[1],
                    "buy_count": buy_count,
                    "sell_count": sell_count,
                    "total_count": total_count
                }), 200
        elif latest_buy:
            return jsonify({
                "ID": latest_buy[0],
                "trade_date": latest_buy[1],
                "buy_count": buy_count,
                "sell_count": sell_count,
                "total_count": total_count
            }), 200
        elif latest_sell:
            return jsonify({
                "ID": latest_sell[0],
                "trade_date": latest_sell[1],
                "buy_count": buy_count,
                "sell_count": sell_count,
                "total_count": total_count
            }), 200
        else:
            return jsonify({
                "ID": None,
                "trade_date": None,
                "buy_count": buy_count,
                "sell_count": sell_count,
                "total_count": total_count
            }), 200

    except Exception as e:
        print(f"获取最新交易数据失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            "ID": None,
            "trade_date": None,
            "buy_count": 0,
            "sell_count": 0,
            "total_count": 0
        }), 500


@steamMarketV1.route('/getEarliestData/<data_user>', methods=['GET'])
def getEarliestData(data_user):
    """获取指定用户的最早一条交易记录（购买或销售）"""
    try:
        # 查询最早购买记录
        buy_sql = f"""
        SELECT ID, trade_date, 'buy' as type
        FROM steam_buy
        WHERE data_user = '{data_user}'
        ORDER BY trade_date ASC
        LIMIT 1
        """
        buy_result = Date_base().select(buy_sql)

        # 查询最早销售记录
        sell_sql = f"""
        SELECT ID, trade_date, 'sell' as type
        FROM steam_sell
        WHERE data_user = '{data_user}'
        ORDER BY trade_date ASC
        LIMIT 1
        """
        sell_result = Date_base().select(sell_sql)
        
        earliest_buy = None
        earliest_sell = None
        
        if buy_result and len(buy_result) == 2 and buy_result[0] and len(buy_result[1]) > 0:
            earliest_buy = buy_result[1][0]
        
        if sell_result and len(sell_result) == 2 and sell_result[0] and len(sell_result[1]) > 0:
            earliest_sell = sell_result[1][0]
        
        # 比较两者的交易时间，返回最早的那条
        if earliest_buy and earliest_sell:
            if earliest_buy[1] < earliest_sell[1]:
                return jsonify({
                    "ID": earliest_buy[0],
                    "trade_date": earliest_buy[1]
                }), 200
            else:
                return jsonify({
                    "ID": earliest_sell[0],
                    "trade_date": earliest_sell[1]
                }), 200
        elif earliest_buy:
            return jsonify({
                "ID": earliest_buy[0],
                "trade_date": earliest_buy[1]
            }), 200
        elif earliest_sell:
            return jsonify({
                "ID": earliest_sell[0],
                "trade_date": earliest_sell[1]
            }), 200
        else:
            return jsonify({"ID": None, "trade_date": None}), 200
            
    except Exception as e:
        print(f"获取最早交易数据失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({"ID": None, "trade_date": None}), 500

def parse_trade_date_to_datetime(trade_date_str):
    """将Steam交易日期字符串转换为datetime对象"""
    if not trade_date_str or trade_date_str == "未知交易日期":
        return None
    
    try:
        # 尝试解析格式: "2024年1月15日"
        match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', trade_date_str)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            return datetime(year, month, day)
        
        # 尝试解析格式: "YYYY-MM-DD"
        try:
            return datetime.strptime(trade_date_str, '%Y-%m-%d')
        except:
            pass
        
        # 尝试解析格式: "YYYY/MM/DD"
        try:
            return datetime.strptime(trade_date_str, '%Y/%m/%d')
        except:
            pass
        
        return None
    except Exception as e:
        print(f"解析交易日期失败: {e}, 原始字符串: {trade_date_str}")
        return None

@steamMarketV1.route('/insertNewData', methods=['POST'])
def insertNewData():
    """插入新的Steam市场交易数据到steam_market表，同时同步到主表"""
    try:
        data = request.get_json()
        if not data:
            print("错误：无效的JSON数据")
            return jsonify({'success': False, 'error': '无效的JSON数据'}), 400
        
        # 获取当前用户（这里需要根据实际认证机制获取）
        trade_type_raw = data.get('trade_type')  # '+' 或 '-'
        steam_id = data.get('steamId')
        trade_date_str = data.get('trade_date')
        
        # 解析交易日期
        order_time = parse_trade_date_to_datetime(trade_date_str)
        
        # 将 trade_type 转换为 'buy' 或 'sell'
        if trade_type_raw == '+':
            trade_type = 'buy'
            operation_type = '购买'
        elif trade_type_raw == '-':
            trade_type = 'sell'
            operation_type = '销售'
        else:
            return jsonify({'success': False, 'error': '无效的交易类型'}), 400
        
        # 插入到steam_market表
        market_record = SteamMarketModel()
        market_record.ID = data.get('ID')
        market_record.trade_type = trade_type  # 'buy' 或 'sell'
        market_record.asset_id = data.get('asset_id')
        market_record.price = data.get('price')
        market_record.price_original = data.get('price_original') if trade_type == 'sell' else None
        market_record.trade_date = trade_date_str
        market_record.listing_date = data.get('listing_date')
        market_record.game_name = data.get('game_name')
        market_record.weapon_type = data.get('weapon_type')
        market_record.weapon_name = data.get('weapon_name')
        market_record.item_name = data.get('item_name')
        market_record.steam_hash_name = None  # 如果需要可以从data中获取
        market_record.float_range = data.get('exterior_wear')
        market_record.weapon_float = None  # Steam数据中没有weapon_float
        market_record.inspect_link = data.get('inspect_link')
        market_record.data_user = steam_id
        market_record.sticker = None  # 如果需要可以从data中获取
        market_record.pendant = None  # 如果需要可以从data中获取
        market_record.rename = None  # 如果需要可以从data中获取
        steam_saved = market_record.save()
        
        # 同步到主表
        if trade_type == 'buy':
            # 同步到buy主表
            main_buy_record = BuyModel()
            main_buy_record.ID = data.get('ID')
            main_buy_record.weapon_name = data.get('weapon_name')
            main_buy_record.weapon_type = data.get('weapon_type')
            main_buy_record.item_name = data.get('item_name')
            main_buy_record.weapon_float = None  # Steam数据中没有weapon_float
            main_buy_record.float_range = data.get('exterior_wear')
            main_buy_record.price = data.get('price')
            main_buy_record.seller_name = None  # Steam市场没有卖家信息
            main_buy_record.status = '已完成'  # Steam市场交易通常是即时完成的
            main_buy_record.status_sub = None
            setattr(main_buy_record, 'from', 'SMK')
            main_buy_record.order_time = order_time
            main_buy_record.steam_id = steam_id
            main_buy_record.data_user = steam_id
            main_saved = main_buy_record.save()
        else:
            # 同步到sell主表
            main_sell_record = SellModel()
            main_sell_record.ID = data.get('ID')
            main_sell_record.weapon_name = data.get('weapon_name')
            main_sell_record.weapon_type = data.get('weapon_type')
            main_sell_record.item_name = data.get('item_name')
            main_sell_record.weapon_float = None  # Steam数据中没有weapon_float
            main_sell_record.float_range = data.get('exterior_wear')
            main_sell_record.price = data.get('price')
            main_sell_record.price_original = data.get('price_original')
            main_sell_record.buyer_name = None  # Steam市场没有买家信息
            main_sell_record.order_time = order_time
            main_sell_record.status = '已完成'  # Steam市场交易通常是即时完成的
            main_sell_record.status_sub = None
            setattr(main_sell_record, 'from', 'SMK')
            main_sell_record.steam_id = steam_id
            main_sell_record.data_user = steam_id
            main_saved = main_sell_record.save()
        
        saved = steam_saved and main_saved
        
        # 检查是否保存成功
        if saved:
            return jsonify({
                'success': True,
                'message': f'{operation_type}数据插入成功（已同步到主表）',
                'data': {
                    'id': data.get('ID'),
                    'trade_type': trade_type,
                    'operation_type': operation_type,
                    'weapon_name': data.get('weapon_name'),
                    'item_name': data.get('item_name'),
                    'price': data.get('price')
                }
            }), 200
        else:
            error_msg = f'数据插入失败: steam_market表保存={steam_saved}, 主表保存={main_saved}'
            print(error_msg)
            return jsonify({'success': False, 'error': error_msg}), 500
            
    except Exception as e:
        print(f"服务器错误: {str(e)}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500

