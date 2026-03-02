"""
Inventory 页面库存统计模块
提供按类型、磨损等级分组统计及多种价格汇总
"""
from flask import jsonify, request
from src.db_manager.database import DatabaseManager


class InventoryStats:

    @staticmethod
    def get_inventory_stats(steam_id):
        """获取库存统计信息（支持筛选参数）"""
        try:
            db = DatabaseManager()

            # 获取查询参数
            search_text = request.args.get('search', '')
            weapon_type = request.args.get('weapon_type', '')
            float_range = request.args.get('float_range', '')
            classid = request.args.get('classid', '')
            pendant_filter = request.args.get('pendant_filter', '')
            sticker_filter = request.args.get('sticker_filter', '')
            rename_filter = request.args.get('rename_filter', '')
            trade_restriction_filter = request.args.get('trade_restriction_filter', '')

            # 构建查询条件
            where_conditions = ["data_user = ?", "if_inventory = '1'"]
            params = [steam_id]

            if search_text:
                where_conditions.append("(item_name LIKE ? OR weapon_name LIKE ?)")
                search_pattern = f"%{search_text}%"
                params.extend([search_pattern, search_pattern])

            if weapon_type:
                where_conditions.append("weapon_type = ?")
                params.append(weapon_type)

            if float_range:
                where_conditions.append("float_range = ?")
                params.append(float_range)

            if classid:
                where_conditions.append("classid = ?")
                params.append(classid)

            if pendant_filter == 'has':
                where_conditions.append("(pendant IS NOT NULL AND pendant != '')")
            elif pendant_filter == 'none':
                where_conditions.append("(pendant IS NULL OR pendant = '')")

            if sticker_filter == 'has':
                where_conditions.append("(sticker IS NOT NULL AND sticker != '')")
            elif sticker_filter == 'none':
                where_conditions.append("(sticker IS NULL OR sticker = '')")

            if rename_filter == 'has':
                where_conditions.append("(rename IS NOT NULL AND rename != '')")
            elif rename_filter == 'none':
                where_conditions.append("(rename IS NULL OR rename = '')")

            if trade_restriction_filter == 'has':
                where_conditions.append("(remark IS NOT NULL AND remark != '')")
            elif trade_restriction_filter == 'none':
                where_conditions.append("(remark IS NULL OR remark = '')")

            where_clause = " AND ".join(where_conditions)
            params_tuple = tuple(params)

            # 统计总数
            total_sql = f"SELECT COUNT(*) FROM steam_inventory WHERE {where_clause}"
            total_result = db.execute_query(total_sql, params_tuple)
            total_count = total_result[0][0] if total_result else 0

            # 按武器类型统计
            type_sql = f"""
            SELECT weapon_type, COUNT(*) as count
            FROM steam_inventory
            WHERE {where_clause} AND weapon_type IS NOT NULL AND weapon_type != ''
            GROUP BY weapon_type
            ORDER BY count DESC
            """
            type_results = db.execute_query(type_sql, params_tuple)

            type_stats = []
            for row in type_results:
                type_stats.append({
                    'weapon_type': row[0],
                    'count': row[1]
                })

            # 按磨损等级统计
            wear_sql = f"""
            SELECT float_range, COUNT(*) as count
            FROM steam_inventory
            WHERE {where_clause} AND float_range IS NOT NULL AND float_range != ''
            GROUP BY float_range
            ORDER BY count DESC
            """
            wear_results = db.execute_query(wear_sql, params_tuple)

            wear_stats = []
            for row in wear_results:
                wear_stats.append({
                    'float_range': row[0],
                    'count': row[1]
                })

            # 统计购入价格
            price_sql = f"""
            SELECT
                COUNT(CASE WHEN CAST(buy_price AS REAL) > 0 THEN 1 END) as priced_count,
                SUM(CAST(buy_price AS REAL)) as total_price,
                AVG(CAST(buy_price AS REAL)) as avg_price,
                MIN(CAST(buy_price AS REAL)) as min_price,
                MAX(CAST(buy_price AS REAL)) as max_price
            FROM steam_inventory
            WHERE {where_clause}
            """
            price_result = db.execute_query(price_sql, params_tuple)

            price_stats = {
                'priced_count': 0, 'total_price': 0, 'avg_price': 0,
                'min_price': 0, 'max_price': 0
            }
            if price_result and len(price_result) > 0:
                priced_count, total_price, avg_price, min_price, max_price = price_result[0]
                price_stats = {
                    'priced_count': priced_count if priced_count else 0,
                    'total_price': round(total_price, 2) if total_price else 0,
                    'avg_price': round(avg_price, 2) if avg_price else 0,
                    'min_price': round(min_price, 2) if min_price else 0,
                    'max_price': round(max_price, 2) if max_price else 0
                }

            # 统计悠悠有品价格
            yyyp_price_stats = _get_platform_price_stats(db, 'yyyp_price', where_clause, params_tuple)

            # 统计BUFF价格
            buff_price_stats = _get_platform_price_stats(db, 'buff_price', where_clause, params_tuple)

            # 统计Steam参考价
            steam_price_stats = _get_platform_price_stats(db, 'steam_price', where_clause, params_tuple)

            return jsonify({
                'success': True,
                'data': {
                    'total_count': total_count,
                    'by_type': type_stats,
                    'by_wear': wear_stats,
                    'price_stats': price_stats,
                    'yyyp_price_stats': yyyp_price_stats,
                    'buff_price_stats': buff_price_stats,
                    'steam_price_stats': steam_price_stats
                }
            }), 200

        except Exception as e:
            print(f"查询统计信息失败: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': f'查询失败: {str(e)}'
            }), 500


def _get_platform_price_stats(db, price_column, where_clause, params_tuple):
    """获取指定平台的价格统计"""
    sql = f"""
    SELECT
        COUNT(CASE WHEN CAST({price_column} AS REAL) > 0 THEN 1 END) as priced_count,
        SUM(CAST({price_column} AS REAL)) as total_price,
        AVG(CAST({price_column} AS REAL)) as avg_price
    FROM steam_inventory
    WHERE {where_clause}
    """
    result = db.execute_query(sql, params_tuple)

    stats = {'priced_count': 0, 'total_price': 0, 'avg_price': 0}
    if result and len(result) > 0:
        priced_count, total_price, avg_price = result[0]
        stats = {
            'priced_count': priced_count if priced_count else 0,
            'total_price': round(total_price, 2) if total_price else 0,
            'avg_price': round(avg_price, 2) if avg_price else 0
        }
    return stats
