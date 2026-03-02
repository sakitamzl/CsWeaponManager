"""
message 处理模块
提供 Spider 所需的消息记录插入与查询接口
"""
from flask import jsonify, request
from src.units.execution_db import Date_base
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

        # 转义单引号
        title = title.replace("'", "''")
        message_text = message_text.replace("'", "''")
        sentName = sentName.replace("'", "''")
        orderNo = orderNo.replace("'", "''")
        templateCode = templateCode.replace("'", "''")

        sql = (
            f"INSERT INTO yyyp_messagebox (message_id, title, templateCode, imageType, readStatus, message_type, orderNo, "
            f"showStyle, sentName, createTime, message_text, status, data_user) VALUES "
            f"('{message_id}', '{title}', '{templateCode}', {imageType if imageType is not None else 'NULL'}, "
            f"{readStatus}, {message_type}, '{orderNo}', "
            f"{showStyle if showStyle is not None else 'NULL'}, '{sentName}', '{createTime}', "
            f"'{message_text}', {status}, '{data_user}');"
        )

        a_status = Date_base().insert(sql)

        if a_status is True:
            insert_status = "写入成功"
        elif a_status == '重复数据':
            insert_status = '重复数据'
        else:
            insert_status = '写入失败'
        return insert_status, 200

    @staticmethod
    def select_apex_time(steamId):
        """获取指定用户最新消息时间，供 Spider 判断增量同步起点"""
        try:
            sql = f"SELECT createTime FROM yyyp_messagebox WHERE data_user = '{steamId}' ORDER BY createTime DESC LIMIT 1"
            success, result = Date_base().select(sql)

            if success and result and len(result) > 0:
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
            sql = f"SELECT COUNT(*) FROM yyyp_messagebox WHERE data_user = '{steamId}'"
            success, result = Date_base().select(sql)

            if success and result:
                return jsonify(result[0][0]), 200
            else:
                return jsonify(0), 200
        except Exception as e:
            Log().write_log(f"查询消息数量失败: {e}", 'error')
            return jsonify(0), 500
