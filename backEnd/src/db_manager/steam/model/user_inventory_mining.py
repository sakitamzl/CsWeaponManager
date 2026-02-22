# -*- coding: utf-8 -*-
"""
用户库存挖掘表模型 - 存储挖掘到的用户及好友库存数据
"""

from typing import Dict, Any, List
from ...base_model import BaseModel


class UserInventoryMiningModel(BaseModel):
    """用户库存挖掘表模型"""
    
    @classmethod
    def get_table_name(cls) -> str:
        return "user_inventory_mining"

    @classmethod
    def get_fields(cls) -> Dict[str, Dict[str, Any]]:
        return {
            'id': {
                'type': 'INTEGER',
                'primary_key': True,
                'auto_increment': True,
                'not_null': True,
                'comment': '自增主键'
            },
            'source_steam_id': {
                'type': 'TEXT',
                'not_null': True,
                'comment': '源Steam ID（发起挖掘的用户）'
            },
            'target_steam_id': {
                'type': 'TEXT',
                'not_null': True,
                'comment': '目标Steam ID（被挖掘的用户或好友）'
            },
            'relationship': {
                'type': 'TEXT',
                'not_null': False,
                'default': 'self',
                'comment': '关系类型：self=自己，friend=好友'
            },
            'persona_name': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '用户昵称'
            },
            'avatar_url': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '头像URL'
            },
            'profile_url': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '个人资料URL'
            },
            'assetid': {
                'type': 'TEXT',
                'not_null': True,
                'comment': '资产ID'
            },
            'instanceid': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '实例ID'
            },
            'classid': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '类ID'
            },
            'item_name': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '物品名称'
            },
            'weapon_name': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '武器名称'
            },
            'steam_hash_name': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': 'Steam 市场 hash name'
            },
            'float_range': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '磨损值范围'
            },
            'weapon_type': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '武器类型'
            },
            'weapon_float': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '武器磨损值'
            },
            'icon_url': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '图标URL'
            },
            'market_price': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '市场参考价格'
            },
            'sticker': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '印花信息(JSON)'
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
            'rarity': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '稀有度'
            },
            'tradable': {
                'type': 'INTEGER',
                'not_null': False,
                'default': 0,
                'comment': '是否可交易：1=可交易，0=不可交易'
            },
            'marketable': {
                'type': 'INTEGER',
                'not_null': False,
                'default': 0,
                'comment': '是否可市场交易：1=可交易，0=不可交易'
            },
            'mining_time': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '挖掘时间'
            },
            'created_at': {
                'type': 'TEXT',
                'not_null': False,
                'default': 'CURRENT_TIMESTAMP',
                'comment': '创建时间'
            }
        }
    
    @classmethod
    def get_indexes(cls) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'user_inventory_mining_idx_source',
                'columns': ['source_steam_id']
            },
            {
                'name': 'user_inventory_mining_idx_target',
                'columns': ['target_steam_id']
            },
            {
                'name': 'user_inventory_mining_idx_relationship',
                'columns': ['relationship']
            },
            {
                'name': 'user_inventory_mining_idx_weapon_type',
                'columns': ['weapon_type']
            },
            {
                'name': 'user_inventory_mining_idx_mining_time',
                'columns': ['mining_time']
            },
            {
                'name': 'user_inventory_mining_idx_unique',
                'columns': ['source_steam_id', 'target_steam_id', 'assetid'],
                'unique': True
            }
        ]

    @classmethod
    def find_by_source(cls, source_steam_id: str, limit: int = None, offset: int = None):
        """根据源Steam ID查找挖掘记录"""
        return cls.find_all(
            "source_steam_id = ? ORDER BY mining_time DESC",
            (source_steam_id,),
            limit,
            offset
        )

    @classmethod
    def find_by_target(cls, target_steam_id: str, limit: int = None, offset: int = None):
        """根据目标Steam ID查找挖掘记录"""
        return cls.find_all(
            "target_steam_id = ? ORDER BY mining_time DESC",
            (target_steam_id,),
            limit,
            offset
        )

    @classmethod
    def find_friends_inventory(cls, source_steam_id: str, limit: int = None, offset: int = None):
        """查找好友的库存记录"""
        return cls.find_all(
            "source_steam_id = ? AND relationship = 'friend' ORDER BY mining_time DESC",
            (source_steam_id,),
            limit,
            offset
        )

    @classmethod
    def get_latest_mining_time(cls, source_steam_id: str):
        """获取最新的挖掘时间"""
        records = cls.find_all(
            "source_steam_id = ? ORDER BY mining_time DESC",
            (source_steam_id,),
            limit=1
        )
        return records[0].get('mining_time') if records else None
