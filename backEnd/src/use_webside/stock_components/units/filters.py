"""
StockComponents 页面筛选选项模块
提供武器类型、磨损等级等筛选下拉数据
"""
from flask import jsonify
from src.db_manager.database import DatabaseManager


class StockComponentsFilters:

    @staticmethod
    def get_weapon_types(steam_id):
        """获取指定用户的所有武器类型（按优先级排序）"""
        try:
            db = DatabaseManager()

            sql = """
            SELECT DISTINCT weapon_type
            FROM steam_stockComponents
            WHERE data_user = ?
              AND weapon_type IS NOT NULL
              AND weapon_type != ''
            ORDER BY
                CASE weapon_type
                    WHEN '匕首' THEN 1
                    WHEN '手套' THEN 2
                    WHEN '手枪' THEN 3
                    WHEN '步枪' THEN 4
                    WHEN '狙击步枪' THEN 5
                    WHEN '微型冲锋枪' THEN 6
                    WHEN '霰弹枪' THEN 7
                    WHEN '机枪' THEN 8
                    WHEN '印花' THEN 9
                    ELSE 999
                END,
                weapon_type
            """
            results = db.execute_query(sql, (steam_id,))

            weapon_types = []
            if results:
                for row in results:
                    if row[0]:
                        weapon_types.append(row[0])

            return jsonify({
                'success': True,
                'data': weapon_types
            }), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': f'查询失败: {str(e)}'
            }), 500

    @staticmethod
    def get_float_ranges(steam_id):
        """获取指定用户的所有磨损等级（按标准顺序排序）"""
        try:
            db = DatabaseManager()

            sql = """
            SELECT DISTINCT float_range
            FROM steam_stockComponents
            WHERE data_user = ?
              AND float_range IS NOT NULL
              AND float_range != ''
            ORDER BY
                CASE float_range
                    WHEN '崭新出厂' THEN 1
                    WHEN '略有磨损' THEN 2
                    WHEN '久经沙场' THEN 3
                    WHEN '破损不堪' THEN 4
                    WHEN '战痕累累' THEN 5
                    ELSE 999
                END,
                float_range
            """
            results = db.execute_query(sql, (steam_id,))

            float_ranges = []
            if results:
                for row in results:
                    if row[0]:
                        float_ranges.append(row[0])

            return jsonify({
                'success': True,
                'data': float_ranges
            }), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': f'查询失败: {str(e)}'
            }), 500
