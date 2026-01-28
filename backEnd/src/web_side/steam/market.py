from flask import jsonify, request, Blueprint
from src.db_manager.steam.steam_market import SteamMarketModel
from src.db_manager.index.buy import BuyModel
from src.db_manager.index.sell import SellModel
from datetime import datetime
import re

steamMarketV1 = Blueprint('steamMarketV1', __name__)

@steamMarketV1.route('/countData/<data_user>', methods=['get'])
def countData(data_user):
    try:
        # 使用steam_market表查询购买记录数量
        buy_records = SteamMarketModel.find_all("data_user = ? AND trade_type = 'buy'", (data_user,))
        buy_count = len(buy_records)
        
        # 使用steam_market表查询销售记录数量
        sell_records = SteamMarketModel.find_all("data_user = ? AND trade_type = 'sell'", (data_user,))
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
        # 使用steam_market表查询购买记录总数
        buy_records = SteamMarketModel.find_all("data_user = ? AND trade_type = 'buy'", (data_user,))
        buy_count = len(buy_records)

        # 使用steam_market表查询销售记录总数
        sell_records = SteamMarketModel.find_all("data_user = ? AND trade_type = 'sell'", (data_user,))
        sell_count = len(sell_records)

        # 计算总数
        total_count = buy_count + sell_count

        # 查询最新的交易记录（不区分买卖）
        latest_records = SteamMarketModel.find_all(
            "data_user = ? ORDER BY trade_date DESC LIMIT 1",
            (data_user,)
        )

        if latest_records and len(latest_records) > 0:
            latest_record = latest_records[0]
            return jsonify({
                "ID": latest_record.ID,
                "trade_date": latest_record.trade_date,
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
        # 查询最早的交易记录（不区分买卖）
        earliest_records = SteamMarketModel.find_all(
            "data_user = ? ORDER BY trade_date ASC LIMIT 1",
            (data_user,)
        )
        
        if earliest_records and len(earliest_records) > 0:
            earliest_record = earliest_records[0]
            return jsonify({
                "ID": earliest_record.ID,
                "trade_date": earliest_record.trade_date
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
        trade_date_datetime = parse_trade_date_to_datetime(trade_date_str)
        listing_date_str = data.get('listing_date')
        listing_date_datetime = parse_trade_date_to_datetime(listing_date_str) if listing_date_str else None
        
        # 将 trade_type 转换为 'buy' 或 'sell'
        if trade_type_raw == '+':
            trade_type = 'buy'
            operation_type = '购买'
        elif trade_type_raw == '-':
            trade_type = 'sell'
            operation_type = '销售'
        else:
            return jsonify({'success': False, 'error': '无效的交易类型'}), 400
        
        # 确保steam_market表存在
        SteamMarketModel.ensure_table_exists()
        
        # 插入到steam_market表
        market_record = SteamMarketModel()
        market_record.ID = data.get('ID')
        market_record.trade_type = trade_type  # 'buy' 或 'sell'
        market_record.asset_id = data.get('asset_id')
        market_record.price = data.get('price')
        market_record.price_original = data.get('price_original') if trade_type == 'sell' else None
        market_record.trade_date = trade_date_datetime  # 使用datetime对象
        market_record.listing_date = listing_date_datetime  # 使用datetime对象
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
        
        # 同步到主表
        if trade_type == 'buy':
            BuyModel.ensure_table_exists()
            
            main_buy_record = BuyModel()
            main_buy_record.ID = data.get('ID')
            setattr(main_buy_record, 'from', 'SMK')
            main_buy_record.weapon_name = data.get('weapon_name')
            main_buy_record.weapon_type = data.get('weapon_type')
            main_buy_record.item_name = data.get('item_name')
            main_buy_record.steam_hash_name = data.get('market_hash_name')
            main_buy_record.sticker = data.get('sticker')
            main_buy_record.pendant = data.get('pendant')
            main_buy_record.rename = data.get('rename')
            main_buy_record.weapon_float = None
            main_buy_record.float_range = data.get('exterior_wear')
            main_buy_record.price = data.get('price')
            main_buy_record.seller_name = None
            main_buy_record.status = '已完成'
            main_buy_record.status_sub = None
            main_buy_record.order_time = trade_date_datetime  # 使用datetime对象
            main_buy_record.steam_id = steam_id
            main_buy_record.data_user = steam_id
            
            main_saved = main_buy_record.save()
        else:
            SellModel.ensure_table_exists()
            
            main_sell_record = SellModel()
            main_sell_record.ID = data.get('ID')
            setattr(main_sell_record, 'from', 'SMK')
            main_sell_record.weapon_name = data.get('weapon_name')
            main_sell_record.weapon_type = data.get('weapon_type')
            main_sell_record.item_name = data.get('item_name')
            main_sell_record.steam_hash_name = data.get('market_hash_name')
            main_sell_record.sticker = data.get('sticker')
            main_sell_record.pendant = data.get('pendant')
            main_sell_record.rename = data.get('rename')
            main_sell_record.weapon_float = None
            main_sell_record.float_range = data.get('exterior_wear')
            main_sell_record.price = data.get('price')
            main_sell_record.price_original = data.get('price_original')
            main_sell_record.buyer_name = None
            main_sell_record.order_time = trade_date_datetime  # 使用datetime对象
            main_sell_record.status = '已完成'
            main_sell_record.status_sub = None
            main_sell_record.steam_id = steam_id
            main_sell_record.data_user = steam_id
            
            main_saved = main_sell_record.save()
        
        saved = steam_saved and main_saved
        
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
            print(f"[错误] {error_msg}")
            return jsonify({'success': False, 'error': error_msg}), 500
            
    except Exception as e:
        print(f"[错误] 插入数据异常: {str(e)}")
        import traceback
        print(f"[错误] 详细信息: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500

