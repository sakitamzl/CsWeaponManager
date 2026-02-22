# -*- coding: utf-8 -*-
"""
CSQAQ映射文件上传处理
处理上传的txt文件（JSON格式），将id值存入weapon_classID表
"""

import json
from typing import Dict, Any
from ...db_manager.index.model.weapon_classID import WeaponClassIDModel


def process_csqaq_mapping_file(file_content: str) -> Dict[str, Any]:
    """
    处理CSQAQ映射文件内容
    
    Args:
        file_content: 文件内容（JSON格式的字符串）
    
    Returns:
        Dict: 处理结果
            {
                'success': bool,
                'message': str,
                'total': int,  # 总记录数
                'updated': int,  # 更新成功数
                'inserted': int,  # 新增成功数
                'failed': int  # 失败数
            }
    """
    try:
        # 解析JSON数据
        data = json.loads(file_content)
        
        if not isinstance(data, list):
            return {
                'success': False,
                'message': '文件格式错误：期望JSON数组',
                'total': 0,
                'updated': 0,
                'not_found': 0,
                'failed': 0
            }
        
        total = len(data)
        updated = 0
        inserted = 0
        failed = 0
        
        # 获取数据库实例
        db = WeaponClassIDModel().db
        
        # 处理每条记录
        for item in data:
            try:
                csqaq_id = item.get('id')
                market_hash_name = item.get('market_hash_name')
                item_name_cn = item.get('name', '')  # 中文名称
                
                if not csqaq_id or not market_hash_name:
                    failed += 1
                    continue
                
                # 通过 market_hash_name 查找对应的 steam_hash_name 记录
                # 注意：market_hash_name 在数据库中对应 steam_hash_name 字段
                existing_records = WeaponClassIDModel.find_by_steam_hash_name(market_hash_name)
                
                if existing_records:
                    # 记录存在，更新 csqaq_id
                    sql = f'''UPDATE {WeaponClassIDModel.get_table_name()} 
                             SET [csqaq_id] = ? 
                             WHERE [steam_hash_name] = ?'''
                    
                    affected_rows = db.execute_update(sql, (csqaq_id, market_hash_name))
                    
                    if affected_rows > 0:
                        updated += 1
                        print(f"✅ 更新成功: csqaq_id={csqaq_id}, market_hash_name={market_hash_name}")
                    else:
                        failed += 1
                else:
                    # 记录不存在，新增一条数据
                    # 只填充必要字段：steam_hash_name（主键）和 csqaq_id
                    # market_listing_item_name 可以用中文名称填充
                    sql = f'''INSERT INTO {WeaponClassIDModel.get_table_name()} 
                             ([steam_hash_name], [market_listing_item_name], [csqaq_id]) 
                             VALUES (?, ?, ?)'''
                    
                    affected_rows = db.execute_insert(sql, (market_hash_name, item_name_cn, csqaq_id))
                    
                    if affected_rows > 0:
                        inserted += 1
                        print(f"✅ 新增成功: csqaq_id={csqaq_id}, market_hash_name={market_hash_name}, name={item_name_cn}")
                    else:
                        failed += 1
                    
            except Exception as e:
                failed += 1
                print(f"处理记录失败: {e}, item={item}")
                import traceback
                print(f"错误堆栈: {traceback.format_exc()}")
                continue
        
        success = (updated + inserted) > 0
        message = f"处理完成：总计 {total} 条，更新 {updated} 条，新增 {inserted} 条，失败 {failed} 条"
        
        return {
            'success': success,
            'message': message,
            'total': total,
            'updated': updated,
            'inserted': inserted,
            'failed': failed
        }
        
    except json.JSONDecodeError as e:
        return {
            'success': False,
            'message': f'JSON解析失败: {str(e)}',
            'total': 0,
            'updated': 0,
            'inserted': 0,
            'failed': 0
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'处理失败: {str(e)}',
            'total': 0,
            'updated': 0,
            'inserted': 0,
            'failed': 0
        }
