from flask import jsonify, request, Blueprint
from src.log import Log
from src.execution_db import Date_base
import requests

youpin898MessageBoxV1 = Blueprint('youpin898MessageBoxV1', __name__)

def get_database_name():
    db_instance = Date_base()
    return db_instance.get_database_name()


@youpin898MessageBoxV1.route('/test', methods=['GET'])
def test():
    """测试端点"""
    return jsonify({'success': True, 'message': 'Message API is working!'}), 200


@youpin898MessageBoxV1.route('/insert_message_data', methods=['POST'])
def insert_message_data():
    """插入消息数据"""
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

    sql = (f"INSERT INTO yyyp_messagebox (message_id, title, templateCode, imageType, readStatus, message_type, orderNo, "
        f"showStyle, sentName, createTime, message_text, status, data_user) VALUES "
        f"('{message_id}', '{title}', '{templateCode}', {imageType if imageType is not None else 'NULL'}, {readStatus}, {message_type}, '{orderNo}', "
        f"{showStyle if showStyle is not None else 'NULL'}, '{sentName}', '{createTime}', '{message_text}', {status}, '{data_user}');")
    
    a_status = Date_base().insert(sql)
    
    if a_status is True:
        insert_status = "写入成功"
    elif a_status == '重复数据':
        insert_status = '重复数据'
    else:
        insert_status = '写入失败'
    return insert_status, 200


@youpin898MessageBoxV1.route('/selectApexTime/<string:steamId>', methods=['GET'])
def selectApexTime(steamId):
    """获取指定用户最新的消息时间"""
    try:
        sql = f"SELECT createTime FROM yyyp_messagebox WHERE data_user = '{steamId}' ORDER BY createTime DESC LIMIT 1"
        success, result = Date_base().select(sql)
        
        if success and result and len(result) > 0:
            return jsonify({
                'success': True,
                'message_time': result[0][0]
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '未找到消息记录'
            }), 200
    except Exception as e:
        Log().write_log(f"查询最新消息时间失败: {e}", 'error')
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@youpin898MessageBoxV1.route('/getCount/<string:steamId>', methods=['GET'])
def getCount(steamId):
    """获取指定用户的消息总数"""
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