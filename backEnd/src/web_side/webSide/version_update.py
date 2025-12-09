import os
from flask import Blueprint, jsonify

version_update_bp = Blueprint('version_update', __name__)

@version_update_bp.route('/api/version/update-log', methods=['GET'])
def get_update_log():
    """读取 updateLog.md 文件内容"""
    try:
        # 获取项目根目录的 updateLog.md 文件路径
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        update_log_path = os.path.join(base_dir, 'updateLog.md')
        
        if not os.path.exists(update_log_path):
            return jsonify({
                'success': False,
                'error': '更新日志文件不存在'
            }), 404
        
        # 读取文件内容
        with open(update_log_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            'success': True,
            'data': {
                'content': content
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
