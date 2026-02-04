from flask import jsonify, request, Blueprint
from src.execution_db import Date_base
from datetime import datetime
import logging
import uuid

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

webSysMessagePageV1 = Blueprint('webSysMessagePageV1', __name__)

@webSysMessagePageV1.route('/getSysMessageData/<int:page>/<int:limit>', methods=['GET'])
def getSysMessageData(page, limit):
    """获取通知列表数据（分页）"""
    try:
        db = Date_base()
        offset = (page - 1) * limit

        # 获取总记录数
        sql_count = "SELECT COUNT(*) FROM sys_message"
        success_count, result_count = db.select(sql_count)
        total_count = result_count[0][0] if success_count and result_count else 0
        logger.info(f"获取通知总数: {total_count}")

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

        success, result = db.select(sql)

        if not success:
            return jsonify({
                'success': False,
                'message': '查询失败',
                'data': [],
                'total': 0
            }), 500

        notifications = []
        if result:
            for row in result:
                notification = {
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
                }
                notifications.append(notification)

        logger.info(f"返回数据: 共 {len(notifications)} 条通知, 总数: {total_count}")
        return jsonify({
            'success': True,
            'data': notifications,
            'total': total_count
        }), 200

    except Exception as e:
        logger.error(f"获取通知列表失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e),
            'data': [],
            'total': 0
        }), 500


@webSysMessagePageV1.route('/getSysMessageStats', methods=['GET'])
def getSysMessageStats():
    """获取通知统计数据"""
    try:
        db = Date_base()

        # 总通知数量
        sql_total = "SELECT COUNT(*) FROM sys_message"
        success_total, result_total = db.select(sql_total)
        total_count = result_total[0][0] if success_total and result_total else 0

        # 未读通知数量
        sql_unread = "SELECT COUNT(*) FROM sys_message WHERE is_read = 0"
        success_unread, result_unread = db.select(sql_unread)
        unread_count = result_unread[0][0] if success_unread and result_unread else 0

        # 按类型统计
        sql_type = """
        SELECT type, COUNT(*) as count
        FROM sys_message
        GROUP BY type
        """
        success_type, result_type = db.select(sql_type)

        type_stats = {}
        if success_type and result_type:
            for row in result_type:
                type_stats[str(row[0])] = row[1]

        # 按级别统计
        sql_level = """
        SELECT level, COUNT(*) as count
        FROM sys_message
        GROUP BY level
        """
        success_level, result_level = db.select(sql_level)

        level_stats = {}
        if success_level and result_level:
            for row in result_level:
                level_stats[str(row[0])] = row[1]

        # 按来源统计
        sql_source = """
        SELECT source, COUNT(*) as count
        FROM sys_message
        WHERE source IS NOT NULL AND source != ''
        GROUP BY source
        ORDER BY count DESC
        """
        success_source, result_source = db.select(sql_source)

        source_stats = {}
        if success_source and result_source:
            for row in result_source:
                source_stats[row[0]] = row[1]

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
        return jsonify({
            'success': False,
            'message': str(e),
            'data': {}
        }), 500


@webSysMessagePageV1.route('/markAsRead', methods=['POST'])
def markAsRead():
    """标记通知为已读"""
    try:
        data = request.get_json()
        notification_ids = data.get('notification_ids', [])

        if not notification_ids:
            return jsonify({
                'success': False,
                'message': '通知ID不能为空'
            }), 400

        db = Date_base()
        read_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 构建IN条件
        ids_str = ', '.join([str(id) for id in notification_ids])

        sql = f"""
        UPDATE sys_message
        SET is_read = 1, read_time = '{read_time}'
        WHERE notification_id IN ({ids_str})
        """

        success, affected_rows = db.update(sql)

        if success:
            return jsonify({
                'success': True,
                'message': f'成功标记 {affected_rows} 条通知为已读'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '标记失败'
            }), 500

    except Exception as e:
        logger.error(f"标记通知已读失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@webSysMessagePageV1.route('/markAllAsRead', methods=['POST'])
def markAllAsRead():
    """标记所有通知为已读"""
    try:
        db = Date_base()
        read_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        sql = f"""
        UPDATE sys_message
        SET is_read = 1, read_time = '{read_time}'
        WHERE is_read = 0
        """

        success, affected_rows = db.update(sql)

        if success:
            return jsonify({
                'success': True,
                'message': f'成功标记 {affected_rows} 条通知为已读'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '标记失败'
            }), 500

    except Exception as e:
        logger.error(f"标记所有通知已读失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@webSysMessagePageV1.route('/deleteSysMessage', methods=['POST'])
def deleteSysMessage():
    """删除通知"""
    try:
        data = request.get_json()
        notification_ids = data.get('notification_ids', [])

        if not notification_ids:
            return jsonify({
                'success': False,
                'message': '通知ID不能为空'
            }), 400

        db = Date_base()

        # 构建IN条件
        ids_str = ', '.join([str(id) for id in notification_ids])

        sql = f"DELETE FROM sys_message WHERE notification_id IN ({ids_str})"

        success, affected_rows = db.delete(sql)

        if success:
            return jsonify({
                'success': True,
                'message': f'成功删除 {affected_rows} 条通知'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '删除失败'
            }), 500

    except Exception as e:
        logger.error(f"删除通知失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@webSysMessagePageV1.route('/searchSysMessageByKeyword', methods=['POST'])
def searchSysMessageByKeyword():
    """根据关键词搜索通知"""
    try:
        data = request.get_json()
        keyword = data.get('keyword', '').strip()
        page = data.get('page', 1)
        page_size = data.get('page_size', 20)

        if not keyword:
            return jsonify({
                'success': False,
                'message': '关键词不能为空',
                'data': []
            }), 400

        offset = (page - 1) * page_size
        db = Date_base()

        # 获取符合条件的总记录数
        sql_count = f"""
        SELECT COUNT(*)
        FROM sys_message
        WHERE title LIKE '%{keyword}%'
           OR content LIKE '%{keyword}%'
           OR related_id LIKE '%{keyword}%'
        """
        success_count, result_count = db.select(sql_count)
        total_count = result_count[0][0] if success_count and result_count else 0

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
        WHERE title LIKE '%{keyword}%'
           OR content LIKE '%{keyword}%'
           OR related_id LIKE '%{keyword}%'
        ORDER BY create_time DESC
        LIMIT {page_size} OFFSET {offset}
        """

        success, result = db.select(sql)

        if not success:
            return jsonify({
                'success': False,
                'message': '搜索失败',
                'data': [],
                'total': 0
            }), 500

        notifications = []
        if result:
            for row in result:
                notification = {
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
                }
                notifications.append(notification)

        return jsonify({
            'success': True,
            'data': notifications,
            'total': total_count
        }), 200

    except Exception as e:
        logger.error(f"搜索通知失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e),
            'data': []
        }), 500


@webSysMessagePageV1.route('/searchSysMessageByTime', methods=['POST'])
def searchSysMessageByTime():
    """根据时间范围搜索通知"""
    try:
        data = request.get_json()
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        page = data.get('page', 1)
        page_size = data.get('page_size', 20)

        if not start_date or not end_date:
            return jsonify({
                'success': False,
                'message': '开始日期和结束日期不能为空',
                'data': []
            }), 400

        offset = (page - 1) * page_size
        db = Date_base()

        # 获取符合条件的总记录数
        sql_count = f"""
        SELECT COUNT(*)
        FROM sys_message
        WHERE DATE(create_time) BETWEEN '{start_date}' AND '{end_date}'
        """
        success_count, result_count = db.select(sql_count)
        total_count = result_count[0][0] if success_count and result_count else 0

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
        WHERE DATE(create_time) BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY create_time DESC
        LIMIT {page_size} OFFSET {offset}
        """

        success, result = db.select(sql)

        if not success:
            return jsonify({
                'success': False,
                'message': '搜索失败',
                'data': [],
                'total': 0
            }), 500

        notifications = []
        if result:
            for row in result:
                notification = {
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
                }
                notifications.append(notification)

        return jsonify({
            'success': True,
            'data': notifications,
            'total': total_count
        }), 200

    except Exception as e:
        logger.error(f"按时间搜索通知失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e),
            'data': []
        }), 500


@webSysMessagePageV1.route('/searchSysMessageByFilter', methods=['POST'])
def searchSysMessageByFilter():
    """根据多条件筛选通知"""
    try:
        data = request.get_json()
        notification_types = data.get('types', [])
        levels = data.get('levels', [])
        sources = data.get('sources', [])
        is_read = data.get('is_read')  # None表示全部, 0表示未读, 1表示已读
        page = data.get('page', 1)
        page_size = data.get('page_size', 20)

        offset = (page - 1) * page_size
        db = Date_base()

        # 构建WHERE条件
        where_conditions = []

        if notification_types and len(notification_types) > 0:
            types_str = "', '".join(notification_types)
            where_conditions.append(f"type IN ('{types_str}')")

        if levels and len(levels) > 0:
            levels_str = "', '".join(levels)
            where_conditions.append(f"level IN ('{levels_str}')")

        if sources and len(sources) > 0:
            sources_str = "', '".join(sources)
            where_conditions.append(f"source IN ('{sources_str}')")

        if is_read is not None:
            where_conditions.append(f"is_read = {is_read}")

        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

        # 获取符合条件的总记录数
        sql_count = f"""
        SELECT COUNT(*)
        FROM sys_message
        WHERE {where_clause}
        """
        success_count, result_count = db.select(sql_count)
        total_count = result_count[0][0] if success_count and result_count else 0

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
        WHERE {where_clause}
        ORDER BY create_time DESC
        LIMIT {page_size} OFFSET {offset}
        """

        success, result = db.select(sql)

        if not success:
            return jsonify({
                'success': False,
                'message': '筛选失败',
                'data': [],
                'total': 0
            }), 500

        notifications = []
        if result:
            for row in result:
                notification = {
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
                }
                notifications.append(notification)

        return jsonify({
            'success': True,
            'data': notifications,
            'total': total_count
        }), 200

    except Exception as e:
        logger.error(f"筛选通知失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e),
            'data': []
        }), 500


@webSysMessagePageV1.route('/getSysMessageTypes', methods=['GET'])
def getSysMessageTypes():
    """获取所有通知类型"""
    try:
        db = Date_base()
        sql = """
        SELECT DISTINCT type
        FROM sys_message
        WHERE type IS NOT NULL AND type != ''
        ORDER BY type
        """
        success, result = db.select(sql)

        types = []
        if success and result:
            for row in result:
                if row[0]:
                    types.append(row[0])

        return jsonify({
            'success': True,
            'data': types
        }), 200

    except Exception as e:
        logger.error(f"获取通知类型失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e),
            'data': []
        }), 500


@webSysMessagePageV1.route('/getSysMessageSources', methods=['GET'])
def getSysMessageSources():
    """获取所有通知来源"""
    try:
        db = Date_base()
        sql = """
        SELECT DISTINCT source
        FROM sys_message
        WHERE source IS NOT NULL AND source != ''
        ORDER BY source
        """
        success, result = db.select(sql)

        sources = []
        if success and result:
            for row in result:
                if row[0]:
                    sources.append(row[0])

        return jsonify({
            'success': True,
            'data': sources
        }), 200

    except Exception as e:
        logger.error(f"获取通知来源失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e),
            'data': []
        }), 500


@webSysMessagePageV1.route('/createSysMessage', methods=['POST'])
def createSysMessage():
    """创建新通知"""
    try:
        data = request.get_json()

        title = data.get('title')
        content = data.get('content')

        if not title or not content:
            return jsonify({
                'success': False,
                'message': '标题和内容不能为空'
            }), 400

        db = Date_base()
        create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 获取当前最大ID
        sql_max_id = "SELECT MAX(notification_id) FROM sys_message"
        success_max, result_max = db.select(sql_max_id)
        max_id = result_max[0][0] if success_max and result_max and result_max[0][0] else 0
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

        success, _ = db.insert(sql)

        if success:
            return jsonify({
                'success': True,
                'message': '通知创建成功',
                'data': {
                    'notification_id': notification_id
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '通知创建失败'
            }), 500

    except Exception as e:
        logger.error(f"创建通知失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
