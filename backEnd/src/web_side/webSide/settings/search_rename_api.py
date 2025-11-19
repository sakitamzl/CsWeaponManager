# -*- coding: utf-8 -*-
"""
改名饰品搜索结果API
提供搜索结果的查询、统计、删除等功能
"""
from flask import Blueprint, request, jsonify
from src.log import Log
from src.db_manager.index import SearchRenameResultModel
from src.db_manager import get_db_manager
from datetime import datetime
import uuid

search_rename_bp = Blueprint('search_rename', __name__, url_prefix='/searchRename')

logger = Log()

print("✅ 改名饰品搜索API蓝图已加载")


# ==================== 会话管理 ====================

@search_rename_bp.route('/session/create', methods=['POST'])
def create_session():
    """
    创建新的搜索会话
    
    请求体:
    {
        "steamId": "76561199136814432"
    }
    
    返回:
    {
        "success": true,
        "sessionId": "uuid-xxx",
        "message": "会话创建成功"
    }
    """
    try:
        data = request.get_json()
        steam_id = data.get('steamId', '')
        data_type = data.get('dataType', 'rename')
        
        # 生成新的会话ID
        session_id = str(uuid.uuid4())
        
        logger.write_log(f"创建搜索会话: {session_id}, Steam ID: {steam_id}, dataType: {data_type}", 'INFO')
        
        return jsonify({
            'success': True,
            'sessionId': session_id,
            'dataType': data_type,
            'steamId': steam_id,
            'message': '会话创建成功'
        })
    
    except Exception as e:
        logger.write_log(f"创建会话失败: {str(e)}", 'ERROR')
        return jsonify({
            'success': False,
            'message': f'创建会话失败: {str(e)}'
        }), 500


# ==================== 数据写入 ====================

@search_rename_bp.route('/item/add', methods=['POST'])
def add_item():
    """
    添加单个搜索结果
    
    请求体:
    {
        "sessionId": "uuid-xxx",
        "steamId": "76561199136814432",
        "weaponId": "53597",
        "weaponName": "沙漠之鹰 | 后发制人 (崭新出厂)",
        "item": {
            "id": "1729655184",
            "commodityNo": "xxx",
            "price": 32.50,
            "lowest_price": 29.89,
            "spread": 2.61,
            "abrade": "0.0123",
            "paintSeed": "123",
            "nameTag": "改名内容",
            "userNickName": "卖家昵称",
            "assetId": "xxx",
            "iconUrl": "https://..."
        }
    }
    
    返回:
    {
        "success": true,
        "itemId": 123,
        "message": "添加成功"
    }
    """
    try:
        data = request.get_json()
        
        steam_id = data.get('steamId')
        weapon_id = data.get('weaponId')
        weapon_name = data.get('weaponName')
        item_data = data.get('item')
        session_id = data.get('sessionId')
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
        
        # 创建记录
        record = SearchRenameResultModel.create_from_search_result(
            steam_id=steam_id,
            weapon_id=weapon_id,
            weapon_name=weapon_name,
            item_data=item_data,
            data_type=data_type,
            session_id=session_id,
            pendant_details=pendants,
            pendant_count=pendant_count,
            pendant_total_price=pendant_total_price,
            price_diff_percentage=price_diff_percentage
        )
        
        # 保存到数据库
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
    
    请求体:
    {
        "sessionId": "uuid-xxx",
        "steamId": "76561199136814432",
        "items": [
            {
                "weaponId": "53597",
                "weaponName": "沙漠之鹰 | 后发制人",
                "item": {...}
            },
            ...
        ]
    }
    
    返回:
    {
        "success": true,
        "count": 10,
        "message": "批量添加成功"
    }
    """
    try:
        data = request.get_json()
        
        steam_id = data.get('steamId')
        items = data.get('items', [])
        session_id = data.get('sessionId')
        data_type = data.get('dataType', 'rename')
        
        if not all([steam_id, items]):
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400
        
        success_count = 0
        for item_wrapper in items:
            try:
                record = SearchRenameResultModel.create_from_search_result(
                    steam_id=steam_id,
                    weapon_id=item_wrapper.get('weaponId'),
                    weapon_name=item_wrapper.get('weaponName'),
                    item_data=item_wrapper.get('item'),
                    data_type=data_type,
                    session_id=session_id,
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
    - sessionId: 会话ID（可选，不提供则返回最近的所有结果）
    - limit: 返回数量限制（可选，默认100）
    - offset: 偏移量（可选，默认0）
    - hours: 查询最近几小时的数据（可选，默认24小时，仅在无sessionId时有效）
    
    返回:
    {
        "success": true,
        "sessionId": "uuid-xxx",
        "total": 50,
        "count": 10,
        "items": [...]
    }
    """
    try:
        session_id = request.args.get('sessionId')
        data_type = request.args.get('dataType', 'rename')
        
        logger.write_log(f"查询搜索结果 - sessionId: {session_id}, dataType: {data_type}", 'INFO')
        
        # 使用模型对象查询，确保字段映射正确
        where_clause = ""
        params = []
        if session_id:
            where_clause = "session_id = ? AND data_type = ?"
            params = (session_id, data_type)
        else:
            where_clause = "data_type = ?"
            params = (data_type,)
        
        if data_type == 'rename':
            where_clause += " AND name_tag IS NOT NULL"
        
        where_clause += " ORDER BY id DESC"
        
        model_results = SearchRenameResultModel.find_all(where_clause, params)
        
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
    - sessionId: 会话ID（必填）
    
    返回:
    {
        "success": true,
        "sessionId": "uuid-xxx",
        "count": 50
    }
    """
    try:
        session_id = request.args.get('sessionId')
        
        if not session_id:
            return jsonify({
                'success': False,
                'message': '缺少sessionId参数'
            }), 400
        
        count = SearchRenameResultModel.count_by_session(session_id)
        
        return jsonify({
            'success': True,
            'sessionId': session_id,
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
    - sessionId: 会话ID（必填）
    - limit: 返回数量（可选，默认20）
    - sinceId: 从此ID之后的记录（可选）
    
    返回:
    {
        "success": true,
        "sessionId": "uuid-xxx",
        "count": 5,
        "items": [...]
    }
    """
    try:
        session_id = request.args.get('sessionId')
        limit = int(request.args.get('limit', 20))
        since_id = request.args.get('sinceId')
        
        if not session_id:
            return jsonify({
                'success': False,
                'message': '缺少sessionId参数'
            }), 400
        
        if since_id:
            # 查询指定ID之后的记录
            results = SearchRenameResultModel.find_all(
                "session_id = ? AND id > ? AND status = 'active' ORDER BY id ASC LIMIT ?",
                (session_id, int(since_id), limit)
            )
        else:
            # 查询最新的N条记录
            results = SearchRenameResultModel.get_latest_by_session(session_id, limit)
        
        items = [result.to_dict() for result in results] if results else []
        
        return jsonify({
            'success': True,
            'sessionId': session_id,
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
        table_name = SearchRenameResultModel.get_table_name()
        
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
        
        count = SearchRenameResultModel.clear_old_sessions(days)
        
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
    获取统计信息
    
    查询参数:
    - sessionId: 会话ID（可选，不提供则返回全部统计）
    
    返回:
    {
        "success": true,
        "stats": {
            "totalItems": 500,
            "totalSessions": 10,
            "avgItemsPerSession": 50,
            ...
        }
    }
    """
    try:
        session_id = request.args.get('sessionId')
        
        if session_id:
            # 单个会话统计
            results = SearchRenameResultModel.find_by_session(session_id)
            
            if not results:
                return jsonify({
                    'success': True,
                    'sessionId': session_id,
                    'stats': {
                        'totalItems': 0,
                        'totalWeapons': 0,
                        'avgPrice': 0,
                        'avgSpread': 0,
                        'avgProfit': 0
                    }
                })
            
            # 计算统计数据
            weapon_ids = set()
            total_price = 0
            total_spread = 0
            total_profit = 0
            
            for result in results:
                weapon_ids.add(result.weapon_id)
                total_price += result.price
                total_spread += result.spread
                if result.price_diff:
                    total_profit += result.price_diff
            
            count = len(results)
            
            return jsonify({
                'success': True,
                'sessionId': session_id,
                'stats': {
                    'totalItems': count,
                    'totalWeapons': len(weapon_ids),
                    'avgPrice': round(total_price / count, 2) if count > 0 else 0,
                    'avgSpread': round(total_spread / count, 2) if count > 0 else 0,
                    'avgProfit': round(total_profit / count, 2) if count > 0 else 0,
                    'totalProfit': round(total_profit, 2)
                }
            })
        else:
            # 全局统计
            all_results = SearchRenameResultModel.find_all("status = 'active'")
            
            if not all_results:
                return jsonify({
                    'success': True,
                    'stats': {
                        'totalItems': 0,
                        'totalSessions': 0
                    }
                })
            
            sessions = set()
            for result in all_results:
                sessions.add(result.session_id)
            
            return jsonify({
                'success': True,
                'stats': {
                    'totalItems': len(all_results),
                    'totalSessions': len(sessions),
                    'avgItemsPerSession': round(len(all_results) / len(sessions), 2) if len(sessions) > 0 else 0
                }
            })
    
    except Exception as e:
        logger.write_log(f"获取统计信息失败: {str(e)}", 'ERROR')
        return jsonify({
            'success': False,
            'message': f'获取统计失败: {str(e)}'
        }), 500
