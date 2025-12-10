# -*- coding: utf-8 -*-
"""
CSQAQ API路由
"""

from flask import Blueprint, request, jsonify
from .upload_mapping import process_csqaq_mapping_file

csqaqApiV1 = Blueprint('csqaqApiV1', __name__)


@csqaqApiV1.route('/api/csqaq/upload-mapping', methods=['POST'])
def upload_csqaq_mapping():
    """
    上传CSQAQ映射文件
    
    接收txt文件（JSON格式），解析并更新weapon_classID表的csqaq_id字段
    """
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': '未找到上传文件'
            }), 400
        
        file = request.files['file']
        
        # 检查文件名
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': '文件名为空'
            }), 400
        
        # 检查文件扩展名
        if not file.filename.endswith('.txt'):
            return jsonify({
                'success': False,
                'message': '仅支持.txt文件'
            }), 400
        
        # 读取文件内容
        file_content = file.read().decode('utf-8')
        
        # 处理文件内容
        result = process_csqaq_mapping_file(file_content)
        
        # 返回结果
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500
