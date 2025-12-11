# -*- coding: utf-8 -*-
"""
CSQAQ API路由
"""

from flask import Blueprint, request, jsonify
from .upload_mapping import process_csqaq_mapping_file
from src.db_manager.index.config import ConfigModel
import json

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


@csqaqApiV1.route('/api/csqaq/config', methods=['GET'])
def get_csqaq_config():
    """
    获取CSQAQ配置（包含ApiToken）
    
    从数据库config表中查询 key1='csqaq' AND key2='config' 的配置
    """
    try:
        # 使用 ConfigModel 查询配置
        configs = ConfigModel.find_by_keys('csqaq', 'config')
        
        if not configs or len(configs) == 0:
            return jsonify({
                'success': False,
                'code': 404,
                'message': 'CSQAQ配置不存在，请先在【设置 > 数据源管理】中添加CSQAQ数据源'
            }), 404
        
        # 获取第一条配置
        config = configs[0]
        
        # 解析 value 字段（JSON格式）
        try:
            config_data = json.loads(config.value)
            api_token = config_data.get('ApiToken', '')
            
            if not api_token:
                return jsonify({
                    'success': False,
                    'code': 400,
                    'message': 'CSQAQ ApiToken未配置'
                }), 400
            
            return jsonify({
                'success': True,
                'code': 200,
                'data': {
                    'ApiToken': api_token,
                    'dataName': config.dataName,
                    'dataID': config.dataID
                }
            }), 200
            
        except json.JSONDecodeError as e:
            return jsonify({
                'success': False,
                'code': 500,
                'message': f'配置数据格式错误: {str(e)}'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'code': 500,
            'message': f'获取配置失败: {str(e)}'
        }), 500
