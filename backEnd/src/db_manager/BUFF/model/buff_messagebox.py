# -*- coding: utf-8 -*-
"""
Buff消息表模型
"""

from typing import Dict, Any, List
from ...base_model import BaseModel


class BuffMessageboxModel(BaseModel):
    """Buff消息表模型"""

    @classmethod
    def get_table_name(cls) -> str:
        return "buff_messagebox"

    @classmethod
    def get_fields(cls) -> Dict[str, Dict[str, Any]]:
        return {
            'message_id': {
                'type': 'TEXT',
                'primary_key': True,
                'not_null': True
            },
            'title': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            'templateCode': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            'imageType': {
                'type': 'INTEGER',
                'not_null': False,
                'default': None
            },
            'readStatus': {
                'type': 'INTEGER',
                'not_null': False,
                'default': None
            },
            'message_type': {
                'type': 'INTEGER',
                'not_null': False,
                'default': None
            },
            'orderNo': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            'showStyle': {
                'type': 'INTEGER',
                'not_null': False,
                'default': None
            },
            'sentName': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            'createTime': {
                'type': 'DATETIME',
                'not_null': False,
                'default': None
            },
            'message_text': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            'status': {
                'type': 'INTEGER',
                'not_null': False,
                'default': 0
            },
            'data_user': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            }
        }

    @classmethod
    def get_indexes(cls) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'buff_messagebox_idx',
                'columns': ['message_type', 'readStatus', 'createTime', 'orderNo']
            }
        ]
