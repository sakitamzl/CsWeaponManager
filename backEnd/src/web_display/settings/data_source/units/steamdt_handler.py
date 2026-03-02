# -*- coding: utf-8 -*-
"""
SteamDT 数据源处理器
迁移自 backEnd/src/web_side/SteamDT/steamdt_api.py
注意：homepage-data 已由 web_display/home/units/steamdt_homepage.py 提供 V2 实现
      此处仅保留 config 接口（架构一致性）
"""

from flask import jsonify


class SteamDTHandler:

    @staticmethod
    def get_config():
        """
        获取SteamDT配置
        SteamDT API不需要token认证，此接口仅为保持架构一致性
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
