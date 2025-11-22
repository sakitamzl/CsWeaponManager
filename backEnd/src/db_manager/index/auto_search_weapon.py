# -*- coding: utf-8 -*-
"""
改名饰品搜索结果表模型
用于存储实时搜索到的改名饰品数据，支持前端轮询获取
"""

from typing import Dict, Any, List
from datetime import datetime
import json
from ..base_model import BaseModel


class AutoSearchWeaponModel(BaseModel):
    """自动搜索饰品结果表模型（改名/挂件等）"""

    @classmethod
    def get_table_name(cls) -> str:
        return "auto_search_weapon"

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
            
            'steam_id': {
                'type': 'TEXT',
                'not_null': True,
                'comment': '执行搜索的Steam账号ID'
            },
            'config_id': {
                'type': 'INTEGER',
                'not_null': False,
                'default': None,
                'comment': '配置ID（用于区分不同的搜索配置）'
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
            'pendant_count': {
                'type': 'INTEGER',
                'not_null': False,
                'default': 0,
                'comment': '挂件数量'
            },
            'pendant_details': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': '挂件详情JSON'
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
            'steam_hash_name': {
                'type': 'TEXT',
                'not_null': False,
                'default': None,
                'comment': 'Steam Market Hash Name'
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
            'pendant_total_price': {
                'type': 'REAL',
                'not_null': False,
                'default': None,
                'comment': '挂件总价'
            },
            'price_diff_percentage': {
                'type': 'REAL',
                'not_null': False,
                'default': None,
                'comment': '收益百分比'
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

    # ==================== 数据维护方法 ====================

    @classmethod
    def clear_old_records(cls, days: int = 7) -> int:
        """
        清理指定天数之前的旧数据
        
        Args:
            days: 保留最近N天的数据
            
        Returns:
            int: 清理的记录数
        """
        from datetime import timedelta
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # 查找需要删除的记录
        old_records = cls.find_all("created_at < ? AND status = 'active'", (cutoff_date,))
        
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
    def drop_legacy_session_column(cls) -> bool:
        """
        如果老表中仍然存在 session_id 字段，则尝试移除
        """
        try:
            instance = cls()
            db = instance.db
            table_name = cls.get_table_name()
            columns = db.get_table_columns(table_name)
            if not any(col['name'] == 'session_id' for col in columns):
                return False
            db.execute_update(f"ALTER TABLE {table_name} DROP COLUMN session_id")
            print("🧹 已移除 auto_search_weapon.session_id 旧字段")
            return True
        except Exception as e:
            print(f"⚠️ 移除 session_id 字段失败: {e}")
            return False

    # ==================== 便捷创建方法 ====================

    @classmethod
    def create_from_search_result(
        cls,
        steam_id: str,
        weapon_id: str,
        weapon_name: str,
        item_data: Dict[str, Any],
        data_type: str = 'rename',
        config_id: int = None,
        pendant_details: List[Dict[str, Any]] = None,
        pendant_count: int = None,
        pendant_total_price: float = None,
        price_diff_percentage: float = None
    ) -> 'AutoSearchWeaponModel':
        """
        从搜索结果数据创建记录
        
        Args:
            steam_id: Steam账号ID
            weapon_id: 饰品ID
            weapon_name: 饰品名称
            item_data: 商品数据字典
            data_type: 数据类型，默认为'rename'
            
        Returns:
            AutoSearchWeaponModel: 创建的记录对象
        """
        # 计算手续费和收益
        price = float(item_data.get('price', 0))
        spread = float(item_data.get('spread', 0))
        commission_fee = price * 0.025
        price_diff = spread - commission_fee
        
        # 处理 name_tag：去除前缀并过滤全*号和空值
        name_tag = item_data.get('nameTag', '')
        if name_tag:
            # 去除 "名称标签："" 前缀和尾部的引号
            name_tag = name_tag.replace('名称标签："', '', 1).strip()
            if name_tag.endswith('"'):
                name_tag = name_tag[:-1]
            # 如果为空或全*号，设置为 None（不入库）
            if not name_tag or all(c == '*' for c in name_tag):
                name_tag = None
        else:
            name_tag = None
        
        # 创建记录
        record = cls(
            steam_id=steam_id,
            config_id=config_id,
            data_type=data_type,
            weapon_id=weapon_id,
            weapon_name=weapon_name,
            commodity_id=str(item_data.get('id', '')),
            commodity_no=item_data.get('commodityNo'),
            price=price,
            lowest_price=float(item_data.get('lowest_price', item_data.get('lowestPrice', 0) or 0)),
            spread=spread,
            abrade=item_data.get('abrade'),
            paint_seed=str(item_data.get('paintSeed')) if item_data.get('paintSeed') else None,
            name_tag=name_tag,
            seller_name=item_data.get('userNickName'),
            asset_id=item_data.get('assetId'),
            icon_url=item_data.get('iconUrl'),
            steam_hash_name=item_data.get('steam_hash_name'),
            commission_fee=commission_fee if data_type == 'rename' else item_data.get('commissionFee', commission_fee),
            price_diff=item_data.get('priceDiff', price_diff),
            pendant_count=pendant_count if pendant_count is not None else (len(pendant_details) if pendant_details else 0),
            pendant_total_price=pendant_total_price or item_data.get('pendantTotalPrice'),
            price_diff_percentage=price_diff_percentage or item_data.get('priceDiffPercentage'),
            pendant_details=json.dumps(pendant_details, ensure_ascii=False) if pendant_details else (json.dumps(item_data.get('pendants'), ensure_ascii=False) if item_data.get('pendants') else None),
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
        pendants_raw = self.pendant_details
        pendants = []
        if pendants_raw:
            if isinstance(pendants_raw, (bytes, bytearray)):
                pendants_raw = pendants_raw.decode('utf-8', errors='ignore')
            if isinstance(pendants_raw, str):
                try:
                    pendants = json.loads(pendants_raw)
                except (json.JSONDecodeError, TypeError):
                    pendants = []
            elif isinstance(pendants_raw, list):
                pendants = pendants_raw

        weapon_id_value = self.weapon_id
        weapon_name_value = self.weapon_name

        if (
            weapon_name_value
            and isinstance(weapon_name_value, str)
            and weapon_name_value.isdigit()
            and weapon_id_value
            and isinstance(weapon_id_value, str)
            and not weapon_id_value.isdigit()
        ):
            weapon_id_value, weapon_name_value = weapon_name_value, weapon_id_value

        return {
            'id': self.id,
            'configId': self.config_id,
            'dataType': self.data_type,
            'weaponId': weapon_id_value,
            'weaponName': weapon_name_value,
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
            'steamHashName': self.steam_hash_name,
            'commissionFee': self.commission_fee,
            'priceDiff': self.price_diff,
            'pendantCount': self.pendant_count or 0,
            'pendantTotalPrice': self.pendant_total_price or 0,
            'priceDiffPercentage': self.price_diff_percentage or 0,
            'pendants': pendants,
            'status': self.status,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at
        }


# 确保表结构同步，并尽力移除遗留的 session_id 字段
try:
    AutoSearchWeaponModel.ensure_table_exists()
    AutoSearchWeaponModel.drop_legacy_session_column()
except Exception as migration_error:
    print(f"⚠️ AutoSearchWeaponModel 初始化时未能移除 session_id 字段: {migration_error}")
