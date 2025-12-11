# -*- coding: utf-8 -*-
"""
饰品搜索 API
用于第三方数据网站的饰品搜索功能
"""

from flask import Blueprint, request, jsonify
from src.db_manager.index.weapon_classID import WeaponClassIDModel
from src.log import Log

itemSearchApiV1 = Blueprint('itemSearchApiV1', __name__)
logger = Log()


@itemSearchApiV1.route('/api/item-search/search', methods=['POST'])
def search_items():
    """
    搜索饰品
    
    请求体:
    {
        "keyword": "AK-47",  # 搜索关键词（在 item_name 中搜索）
        "weaponType": "步枪",  # 可选：武器类型
        "weaponName": "AK-47",  # 可选：武器名称
        "rarity": "隐秘"  # 可选：稀有度
    }
    
    返回:
    {
        "success": true,
        "data": [
            {
                "csqaq_id": 123,
                "market_listing_item_name": "AK-47 | 二西莫夫 (久经沙场)",
                "steam_hash_name": "AK-47 | Asiimov (Field-Tested)",
                "weapon_type": "步枪",
                "weapon_name": "AK-47",
                "item_name": "二西莫夫",
                "rarity": "隐秘",
                "yyyp_Price": "1234.56",
                "on_sale_count": 100
            }
        ]
    }
    """
    try:
        data = request.get_json()
        keyword = data.get('keyword', '').strip()
        weapon_type = data.get('weaponType', '').strip()
        weapon_name = data.get('weaponName', '').strip()
        rarity = data.get('rarity', '').strip()
        
        logger.write_log(
            f"饰品搜索请求: keyword={keyword}, weaponType={weapon_type}, "
            f"weaponName={weapon_name}, rarity={rarity}",
            'info'
        )
        
        # 构建 SQL 查询
        conditions = []
        params = []
        
        # 关键词搜索（在 item_name 中搜索）
        if keyword:
            conditions.append("item_name LIKE ?")
            params.append(f"%{keyword}%")
        
        # 武器类型筛选
        if weapon_type:
            conditions.append("weapon_type = ?")
            params.append(weapon_type)
        
        # 武器名称筛选
        if weapon_name:
            conditions.append("weapon_name = ?")
            params.append(weapon_name)
        
        # 稀有度筛选
        if rarity:
            conditions.append("Rarity = ?")
            params.append(rarity)
        
        # 如果没有任何搜索条件，返回空结果
        if not conditions:
            return jsonify({
                'success': True,
                'data': [],
                'message': '请提供搜索条件'
            }), 200
        
        # 构建完整的 SQL 查询
        where_clause = " AND ".join(conditions)
        sql = f"""
            SELECT 
                csqaq_id,
                market_listing_item_name,
                steam_hash_name,
                weapon_type,
                weapon_name,
                item_name,
                Rarity as rarity,
                yyyp_Price,
                yyyp_OnSaleCount as on_sale_count
            FROM weapon_classID
            WHERE {where_clause}
            ORDER BY 
                CASE 
                    WHEN csqaq_id IS NOT NULL THEN 0 
                    ELSE 1 
                END,
                yyyp_OnSaleCount DESC,
                yyyp_Price ASC
            LIMIT 50
        """
        
        logger.write_log(f"执行SQL: {sql}", 'debug')
        logger.write_log(f"参数: {params}", 'debug')
        
        # 执行查询
        instance = WeaponClassIDModel()
        results = instance.db.execute_query(sql, tuple(params))
        
        # 格式化结果
        items = []
        for row in results:
            item = {
                'csqaq_id': row[0],
                'market_listing_item_name': row[1],
                'steam_hash_name': row[2],
                'weapon_type': row[3],
                'weapon_name': row[4],
                'item_name': row[5],
                'rarity': row[6],
                'yyyp_Price': row[7],
                'on_sale_count': int(row[8]) if row[8] else 0
            }
            items.append(item)
        
        logger.write_log(f"搜索完成，找到 {len(items)} 件饰品", 'info')
        
        return jsonify({
            'success': True,
            'data': items,
            'total': len(items)
        }), 200
        
    except Exception as e:
        logger.write_log(f"饰品搜索失败: {str(e)}", 'error')
        import traceback
        logger.write_log(f"详细错误: {traceback.format_exc()}", 'error')
        return jsonify({
            'success': False,
            'message': f'搜索失败: {str(e)}'
        }), 500


@itemSearchApiV1.route('/api/item-search/weapon-names', methods=['POST'])
def get_weapon_names():
    """
    获取指定武器类型的所有武器名称列表
    
    请求体:
    {
        "weaponType": "步枪"
    }
    
    返回:
    {
        "success": true,
        "data": ["AK-47", "M4A4", "M4A1-S", ...]
    }
    """
    try:
        data = request.get_json()
        weapon_type = data.get('weaponType', '').strip()
        
        if not weapon_type:
            return jsonify({
                'success': False,
                'message': '请提供武器类型'
            }), 400
        
        sql = """
            SELECT DISTINCT weapon_name
            FROM weapon_classID
            WHERE weapon_type = ? AND weapon_name IS NOT NULL AND weapon_name != ''
            ORDER BY weapon_name
        """
        
        instance = WeaponClassIDModel()
        results = instance.db.execute_query(sql, (weapon_type,))
        weapon_names = [row[0] for row in results if row[0]]
        
        return jsonify({
            'success': True,
            'data': weapon_names
        }), 200
        
    except Exception as e:
        logger.write_log(f"获取武器名称列表失败: {str(e)}", 'error')
        return jsonify({
            'success': False,
            'message': f'获取失败: {str(e)}'
        }), 500


@itemSearchApiV1.route('/api/item-search/csqaq-detail', methods=['GET'])
def get_csqaq_detail():
    """
    获取 CSQAQ 饰品详细信息
    
    Query 参数:
    - id: CSQAQ ID
    
    返回:
    {
        "success": true,
        "data": {...}  # CSQAQ API 返回的完整数据
    }
    """
    try:
        import requests
        from src.db_manager.index.config import ConfigModel
        import json
        
        csqaq_id = request.args.get('id')
        if not csqaq_id:
            return jsonify({
                'success': False,
                'message': '请提供 CSQAQ ID'
            }), 400
        
        logger.write_log(f"获取 CSQAQ 详细信息: id={csqaq_id}", 'info')
        
        # 从数据库获取 CSQAQ ApiToken
        configs = ConfigModel.find_by_keys('csqaq', 'config')
        
        if not configs or len(configs) == 0:
            return jsonify({
                'success': False,
                'message': 'CSQAQ配置不存在，请先在【设置 > 数据源管理】中添加CSQAQ数据源'
            }), 404
        
        config = configs[0]
        config_data = json.loads(config.value)
        api_token = config_data.get('ApiToken', '')
        
        if not api_token:
            return jsonify({
                'success': False,
                'message': 'CSQAQ ApiToken未配置'
            }), 400
        
        # 调用 CSQAQ API
        headers = {
            'ApiToken': api_token
        }
        
        response = requests.get(
            f'https://api.csqaq.com/api/v1/info/good',
            params={'id': csqaq_id},
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                logger.write_log(f"CSQAQ 详细信息获取成功: id={csqaq_id}", 'info')
                return jsonify({
                    'success': True,
                    'data': data.get('data')
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': data.get('msg', 'CSQAQ API 返回错误')
                }), 400
        else:
            return jsonify({
                'success': False,
                'message': f'CSQAQ API 请求失败: {response.status_code}'
            }), response.status_code
        
    except Exception as e:
        logger.write_log(f"获取 CSQAQ 详细信息失败: {str(e)}", 'error')
        import traceback
        logger.write_log(f"详细错误: {traceback.format_exc()}", 'error')
        return jsonify({
            'success': False,
            'message': f'获取失败: {str(e)}'
        }), 500


# 导出 Blueprint
__all__ = ['itemSearchApiV1']
