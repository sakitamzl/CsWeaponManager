# -*- coding: utf-8 -*-
"""
租赁主表模型（与 buy / sell 主表结构保持一致风格）
"""

from typing import Dict, Any, List
from ...base_model import BaseModel


class LentModel(BaseModel):
    """租赁记录主表模型"""

    @classmethod
    def get_table_name(cls) -> str:
        return "lent"

    @classmethod
    def get_fields(cls) -> Dict[str, Dict[str, Any]]:
        """
        字段设计对齐 buy / sell 主表：
        - 统一使用 steam_hash_name / sticker / pendant / rename
        - 特有字段：租金、租期、租赁时间段等
        """
        return {
            'ID': {
                'type': 'TEXT',
                'primary_key': True,
                'not_null': True
            },
            'weapon_name': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            'weapon_type': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            'item_name': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            'steam_hash_name': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': 'Steam 市场 hash name'
            },
            'sticker': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '饰品印花信息(JSON)'
            },
            'pendant': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '挂件信息(JSON)'
            },
            'rename': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '改名信息'
            },
            'weapon_float': {
                'type': 'REAL',
                'not_null': False,
                'default': None
            },
            'float_range': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            # 租金 (单价，元/天)
            'price': {
                'type': 'REAL',
                'not_null': False,
                'default': None
            },
            # 总租赁天数
            'total_Lease_Days': {
                'type': 'INTEGER',
                'not_null': False,
                'default': None
            },
            # 最大租期天数（如果有）
            'max_Lease_Days': {
                'type': 'INTEGER',
                'not_null': False,
                'default': None
            },
            # 租赁开始时间
            'lean_start_time': {
                'type': 'DATETIME',
                'not_null': False,
                'default': None
            },
            # 租赁结束时间
            'lean_end_time': {
                'type': 'DATETIME',
                'not_null': False,
                'default': None
            },
            # 承租人昵称（主表可以保留，前端可选显示）
            'lenter_name': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            # 平台来源（yyyp / buff 等）
            'from': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            # 三种状态字段，对齐 yyyp_lent
            'status': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            'status_sub': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            'last_status': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            # 关联 steam 账号
            'steam_id': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            # 数据所属用户（data_user）
            'data_user': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            }
        }

    @classmethod
    def get_indexes(cls) -> List[Dict[str, Any]]:
        """
        索引设计类似 buy / sell，用于加速前端查询：
        - 综合索引：按名称、磨损、价格、时间、状态等
        """
        return [
            {
                'name': 'lent_idx',
                'columns': [
                    'weapon_name',
                    'item_name',
                    'weapon_float',
                    'float_range',
                    'price',
                    'lenter_name',
                    'lean_start_time',
                    'status',
                    'from'
                ]
            }
        ]


