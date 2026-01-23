# -*- coding: utf-8 -*-
"""
饰品价格历史表模型
用于记录饰品价格的历史变化数据
"""

from typing import Dict, Any, List
from datetime import datetime
from ..base_model import BaseModel


class WeaponPriceHistoryModel(BaseModel):
    """饰品价格历史表模型"""

    @classmethod
    def get_table_name(cls) -> str:
        return "weapon_price_history"

    @classmethod
    def get_fields(cls) -> Dict[str, Dict[str, Any]]:
        """
        字段说明：
        - id: 自增主键
        - steam_hash_name: Steam市场名称（关联weapon_classID表）
        - yyyp_price: 悠悠有品价格
        - record_time: 记录时间
        """
        return {
            'id': {
                'type': 'INTEGER',
                'primary_key': True,
                'auto_increment': True,
                'not_null': True
            },
            'steam_hash_name': {
                'type': 'TEXT',
                'not_null': True,
                'default': None
            },
            'yyyp_price': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            'record_time': {
                'type': 'TEXT',
                'not_null': True,
                'default': None
            }
        }

    @classmethod
    def get_indexes(cls) -> List[Dict[str, Any]]:
        """定义索引"""
        return [
            {
                'name': 'idx_steam_hash_name',
                'columns': ['steam_hash_name']
            },
            {
                'name': 'idx_record_time',
                'columns': ['record_time']
            },
            {
                'name': 'idx_steam_hash_name_time',
                'columns': ['steam_hash_name', 'record_time']
            }
        ]

    @classmethod
    def batch_insert_price_records(cls, price_records: List[Dict[str, Any]]) -> int:
        """
        批量插入价格历史记录
        
        :param price_records: 价格记录列表，每项包含 steam_hash_name, yyyp_price, record_time
        :return: 成功插入的数量
        """
        if not price_records:
            return 0
            
        success_count = 0
        db = cls().db

        for record in price_records:
            try:
                steam_hash_name = record.get('steam_hash_name')
                yyyp_price = record.get('yyyp_price')
                record_time = record.get('record_time')

                if not steam_hash_name or not record_time:
                    print(f"价格记录缺少必要字段，跳过: {record}")
                    continue

                sql_insert = f'''INSERT INTO {cls.get_table_name()} 
                                ([steam_hash_name], [yyyp_price], [record_time]) 
                                VALUES (?, ?, ?)'''
                
                affected_rows = db.execute_insert(sql_insert, (
                    steam_hash_name, yyyp_price, record_time
                ))

                if affected_rows > 0:
                    success_count += 1

            except Exception as e:
                print(f"插入价格历史记录失败: steam_hash_name={record.get('steam_hash_name')}, 错误: {e}")
                import traceback
                print(f"错误堆栈: {traceback.format_exc()}")
                continue

        print(f"价格历史记录插入完成: 成功 {success_count} 条")
        return success_count

    @classmethod
    def find_by_steam_hash_name(cls, steam_hash_name: str, limit: int = None):
        """
        根据steam_hash_name查询价格历史
        
        :param steam_hash_name: Steam市场名称
        :param limit: 限制返回数量
        :return: 价格历史记录列表
        """
        where_clause = "[steam_hash_name] = ?"
        order_by = "record_time DESC"
        
        if limit:
            return cls.find_all(
                where=where_clause, 
                params=(steam_hash_name,),
                order_by=order_by,
                limit=limit
            )
        else:
            return cls.find_all(
                where=where_clause, 
                params=(steam_hash_name,),
                order_by=order_by
            )

    @classmethod
    def find_by_time_range(cls, start_time: str, end_time: str):
        """
        根据时间范围查询价格历史
        
        :param start_time: 开始时间 (格式: YYYY-MM-DD HH:MM:SS)
        :param end_time: 结束时间 (格式: YYYY-MM-DD HH:MM:SS)
        :return: 价格历史记录列表
        """
        where_clause = "[record_time] >= ? AND [record_time] <= ?"
        return cls.find_all(
            where=where_clause,
            params=(start_time, end_time),
            order_by="record_time DESC"
        )

    @classmethod
    def get_latest_price(cls, steam_hash_name: str):
        """
        获取指定饰品的最新价格记录
        
        :param steam_hash_name: Steam市场名称
        :return: 最新价格记录或None
        """
        records = cls.find_by_steam_hash_name(steam_hash_name, limit=1)
        return records[0] if records else None
