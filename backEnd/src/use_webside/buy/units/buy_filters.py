"""
Buy 页面筛选选项模块
提供下拉框数据：数据用户列表、武器类型、磨损等级、状态、子状态
"""
from flask import jsonify, request
from src.execution_db import Date_base
import logging

logger = logging.getLogger(__name__)


class BuyFilters:

    @staticmethod
    def get_data_user_list():
        """获取 buy 表中 data_user 去重列表"""
        sql = """
        SELECT DISTINCT data_user
        FROM buy
        WHERE data_user IS NOT NULL AND data_user != ''
        ORDER BY data_user
        """
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag:
                users = [row[0] for row in data if row and row[0]]
                return jsonify(users), 200
        return jsonify([]), 500

    @staticmethod
    def get_weapon_types():
        """获取所有武器类型的唯一值（按优先级排序）"""
        try:
            db = Date_base()
            sql = """
            SELECT DISTINCT weapon_type
            FROM buy
            WHERE weapon_type IS NOT NULL AND weapon_type != ''
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
            success, result = db.select(sql)

            weapon_types = []
            if success and result:
                for row in result:
                    if row[0]:
                        weapon_types.append(row[0])

            return jsonify({
                'success': True,
                'data': weapon_types
            }), 200

        except Exception as e:
            logger.error(f"获取武器类型失败: {e}")
            return jsonify({
                'success': False,
                'message': str(e),
                'data': []
            }), 500

    @staticmethod
    def get_float_ranges():
        """获取所有磨损等级的唯一值（优先显示主要磨损等级）"""
        try:
            db = Date_base()
            sql = """
            SELECT DISTINCT float_range
            FROM buy
            WHERE float_range IS NOT NULL AND float_range != ''
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
            success, result = db.select(sql)

            float_ranges = []
            if success and result:
                for row in result:
                    if row[0]:
                        float_ranges.append(row[0])

            return jsonify({
                'success': True,
                'data': float_ranges
            }), 200

        except Exception as e:
            logger.error(f"获取磨损等级失败: {e}")
            return jsonify({
                'success': False,
                'message': str(e),
                'data': []
            }), 500

    @staticmethod
    def get_status_list():
        """获取所有状态的唯一值"""
        try:
            db = Date_base()
            sql = """
            SELECT DISTINCT status
            FROM buy
            WHERE status IS NOT NULL AND status != ''
            ORDER BY
                CASE status
                    WHEN '已完成' THEN 1
                    WHEN '待收货' THEN 2
                    WHEN '已取消' THEN 3
                    ELSE 999
                END,
                status
            """
            success, result = db.select(sql)

            status_list = []
            if success and result:
                for row in result:
                    if row[0]:
                        status_list.append(row[0])

            return jsonify({
                'success': True,
                'data': status_list
            }), 200

        except Exception as e:
            logger.error(f"获取状态列表失败: {e}")
            return jsonify({
                'success': False,
                'message': str(e),
                'data': []
            }), 500

    @staticmethod
    def get_status_sub_list():
        """根据指定状态获取对应的子状态唯一值列表"""
        try:
            status = request.args.get('status', '').strip()
            db = Date_base()
            if not status or status == 'all':
                sql = """
                SELECT DISTINCT status_sub
                FROM buy
                WHERE status_sub IS NOT NULL
                  AND status_sub != ''
                ORDER BY status_sub
                """
            else:
                safe_status = status.replace("'", "''")
                sql = f"""
                SELECT DISTINCT status_sub
                FROM buy
                WHERE status = '{safe_status}'
                  AND status_sub IS NOT NULL
                  AND status_sub != ''
                ORDER BY status_sub
                """
            success, result = db.select(sql)

            sub_list = []
            if success and result:
                for row in result:
                    if row[0]:
                        sub_list.append(row[0])

            return jsonify({
                'success': True,
                'data': sub_list
            }), 200

        except Exception as e:
            logger.error(f"获取子状态列表失败: {e}")
            return jsonify({
                'success': False,
                'message': str(e),
                'data': []
            }), 500
