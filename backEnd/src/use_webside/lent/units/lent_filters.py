"""
Lent 页面筛选选项模块
提供武器类型、磨损等级、状态、子状态、平台、用户等下拉选项数据
"""
from flask import jsonify, request
from src.db_manager.database import DatabaseManager


class LentFilters:

    @staticmethod
    def get_weapon_types():
        """获取租赁武器类型唯一值（UNION lent + yyyp_lent）"""
        try:
            db = DatabaseManager()
            sql = """
            SELECT DISTINCT weapon_type
            FROM (
                SELECT weapon_type FROM lent WHERE weapon_type IS NOT NULL AND weapon_type != ''
                UNION
                SELECT weapon_type FROM yyyp_lent WHERE weapon_type IS NOT NULL AND weapon_type != ''
            ) t
            ORDER BY weapon_type
            """
            result = db.execute_query(sql)

            weapon_types = []
            if result:
                for row in result:
                    if row[0]:
                        weapon_types.append(row[0])

            return jsonify({
                'success': True,
                'data': weapon_types
            }), 200

        except Exception as e:
            print(f"获取武器类型失败: {e}")
            return jsonify({
                'success': False,
                'message': str(e),
                'data': []
            }), 500

    @staticmethod
    def get_float_ranges():
        """获取磨损等级唯一值（UNION lent + yyyp_lent）"""
        try:
            db = DatabaseManager()
            sql = """
            SELECT DISTINCT float_range
            FROM (
                SELECT float_range FROM lent WHERE float_range IS NOT NULL AND float_range != ''
                UNION
                SELECT float_range FROM yyyp_lent WHERE float_range IS NOT NULL AND float_range != ''
            ) t
            ORDER BY float_range
            """
            result = db.execute_query(sql)

            float_ranges = []
            if result:
                for row in result:
                    if row[0]:
                        float_ranges.append(row[0])

            return jsonify({
                'success': True,
                'data': float_ranges
            }), 200

        except Exception as e:
            print(f"获取磨损等级失败: {e}")
            return jsonify({
                'success': False,
                'message': str(e),
                'data': []
            }), 500

    @staticmethod
    def get_status_list():
        """获取租赁状态唯一值（UNION lent + yyyp_lent）"""
        try:
            db = DatabaseManager()
            sql = """
            SELECT DISTINCT status FROM lent WHERE status IS NOT NULL AND status != ''
            UNION
            SELECT DISTINCT status FROM yyyp_lent WHERE status IS NOT NULL AND status != ''
            """
            result = db.execute_query(sql)

            status_list = []
            if result:
                for row in result:
                    if row[0]:
                        status_list.append(row[0])

            # 排序：核心状态优先，其余按字典序
            def sort_key(val):
                order_map = {'租赁中': 1, '已完成': 2, '已取消': 3}
                return (order_map.get(val, 999), val)
            status_list = sorted(set(status_list), key=sort_key)

            return jsonify({
                'success': True,
                'data': status_list
            }), 200

        except Exception as e:
            print(f"获取状态列表失败: {e}")
            return jsonify({
                'success': False,
                'message': str(e),
                'data': []
            }), 500

    @staticmethod
    def get_status_sub_list():
        """获取租赁子状态（query param: ?status=）"""
        try:
            status = request.args.get('status', '').strip()
            db = DatabaseManager()
            params = []

            if not status or status.lower() == 'all':
                sql = """
                SELECT DISTINCT COALESCE(last_status, status) AS status_sub
                FROM lent
                WHERE COALESCE(last_status, status) IS NOT NULL AND COALESCE(last_status, status) != ''
                UNION
                SELECT DISTINCT COALESCE(status_sub, last_status, status) AS status_sub
                FROM yyyp_lent
                WHERE COALESCE(status_sub, last_status, status) IS NOT NULL
                  AND COALESCE(status_sub, last_status, status) != ''
                """
            else:
                sql = """
                SELECT DISTINCT COALESCE(last_status, status) AS status_sub
                FROM lent
                WHERE status = ?
                  AND COALESCE(last_status, status) IS NOT NULL AND COALESCE(last_status, status) != ''
                UNION
                SELECT DISTINCT COALESCE(status_sub, last_status, status) AS status_sub
                FROM yyyp_lent
                WHERE status = ?
                  AND COALESCE(status_sub, last_status, status) IS NOT NULL
                  AND COALESCE(status_sub, last_status, status) != ''
                """
                params.extend([status, status])

            if params:
                result = db.execute_query(sql, tuple(params))
            else:
                result = db.execute_query(sql)

            sub_list = []
            if result:
                for row in result:
                    if row[0]:
                        sub_list.append(row[0])
            sub_list = sorted(set(sub_list))

            return jsonify({'success': True, 'data': sub_list}), 200
        except Exception as e:
            print(f"获取租赁子状态失败: {e}")
            return jsonify({'success': False, 'message': str(e), 'data': []}), 500

    @staticmethod
    def get_platform_list():
        """获取平台来源唯一值（UNION lent + yyyp_lent）"""
        try:
            db = DatabaseManager()
            sql = """
            SELECT DISTINCT "from" AS platform
            FROM lent
            WHERE "from" IS NOT NULL AND "from" != ''
            UNION
            SELECT DISTINCT "from" AS platform
            FROM yyyp_lent
            WHERE "from" IS NOT NULL AND "from" != ''
            ORDER BY platform
            """
            result = db.execute_query(sql)
            platforms = [row[0] for row in result or [] if row[0]]
            return jsonify({'success': True, 'data': platforms}), 200
        except Exception as e:
            print(f"获取平台列表失败: {e}")
            return jsonify({'success': False, 'message': str(e), 'data': []}), 500

    @staticmethod
    def get_lenter_list():
        """获取出租用户唯一值（UNION lent + yyyp_lent）"""
        try:
            db = DatabaseManager()
            sql = """
            SELECT DISTINCT data_user
            FROM lent
            WHERE data_user IS NOT NULL AND data_user != ''
            UNION
            SELECT DISTINCT data_user
            FROM yyyp_lent
            WHERE data_user IS NOT NULL AND data_user != ''
            ORDER BY data_user
            """
            result = db.execute_query(sql)
            users = [row[0] for row in result or [] if row[0]]
            return jsonify({'success': True, 'data': users}), 200
        except Exception as e:
            print(f"获取用户列表失败: {e}")
            return jsonify({'success': False, 'message': str(e), 'data': []}), 500
