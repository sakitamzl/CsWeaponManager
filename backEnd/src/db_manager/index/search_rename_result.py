# -*- coding: utf-8 -*-
"""
改名饰品搜索结果表模型
用于存储实时搜索到的改名饰品数据，支持前端轮询获取
"""

from typing import Dict, Any, List
from datetime import datetime
from ..base_model import BaseModel


class SearchRenameResultModel(BaseModel):
    """改名饰品搜索结果表模型"""

    @classmethod
    def get_table_name(cls) -> str:
        return "search_rename_result"

    @classmethod
    def get_fields(cls) -> Dict[str, Dict[str, Any]]:
        """
        定义表字段结构
        用于存储每次搜索到的改名饰品数据
        """
        return {
            # 主键 - 自增ID
            'id': {
                'type': 'INTEGER',
                'primary_key': True,
                'autoincrement': True,
                'not_null': True
            },
            
            # 搜索会话信息
            'steam_id': {
                'type': 'TEXT',
                'not_null': True,
                'comment': '执行搜索的Steam账号ID'
            },
            'data_type': {
                'type': 'TEXT',
                'not_null': True,
                'default': "'rename'",
                'comment': '数据类型：rename(改名饰品)、pendant(挂件)等'
            },
            
            # 饰品基本信息
            'weapon_id': {
                'type': 'TEXT',
                'not_null': True,
                'comment': '饰品模板ID（yyyp_id）'
            },
            'weapon_name': {
                'type': 'TEXT',
                'not_null': True,
                'comment': '饰品名称'
            },
            
            # 商品详细信息
            'commodity_id': {
                'type': 'TEXT',
                'not_null': True,
                'comment': '商品ID'
            },
            'commodity_no': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '商品编号'
            },
            'price': {
                'type': 'REAL',
                'not_null': True,
                'comment': '商品价格'
            },
            'lowest_price': {
                'type': 'REAL',
                'not_null': True,
                'comment': '该饰品最低价格'
            },
            'spread': {
                'type': 'REAL',
                'not_null': True,
                'comment': '溢价（价格-最低价）'
            },
            
            # 饰品属性
            'abrade': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '磨损度'
            },
            'paint_seed': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '模板/图案'
            },
            'name_tag': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '改名标签内容'
            },
            
            # 卖家信息
            'seller_name': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '卖家昵称'
            },
            
            # Steam资产信息
            'asset_id': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': 'Steam资产ID'
            },
            'icon_url': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '图标URL'
            },
            
            # 计算字段
            'commission_fee': {
                'type': 'REAL',
                'not_null': False,
                'default': None,
                'comment': '手续费（价格*0.025）'
            },
            'price_diff': {
                'type': 'REAL',
                'not_null': False,
                'default': None,
                'comment': '收益（溢价-手续费）'
            },
            
            # 状态和时间
            'status': {
                'type': 'TEXT',
                'not_null': True,
                'default': "'active'",
                'comment': '状态: active-有效, deleted-已删除'
            },
            'created_at': {
                'type': 'TEXT',
                'not_null': True,
                'comment': '创建时间'
            },
            'updated_at': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '更新时间'
            }
        }

    # ==================== 自定义查询方法 ====================

    @classmethod
    def find_by_session(cls, session_id: str, status: str = 'active', data_type: str = 'rename'):
        """
        根据会话ID查询所有结果
        
        Args:
            session_id: 搜索会话ID
            status: 状态过滤，默认只返回active状态
            data_type: 数据类型过滤，默认为'rename'
            
        Returns:
            List[SearchRenameResultModel]: 结果列表
        """
        if status:
            return cls.find_all(
                "session_id = ? AND status = ? AND data_type = ? ORDER BY price_diff DESC, created_at ASC",
                (session_id, status, data_type)
            )
        else:
            return cls.find_all(
                "session_id = ? AND data_type = ? ORDER BY price_diff DESC, created_at ASC",
                (session_id, data_type)
            )

    @classmethod
    def count_by_session(cls, session_id: str, status: str = 'active', data_type: str = 'rename') -> int:
        """
        统计某个会话的结果数量
        
        Args:
            session_id: 搜索会话ID
            status: 状态过滤
            data_type: 数据类型过滤，默认为'rename'
            
        Returns:
            int: 结果数量
        """
        results = cls.find_by_session(session_id, status, data_type)
        return len(results) if results else 0

    @classmethod
    def delete_by_session(cls, session_id: str) -> bool:
        """
        删除某个会话的所有结果（软删除）
        
        Args:
            session_id: 搜索会话ID
            
        Returns:
            bool: 是否成功
        """
        results = cls.find_by_session(session_id, status=None)
        if not results:
            return True
        
        success = True
        for result in results:
            result.status = 'deleted'
            result.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if not result.save():
                success = False
        
        return success

    @classmethod
    def clear_old_sessions(cls, days: int = 7) -> int:
        """
        清理旧的搜索会话数据
        
        Args:
            days: 保留最近N天的数据
            
        Returns:
            int: 清理的记录数
        """
        from datetime import timedelta
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # 查找需要删除的记录
        old_records = cls.find_all(
            "created_at < ? AND status = 'active'",
            (cutoff_date,)
        )
        
        if not old_records:
            return 0
        
        # 软删除
        count = 0
        for record in old_records:
            record.status = 'deleted'
            record.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if record.save():
                count += 1
        
        return count

    @classmethod
    def get_latest_by_session(cls, session_id: str, limit: int = 50):
        """
        获取某个会话最新的N条结果
        
        Args:
            session_id: 搜索会话ID
            limit: 返回数量限制
            
        Returns:
            List[SearchRenameResultModel]: 结果列表
        """
        return cls.find_all(
            "session_id = ? AND status = 'active' ORDER BY created_at DESC LIMIT ?",
            (session_id, limit)
        )

    # ==================== 便捷创建方法 ====================

    @classmethod
    def create_from_search_result(cls, steam_id: str, 
                                  weapon_id: str, weapon_name: str, 
                                  item_data: Dict[str, Any], data_type: str = 'rename') -> 'SearchRenameResultModel':
        """
        从搜索结果数据创建记录
        
        Args:
            steam_id: Steam账号ID
            weapon_id: 饰品ID
            weapon_name: 饰品名称
            item_data: 商品数据字典
            data_type: 数据类型，默认为'rename'
            
        Returns:
            SearchRenameResultModel: 创建的记录对象
        """
        # 计算手续费和收益
        price = float(item_data.get('price', 0))
        spread = float(item_data.get('spread', 0))
        commission_fee = price * 0.025
        price_diff = spread - commission_fee
        
        # 处理 name_tag：去除前缀并过滤全*号和空值
        name_tag = item_data.get('nameTag', '')
        if name_tag:
            # 去除 "名称标签："" 前缀
            name_tag = name_tag.replace('名称标签："', '').replace('"', '').strip()
            # 如果为空或全*号，设置为 None（不入库）
            if not name_tag or all(c == '*' for c in name_tag):
                name_tag = None
        else:
            name_tag = None
        
        # 创建记录
        record = cls(
            steam_id=steam_id,
            data_type=data_type,
            weapon_id=weapon_id,
            weapon_name=weapon_name,
            commodity_id=str(item_data.get('id', '')),
            commodity_no=item_data.get('commodityNo'),
            price=price,
            lowest_price=float(item_data.get('lowest_price', 0)),
            spread=spread,
            abrade=item_data.get('abrade'),
            paint_seed=str(item_data.get('paintSeed')) if item_data.get('paintSeed') else None,
            name_tag=name_tag,
            seller_name=item_data.get('userNickName'),
            asset_id=item_data.get('assetId'),
            icon_url=item_data.get('iconUrl'),
            commission_fee=commission_fee,
            price_diff=price_diff,
            status='active',
            created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        return record

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式（适合前端使用）
        
        Returns:
            Dict[str, Any]: 字典数据
        """
        return {
            'id': self.id,
            'weaponId': self.weapon_id,
            'weaponName': self.weapon_name,
            'commodityId': self.commodity_id,
            'commodityNo': self.commodity_no,
            'price': self.price,
            'lowestPrice': self.lowest_price,
            'spread': self.spread,
            'abrade': self.abrade,
            'paintSeed': self.paint_seed,
            'nameTag': self.name_tag,
            'sellerName': self.seller_name,
            'assetId': self.asset_id,
            'iconUrl': self.icon_url,
            'commissionFee': self.commission_fee,
            'priceDiff': self.price_diff,
            'status': self.status,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at
        }
