"""
Sell 页面价格查询模块
根据 steam_hash_name 查询 weapon_classID 表中的悠悠有品和BUFF价格信息
"""
from flask import jsonify


def get_yyyp_price_info(steam_hash_name):
    """根据 steam_hash_name 查询价格信息（包括悠悠有品和BUFF）"""
    try:
        from src.db_manager.index.model.weapon_classID import WeaponClassIDModel

        results = WeaponClassIDModel.find_by_steam_hash_name(steam_hash_name)

        if results and len(results) > 0:
            weapon_info = results[0]
            return jsonify({
                'success': True,
                'data': {
                    'yyyp_price': weapon_info.yyyp_Price if weapon_info.yyyp_Price else None,
                    'yyyp_on_sale_count': weapon_info.yyyp_OnSaleCount if weapon_info.yyyp_OnSaleCount else None,
                    'buff_price': weapon_info.buff_Price if weapon_info.buff_Price else None,
                    'buff_on_sale_count': weapon_info.buff_OnSaleCount if weapon_info.buff_OnSaleCount else None,
                    'market_listing_item_name': weapon_info.market_listing_item_name if weapon_info.market_listing_item_name else None
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
