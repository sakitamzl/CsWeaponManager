from flask import jsonify, request
from src.db_manager.database import DatabaseManager
from src.units.execution_db import Date_base
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SysMessageHandler:

    @staticmethod
    def get_sys_message_data(page, limit):
        """获取通知列表数据（分页）"""
        try:
            db = DatabaseManager()
            offset = (page - 1) * limit

            sql_count = "SELECT COUNT(*) FROM sys_message"
            result_count = db.execute_query(sql_count, ())
            total_count = result_count[0][0] if result_count else 0

            sql = f"""
            SELECT
                notification_id,
                title,
                content,
                type,
                level,
                is_read,
                source,
                related_id,
                action_url,
                create_time,
                read_time,
                expire_time,
                extra_data
            FROM sys_message
            ORDER BY create_time DESC
            LIMIT {limit} OFFSET {offset}
            """

            result = db.execute_query(sql, ())

            notifications = []
            if result:
                for row in result:
                    notifications.append({
                        'notification_id': row[0],
                        'title': row[1],
                        'content': row[2],
                        'type': row[3],
                        'level': row[4],
                        'is_read': row[5],
                        'source': row[6],
                        'related_id': row[7],
                        'action_url': row[8],
                        'create_time': row[9],
                        'read_time': row[10],
                        'expire_time': row[11],
                        'extra_data': row[12]
                    })

            return jsonify({'success': True, 'data': notifications, 'total': total_count}), 200

        except Exception as e:
            logger.error(f"获取通知列表失败: {e}")
            return jsonify({'success': False, 'message': str(e), 'data': [], 'total': 0}), 500

    @staticmethod
    def get_sys_message_stats():
        """获取通知统计数据"""
        try:
            db = DatabaseManager()

            result_total = db.execute_query("SELECT COUNT(*) FROM sys_message", ())
            total_count = result_total[0][0] if result_total else 0

            result_unread = db.execute_query("SELECT COUNT(*) FROM sys_message WHERE is_read = 0", ())
            unread_count = result_unread[0][0] if result_unread else 0

            result_type = db.execute_query("SELECT type, COUNT(*) as count FROM sys_message GROUP BY type", ())
            type_stats = {str(row[0]): row[1] for row in result_type} if result_type else {}

            result_level = db.execute_query("SELECT level, COUNT(*) as count FROM sys_message GROUP BY level", ())
            level_stats = {str(row[0]): row[1] for row in result_level} if result_level else {}

            result_source = db.execute_query("""
                SELECT source, COUNT(*) as count FROM sys_message
                WHERE source IS NOT NULL AND source != ''
                GROUP BY source ORDER BY count DESC
            """, ())
            source_stats = {row[0]: row[1] for row in result_source} if result_source else {}

            return jsonify({
                'success': True,
                'data': {
                    'totalCount': total_count,
                    'unreadCount': unread_count,
                    'readCount': total_count - unread_count,
                    'typeStats': type_stats,
                    'levelStats': level_stats,
                    'sourceStats': source_stats
                }
            }), 200

        except Exception as e:
            logger.error(f"获取通知统计失败: {e}")
            return jsonify({'success': False, 'message': str(e), 'data': {}}), 500

    @staticmethod
    def get_sys_message_types():
        """获取所有通知类型"""
        try:
            db = DatabaseManager()
            result = db.execute_query("""
                SELECT DISTINCT type FROM sys_message
                WHERE type IS NOT NULL AND type != '' ORDER BY type
            """, ())
            types = [row[0] for row in result if row[0]] if result else []
            return jsonify({'success': True, 'data': types}), 200
        except Exception as e:
            logger.error(f"获取通知类型失败: {e}")
            return jsonify({'success': False, 'message': str(e), 'data': []}), 500

    @staticmethod
    def get_sys_message_sources():
        """获取所有通知来源"""
        try:
            db = DatabaseManager()
            result = db.execute_query("""
                SELECT DISTINCT source FROM sys_message
                WHERE source IS NOT NULL AND source != '' ORDER BY source
            """, ())
            sources = [row[0] for row in result if row[0]] if result else []
            return jsonify({'success': True, 'data': sources}), 200
        except Exception as e:
            logger.error(f"获取通知来源失败: {e}")
            return jsonify({'success': False, 'message': str(e), 'data': []}), 500

    @staticmethod
    def mark_as_read():
        """标记通知为已读"""
        try:
            data = request.get_json()
            notification_ids = data.get('message_ids', [])

            if not notification_ids:
                return jsonify({'success': False, 'message': '通知ID不能为空'}), 400

            db = DatabaseManager()
            read_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ids_str = ', '.join([str(id) for id in notification_ids])

            sql = f"UPDATE sys_message SET is_read = 1, read_time = '{read_time}' WHERE notification_id IN ({ids_str})"
            affected_rows = db.execute_update(sql, ())

            if affected_rows >= 0:
                return jsonify({'success': True, 'message': f'成功标记 {affected_rows} 条通知为已读'}), 200
            return jsonify({'success': False, 'message': '标记失败'}), 500

        except Exception as e:
            logger.error(f"标记通知已读失败: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500

    @staticmethod
    def mark_all_as_read():
        """标记所有通知为已读"""
        try:
            db = DatabaseManager()
            read_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            sql = f"UPDATE sys_message SET is_read = 1, read_time = '{read_time}' WHERE is_read = 0"
            affected_rows = db.execute_update(sql, ())

            if affected_rows >= 0:
                return jsonify({'success': True, 'message': f'成功标记 {affected_rows} 条通知为已读'}), 200
            return jsonify({'success': False, 'message': '标记失败'}), 500

        except Exception as e:
            logger.error(f"标记所有通知已读失败: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500

    @staticmethod
    def delete_sys_message():
        """删除通知"""
        try:
            data = request.get_json()
            notification_ids = data.get('message_ids', [])

            if not notification_ids:
                return jsonify({'success': False, 'message': '通知ID不能为空'}), 400

            db = DatabaseManager()
            ids_str = ', '.join([str(id) for id in notification_ids])
            sql = f"DELETE FROM sys_message WHERE notification_id IN ({ids_str})"
            affected_rows = db.execute_update(sql, ())

            if affected_rows >= 0:
                return jsonify({'success': True, 'message': f'成功删除 {affected_rows} 条通知'}), 200
            return jsonify({'success': False, 'message': '删除失败'}), 500

        except Exception as e:
            logger.error(f"删除通知失败: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500

    @staticmethod
    def search_by_keyword():
        """根据关键词搜索通知"""
        try:
            data = request.get_json()
            keyword = data.get('keyword', '').strip()
            page = data.get('page', 1)
            page_size = data.get('page_size', 20)

            if not keyword:
                return jsonify({'success': False, 'message': '关键词不能为空', 'data': []}), 400

            offset = (page - 1) * page_size
            db = DatabaseManager()

            result_count = db.execute_query(f"""
                SELECT COUNT(*) FROM sys_message
                WHERE title LIKE '%{keyword}%' OR content LIKE '%{keyword}%' OR related_id LIKE '%{keyword}%'
            """, ())
            total_count = result_count[0][0] if result_count else 0

            result = db.execute_query(f"""
                SELECT notification_id, title, content, type, level, is_read, source,
                       related_id, action_url, create_time, read_time, expire_time, extra_data
                FROM sys_message
                WHERE title LIKE '%{keyword}%' OR content LIKE '%{keyword}%' OR related_id LIKE '%{keyword}%'
                ORDER BY create_time DESC LIMIT {page_size} OFFSET {offset}
            """, ())

            notifications = []
            if result:
                for row in result:
                    notifications.append({
                        'notification_id': row[0], 'title': row[1], 'content': row[2],
                        'type': row[3], 'level': row[4], 'is_read': row[5], 'source': row[6],
                        'related_id': row[7], 'action_url': row[8], 'create_time': row[9],
                        'read_time': row[10], 'expire_time': row[11], 'extra_data': row[12]
                    })

            return jsonify({'success': True, 'data': notifications, 'total': total_count}), 200

        except Exception as e:
            logger.error(f"搜索通知失败: {e}")
            return jsonify({'success': False, 'message': str(e), 'data': []}), 500

    @staticmethod
    def search_by_time():
        """根据时间范围搜索通知"""
        try:
            data = request.get_json()
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            page = data.get('page', 1)
            page_size = data.get('page_size', 20)

            if not start_date or not end_date:
                return jsonify({'success': False, 'message': '开始日期和结束日期不能为空', 'data': []}), 400

            offset = (page - 1) * page_size
            db = DatabaseManager()

            result_count = db.execute_query(f"""
                SELECT COUNT(*) FROM sys_message
                WHERE DATE(create_time) BETWEEN '{start_date}' AND '{end_date}'
            """, ())
            total_count = result_count[0][0] if result_count else 0

            result = db.execute_query(f"""
                SELECT notification_id, title, content, type, level, is_read, source,
                       related_id, action_url, create_time, read_time, expire_time, extra_data
                FROM sys_message
                WHERE DATE(create_time) BETWEEN '{start_date}' AND '{end_date}'
                ORDER BY create_time DESC LIMIT {page_size} OFFSET {offset}
            """, ())

            notifications = []
            if result:
                for row in result:
                    notifications.append({
                        'notification_id': row[0], 'title': row[1], 'content': row[2],
                        'type': row[3], 'level': row[4], 'is_read': row[5], 'source': row[6],
                        'related_id': row[7], 'action_url': row[8], 'create_time': row[9],
                        'read_time': row[10], 'expire_time': row[11], 'extra_data': row[12]
                    })

            return jsonify({'success': True, 'data': notifications, 'total': total_count}), 200

        except Exception as e:
            logger.error(f"按时间搜索通知失败: {e}")
            return jsonify({'success': False, 'message': str(e), 'data': []}), 500

    @staticmethod
    def search_by_filter():
        """根据多条件筛选通知"""
        try:
            data = request.get_json()
            notification_types = data.get('types', [])
            levels = data.get('levels', [])
            sources = data.get('sources', [])
            is_read = data.get('is_read')
            page = data.get('page', 1)
            page_size = data.get('page_size', 20)

            offset = (page - 1) * page_size
            db = DatabaseManager()

            where_conditions = []
            if notification_types:
                types_str = "', '".join(notification_types)
                where_conditions.append(f"type IN ('{types_str}')")
            if levels:
                levels_str = "', '".join(levels)
                where_conditions.append(f"level IN ('{levels_str}')")
            if sources:
                sources_str = "', '".join(sources)
                where_conditions.append(f"source IN ('{sources_str}')")
            if is_read is not None:
                where_conditions.append(f"is_read = {is_read}")

            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

            result_count = db.execute_query(f"SELECT COUNT(*) FROM sys_message WHERE {where_clause}", ())
            total_count = result_count[0][0] if result_count else 0

            result = db.execute_query(f"""
                SELECT notification_id, title, content, type, level, is_read, source,
                       related_id, action_url, create_time, read_time, expire_time, extra_data
                FROM sys_message WHERE {where_clause}
                ORDER BY create_time DESC LIMIT {page_size} OFFSET {offset}
            """, ())

            notifications = []
            if result:
                for row in result:
                    notifications.append({
                        'notification_id': row[0], 'title': row[1], 'content': row[2],
                        'type': row[3], 'level': row[4], 'is_read': row[5], 'source': row[6],
                        'related_id': row[7], 'action_url': row[8], 'create_time': row[9],
                        'read_time': row[10], 'expire_time': row[11], 'extra_data': row[12]
                    })

            return jsonify({'success': True, 'data': notifications, 'total': total_count}), 200

        except Exception as e:
            logger.error(f"筛选通知失败: {e}")
            return jsonify({'success': False, 'message': str(e), 'data': []}), 500

    @staticmethod
    def create_sys_message():
        """创建新通知"""
        try:
            data = request.get_json()
            title = data.get('title')
            content = data.get('content')

            if not title or not content:
                return jsonify({'success': False, 'message': '标题和内容不能为空'}), 400

            db = DatabaseManager()
            create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            result_max = db.execute_query("SELECT MAX(notification_id) FROM sys_message", ())
            max_id = result_max[0][0] if result_max and result_max[0][0] else 0
            notification_id = max_id + 1

            notification_type = data.get('type', 'system')
            level = data.get('level', 'info')
            source = data.get('source', 'system')
            related_id = data.get('related_id', '')
            action_url = data.get('action_url', '')
            expire_time = data.get('expire_time', '')
            extra_data = data.get('extra_data', '')

            sql = f"""
            INSERT INTO sys_message (
                notification_id, title, content, type, level, is_read, source,
                related_id, action_url, create_time, expire_time, extra_data
            ) VALUES (
                {notification_id}, '{title}', '{content}', '{notification_type}', '{level}',
                0, '{source}', '{related_id}', '{action_url}', '{create_time}',
                '{expire_time}', '{extra_data}'
            )
            """

            ok = Date_base().insert(sql)

            if ok is True:
                return jsonify({'success': True, 'message': '通知创建成功', 'data': {'notification_id': notification_id}}), 200
            return jsonify({'success': False, 'message': '通知创建失败'}), 500

        except Exception as e:
            logger.error(f"创建通知失败: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500
