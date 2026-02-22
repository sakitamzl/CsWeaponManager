# -*- coding: utf-8 -*-
"""
库存挖掘API - 处理挖掘数据的保存和查询
"""

from flask import jsonify, request, Blueprint
from backEnd.src.db_manager.steam.model.user_inventory_mining import UserInventoryMiningModel
from src.db_manager.database import DatabaseManager
from src.log import Log
from datetime import datetime

logger = Log()
inventoryMiningV1 = Blueprint('inventoryMiningV1', __name__)


@inventoryMiningV1.route('/clear', methods=['POST'])
def clear_mining_data():
    """
    清空指定Steam ID的挖掘数据
    
    请求参数:
    {
        "source_steam_id": "源Steam ID"
    }
    """
    try:
        data = request.get_json()
        if not data or 'source_steam_id' not in data:
            return jsonify({
                'success': False,
                'message': '缺少source_steam_id参数'
            }), 400
        
        source_steam_id = data['source_steam_id']
        
        logger.write_log(f"[库存挖掘] 开始清空数据 - Steam ID: {source_steam_id}", 'info')
        
        db = DatabaseManager()
        
        # 先查询要删除的记录数
        count_sql = "SELECT COUNT(*) FROM user_inventory_mining WHERE source_steam_id = ?"
        count_result = db.execute_query(count_sql, (source_steam_id,))
        delete_count = count_result[0][0] if count_result else 0
        
        # 删除数据
        delete_sql = "DELETE FROM user_inventory_mining WHERE source_steam_id = ?"
        affected = db.execute_update(delete_sql, (source_steam_id,))
        
        logger.write_log(f"[库存挖掘] 清空完成 - 删除 {affected} 条记录", 'info')
        
        return jsonify({
            'success': True,
            'message': f'成功清空 {affected} 条记录',
            'data': {
                'deleted_count': affected
            }
        }), 200
        
    except Exception as e:
        import traceback
        error_msg = f'清空挖掘数据失败: {str(e)}'
        logger.write_log(error_msg, 'error')
        logger.write_log(f"详细错误: {traceback.format_exc()}", 'error')
        return jsonify({
            'success': False,
            'message': error_msg
        }), 500


@inventoryMiningV1.route('/batch', methods=['POST'])
def batch_save_mining_data():
    """
    批量保存库存挖掘数据
    
    请求参数:
    {
        "items": [
            {
                "source_steam_id": "源Steam ID",
                "target_steam_id": "目标Steam ID",
                "relationship": "self/friend",
                "persona_name": "用户昵称",
                "avatar_url": "头像URL",
                "profile_url": "个人资料URL",
                "assetid": "资产ID",
                "instanceid": "实例ID",
                "classid": "类ID",
                "item_name": "物品名称",
                "weapon_name": "武器名称",
                "steam_hash_name": "Steam hash name",
                "float_range": "磨损范围",
                "weapon_type": "武器类型",
                "weapon_float": "磨损值",
                "icon_url": "图标URL",
                "market_price": "市场价格",
                "sticker": "印花信息",
                "pendant": "挂件信息",
                "rename": "改名信息",
                "rarity": "稀有度",
                "tradable": 1/0,
                "marketable": 1/0,
                "mining_time": "挖掘时间"
            }
        ]
    }
    """
    try:
        data = request.get_json()
        if not data or 'items' not in data:
            return jsonify({
                'success': False,
                'message': '缺少items参数'
            }), 400
        
        items = data['items']
        if not items:
            return jsonify({
                'success': False,
                'message': '物品列表为空'
            }), 400
        
        logger.write_log(f"[库存挖掘] 开始批量保存数据 - 共 {len(items)} 件物品", 'info')
        
        db = DatabaseManager()
        success_count = 0
        update_count = 0
        insert_count = 0
        fail_count = 0
        failed_items = []
        
        for item in items:
            try:
                source_steam_id = item.get('source_steam_id')
                target_steam_id = item.get('target_steam_id')
                assetid = item.get('assetid')
                steam_hash_name = item.get('steam_hash_name')
                
                if not all([source_steam_id, target_steam_id, assetid]):
                    fail_count += 1
                    failed_items.append({
                        'assetid': assetid,
                        'reason': '缺少必要字段'
                    })
                    continue
                
                # 从 weapon_classID 表中获取价格信息
                market_price = None
                if steam_hash_name:
                    try:
                        price_sql = """
                            SELECT yyyp_Price, buff_Price 
                            FROM weapon_classID 
                            WHERE steam_hash_name = ?
                        """
                        price_result = db.execute_query(price_sql, (steam_hash_name,))
                        if price_result and len(price_result) > 0:
                            yyyp_price = price_result[0][0]
                            buff_price = price_result[0][1]
                            
                            # 优先使用悠悠有品价格，如果没有则使用BUFF价格
                            if yyyp_price and yyyp_price != '0':
                                market_price = yyyp_price
                            elif buff_price and buff_price != '0':
                                market_price = buff_price
                    except Exception as e:
                        logger.write_log(f"[库存挖掘] 获取价格失败 - steam_hash_name: {steam_hash_name}, 错误: {str(e)}", 'warning')
                
                # 如果从weapon_classID获取到了价格，更新item中的market_price
                if market_price:
                    item['market_price'] = market_price
                
                # 检查是否已存在
                check_sql = """
                    SELECT id FROM user_inventory_mining 
                    WHERE source_steam_id = ? AND target_steam_id = ? AND assetid = ?
                """
                existing = db.execute_query(check_sql, (source_steam_id, target_steam_id, assetid))
                
                if existing:
                    # 更新现有记录
                    update_sql = """
                        UPDATE user_inventory_mining SET
                            relationship = ?,
                            persona_name = ?,
                            avatar_url = ?,
                            profile_url = ?,
                            instanceid = ?,
                            classid = ?,
                            item_name = ?,
                            weapon_name = ?,
                            steam_hash_name = ?,
                            float_range = ?,
                            weapon_type = ?,
                            weapon_float = ?,
                            icon_url = ?,
                            market_price = ?,
                            sticker = ?,
                            pendant = ?,
                            rename = ?,
                            rarity = ?,
                            tradable = ?,
                            marketable = ?,
                            mining_time = ?
                        WHERE source_steam_id = ? AND target_steam_id = ? AND assetid = ?
                    """
                    params = (
                        item.get('relationship'),
                        item.get('persona_name'),
                        item.get('avatar_url'),
                        item.get('profile_url'),
                        item.get('instanceid'),
                        item.get('classid'),
                        item.get('item_name'),
                        item.get('weapon_name'),
                        item.get('steam_hash_name'),
                        item.get('float_range'),
                        item.get('weapon_type'),
                        item.get('weapon_float'),
                        item.get('icon_url'),
                        item.get('market_price'),
                        item.get('sticker'),
                        item.get('pendant'),
                        item.get('rename'),
                        item.get('rarity'),
                        item.get('tradable'),
                        item.get('marketable'),
                        item.get('mining_time'),
                        source_steam_id,
                        target_steam_id,
                        assetid
                    )
                    affected = db.execute_update(update_sql, params)
                    if affected > 0:
                        update_count += 1
                        success_count += 1
                else:
                    # 插入新记录
                    insert_sql = """
                        INSERT INTO user_inventory_mining (
                            source_steam_id, target_steam_id, relationship, persona_name,
                            avatar_url, profile_url, assetid, instanceid, classid,
                            item_name, weapon_name, steam_hash_name, float_range,
                            weapon_type, weapon_float, icon_url, market_price,
                            sticker, pendant, rename, rarity, tradable, marketable,
                            mining_time
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    params = (
                        source_steam_id,
                        target_steam_id,
                        item.get('relationship'),
                        item.get('persona_name'),
                        item.get('avatar_url'),
                        item.get('profile_url'),
                        assetid,
                        item.get('instanceid'),
                        item.get('classid'),
                        item.get('item_name'),
                        item.get('weapon_name'),
                        item.get('steam_hash_name'),
                        item.get('float_range'),
                        item.get('weapon_type'),
                        item.get('weapon_float'),
                        item.get('icon_url'),
                        item.get('market_price'),
                        item.get('sticker'),
                        item.get('pendant'),
                        item.get('rename'),
                        item.get('rarity'),
                        item.get('tradable'),
                        item.get('marketable'),
                        item.get('mining_time')
                    )
                    affected = db.execute_update(insert_sql, params)
                    if affected > 0:
                        insert_count += 1
                        success_count += 1
                
            except Exception as e:
                fail_count += 1
                failed_items.append({
                    'assetid': item.get('assetid'),
                    'reason': str(e)
                })
                logger.write_log(f"[库存挖掘] 保存物品失败 - assetid: {item.get('assetid')}, 错误: {str(e)}", 'error')
                continue
        
        logger.write_log(
            f"[库存挖掘] 批量保存完成 - 成功: {success_count} (更新: {update_count}, 新增: {insert_count}), 失败: {fail_count}",
            'info'
        )
        
        return jsonify({
            'success': True,
            'message': f'批量保存完成',
            'data': {
                'success_count': success_count,
                'update_count': update_count,
                'insert_count': insert_count,
                'fail_count': fail_count,
                'total': len(items),
                'failed_items': failed_items[:10]  # 只返回前10个失败项
            }
        }), 200
        
    except Exception as e:
        import traceback
        error_msg = f'批量保存挖掘数据失败: {str(e)}'
        logger.write_log(error_msg, 'error')
        logger.write_log(f"详细错误: {traceback.format_exc()}", 'error')
        return jsonify({
            'success': False,
            'message': error_msg
        }), 500


@inventoryMiningV1.route('/latest', methods=['GET'])
def get_latest_source_steam_id():
    """
    获取最新的挖掘记录的source_steam_id
    """
    try:
        db = DatabaseManager()
        
        # 查询最新的一条记录
        query_sql = """
            SELECT source_steam_id, MAX(mining_time) as latest_time
            FROM user_inventory_mining
            GROUP BY source_steam_id
            ORDER BY latest_time DESC
            LIMIT 1
        """
        
        result = db.execute_query(query_sql)
        
        if result and len(result) > 0:
            return jsonify({
                'success': True,
                'data': {
                    'source_steam_id': result[0][0],
                    'latest_time': result[0][1]
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '没有找到挖掘记录'
            }), 404
            
    except Exception as e:
        import traceback
        error_msg = f'获取最新Steam ID失败: {str(e)}'
        logger.write_log(error_msg, 'error')
        logger.write_log(f"详细错误: {traceback.format_exc()}", 'error')
        return jsonify({
            'success': False,
            'message': error_msg
        }), 500


@inventoryMiningV1.route('/query', methods=['POST'])
def query_mining_data():
    """
    查询库存挖掘数据
    
    请求参数:
    {
        "source_steam_id": "源Steam ID",
        "relationship": "self/friend/all",  // 可选，默认all
        "weapon_type": "武器类型",  // 可选
        "limit": null,  // 可选，不传或null表示获取所有数据
        "offset": 0  // 可选
    }
    """
    try:
        data = request.get_json()
        if not data or 'source_steam_id' not in data:
            return jsonify({
                'success': False,
                'message': '缺少source_steam_id参数'
            }), 400
        
        source_steam_id = data['source_steam_id']
        relationship = data.get('relationship', 'all')
        weapon_type = data.get('weapon_type')
        limit = data.get('limit')  # 不设置默认值，None表示不限制
        offset = data.get('offset', 0)
        
        db = DatabaseManager()
        
        # 构建查询条件
        where_clauses = ['source_steam_id = ?']
        params = [source_steam_id]
        
        if relationship and relationship != 'all':
            where_clauses.append('relationship = ?')
            params.append(relationship)
        
        if weapon_type:
            where_clauses.append('weapon_type = ?')
            params.append(weapon_type)
        
        where_sql = ' AND '.join(where_clauses)
        
        # 查询数据 - 如果没有limit则查询所有数据
        if limit is not None:
            query_sql = f"""
                SELECT * FROM user_inventory_mining
                WHERE {where_sql}
                ORDER BY mining_time DESC
                LIMIT ? OFFSET ?
            """
            params.extend([limit, offset])
        else:
            # 不限制数量，查询所有数据
            query_sql = f"""
                SELECT * FROM user_inventory_mining
                WHERE {where_sql}
                ORDER BY mining_time DESC
            """
            if offset > 0:
                query_sql += f" OFFSET ?"
                params.append(offset)
        
        results = db.execute_query(query_sql, tuple(params))
        
        # 查询总数
        count_params = [p for p in params if p not in [limit, offset]]
        count_sql = f"SELECT COUNT(*) FROM user_inventory_mining WHERE {where_sql}"
        count_result = db.execute_query(count_sql, tuple(count_params))
        total_count = count_result[0][0] if count_result else 0
        
        # 转换为字典列表
        items = []
        if results:
            columns = [
                'id', 'source_steam_id', 'target_steam_id', 'relationship',
                'persona_name', 'avatar_url', 'profile_url', 'assetid',
                'instanceid', 'classid', 'item_name', 'weapon_name',
                'steam_hash_name', 'float_range', 'weapon_type', 'weapon_float',
                'icon_url', 'market_price', 'sticker', 'pendant', 'rename',
                'rarity', 'tradable', 'marketable', 'mining_time', 'created_at'
            ]
            for row in results:
                item = dict(zip(columns, row))
                items.append(item)
        
        return jsonify({
            'success': True,
            'data': {
                'items': items,
                'total': total_count,
                'limit': limit,
                'offset': offset
            }
        }), 200
        
    except Exception as e:
        import traceback
        error_msg = f'查询挖掘数据失败: {str(e)}'
        logger.write_log(error_msg, 'error')
        logger.write_log(f"详细错误: {traceback.format_exc()}", 'error')
        return jsonify({
            'success': False,
            'message': error_msg
        }), 500


@inventoryMiningV1.route('/stats', methods=['POST'])
def get_mining_stats():
    """
    获取挖掘统计信息（包含价值统计）
    
    请求参数:
    {
        "source_steam_id": "源Steam ID"
    }
    """
    try:
        data = request.get_json()
        if not data or 'source_steam_id' not in data:
            return jsonify({
                'success': False,
                'message': '缺少source_steam_id参数'
            }), 400
        
        source_steam_id = data['source_steam_id']
        db = DatabaseManager()
        
        # 总物品数
        total_sql = "SELECT COUNT(*) FROM user_inventory_mining WHERE source_steam_id = ?"
        total_result = db.execute_query(total_sql, (source_steam_id,))
        total_items = total_result[0][0] if total_result else 0
        
        # 自己的物品数
        self_sql = "SELECT COUNT(*) FROM user_inventory_mining WHERE source_steam_id = ? AND relationship = 'self'"
        self_result = db.execute_query(self_sql, (source_steam_id,))
        self_items = self_result[0][0] if self_result else 0
        
        # 好友的物品数
        friends_sql = "SELECT COUNT(*) FROM user_inventory_mining WHERE source_steam_id = ? AND relationship = 'friend'"
        friends_result = db.execute_query(friends_sql, (source_steam_id,))
        friends_items = friends_result[0][0] if friends_result else 0
        
        # 好友数量
        friends_count_sql = """
            SELECT COUNT(DISTINCT target_steam_id) 
            FROM user_inventory_mining 
            WHERE source_steam_id = ? AND relationship = 'friend'
        """
        friends_count_result = db.execute_query(friends_count_sql, (source_steam_id,))
        friends_count = friends_count_result[0][0] if friends_count_result else 0
        
        # 最新挖掘时间
        latest_sql = """
            SELECT mining_time FROM user_inventory_mining 
            WHERE source_steam_id = ? 
            ORDER BY mining_time DESC LIMIT 1
        """
        latest_result = db.execute_query(latest_sql, (source_steam_id,))
        latest_time = latest_result[0][0] if latest_result else None
        
        # 计算总价值（所有有价格的物品）
        total_value_sql = """
            SELECT SUM(CAST(market_price AS REAL))
            FROM user_inventory_mining
            WHERE source_steam_id = ? 
            AND market_price IS NOT NULL 
            AND market_price != '' 
            AND market_price != '0'
        """
        total_value_result = db.execute_query(total_value_sql, (source_steam_id,))
        total_value = round(total_value_result[0][0], 2) if total_value_result and total_value_result[0][0] else 0
        
        # 计算自己的库存价值
        self_value_sql = """
            SELECT SUM(CAST(market_price AS REAL))
            FROM user_inventory_mining
            WHERE source_steam_id = ? 
            AND relationship = 'self'
            AND market_price IS NOT NULL 
            AND market_price != '' 
            AND market_price != '0'
        """
        self_value_result = db.execute_query(self_value_sql, (source_steam_id,))
        self_value = round(self_value_result[0][0], 2) if self_value_result and self_value_result[0][0] else 0
        
        # 计算好友的库存价值
        friends_value_sql = """
            SELECT SUM(CAST(market_price AS REAL))
            FROM user_inventory_mining
            WHERE source_steam_id = ? 
            AND relationship = 'friend'
            AND market_price IS NOT NULL 
            AND market_price != '' 
            AND market_price != '0'
        """
        friends_value_result = db.execute_query(friends_value_sql, (source_steam_id,))
        friends_value = round(friends_value_result[0][0], 2) if friends_value_result and friends_value_result[0][0] else 0
        
        # 按用户统计价值（Top 10）
        user_value_sql = """
            SELECT 
                target_steam_id,
                persona_name,
                relationship,
                COUNT(*) as item_count,
                SUM(CAST(CASE WHEN market_price IS NOT NULL AND market_price != '' AND market_price != '0' 
                    THEN market_price ELSE '0' END AS REAL)) as total_value
            FROM user_inventory_mining
            WHERE source_steam_id = ?
            GROUP BY target_steam_id, persona_name, relationship
            ORDER BY total_value DESC
            LIMIT 10
        """
        user_value_result = db.execute_query(user_value_sql, (source_steam_id,))
        
        top_users = []
        if user_value_result:
            for row in user_value_result:
                top_users.append({
                    'steam_id': row[0],
                    'name': row[1] or f'用户_{row[0][-4:]}',
                    'relationship': row[2],
                    'item_count': row[3],
                    'total_value': round(row[4], 2)
                })
        
        return jsonify({
            'success': True,
            'data': {
                'total_items': total_items,
                'self_items': self_items,
                'friends_items': friends_items,
                'friends_count': friends_count,
                'latest_mining_time': latest_time,
                'total_value': total_value,
                'self_value': self_value,
                'friends_value': friends_value,
                'top_users': top_users
            }
        }), 200
        
    except Exception as e:
        import traceback
        error_msg = f'获取统计信息失败: {str(e)}'
        logger.write_log(error_msg, 'error')
        logger.write_log(f"详细错误: {traceback.format_exc()}", 'error')
        return jsonify({
            'success': False,
            'message': error_msg
        }), 500


@inventoryMiningV1.route('/history', methods=['GET'])
def get_mining_history():
    """
    获取所有挖掘历史记录列表
    
    返回每个source_steam_id的最新挖掘记录
    """
    try:
        db = DatabaseManager()
        
        # 查询所有不同的source_steam_id及其最新挖掘时间和统计信息
        # 同时获取主用户的昵称和头像（从relationship='self'的记录中获取）
        query_sql = """
            SELECT 
                m.source_steam_id,
                MAX(m.mining_time) as latest_time,
                COUNT(*) as total_items,
                SUM(CAST(CASE WHEN m.market_price IS NOT NULL AND m.market_price != '' AND m.market_price != '0' 
                    THEN m.market_price ELSE '0' END AS REAL)) as total_value,
                (SELECT persona_name FROM user_inventory_mining 
                 WHERE source_steam_id = m.source_steam_id AND relationship = 'self' 
                 LIMIT 1) as persona_name,
                (SELECT avatar_url FROM user_inventory_mining 
                 WHERE source_steam_id = m.source_steam_id AND relationship = 'self' 
                 LIMIT 1) as avatar_url
            FROM user_inventory_mining m
            GROUP BY m.source_steam_id
            ORDER BY latest_time DESC
        """
        
        results = db.execute_query(query_sql)
        
        history_list = []
        if results:
            for row in results:
                source_steam_id = row[0]
                persona_name = row[4] if row[4] else source_steam_id
                
                # 如果昵称是默认的"用户_xxxx"格式，使用Steam ID
                if persona_name and persona_name.startswith('用户_'):
                    persona_name = source_steam_id
                
                history_list.append({
                    'source_steam_id': source_steam_id,
                    'persona_name': persona_name,
                    'avatar_url': row[5] if row[5] else '',
                    'latest_time': row[1],
                    'total_items': row[2],
                    'total_value': round(row[3], 2) if row[3] else 0
                })
        
        return jsonify({
            'success': True,
            'data': history_list
        }), 200
        
    except Exception as e:
        import traceback
        error_msg = f'获取历史记录失败: {str(e)}'
        logger.write_log(error_msg, 'error')
        logger.write_log(f"详细错误: {traceback.format_exc()}", 'error')
        return jsonify({
            'success': False,
            'message': error_msg
        }), 500


@inventoryMiningV1.route('/history/<steam_id>', methods=['DELETE'])
def delete_mining_history(steam_id):
    """
    删除指定Steam ID的挖掘历史记录
    
    URL参数:
        steam_id: 要删除的Steam ID
    """
    try:
        if not steam_id:
            return jsonify({
                'success': False,
                'message': '缺少steam_id参数'
            }), 400
        
        logger.write_log(f"[库存挖掘] 开始删除历史记录 - Steam ID: {steam_id}", 'info')
        
        db = DatabaseManager()
        
        # 先查询要删除的记录数
        count_sql = "SELECT COUNT(*) FROM user_inventory_mining WHERE source_steam_id = ?"
        count_result = db.execute_query(count_sql, (steam_id,))
        delete_count = count_result[0][0] if count_result else 0
        
        if delete_count == 0:
            return jsonify({
                'success': False,
                'message': '未找到该Steam ID的历史记录'
            }), 404
        
        # 删除数据
        delete_sql = "DELETE FROM user_inventory_mining WHERE source_steam_id = ?"
        affected = db.execute_update(delete_sql, (steam_id,))
        
        logger.write_log(f"[库存挖掘] 删除历史记录完成 - 删除 {affected} 条记录", 'info')
        
        return jsonify({
            'success': True,
            'message': f'成功删除 {affected} 条记录',
            'data': {
                'deleted_count': affected
            }
        }), 200
        
    except Exception as e:
        import traceback
        error_msg = f'删除历史记录失败: {str(e)}'
        logger.write_log(error_msg, 'error')
        logger.write_log(f"详细错误: {traceback.format_exc()}", 'error')
        return jsonify({
            'success': False,
            'message': error_msg
        }), 500
