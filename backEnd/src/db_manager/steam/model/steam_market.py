# -*- coding: utf-8 -*-
"""
Steam市场记录表模型（合并购买和销售记录）
"""

from typing import Dict, Any, List
from ...base_model import BaseModel


class SteamMarketModel(BaseModel):
    """Steam市场记录表模型（合并购买和销售记录）"""
    
    @classmethod
    def get_table_name(cls) -> str:
        return "steam_market"
    
    @classmethod
    def get_fields(cls) -> Dict[str, Dict[str, Any]]:
        return {
            'ID': {
                'type': 'TEXT',
                'primary_key': True,
                'not_null': True
            },
            'trade_type': {
                'type': 'TEXT',
                'not_null': False,
                'default': None  # 'buy' 或 'sell'
            },
            'asset_id': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            'price': {
                'type': 'REAL',
                'not_null': False,
                'default': None
            },
            'price_original': {
                'type': 'REAL',
                'not_null': False,
                'default': None  # 仅销售记录有此字段，表示原始价格（含手续费）
            },
            'trade_date': {
                'type': 'DATETIME',
                'not_null': False,
                'default': None
            },
            'listing_date': {
                'type': 'DATETIME',
                'not_null': False,
                'default': None
            },
            'game_name': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            'weapon_type': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            'weapon_name': {
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
                'default': None
            },
            'float_range': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            'weapon_float': {
                'type': 'REAL',
                'not_null': False,
                'default': None
            },
            'inspect_link': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            'data_user': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            'sticker': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            'pendant': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            },
            'rename': {
                'type': 'TEXT',
                'not_null': False,
                'default': None
            }
        }
    
    @classmethod
    def get_indexes(cls) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'steam_market_idx_weapon',
                'columns': ['weapon_name', 'item_name']
            },
            {
                'name': 'steam_market_idx_date',
                'columns': ['trade_date']
            },
            {
                'name': 'steam_market_idx_price',
                'columns': ['price']
            },
            {
                'name': 'steam_market_idx_user',
                'columns': ['data_user']
            },
            {
                'name': 'steam_market_idx_trade_type',
                'columns': ['trade_type']
            }
        ]
    
    @classmethod
    def find_by_user(cls, data_user: str, limit: int = None, offset: int = None):
        """根据用户查找市场记录"""
        return cls.find_all("data_user = ?", (data_user,), limit, offset)
    
    @classmethod
    def find_by_trade_type(cls, trade_type: str, limit: int = None, offset: int = None):
        """根据交易类型查找记录（'buy' 或 'sell'）"""
        return cls.find_all("trade_type = ?", (trade_type,), limit, offset)
    
    @classmethod
    def find_by_weapon(cls, weapon_name: str = None, item_name: str = None, limit: int = None, offset: int = None):
        """根据武器名称和皮肤名称查找市场记录"""
        where_conditions = []
        params = []
        
        if weapon_name:
            where_conditions.append("weapon_name LIKE ?")
            params.append(f"%{weapon_name}%")
        
        if item_name:
            where_conditions.append("item_name LIKE ?")
            params.append(f"%{item_name}%")
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        return cls.find_all(where_clause, tuple(params), limit, offset)
    
    @classmethod
    def get_recent_transactions(cls, data_user: str = None, trade_type: str = None, limit: int = 20, offset: int = 0):
        """获取最近的交易记录"""
        where_conditions = []
        params = []
        
        if data_user:
            where_conditions.append("data_user = ?")
            params.append(data_user)
        
        if trade_type:
            where_conditions.append("trade_type = ?")
            params.append(trade_type)
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        where_clause += " ORDER BY trade_date DESC"
        return cls.find_all(where_clause, tuple(params), limit, offset)
    
    @classmethod
    def get_market_statistics(cls, data_user: str = None, trade_type: str = None) -> Dict[str, Any]:
        """获取市场统计信息"""
        db = cls().db
        where_conditions = []
        params = []
        
        if data_user:
            where_conditions.append("data_user = ?")
            params.append(data_user)
        
        if trade_type:
            where_conditions.append("trade_type = ?")
            params.append(trade_type)
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        sql = f"""
        SELECT 
            COUNT(*) as total_count,
            COALESCE(SUM(price), 0) as total_amount,
            COALESCE(AVG(price), 0) as avg_price,
            MIN(price) as min_price,
            MAX(price) as max_price,
            COALESCE(SUM(CASE WHEN trade_type = 'sell' THEN price_original ELSE 0 END), 0) as total_original
        FROM steam_market 
        {where_clause}
        """
        
        try:
            result = db.execute_query(sql, tuple(params))
            if result:
                return {
                    'total_count': result[0][0],
                    'total_amount': result[0][1],
                    'avg_price': result[0][2],
                    'min_price': result[0][3],
                    'max_price': result[0][4],
                    'total_original': result[0][5]
                }
            return {
                'total_count': 0, 
                'total_amount': 0, 
                'avg_price': 0, 
                'min_price': 0, 
                'max_price': 0,
                'total_original': 0
            }
        except Exception as e:
            print(f"获取市场统计信息失败: {e}")
            return {
                'total_count': 0, 
                'total_amount': 0, 
                'avg_price': 0, 
                'min_price': 0, 
                'max_price': 0,
                'total_original': 0
            }

