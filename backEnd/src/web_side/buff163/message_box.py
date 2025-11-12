from flask import jsonify, request, Blueprint
from src.db_manager.buff.buff_messagebox import BuffMessageboxModel
from datetime import datetime

buff163MessageV1 = Blueprint('buff163MessageV1', __name__)

@buff163MessageV1.route('/getLatest/<user_id>', methods=['GET'])
def get_latest(user_id):
    try:
        records = BuffMessageboxModel.find_all(
            "data_user = ? ORDER BY createTime DESC", (user_id,), limit=1
        )
        if records:
            r = records[0]
            return jsonify({
                'message_id': r.message_id,
                'createTime': r.createTime
            }), 200
        return jsonify({'message_id': None, 'createTime': None}), 200
    except Exception as e:
        return jsonify({'message': '查询失败', 'error': str(e)}), 500

@buff163MessageV1.route('/insert_db', methods=['POST'])
def insert_db():
    try:
        data = request.get_json() or {}
        message_id = data.get('message_id') or data.get('id')
        if not message_id:
            return jsonify({'success': False, 'error': '缺少 message_id'}), 400

        record = BuffMessageboxModel()
        record.message_id = str(message_id)
        # 标题映射：action_title -> title
        record.title = data.get('title') or data.get('action_title')
        record.templateCode = data.get('templateCode')
        record.imageType = data.get('imageType')
        record.readStatus = data.get('readStatus')
        record.message_type = data.get('message_type') or data.get('type')
        record.orderNo = data.get('orderNo')
        record.showStyle = data.get('showStyle')
        record.sentName = data.get('sentName')
        # 时间映射：created_at(时间戳) -> createTime(YYYY-MM-DD)
        record.createTime = data.get('createTime') or _parse_epoch_to_date(data.get('created_at'))
        # 内容映射：content -> message_text
        record.message_text = data.get('message_text') or data.get('text') or data.get('content')
        record.status = data.get('status', 0)
        record.data_user = data.get('data_user')

        saved = record.save()
        if saved:
            return jsonify({'success': True, 'message': '插入成功', 'id': record.message_id}), 200
        return jsonify({'success': False, 'error': '插入失败'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500

@buff163MessageV1.route('/batch_insert', methods=['POST'])
def batch_insert():
    try:
        payload = request.get_json() or {}
        items = payload.get('items', [])
        data_user = payload.get('data_user')
        if not isinstance(items, list):
            return jsonify({'success': False, 'error': 'items 必须为数组'}), 400

        success = 0
        for it in items:
            message_id = it.get('message_id') or it.get('id')
            if not message_id:
                continue
            rec = BuffMessageboxModel()
            rec.message_id = str(message_id)
            # 标题映射
            rec.title = it.get('title') or it.get('action_title')
            rec.templateCode = it.get('templateCode')
            rec.imageType = it.get('imageType')
            rec.readStatus = it.get('readStatus')
            rec.message_type = it.get('message_type') or it.get('type')
            rec.orderNo = it.get('orderNo')
            rec.showStyle = it.get('showStyle')
            rec.sentName = it.get('sentName')
            # 时间映射
            rec.createTime = it.get('createTime') or _parse_epoch_to_date(it.get('created_at'))
            # 内容映射
            rec.message_text = it.get('message_text') or it.get('text') or it.get('content')
            rec.status = it.get('status', 0)
            rec.data_user = it.get('data_user') or data_user
            if rec.save():
                success += 1
        return jsonify({'success': True, 'inserted': success, 'total': len(items)}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500


def _parse_epoch_to_date(value):
    """将时间戳(秒)转换为 YYYY-MM-DD 字符串。非数值则返回原值。"""
    if value is None:
        return None
    try:
        # 兼容字符串数字
        if isinstance(value, str) and value.isdigit():
            value = int(value)
        # 浮点或整型
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(int(value)).strftime('%Y-%m-%d')
        return value
    except Exception:
        return value
