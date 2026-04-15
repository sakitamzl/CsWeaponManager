# -*- coding: utf-8 -*-
"""
Steam mining 处理模块
提供 Spider 所需的库存挖掘数据保存、查询、统计与历史管理接口
逻辑完整迁移自 web_side/steam/inventory_mining.py
"""
import traceback
from datetime import datetime
from flask import jsonify, request
from src.db_manager.steam.model.user_inventory_mining import UserInventoryMiningModel
from src.db_manager.database import DatabaseManager
from src.units.log import Log

logger = Log()


class MiningHandler:

    @staticmethod
    def clear():
        """清空指定 Steam ID 的挖掘数据"""
        try:
            data = request.get_json()
            if not data or 'source_steam_id' not in data:
                return jsonify({'success': False, 'message': '缺少source_steam_id参数'}), 400

            source_steam_id = data['source_steam_id']
            logger.write_log(f"[库存挖掘] 开始清空数据 - Steam ID: {source_steam_id}", 'info')

            db = DatabaseManager()
            affected = db.execute_update(
                "DELETE FROM user_inventory_mining WHERE source_steam_id = ?",
                (source_steam_id,)
            )
            logger.write_log(f"[库存挖掘] 清空完成 - 删除 {affected} 条记录", 'info')
            return jsonify({'success': True, 'message': f'成功清空 {affected} 条记录', 'data': {'deleted_count': affected}}), 200

        except Exception as e:
            error_msg = f'清空挖掘数据失败: {str(e)}'
            logger.write_log(error_msg, 'error')
            logger.write_log(f"详细错误: {traceback.format_exc()}", 'error')
            return jsonify({'success': False, 'message': error_msg}), 500

    @staticmethod
    def batch():
        """批量保存库存挖掘数据"""
        try:
            data = request.get_json()
            if not data or 'items' not in data:
                return jsonify({'success': False, 'message': '缺少items参数'}), 400

            items = data['items']
            if not items:
                return jsonify({'success': False, 'message': '物品列表为空'}), 400

            logger.write_log(f"[库存挖掘] 开始批量保存数据 - 共 {len(items)} 件物品", 'info')

            db = DatabaseManager()
            success_count = update_count = insert_count = fail_count = 0
            failed_items = []

            for item in items:
                try:
                    source_steam_id = item.get('source_steam_id')
                    target_steam_id = item.get('target_steam_id')
                    assetid = item.get('assetid')
                    steam_hash_name = item.get('steam_hash_name')

                    if not all([source_steam_id, target_steam_id, assetid]):
                        fail_count += 1
                        failed_items.append({'assetid': assetid, 'reason': '缺少必要字段'})
                        continue

                    # 从 weapon_classID 表获取价格
                    market_price = None
                    if steam_hash_name:
                        try:
                            price_result = db.execute_query(
                                "SELECT yyyp_Price, buff_Price FROM weapon_classID WHERE steam_hash_name = ?",
                                (steam_hash_name,)
                            )
                            if price_result:
                                yyyp_price = price_result[0][0]
                                buff_price = price_result[0][1]
                                if yyyp_price and yyyp_price != '0':
                                    market_price = yyyp_price
                                elif buff_price and buff_price != '0':
                                    market_price = buff_price
                        except Exception as e:
                            logger.write_log(f"[库存挖掘] 获取价格失败 - {steam_hash_name}: {str(e)}", 'warning')

                    if market_price:
                        item['market_price'] = market_price

                    # 检查是否已存在
                    existing = db.execute_query(
                        "SELECT id FROM user_inventory_mining WHERE source_steam_id = ? AND target_steam_id = ? AND assetid = ?",
                        (source_steam_id, target_steam_id, assetid)
                    )

                    common_fields = (
                        item.get('relationship'), item.get('persona_name'), item.get('avatar_url'),
                        item.get('profile_url'), item.get('instanceid'), item.get('classid'),
                        item.get('item_name'), item.get('weapon_name'), item.get('steam_hash_name'),
                        item.get('float_range'), item.get('weapon_type'), item.get('weapon_float'),
                        item.get('icon_url'), item.get('market_price'), item.get('sticker'),
                        item.get('pendant'), item.get('rename'), item.get('rarity'),
                        item.get('tradable'), item.get('marketable'), item.get('mining_time'),
                    )

                    if existing:
                        affected = db.execute_update(
                            """UPDATE user_inventory_mining SET
                                relationship=?, persona_name=?, avatar_url=?, profile_url=?,
                                instanceid=?, classid=?, item_name=?, weapon_name=?,
                                steam_hash_name=?, float_range=?, weapon_type=?, weapon_float=?,
                                icon_url=?, market_price=?, sticker=?, pendant=?, rename=?,
                                rarity=?, tradable=?, marketable=?, mining_time=?
                               WHERE source_steam_id=? AND target_steam_id=? AND assetid=?""",
                            common_fields + (source_steam_id, target_steam_id, assetid)
                        )
                        if affected > 0:
                            update_count += 1
                            success_count += 1
                    else:
                        affected = db.execute_update(
                            """INSERT INTO user_inventory_mining (
                                source_steam_id, target_steam_id, relationship, persona_name,
                                avatar_url, profile_url, assetid, instanceid, classid,
                                item_name, weapon_name, steam_hash_name, float_range,
                                weapon_type, weapon_float, icon_url, market_price,
                                sticker, pendant, rename, rarity, tradable, marketable, mining_time
                               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            (source_steam_id, target_steam_id) + common_fields[:5] + (assetid,) + common_fields[5:]
                        )
                        if affected > 0:
                            insert_count += 1
                            success_count += 1

                except Exception as e:
                    fail_count += 1
                    failed_items.append({'assetid': item.get('assetid'), 'reason': str(e)})
                    logger.write_log(f"[库存挖掘] 保存物品失败 - {item.get('assetid')}: {str(e)}", 'error')

            logger.write_log(
                f"[库存挖掘] 批量保存完成 - 成功: {success_count} (更新: {update_count}, 新增: {insert_count}), 失败: {fail_count}",
                'info'
            )
            return jsonify({'success': True, 'message': '批量保存完成', 'data': {'success_count': success_count, 'update_count': update_count, 'insert_count': insert_count, 'fail_count': fail_count, 'total': len(items), 'failed_items': failed_items[:10]}}), 200

        except Exception as e:
            error_msg = f'批量保存挖掘数据失败: {str(e)}'
            logger.write_log(error_msg, 'error')
            logger.write_log(f"详细错误: {traceback.format_exc()}", 'error')
            return jsonify({'success': False, 'message': error_msg}), 500

    @staticmethod
    def latest():
        """获取最新挖掘记录的 source_steam_id"""
        try:
            db = DatabaseManager()
            result = db.execute_query(
                "SELECT source_steam_id, MAX(mining_time) as latest_time FROM user_inventory_mining GROUP BY source_steam_id ORDER BY latest_time DESC LIMIT 1",
                (),
            )
            if result:
                return jsonify({'success': True, 'data': {'source_steam_id': result[0][0], 'latest_time': result[0][1]}}), 200
            return jsonify({'success': False, 'message': '没有找到挖掘记录'}), 404
        except Exception as e:
            error_msg = f'获取最新Steam ID失败: {str(e)}'
            logger.write_log(error_msg, 'error')
            logger.write_log(f"详细错误: {traceback.format_exc()}", 'error')
            return jsonify({'success': False, 'message': error_msg}), 500

    @staticmethod
    def query():
        """查询库存挖掘数据"""
        try:
            data = request.get_json()
            if not data or 'source_steam_id' not in data:
                return jsonify({'success': False, 'message': '缺少source_steam_id参数'}), 400

            source_steam_id = data['source_steam_id']
            relationship = data.get('relationship', 'all')
            weapon_type = data.get('weapon_type')
            limit = data.get('limit')
            offset = data.get('offset', 0)

            db = DatabaseManager()
            where_clauses = ['source_steam_id = ?']
            params = [source_steam_id]

            if relationship and relationship != 'all':
                where_clauses.append('relationship = ?')
                params.append(relationship)
            if weapon_type:
                where_clauses.append('weapon_type = ?')
                params.append(weapon_type)

            where_sql = ' AND '.join(where_clauses)

            if limit is not None:
                query_sql = f"SELECT * FROM user_inventory_mining WHERE {where_sql} ORDER BY mining_time DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
            else:
                query_sql = f"SELECT * FROM user_inventory_mining WHERE {where_sql} ORDER BY mining_time DESC"
                if offset > 0:
                    query_sql += " OFFSET ?"
                    params.append(offset)

            results = db.execute_query(query_sql, tuple(params))

            count_result = db.execute_query(
                f"SELECT COUNT(*) FROM user_inventory_mining WHERE {where_sql}",
                tuple(params[: len(where_clauses)]),
            )
            total_count = count_result[0][0] if count_result else 0

            columns = ['id', 'source_steam_id', 'target_steam_id', 'relationship', 'persona_name', 'avatar_url', 'profile_url', 'assetid', 'instanceid', 'classid', 'item_name', 'weapon_name', 'steam_hash_name', 'float_range', 'weapon_type', 'weapon_float', 'icon_url', 'market_price', 'sticker', 'pendant', 'rename', 'rarity', 'tradable', 'marketable', 'mining_time', 'created_at']
            items = [dict(zip(columns, row)) for row in results] if results else []

            return jsonify({'success': True, 'data': {'items': items, 'total': total_count, 'limit': limit, 'offset': offset}}), 200

        except Exception as e:
            error_msg = f'查询挖掘数据失败: {str(e)}'
            logger.write_log(error_msg, 'error')
            logger.write_log(f"详细错误: {traceback.format_exc()}", 'error')
            return jsonify({'success': False, 'message': error_msg}), 500

    @staticmethod
    def stats():
        """获取挖掘统计信息（含价值统计）"""
        try:
            data = request.get_json()
            if not data or 'source_steam_id' not in data:
                return jsonify({'success': False, 'message': '缺少source_steam_id参数'}), 400

            source_steam_id = data['source_steam_id']
            db = DatabaseManager()

            def _q(sql, params=()):
                r = db.execute_query(sql, params)
                return r[0][0] if r else 0

            total_items = _q("SELECT COUNT(*) FROM user_inventory_mining WHERE source_steam_id = ?", (source_steam_id,))
            self_items = _q("SELECT COUNT(*) FROM user_inventory_mining WHERE source_steam_id = ? AND relationship = 'self'", (source_steam_id,))
            friends_items = _q("SELECT COUNT(*) FROM user_inventory_mining WHERE source_steam_id = ? AND relationship = 'friend'", (source_steam_id,))
            friends_count = _q("SELECT COUNT(DISTINCT target_steam_id) FROM user_inventory_mining WHERE source_steam_id = ? AND relationship = 'friend'", (source_steam_id,))
            latest_r = db.execute_query("SELECT mining_time FROM user_inventory_mining WHERE source_steam_id = ? ORDER BY mining_time DESC LIMIT 1", (source_steam_id,))
            latest_time = latest_r[0][0] if latest_r else None

            value_base = (
                "SELECT SUM(CAST(market_price AS REAL)) FROM user_inventory_mining "
                "WHERE source_steam_id = ? AND market_price IS NOT NULL AND market_price != '' AND market_price != '0'"
            )
            total_value_r = db.execute_query(value_base, (source_steam_id,))
            total_value = round(total_value_r[0][0], 2) if total_value_r and total_value_r[0][0] else 0

            self_value_r = db.execute_query(
                value_base + " AND relationship = 'self'",
                (source_steam_id,),
            )
            self_value = round(self_value_r[0][0], 2) if self_value_r and self_value_r[0][0] else 0

            friends_value_r = db.execute_query(
                value_base + " AND relationship = 'friend'",
                (source_steam_id,),
            )
            friends_value = round(friends_value_r[0][0], 2) if friends_value_r and friends_value_r[0][0] else 0

            user_value_result = db.execute_query(
                """SELECT target_steam_id, persona_name, relationship, COUNT(*) as item_count,
                          SUM(CAST(CASE WHEN market_price IS NOT NULL AND market_price != '' AND market_price != '0'
                              THEN market_price ELSE '0' END AS REAL)) as total_value
                   FROM user_inventory_mining WHERE source_steam_id = ?
                   GROUP BY target_steam_id, persona_name, relationship
                   ORDER BY total_value DESC LIMIT 10""",
                (source_steam_id,)
            )
            top_users = [{'steam_id': r[0], 'name': r[1] or f'用户_{r[0][-4:]}', 'relationship': r[2], 'item_count': r[3], 'total_value': round(r[4], 2)} for r in user_value_result] if user_value_result else []

            return jsonify({'success': True, 'data': {'total_items': total_items, 'self_items': self_items, 'friends_items': friends_items, 'friends_count': friends_count, 'latest_mining_time': latest_time, 'total_value': total_value, 'self_value': self_value, 'friends_value': friends_value, 'top_users': top_users}}), 200

        except Exception as e:
            error_msg = f'获取统计信息失败: {str(e)}'
            logger.write_log(error_msg, 'error')
            logger.write_log(f"详细错误: {traceback.format_exc()}", 'error')
            return jsonify({'success': False, 'message': error_msg}), 500

    @staticmethod
    def history():
        """获取所有挖掘历史记录列表"""
        try:
            db = DatabaseManager()
            results = db.execute_query(
                """SELECT m.source_steam_id, MAX(m.mining_time) as latest_time, COUNT(*) as total_items,
                          SUM(CAST(CASE WHEN m.market_price IS NOT NULL AND m.market_price != '' AND m.market_price != '0'
                              THEN m.market_price ELSE '0' END AS REAL)) as total_value,
                          (SELECT persona_name FROM user_inventory_mining WHERE source_steam_id = m.source_steam_id AND relationship = 'self' LIMIT 1) as persona_name,
                          (SELECT avatar_url FROM user_inventory_mining WHERE source_steam_id = m.source_steam_id AND relationship = 'self' LIMIT 1) as avatar_url
                   FROM user_inventory_mining m
                   GROUP BY m.source_steam_id ORDER BY latest_time DESC"""
            )
            history_list = []
            if results:
                for row in results:
                    source_steam_id = row[0]
                    persona_name = row[4] if row[4] else source_steam_id
                    if persona_name and persona_name.startswith('用户_'):
                        persona_name = source_steam_id
                    history_list.append({'source_steam_id': source_steam_id, 'persona_name': persona_name, 'avatar_url': row[5] or '', 'latest_time': row[1], 'total_items': row[2], 'total_value': round(row[3], 2) if row[3] else 0})
            return jsonify({'success': True, 'data': history_list}), 200

        except Exception as e:
            error_msg = f'获取历史记录失败: {str(e)}'
            logger.write_log(error_msg, 'error')
            logger.write_log(f"详细错误: {traceback.format_exc()}", 'error')
            return jsonify({'success': False, 'message': error_msg}), 500

    @staticmethod
    def delete_history(steam_id):
        """删除指定 Steam ID 的挖掘历史记录"""
        try:
            if not steam_id:
                return jsonify({'success': False, 'message': '缺少steam_id参数'}), 400

            logger.write_log(f"[库存挖掘] 开始删除历史记录 - Steam ID: {steam_id}", 'info')
            db = DatabaseManager()

            count_result = db.execute_query("SELECT COUNT(*) FROM user_inventory_mining WHERE source_steam_id = ?", (steam_id,))
            delete_count = count_result[0][0] if count_result else 0

            if delete_count == 0:
                return jsonify({'success': False, 'message': '未找到该Steam ID的历史记录'}), 404

            affected = db.execute_update("DELETE FROM user_inventory_mining WHERE source_steam_id = ?", (steam_id,))
            logger.write_log(f"[库存挖掘] 删除历史记录完成 - 删除 {affected} 条记录", 'info')
            return jsonify({'success': True, 'message': f'成功删除 {affected} 条记录', 'data': {'deleted_count': affected}}), 200

        except Exception as e:
            error_msg = f'删除历史记录失败: {str(e)}'
            logger.write_log(error_msg, 'error')
            logger.write_log(f"详细错误: {traceback.format_exc()}", 'error')
            return jsonify({'success': False, 'message': error_msg}), 500
