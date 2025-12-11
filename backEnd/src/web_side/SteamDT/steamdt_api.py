# -*- coding: utf-8 -*-
"""
SteamDT API路由
"""

from flask import Blueprint, request, jsonify

steamdtApiV1 = Blueprint('steamdtApiV1', __name__)


@steamdtApiV1.route('/api/steamdt/config', methods=['GET'])
def get_steamdt_config():
    """
    获取SteamDT配置
    
    注意：SteamDT API不需要token认证，此接口仅为保持架构一致性
    """
    try:
        return jsonify({
            'success': True,
            'code': 200,
            'data': {
                'needAuth': False,
                'message': 'SteamDT API不需要认证'
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'code': 500,
            'message': f'获取配置失败: {str(e)}'
        }), 500
