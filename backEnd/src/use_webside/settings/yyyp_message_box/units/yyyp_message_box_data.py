"""
YyypMessageBox Data 模块
提供悠悠有品消息盒子的数据查询端点
"""
from flask import jsonify, request
from src.execution_db import Date_base


class YyypMessageBoxData:

    @staticmethod
    def get_message_data(page, limit):
        """获取消息列表数据（分页）"""
        try:
            db = Date_base()
            offset = (page - 1) * limit

            sql_count = "SELECT COUNT(*) FROM yyyp_messagebox"
            success_count, result_count = db.select(sql_count)
            total_count = result_count[0][0] if success_count and result_count else 0

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
            FROM yyyp_messagebox
            ORDER BY createTime DESC
            LIMIT {limit} OFFSET {offset}
            """
            success, result = db.select(sql)

            if not success:
                return jsonify({'success': False, 'message': '查询失败', 'data': [], 'total': 0}), 500

            messages = []
            if result:
                for row in result:
                    messages.append({
                        'message_id': row[0],
                        'title': row[1],
                        'templateCode': row[2],
                        'imageType': row[3],
                        'readStatus': row[4],
                        'message_type': row[5],
                        'orderNo': row[6],
                        'showStyle': row[7],
                        'sentName': row[8],
                        'createTime': row[9],
                        'message_text': row[10],
                        'status': row[11],
                        'data_user': row[12]
                    })

            return jsonify({'success': True, 'data': messages, 'total': total_count}), 200

        except Exception as e:
            return jsonify({'success': False, 'message': str(e), 'data': [], 'total': 0}), 500

    @staticmethod
    def get_message_stats():
        """获取消息统计数据"""
        try:
            db = Date_base()

            sql_total = "SELECT COUNT(*) FROM yyyp_messagebox"
            success_total, result_total = db.select(sql_total)
            total_count = result_total[0][0] if success_total and result_total else 0

            sql_type = """
            SELECT message_type, COUNT(*) as count
            FROM yyyp_messagebox
            GROUP BY message_type
            """
            success_type, result_type = db.select(sql_type)
            type_stats = {}
            if success_type and result_type:
                for row in result_type:
                    type_stats[str(row[0])] = row[1]

            sql_sent = """
            SELECT sentName, COUNT(*) as count
            FROM yyyp_messagebox
            WHERE sentName IS NOT NULL AND sentName != ''
            GROUP BY sentName
            ORDER BY count DESC
            """
            success_sent, result_sent = db.select(sql_sent)
            sent_stats = {}
            if success_sent and result_sent:
                for row in result_sent:
                    sent_stats[row[0]] = row[1]

            sql_read = """
            SELECT readStatus, COUNT(*) as count
            FROM yyyp_messagebox
            GROUP BY readStatus
            """
            success_read, result_read = db.select(sql_read)
            read_count = 0
            unread_count = 0
            if success_read and result_read:
                for row in result_read:
                    if row[0] == 1:
                        read_count = row[1]
                    elif row[0] == 0:
                        unread_count = row[1]

            return jsonify({
                'success': True,
                'data': {
                    'totalCount': total_count,
                    'typeStats': type_stats,
                    'sentStats': sent_stats,
                    'readCount': read_count,
                    'unreadCount': unread_count
                }
            }), 200

        except Exception as e:
            return jsonify({'success': False, 'message': str(e), 'data': {}}), 500

    @staticmethod
    def get_message_types():
        """获取所有消息类型（distinct sentName）"""
        try:
            db = Date_base()
            sql = """
            SELECT DISTINCT sentName
            FROM yyyp_messagebox
            WHERE sentName IS NOT NULL AND sentName != ''
            ORDER BY sentName
            """
            success, result = db.select(sql)

            types = []
            if success and result:
                for row in result:
                    if row[0]:
                        types.append(row[0])

            return jsonify({'success': True, 'data': types}), 200

        except Exception as e:
            return jsonify({'success': False, 'message': str(e), 'data': []}), 500

    @staticmethod
    def search_by_keyword():
        """根据关键词搜索消息"""
        try:
            data = request.get_json()
            keyword = data.get('keyword', '').strip()
            page = data.get('page', 1)
            page_size = data.get('page_size', 20)

            if not keyword:
                return jsonify({'success': False, 'message': '关键词不能为空', 'data': []}), 400

            keyword_escaped = keyword.replace("'", "''")
            offset = (page - 1) * page_size
            db = Date_base()

            sql_count = f"""
            SELECT COUNT(*)
            FROM yyyp_messagebox
            WHERE title LIKE '%{keyword_escaped}%'
               OR message_text LIKE '%{keyword_escaped}%'
               OR orderNo LIKE '%{keyword_escaped}%'
               OR sentName LIKE '%{keyword_escaped}%'
            """
            success_count, result_count = db.select(sql_count)
            total_count = result_count[0][0] if success_count and result_count else 0

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
            FROM yyyp_messagebox
            WHERE title LIKE '%{keyword_escaped}%'
               OR message_text LIKE '%{keyword_escaped}%'
               OR orderNo LIKE '%{keyword_escaped}%'
               OR sentName LIKE '%{keyword_escaped}%'
            ORDER BY createTime DESC
            LIMIT {page_size} OFFSET {offset}
            """
            success, result = db.select(sql)

            if not success:
                return jsonify({'success': False, 'message': '搜索失败', 'data': [], 'total': 0}), 500

            messages = []
            if result:
                for row in result:
                    messages.append({
                        'message_id': row[0],
                        'title': row[1],
                        'templateCode': row[2],
                        'imageType': row[3],
                        'readStatus': row[4],
                        'message_type': row[5],
                        'orderNo': row[6],
                        'showStyle': row[7],
                        'sentName': row[8],
                        'createTime': row[9],
                        'message_text': row[10],
                        'status': row[11],
                        'data_user': row[12]
                    })

            return jsonify({'success': True, 'data': messages, 'total': total_count}), 200

        except Exception as e:
            return jsonify({'success': False, 'message': str(e), 'data': []}), 500

    @staticmethod
    def search_by_time():
        """根据时间范围搜索消息"""
        try:
            data = request.get_json()
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            page = data.get('page', 1)
            page_size = data.get('page_size', 20)

            if not start_date or not end_date:
                return jsonify({'success': False, 'message': '开始日期和结束日期不能为空', 'data': []}), 400

            start_date = str(start_date).replace("'", "''")
            end_date = str(end_date).replace("'", "''")
            offset = (page - 1) * page_size
            db = Date_base()

            sql_count = f"""
            SELECT COUNT(*)
            FROM yyyp_messagebox
            WHERE DATE(createTime) BETWEEN '{start_date}' AND '{end_date}'
            """
            success_count, result_count = db.select(sql_count)
            total_count = result_count[0][0] if success_count and result_count else 0

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
            FROM yyyp_messagebox
            WHERE DATE(createTime) BETWEEN '{start_date}' AND '{end_date}'
            ORDER BY createTime DESC
            LIMIT {page_size} OFFSET {offset}
            """
            success, result = db.select(sql)

            if not success:
                return jsonify({'success': False, 'message': '搜索失败', 'data': [], 'total': 0}), 500

            messages = []
            if result:
                for row in result:
                    messages.append({
                        'message_id': row[0],
                        'title': row[1],
                        'templateCode': row[2],
                        'imageType': row[3],
                        'readStatus': row[4],
                        'message_type': row[5],
                        'orderNo': row[6],
                        'showStyle': row[7],
                        'sentName': row[8],
                        'createTime': row[9],
                        'message_text': row[10],
                        'status': row[11],
                        'data_user': row[12]
                    })

            return jsonify({'success': True, 'data': messages, 'total': total_count}), 200

        except Exception as e:
            return jsonify({'success': False, 'message': str(e), 'data': []}), 500

    @staticmethod
    def search_by_type():
        """根据消息类型（sentName）搜索"""
        try:
            data = request.get_json()
            message_types = data.get('message_types', [])
            page = data.get('page', 1)
            page_size = data.get('page_size', 20)

            if not message_types:
                return jsonify({'success': False, 'message': '消息类型不能为空', 'data': []}), 400

            escaped_types = [t.replace("'", "''") for t in message_types]
            types_str = "', '".join(escaped_types)
            offset = (page - 1) * page_size
            db = Date_base()

            sql_count = f"""
            SELECT COUNT(*)
            FROM yyyp_messagebox
            WHERE sentName IN ('{types_str}')
            """
            success_count, result_count = db.select(sql_count)
            total_count = result_count[0][0] if success_count and result_count else 0

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
            FROM yyyp_messagebox
            WHERE sentName IN ('{types_str}')
            ORDER BY createTime DESC
            LIMIT {page_size} OFFSET {offset}
            """
            success, result = db.select(sql)

            if not success:
                return jsonify({'success': False, 'message': '搜索失败', 'data': [], 'total': 0}), 500

            messages = []
            if result:
                for row in result:
                    messages.append({
                        'message_id': row[0],
                        'title': row[1],
                        'templateCode': row[2],
                        'imageType': row[3],
                        'readStatus': row[4],
                        'message_type': row[5],
                        'orderNo': row[6],
                        'showStyle': row[7],
                        'sentName': row[8],
                        'createTime': row[9],
                        'message_text': row[10],
                        'status': row[11],
                        'data_user': row[12]
                    })

            return jsonify({'success': True, 'data': messages, 'total': total_count}), 200

        except Exception as e:
            return jsonify({'success': False, 'message': str(e), 'data': []}), 500
