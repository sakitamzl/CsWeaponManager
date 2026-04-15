"""
Sell 页面价格查询模块
根据 steam_hash_name 查询 weapon_classID 表中的悠悠有品和BUFF价格信息
使用 DatabaseManager + 参数化 SQL
"""
from flask import jsonify
from src.db_manager.database import DatabaseManager


class SellPriceInfo:

    @staticmethod
    def get_yyyp_price_info(steam_hash_name):
        """根据 steam_hash_name 查询价格信息（包括悠悠有品和BUFF）"""
        try:
            sql = """
            SELECT [yyyp_Price], [yyyp_OnSaleCount], [buff_Price], [buff_OnSaleCount], [market_listing_item_name]
            FROM weapon_classID
            WHERE [steam_hash_name] = ?
            LIMIT 1
            """
            db = DatabaseManager()
            rows = db.execute_query(sql, (steam_hash_name,))

            if rows and len(rows) > 0:
                row = rows[0]
                yyyp_price, yyyp_on_sale_count, buff_price, buff_on_sale_count, market_listing_item_name = row
                return jsonify({
                    'success': True,
                    'data': {
                        'yyyp_price': yyyp_price if yyyp_price else None,
                        'yyyp_on_sale_count': yyyp_on_sale_count if yyyp_on_sale_count else None,
                        'buff_price': buff_price if buff_price else None,
                        'buff_on_sale_count': buff_on_sale_count if buff_on_sale_count else None,
                        'market_listing_item_name': market_listing_item_name if market_listing_item_name else None
                    }
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': '未找到该武器的价格信息',
                    'data': {
                        'yyyp_price': None,
                        'yyyp_on_sale_count': None,
                        'buff_price': None,
                        'buff_on_sale_count': None,
                        'market_listing_item_name': None
                    }
                }), 404

        except Exception as e:
            print(f"查询价格信息失败: {str(e)}")
            import traceback
            print(f"详细错误信息: {traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': f'服务器错误: {str(e)}',
                'data': {
                    'yyyp_price': None,
                    'yyyp_on_sale_count': None,
                    'buff_price': None,
                    'buff_on_sale_count': None
                }
            }), 500
