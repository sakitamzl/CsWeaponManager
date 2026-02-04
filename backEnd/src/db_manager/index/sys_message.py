# -*- coding: utf-8 -*-
"""
系统消息表模型
"""

from typing import Dict, Any
from ..base_model import BaseModel


class SysMessageModel(BaseModel):
    """系统消息表模型"""

    @classmethod
    def get_table_name(cls) -> str:
        return "sys_message"

    @classmethod
    def get_fields(cls) -> Dict[str, Dict[str, Any]]:
        return {
            'notification_id': {
                'type': 'INTEGER',
                'primary_key': True,
                'not_null': True
            },
            'title': {
                'type': 'TEXT',
                'not_null': True,
                'default': None
            },
            'content': {
                'type': 'TEXT',
                'not_null': True,
                'default': None
            },
            'type': {
                'type': 'TEXT',
                'not_null': False,
                'default': 'system'  # system, transaction, warning, error, info
            },
            'level': {
                'type': 'TEXT',
                'not_null': False,
                'default': 'info'  # info, warning, error, success
            },
            'is_read': {
                'type': 'INTEGER',
                'not_null': False,
                'default': 0  # 0: 未读, 1: 已读
            },
            'source': {
                'type': 'TEXT',
                'not_null': False,
                'default': 'system'  # system, buff, yyyp, steam, igxe, etc.
            },
            'related_id': {
                'type': 'TEXT',
                'not_null': False,
                'default': None  # 关联的业务ID，如订单号
            },
            'action_url': {
                'type': 'TEXT',
                'not_null': False,
                'default': None  # 点击后跳转的URL
            },
            'create_time': {
                'type': 'DATETIME',
                'not_null': True,
                'default': None
            },
            'read_time': {
                'type': 'DATETIME',
                'not_null': False,
                'default': None  # 阅读时间
            },
            'expire_time': {
                'type': 'DATETIME',
                'not_null': False,
                'default': None  # 过期时间，过期后可自动清理
            },
            'extra_data': {
                'type': 'TEXT',
                'not_null': False,
                'default': None  # 额外的JSON数据
            }
        }

    @classmethod
    def get_indexes(cls):
        """获取索引定义"""
        return [
            {
                'name': 'idx_notification_create_time',
                'columns': ['create_time'],
                'unique': False
            },
            {
                'name': 'idx_notification_is_read',
                'columns': ['is_read'],
                'unique': False
            },
            {
                'name': 'idx_notification_type',
                'columns': ['type'],
                'unique': False
            },
            {
                'name': 'idx_notification_source',
                'columns': ['source'],
                'unique': False
            }
        ]
