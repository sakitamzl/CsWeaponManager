"""
message 处理模块
提供 Spider 所需的消息记录插入与查询接口
"""
import sqlite3
from flask import jsonify, request
from src.db_manager.database import DatabaseManager
from src.units.log import Log


class MessageHandler:

    @staticmethod
    def insert_message_data():
        """插入消息数据（写入 yyyp_messagebox 表）"""
        data = request.get_json()
        message_id = data.get('message_id')
        title = data.get('title', '')
        templateCode = data.get('templateCode', '')
        imageType = data.get('imageType')
        readStatus = data.get('readStatus', 0)
        message_type = data.get('message_type', 0)
        orderNo = data.get('orderNo', '')
        showStyle = data.get('showStyle')
        sentName = data.get('sentName', '')
        createTime = data.get('createTime')
        message_text = data.get('message_text', '')
        status = data.get('status', 0)
        data_user = data.get('data_user', '')

        sql = """
        INSERT INTO yyyp_messagebox (
            message_id, title, templateCode, imageType, readStatus, message_type, orderNo,
            showStyle, sentName, createTime, message_text, status, data_user
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            str(message_id) if message_id is not None else None,
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
            data_user,
        )

        try:
            db = DatabaseManager()
            db.execute_insert(sql, params)
            insert_status = "写入成功"
        except sqlite3.IntegrityError:
            insert_status = '重复数据'
        except Exception:
            insert_status = '写入失败'

        return insert_status, 200

    @staticmethod
    def select_apex_time(steamId):
        """获取指定用户最新消息时间，供 Spider 判断增量同步起点"""
        try:
            db = DatabaseManager()
            result = db.execute_query(
                "SELECT createTime FROM yyyp_messagebox WHERE data_user = ? ORDER BY createTime DESC LIMIT 1",
                (steamId,),
            )

            if result and len(result) > 0:
                return jsonify({'success': True, 'message_time': result[0][0]}), 200
            else:
                return jsonify({'success': False, 'message': '未找到消息记录'}), 200
        except Exception as e:
            Log().write_log(f"查询最新消息时间失败: {e}", 'error')
            return jsonify({'success': False, 'message': str(e)}), 500

    @staticmethod
    def get_count(steamId):
        """获取指定用户消息总数，供 Spider 计算分页起点"""
        try:
            db = DatabaseManager()
            result = db.execute_query(
                "SELECT COUNT(*) FROM yyyp_messagebox WHERE data_user = ?",
                (steamId,),
            )

            if result:
                return jsonify(result[0][0]), 200
            else:
                return jsonify(0), 200
        except Exception as e:
            Log().write_log(f"查询消息数量失败: {e}", 'error')
            return jsonify(0), 500
