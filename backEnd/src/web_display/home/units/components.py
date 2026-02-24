"""
Home 页面指定账号组件模块
从 webStockComponentsV1/components 分离的 Home 简化版
仅支持 search/page/page_size 参数
"""
from flask import jsonify, request
from src.db_manager.database import DatabaseManager
import logging

logger = logging.getLogger(__name__)


def safe_float(value, default=0.0):
    """安全的浮点数转换"""
    if value is None or value == '' or value == '--':
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


class HomeComponents:

    @staticmethod
    def get_components(steam_id):
        """获取指定Steam账号的库存组件数据（Home页面简化版）"""
        try:
            search_text = request.args.get('search', '')
            page = request.args.get('page', 1, type=int)
            page_size = request.args.get('page_size', 999999, type=int)

            offset = (page - 1) * page_size

            db = DatabaseManager()

            where_conditions = ["data_user = ?"]
            params = [steam_id]

            if search_text:
                where_conditions.append("(weapon_name LIKE ? OR item_name LIKE ?)")
                params.append(f"%{search_text}%")
                params.append(f"%{search_text}%")

            where_clause = " AND ".join(where_conditions)

            sql = f"""
            SELECT
                assetid, goods_assetid, classid, item_name, weapon_name,
                float_range, weapon_type, weapon_float, weapon_level, data_user,
                buy_price, yyyp_price, buff_price, order_time, steam_price,
                steam_hash_name, sticker, pendant, rename
            FROM steam_stockComponents
            WHERE {where_clause}
            ORDER BY order_time DESC
            LIMIT ? OFFSET ?
            """
            params.extend([page_size, offset])
            results = db.execute_query(sql, tuple(params))

            components_list = []
            if results:
                for row in results:
                    component = {
                        'assetid': row[0],
                        'goods_assetid': row[1],
                        'component_id': row[1],
                        'classid': row[2],
                        'item_name': row[3],
                        'weapon_name': row[4],
                        'float_range': row[5],
                        'weapon_type': row[6],
                        'weapon_float': row[7],
                        'weapon_level': row[8],
                        'data_user': row[9],
                        'buy_price': safe_float(row[10]),
                        'yyyp_price': safe_float(row[11]),
                        'buff_price': safe_float(row[12]),
                        'order_time': row[13],
                        'steam_price': safe_float(row[14]),
                        'steam_hash_name': row[15],
                        'sticker': row[16],
                        'pendant': row[17],
                        'rename': row[18]
                    }
                    components_list.append(component)

            return jsonify({
                'success': True,
                'data': components_list,
                'total': len(components_list)
            }), 200

        except Exception as e:
            logger.error(f"获取指定账号组件数据失败: {e}")
            return jsonify({
                'success': False,
                'message': str(e),
                'data': []
            }), 500
