"""
StockComponents 页面库存统计模块
提供组件统计信息（总数、各平台价格汇总）
"""
from flask import jsonify, request
from src.db_manager.database import DatabaseManager


class StockComponentsStats:

    @staticmethod
    def get_components_stats(steam_id):
        """获取库存组件统计信息（支持筛选参数）"""
        try:
            search_text = request.args.get('search', '')
            weapon_type = request.args.get('weapon_type', '')
            float_range = request.args.get('float_range', '')
            assetid = request.args.get('assetid', '')
            pendant_filter = request.args.get('pendant_filter', '')
            sticker_filter = request.args.get('sticker_filter', '')
            rename_filter = request.args.get('rename_filter', '')

            db = DatabaseManager()

            # 构建查询条件
            where_conditions = ["data_user = ?"]
            params = [steam_id]

            if assetid:
                where_conditions.append("assetid = ?")
                params.append(assetid)

            if search_text:
                where_conditions.append("(weapon_name LIKE ? OR item_name LIKE ?)")
                params.append(f"%{search_text}%")
                params.append(f"%{search_text}%")

            if weapon_type:
                where_conditions.append("weapon_type = ?")
                params.append(weapon_type)

            if float_range:
                where_conditions.append("float_range = ?")
                params.append(float_range)

            if pendant_filter == 'has':
                where_conditions.append("(pendant IS NOT NULL AND pendant != '' AND pendant != 'None' AND pendant != '[]')")
            elif pendant_filter == 'none':
                where_conditions.append("(pendant IS NULL OR pendant = '' OR pendant = 'None' OR pendant = '[]')")

            if sticker_filter == 'has':
                where_conditions.append("(sticker IS NOT NULL AND sticker != '' AND sticker != 'None' AND sticker != '[]')")
            elif sticker_filter == 'none':
                where_conditions.append("(sticker IS NULL OR sticker = '' OR sticker = 'None' OR sticker = '[]')")

            if rename_filter == 'has':
                where_conditions.append("(rename IS NOT NULL AND rename != '' AND rename != 'None')")
            elif rename_filter == 'none':
                where_conditions.append("(rename IS NULL OR rename = '' OR rename = 'None')")

            where_clause = " AND ".join(where_conditions)

            # 统计总数和各种价格总和
            stats_sql = f"""
            SELECT
                COUNT(*) as total_count,
                SUM(CAST(buy_price AS REAL)) as total_buy_price,
                SUM(CAST(yyyp_price AS REAL)) as total_yyyp_price,
                SUM(CAST(buff_price AS REAL)) as total_buff_price,
                SUM(CAST(steam_price AS REAL)) as total_steam_price
            FROM steam_stockComponents
            WHERE {where_clause}
            """
            stats_result = db.execute_query(stats_sql, tuple(params))

            total_count = 0
            total_cost = 0
            total_yyyp_price = 0
            total_buff_price = 0
            total_steam_price = 0

            if stats_result and stats_result[0][0] is not None:
                total_count = stats_result[0][0] or 0
                total_cost = round(stats_result[0][1] or 0, 2)
                total_yyyp_price = round(stats_result[0][2] or 0, 2)
                total_buff_price = round(stats_result[0][3] or 0, 2)
                total_steam_price = round(stats_result[0][4] or 0, 2)

            return jsonify({
                'success': True,
                'data': {
                    'totalCount': total_count,
                    'totalCost': total_cost,
                    'totalYYYPPrice': total_yyyp_price,
                    'totalBuffPrice': total_buff_price,
                    'totalSteamPrice': total_steam_price
                }
            }), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': f'查询失败: {str(e)}'
            }), 500
