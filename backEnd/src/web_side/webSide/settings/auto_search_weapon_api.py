# -*- coding: utf-8 -*-
"""
改名饰品搜索结果API
提供搜索结果的查询、统计、删除等功能
"""
from flask import Blueprint, request, jsonify
from src.log import Log
from src.db_manager.index import AutoSearchWeaponModel
from src.db_manager import get_db_manager

search_rename_bp = Blueprint('search_rename', __name__, url_prefix='/searchRename')

logger = Log()

print("✅ 改名饰品搜索API蓝图已加载")


# ==================== 数据写入 ====================

@search_rename_bp.route('/item/add', methods=['POST'])
def add_item():
    """
    添加单个搜索结果
    """
    try:
        data = request.get_json()
        
        steam_id = data.get('steamId')
        weapon_id = data.get('weaponId')
        weapon_name = data.get('weaponName')
        item_data = data.get('item')
        data_type = data.get('dataType', 'rename')
        pendants = data.get('pendants')
        pendant_count = data.get('pendantCount')
        pendant_total_price = data.get('pendantTotalPrice')
        price_diff_percentage = data.get('priceDiffPercentage')
        
        if not all([steam_id, weapon_id, weapon_name, item_data]):
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400
        
        record = AutoSearchWeaponModel.create_from_search_result(
            steam_id=steam_id,
            weapon_id=weapon_id,
            weapon_name=weapon_name,
            item_data=item_data,
            data_type=data_type,
            pendant_details=pendants,
            pendant_count=pendant_count,
            pendant_total_price=pendant_total_price,
            price_diff_percentage=price_diff_percentage
        )
        
        if record.save():
            logger.write_log(
                f"添加搜索结果: Weapon={weapon_name}, Price={item_data.get('price')}, NameTag={item_data.get('nameTag')}",
                'INFO'
            )
            return jsonify({
                'success': True,
                'itemId': record.id,
                'message': '添加成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '保存失败'
            }), 500
    
    except Exception as e:
        logger.write_log(f"添加搜索结果失败: {str(e)}", 'ERROR')
        import traceback
        logger.write_log(f"详细错误: {traceback.format_exc()}", 'ERROR')
        return jsonify({
            'success': False,
            'message': f'添加失败: {str(e)}'
        }), 500


@search_rename_bp.route('/items/batch', methods=['POST'])
def add_items_batch():
    """
    批量添加搜索结果
    """
    try:
        data = request.get_json()
        
        steam_id = data.get('steamId')
        items = data.get('items', [])
        data_type = data.get('dataType', 'rename')
        
        if not all([steam_id, items]):
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400
        
        success_count = 0
        for item_wrapper in items:
            try:
                record = AutoSearchWeaponModel.create_from_search_result(
                    steam_id=steam_id,
                    weapon_id=item_wrapper.get('weaponId'),
                    weapon_name=item_wrapper.get('weaponName'),
                    item_data=item_wrapper.get('item'),
                    data_type=data_type,
                    pendant_details=item_wrapper.get('pendants'),
                    pendant_count=item_wrapper.get('pendantCount'),
                    pendant_total_price=item_wrapper.get('pendantTotalPrice'),
                    price_diff_percentage=item_wrapper.get('priceDiffPercentage')
                )
                if record.save():
                    success_count += 1
            except Exception as e:
                logger.write_log(f"批量添加单项失败: {str(e)}", 'WARNING')
                continue
        
        logger.write_log(f"批量添加完成: 成功={success_count}/{len(items)}", 'INFO')
        
        return jsonify({
            'success': True,
            'count': success_count,
            'total': len(items),
            'message': f'批量添加完成，成功{success_count}条'
        })
    
    except Exception as e:
        logger.write_log(f"批量添加失败: {str(e)}", 'ERROR')
        return jsonify({
            'success': False,
            'message': f'批量添加失败: {str(e)}'
        }), 500


# ==================== 数据查询 ====================

@search_rename_bp.route('/items/list', methods=['GET'])
def get_items_list():
    """
    获取搜索结果列表（支持轮询）
    
    查询参数:
    - dataType: 数据类型（rename/pendant），默认 rename
    - steamId: 过滤指定 Steam ID 的数据（可选）
    - status: 状态过滤，默认 active
    - limit: 返回数量限制（可选）
    - offset: 偏移量（可选）
    
    返回:
    {
        "success": true,
        "count": 10,
        "items": [...]
    }
    """
    try:
        data_type = request.args.get('dataType', 'rename')
        steam_id = request.args.get('steamId')
        status = request.args.get('status', 'active')
        limit = request.args.get('limit')
        offset = request.args.get('offset')
        
        logger.write_log(f"查询搜索结果 - dataType: {data_type}, steamId: {steam_id}, status: {status}", 'INFO')
        
        where_clause_parts = ["data_type = ?"]
        params = [data_type]
        
        if steam_id:
            where_clause_parts.append("steam_id = ?")
            params.append(steam_id)
        
        if status:
            where_clause_parts.append("status = ?")
            params.append(status)
        
        if data_type == 'rename':
            where_clause_parts.append("name_tag IS NOT NULL")
        
        where_clause = " AND ".join(where_clause_parts) + " ORDER BY spread ASC, id DESC"
        
        list_limit = int(limit) if limit else None
        list_offset = int(offset) if offset else None
        
        model_results = AutoSearchWeaponModel.find_all(where_clause, tuple(params), limit=list_limit, offset=list_offset)
        
        logger.write_log(f"查询结果: {len(model_results) if model_results else 0} 条", 'INFO')
        
        if not model_results:
            logger.write_log("查询结果为空", 'INFO')
            return jsonify({
                'success': True,
                'count': 0,
                'items': []
            })
        
        # 转换为字典列表
        results = [item.to_dict() for item in model_results]
        
        # 输出第一条数据示例
        if results:
            logger.write_log(f"第一条数据示例: weapon_name={results[0].get('weaponName')}, commodity_id={results[0].get('commodityId')}", 'INFO')
        
        logger.write_log(f"查询成功，返回 {len(results)} 条数据", 'INFO')
        
        return jsonify({
            'success': True,
            'count': len(results),
            'items': results
        })
    
    except Exception as e:
        logger.write_log(f"查询搜索结果失败: {str(e)}", 'ERROR')
        import traceback
        logger.write_log(f"详细错误: {traceback.format_exc()}", 'ERROR')
        # 返回200 + 空数组，而不是500错误
        return jsonify({
            'success': True,
            'count': 0,
            'items': [],
            'error': str(e)
        })


@search_rename_bp.route('/items/count', methods=['GET'])
def get_items_count():
    """
    获取搜索结果数量
    
    查询参数:
    - dataType: 数据类型（默认 rename）
    - steamId: Steam ID 过滤（可选）
    - status: 状态过滤，默认 active
    
    返回:
    {
        "success": true,
        "count": 50
    }
    """
    try:
        data_type = request.args.get('dataType', 'rename')
        steam_id = request.args.get('steamId')
        status = request.args.get('status', 'active')
        
        where_clause_parts = ["data_type = ?"]
        params = [data_type]
        
        if steam_id:
            where_clause_parts.append("steam_id = ?")
            params.append(steam_id)
        
        if status:
            where_clause_parts.append("status = ?")
            params.append(status)
        
        if data_type == 'rename':
            where_clause_parts.append("name_tag IS NOT NULL")
        
        count = AutoSearchWeaponModel.count(" AND ".join(where_clause_parts), tuple(params))
        
        return jsonify({
            'success': True,
            'count': count
        })
    
    except Exception as e:
        logger.write_log(f"统计搜索结果失败: {str(e)}", 'ERROR')
        return jsonify({
            'success': False,
            'message': f'统计失败: {str(e)}'
        }), 500


@search_rename_bp.route('/items/latest', methods=['GET'])
def get_latest_items():
    """
    获取最新的搜索结果（用于实时更新）
    
    查询参数:
    - dataType: 数据类型（默认 rename）
    - steamId: Steam ID（可选）
    - limit: 返回数量（可选，默认20）
    - sinceId: 从此ID之后的记录（可选）
    
    返回:
    {
        "success": true,
        "count": 5,
        "items": [...]
    }
    """
    try:
        data_type = request.args.get('dataType', 'rename')
        steam_id = request.args.get('steamId')
        limit = int(request.args.get('limit', 20))
        since_id = request.args.get('sinceId')
        status = request.args.get('status', 'active')
        
        where_clause_parts = ["data_type = ?"]
        params = [data_type]
        
        if steam_id:
            where_clause_parts.append("steam_id = ?")
            params.append(steam_id)
        
        if status:
            where_clause_parts.append("status = ?")
            params.append(status)
        
        if since_id:
            where_clause_parts.append("id > ?")
            params.append(int(since_id))
            order_clause = " ORDER BY id ASC"
        else:
            order_clause = " ORDER BY id DESC"
        
        where_clause = " AND ".join(where_clause_parts) + order_clause
        
        results = AutoSearchWeaponModel.find_all(where_clause, tuple(params), limit=limit)
        
        items = [result.to_dict() for result in results] if results else []
        
        return jsonify({
            'success': True,
            'count': len(items),
            'items': items
        })
    
    except Exception as e:
        logger.write_log(f"获取最新结果失败: {str(e)}", 'ERROR')
        return jsonify({
            'success': False,
            'message': f'获取失败: {str(e)}'
        }), 500


# ==================== 数据管理 ====================

@search_rename_bp.route('/clear', methods=['POST'])
def clear_all_rename_data():
    """
    清空所有改名饰品数据（data_type='rename'）
    
    返回:
    {
        "success": true,
        "count": 100,
        "message": "清空成功，删除了100条记录"
    }
    """
    try:
        from src.execution_db import DatabaseManager
        
        data = request.get_json() or {}
        data_type = data.get('dataType', 'rename')
        
        db = DatabaseManager()
        table_name = AutoSearchWeaponModel.get_table_name()
        
        # 先统计要删除的记录数
        count_sql = f"SELECT COUNT(*) FROM {table_name} WHERE data_type = ?"
        count_result = db.execute_query(count_sql, (data_type,))
        count = count_result[0][0] if count_result else 0
        
        # 删除所有指定 data_type 的数据
        delete_sql = f"DELETE FROM {table_name} WHERE data_type = ?"
        db.execute_update(delete_sql, (data_type,))
        
        logger.write_log(f"清空搜索数据(data_type={data_type}): 删除{count}条记录", 'INFO')
        
        return jsonify({
            'success': True,
            'count': count,
            'message': f'清空成功，删除了{count}条记录'
        })
    
    except Exception as e:
        logger.write_log(f"清空数据失败: {str(e)}", 'ERROR')
        import traceback
        logger.write_log(f"详细错误: {traceback.format_exc()}", 'ERROR')
        return jsonify({
            'success': False,
            'message': f'清空失败: {str(e)}'
        }), 500


@search_rename_bp.route('/cleanup', methods=['POST'])
def cleanup_old_data():
    """
    清理旧数据
    
    请求体:
    {
        "days": 7  // 保留最近N天的数据，默认7天
    }
    
    返回:
    {
        "success": true,
        "count": 100,
        "message": "清理了100条记录"
    }
    """
    try:
        data = request.get_json() or {}
        days = data.get('days', 7)
        
        count = AutoSearchWeaponModel.clear_old_records(days)
        
        logger.write_log(f"清理旧数据: 删除{count}条记录（{days}天前）", 'INFO')
        
        return jsonify({
            'success': True,
            'count': count,
            'message': f'清理了{count}条记录'
        })
    
    except Exception as e:
        logger.write_log(f"清理旧数据失败: {str(e)}", 'ERROR')
        return jsonify({
            'success': False,
            'message': f'清理失败: {str(e)}'
        }), 500


# ==================== 统计信息 ====================

@search_rename_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    获取统计信息，可按 dataType / steamId / status 过滤
    """
    try:
        data_type = request.args.get('dataType')
        steam_id = request.args.get('steamId')
        status = request.args.get('status', 'active')
        
        where_clause_parts = []
        params = []
        
        if status:
            where_clause_parts.append("status = ?")
            params.append(status)
        
        if data_type:
            where_clause_parts.append("data_type = ?")
            params.append(data_type)
        
        if steam_id:
            where_clause_parts.append("steam_id = ?")
            params.append(steam_id)
        
        where_clause = " AND ".join(where_clause_parts)
        params_tuple = tuple(params)
        
        results = AutoSearchWeaponModel.find_all(where_clause, params_tuple) if where_clause else AutoSearchWeaponModel.find_all()
        
        if not results:
            return jsonify({
                'success': True,
                'stats': {
                    'totalItems': 0,
                    'totalWeapons': 0,
                    'avgPrice': 0,
                    'avgSpread': 0,
                    'avgProfit': 0,
                    'totalProfit': 0
                }
            })
        
        weapon_ids = set()
        total_price = 0
        total_spread = 0
        total_profit = 0
        rename_items = 0
        pendant_items = 0
        
        for result in results:
            weapon_ids.add(result.weapon_id)
            total_price += result.price or 0
            total_spread += result.spread or 0
            if result.price_diff:
                total_profit += result.price_diff
            if result.data_type == 'rename':
                rename_items += 1
            elif result.data_type == 'pendant':
                pendant_items += 1
        
        count = len(results)
        
        return jsonify({
            'success': True,
            'stats': {
                'totalItems': count,
                'totalWeapons': len(weapon_ids),
                'avgPrice': round(total_price / count, 2) if count else 0,
                'avgSpread': round(total_spread / count, 2) if count else 0,
                'avgProfit': round(total_profit / count, 2) if count else 0,
                'totalProfit': round(total_profit, 2),
                'renameItems': rename_items,
                'pendantItems': pendant_items
            }
        })
    
    except Exception as e:
        logger.write_log(f"获取统计信息失败: {str(e)}", 'ERROR')
        return jsonify({
            'success': False,
            'message': f'获取统计失败: {str(e)}'
        }), 500
