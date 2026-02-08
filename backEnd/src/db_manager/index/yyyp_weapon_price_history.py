# -*- coding: utf-8 -*-
"""
悠悠有品饰品价格历史表模型
用于记录悠悠有品饰品价格的历史变化数据
"""

from typing import Dict, Any, List
from datetime import datetime
from ..base_model import BaseModel


class YyypWeaponPriceHistoryModel(BaseModel):
    """悠悠有品饰品价格历史表模型"""

    @classmethod
    def get_table_name(cls) -> str:
        return "yyyp_weapon_price_history"

    @classmethod
    def get_fields(cls) -> Dict[str, Dict[str, Any]]:
        """
        字段说明：
        - id: 自增主键
        - yyyp_id: 悠悠有品模板ID（关联weapon_classID表）
        - yyyp_price: 悠悠有品价格（浮点数）
        - yyyp_rent: 悠悠有品租金（浮点数）
        - yyyp_on_sale_count: 悠悠有品在售数量（整数）
        - yyyp_on_lease_count: 悠悠有品出租数量（整数）
        - record_time: 记录时间（DATETIME类型）
        """
        return {
            'id': {
                'type': 'INTEGER',
                'primary_key': True,
                'auto_increment': True,
                'not_null': True
            },
            'yyyp_id': {
                'type': 'INTEGER',
                'not_null': True,
                'default': None
            },
            'yyyp_price': {
                'type': 'REAL',
                'not_null': False,
                'default': None
            },
            'yyyp_rent': {
                'type': 'REAL',
                'not_null': False,
                'default': None
            },
            'yyyp_on_sale_count': {
                'type': 'INTEGER',
                'not_null': False,
                'default': None
            },
            'yyyp_on_lease_count': {
                'type': 'INTEGER',
                'not_null': False,
                'default': None
            },
            'record_time': {
                'type': 'DATETIME',
                'not_null': True,
                'default': None
            }
        }

    @classmethod
    def get_indexes(cls) -> List[Dict[str, Any]]:
        """定义索引"""
        return [
            {
                'name': 'idx_yyyp_id',
                'columns': ['yyyp_id']
            },
            {
                'name': 'idx_record_time',
                'columns': ['record_time']
            },
            {
                'name': 'idx_yyyp_id_time',
                'columns': ['yyyp_id', 'record_time']
            }
        ]

    @classmethod
    def batch_insert_price_records(cls, price_records: List[Dict[str, Any]]) -> int:
        """
        批量插入价格历史记录

        :param price_records: 价格记录列表，每项包含 yyyp_id, yyyp_price, yyyp_rent,
                             yyyp_on_sale_count, yyyp_on_lease_count, record_time
        :return: 成功插入的数量
        """
        if not price_records:
            return 0

        success_count = 0
        db = cls().db

        for record in price_records:
            try:
                yyyp_id = record.get('yyyp_id')
                yyyp_price = record.get('yyyp_price')
                yyyp_rent = record.get('yyyp_rent')
                yyyp_on_sale_count = record.get('yyyp_on_sale_count')
                yyyp_on_lease_count = record.get('yyyp_on_lease_count')
                record_time = record.get('record_time')

                if not yyyp_id or not record_time:
                    print(f"价格记录缺少必要字段，跳过: {record}")
                    continue

                # 类型转换：确保价格和租金为float，数量为int
                try:
                    yyyp_price = float(yyyp_price) if yyyp_price is not None and yyyp_price != '' else None
                except (ValueError, TypeError):
                    yyyp_price = None

                try:
                    yyyp_rent = float(yyyp_rent) if yyyp_rent is not None and yyyp_rent != '' else None
                except (ValueError, TypeError):
                    yyyp_rent = None

                try:
                    yyyp_on_sale_count = int(yyyp_on_sale_count) if yyyp_on_sale_count is not None and yyyp_on_sale_count != '' else None
                except (ValueError, TypeError):
                    yyyp_on_sale_count = None

                try:
                    yyyp_on_lease_count = int(yyyp_on_lease_count) if yyyp_on_lease_count is not None and yyyp_on_lease_count != '' else None
                except (ValueError, TypeError):
                    yyyp_on_lease_count = None

                sql_insert = f'''INSERT INTO {cls.get_table_name()}
                                ([yyyp_id], [yyyp_price], [yyyp_rent], [yyyp_on_sale_count],
                                 [yyyp_on_lease_count], [record_time])
                                VALUES (?, ?, ?, ?, ?, ?)'''

                affected_rows = db.execute_insert(sql_insert, (
                    yyyp_id, yyyp_price, yyyp_rent,
                    yyyp_on_sale_count, yyyp_on_lease_count, record_time
                ))

                if affected_rows > 0:
                    success_count += 1

            except Exception as e:
                print(f"插入价格历史记录失败: yyyp_id={record.get('yyyp_id')}, 错误: {e}")
                import traceback
                print(f"错误堆栈: {traceback.format_exc()}")
                continue

        print(f"价格历史记录插入完成: 成功 {success_count} 条")
        return success_count

    @classmethod
    def find_by_yyyp_id(cls, yyyp_id: int, limit: int = None):
        """
        根据yyyp_id查询价格历史

        :param yyyp_id: 悠悠有品模板ID
        :param limit: 限制返回数量
        :return: 价格历史记录列表
        """
        where_clause = "[yyyp_id] = ?"
        order_by = "record_time DESC"

        if limit:
            return cls.find_all(
                where=where_clause,
                params=(yyyp_id,),
                order_by=order_by,
                limit=limit
            )
        else:
            return cls.find_all(
                where=where_clause,
                params=(yyyp_id,),
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
    def get_latest_price(cls, yyyp_id: int):
        """
        获取指定饰品的最新价格记录

        :param yyyp_id: 悠悠有品模板ID
        :return: 最新价格记录或None
        """
        records = cls.find_by_yyyp_id(yyyp_id, limit=1)
        return records[0] if records else None
