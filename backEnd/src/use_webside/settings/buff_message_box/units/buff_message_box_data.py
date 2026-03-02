"""
BuffMessageBox Data 模块
提供 BUFF 消息盒子的数据查询端点
"""
from flask import jsonify
from src.units.execution_db import Date_base


class BuffMessageBoxData:

    @staticmethod
    def get_message_data(page, limit):
        """获取消息列表数据（分页）"""
        try:
            db = Date_base()
            offset = (page - 1) * limit

            sql_count = "SELECT COUNT(*) FROM buff_messagebox"
            success_count, result_count = db.select(sql_count)
            total = result_count[0][0] if success_count and result_count else 0

            sql = f"""
            SELECT
                message_id,
                title,
                templateCode,
                imageType,
                readStatus,
                message_type,
                orderNo,
                showStyle,
                sentName,
                createTime,
                message_text,
                status,
                data_user
            FROM buff_messagebox
            ORDER BY createTime DESC
            LIMIT {limit} OFFSET {offset}
            """
            success, result = db.select(sql)

            if not success:
                return jsonify({'success': False, 'error': '查询失败', 'data': [], 'total': 0}), 500

            data = []
            if result:
                for r in result:
                    data.append({
                        'message_id': r[0],
                        'title': r[1],
                        'templateCode': r[2],
                        'imageType': r[3],
                        'readStatus': r[4],
                        'message_type': r[5],
                        'orderNo': r[6],
                        'showStyle': r[7],
                        'sentName': r[8],
                        'createTime': r[9],
                        'message_text': r[10],
                        'status': r[11],
                        'data_user': r[12],
                    })

            return jsonify({'success': True, 'data': data, 'total': total}), 200

        except Exception as e:
            return jsonify({'success': False, 'error': f'查询失败: {str(e)}', 'data': [], 'total': 0}), 500

    @staticmethod
    def get_message_types():
        """获取所有消息类型（distinct sentName）"""
        try:
            db = Date_base()
            sql = "SELECT DISTINCT sentName FROM buff_messagebox WHERE sentName IS NOT NULL AND sentName != '' ORDER BY sentName"
            success, result = db.select(sql)

            types = []
            if success and result:
                for r in result:
                    if r[0]:
                        types.append(r[0])

            return jsonify({'success': True, 'data': types}), 200

        except Exception as e:
            return jsonify({'success': False, 'error': f'查询失败: {str(e)}', 'data': []}), 500
