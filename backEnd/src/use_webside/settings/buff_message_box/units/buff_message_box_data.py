"""
BuffMessageBox Data 模块
提供 BUFF 消息盒子的数据查询端点
"""
from flask import jsonify
from src.db_manager.database import DatabaseManager


class BuffMessageBoxData:

    @staticmethod
    def get_message_data(page, limit):
        """获取消息列表数据（分页）"""
        try:
            db = DatabaseManager()
            offset = (page - 1) * limit

            sql_count = "SELECT COUNT(*) FROM buff_messagebox"
            result_count = db.execute_query(sql_count, ())
            total = result_count[0][0] if result_count else 0

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
            result = db.execute_query(sql, ())

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
            db = DatabaseManager()
            sql = "SELECT DISTINCT sentName FROM buff_messagebox WHERE sentName IS NOT NULL AND sentName != '' ORDER BY sentName"
            result = db.execute_query(sql, ())

            types = []
            if result:
                for r in result:
                    if r[0]:
                        types.append(r[0])

            return jsonify({'success': True, 'data': types}), 200

        except Exception as e:
            return jsonify({'success': False, 'error': f'查询失败: {str(e)}', 'data': []}), 500
