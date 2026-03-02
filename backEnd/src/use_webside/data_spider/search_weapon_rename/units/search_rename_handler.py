# -*- coding: utf-8 -*-
"""
改名饰品搜索结果 Handler
对应前端页面：SearchWeaponRename
"""
from flask import request, jsonify
from src.units.log import Log
from src.db_manager.index.model import AutoSearchWeaponModel
from src.db_manager import get_db_manager

logger = Log()


class SearchRenameHandler:

    @staticmethod
    def add_item():
        """添加单个搜索结果"""
        try:
            data = request.get_json()
            steam_id = data.get('steamId')
            weapon_id = data.get('weaponId')
            weapon_name = data.get('weaponName')
            item_data = data.get('item')
            data_type = data.get('dataType', 'rename')
            config_id = data.get('configId')
            pendants = data.get('pendants')
            pendant_count = data.get('pendantCount')
            pendant_total_price = data.get('pendantTotalPrice')
            price_diff_percentage = data.get('priceDiffPercentage')
            total_count = data.get('totalCount')

            if not all([steam_id, weapon_id, weapon_name, item_data]):
                return jsonify({'success': False, 'message': '缺少必要参数'}), 400

            config_id_int = None
            if config_id is not None:
                try:
                    config_id_int = int(config_id)
                except (ValueError, TypeError):
                    config_id_int = None

            record = AutoSearchWeaponModel.create_from_search_result(
                steam_id=steam_id,
                weapon_id=weapon_id,
                weapon_name=weapon_name,
                item_data=item_data,
                data_type=data_type,
                config_id=config_id_int,
                pendant_details=pendants,
                pendant_count=pendant_count,
                pendant_total_price=pendant_total_price,
                price_diff_percentage=price_diff_percentage,
                total_count=total_count
            )

            if record.save():
                logger.write_log(
                    f"添加搜索结果: Weapon={weapon_name}, Price={item_data.get('price')}, NameTag={item_data.get('nameTag')}",
                    'INFO'
                )
                return jsonify({'success': True, 'itemId': record.id, 'message': '添加成功'})
            return jsonify({'success': False, 'message': '保存失败'}), 500

        except Exception as e:
            logger.write_log(f"添加搜索结果失败: {str(e)}", 'ERROR')
            import traceback
            logger.write_log(f"详细错误: {traceback.format_exc()}", 'ERROR')
            return jsonify({'success': False, 'message': f'添加失败: {str(e)}'}), 500

    @staticmethod
    def get_item(item_id):
        """根据ID获取单个商品信息"""
        try:
            records = AutoSearchWeaponModel.find_all("id = ?", (item_id,), limit=1)
            if not records:
                return jsonify({'success': False, 'message': f'未找到ID为 {item_id} 的商品'}), 404
            return jsonify({'success': True, 'data': records[0].to_dict()})
        except Exception as e:
            logger.write_log(f"获取商品信息失败: {str(e)}", 'ERROR')
            return jsonify({'success': False, 'message': f'获取商品信息失败: {str(e)}'}), 500

    @staticmethod
    def update_item_status():
        """更新商品状态"""
        try:
            data = request.get_json()
            commodity_id = data.get('commodityId')
            new_status = data.get('status')

            if not commodity_id or not new_status:
                return jsonify({'success': False, 'message': '缺少必要参数：commodityId 和 status'}), 400

            records = AutoSearchWeaponModel.find_all(
                "commodity_id = ? AND status = 'active'", (str(commodity_id),)
            )
            if not records:
                return jsonify({'success': False, 'message': '未找到对应的商品记录'}), 404

            updated_count = 0
            from datetime import datetime
            for record in records:
                record.status = new_status
                record.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if record.save():
                    updated_count += 1

            if updated_count > 0:
                return jsonify({'success': True, 'message': f'状态更新成功，更新了{updated_count}条记录'})
            return jsonify({'success': False, 'message': '状态更新失败'}), 500

        except Exception as e:
            logger.write_log(f"更新商品状态失败: {str(e)}", 'ERROR')
            return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

    @staticmethod
    def add_items_batch():
        """批量添加搜索结果"""
        try:
            data = request.get_json()
            steam_id = data.get('steamId')
            items = data.get('items', [])
            data_type = data.get('dataType', 'rename')
            config_id = data.get('configId')

            if not all([steam_id, items]):
                return jsonify({'success': False, 'message': '缺少必要参数'}), 400

            config_id_int = None
            if config_id is not None:
                try:
                    config_id_int = int(config_id)
                except (ValueError, TypeError):
                    config_id_int = None

            success_count = 0
            for item_wrapper in items:
                try:
                    record = AutoSearchWeaponModel.create_from_search_result(
                        steam_id=steam_id,
                        weapon_id=item_wrapper.get('weaponId'),
                        weapon_name=item_wrapper.get('weaponName'),
                        item_data=item_wrapper.get('item'),
                        data_type=data_type,
                        config_id=config_id_int,
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

            return jsonify({
                'success': True,
                'count': success_count,
                'total': len(items),
                'message': f'批量添加完成，成功{success_count}条'
            })

        except Exception as e:
            logger.write_log(f"批量添加失败: {str(e)}", 'ERROR')
            return jsonify({'success': False, 'message': f'批量添加失败: {str(e)}'}), 500

    @staticmethod
    def get_items_list():
        """获取搜索结果列表（支持轮询）"""
        try:
            data_type = request.args.get('dataType', 'rename')
            steam_id = request.args.get('steamId')
            config_id = request.args.get('configId')
            status = request.args.get('status', 'active')
            limit = request.args.get('limit')
            offset = request.args.get('offset')

            where_clause_parts = ["data_type = ?"]
            params = [data_type]

            if steam_id:
                where_clause_parts.append("steam_id = ?")
                params.append(steam_id)

            if config_id:
                try:
                    where_clause_parts.append("config_id = ?")
                    params.append(int(config_id))
                except (ValueError, TypeError):
                    pass

            if status:
                where_clause_parts.append("status = ?")
                params.append(status)

            if data_type == 'rename':
                where_clause_parts.append("name_tag IS NOT NULL")

            where_clause = " AND ".join(where_clause_parts) + " ORDER BY spread ASC, id DESC"
            list_limit = int(limit) if limit else None
            list_offset = int(offset) if offset else None

            model_results = AutoSearchWeaponModel.find_all(where_clause, tuple(params), limit=list_limit, offset=list_offset)

            results = [item.to_dict() for item in model_results] if model_results else []
            return jsonify({'success': True, 'count': len(results), 'items': results})

        except Exception as e:
            logger.write_log(f"查询搜索结果失败: {str(e)}", 'ERROR')
            return jsonify({'success': True, 'count': 0, 'items': [], 'error': str(e)})

    @staticmethod
    def get_items_count():
        """获取搜索结果数量"""
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
            return jsonify({'success': True, 'count': count})

        except Exception as e:
            logger.write_log(f"统计搜索结果失败: {str(e)}", 'ERROR')
            return jsonify({'success': False, 'message': f'统计失败: {str(e)}'}), 500

    @staticmethod
    def get_latest_items():
        """获取最新的搜索结果"""
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
            items = [r.to_dict() for r in results] if results else []

            return jsonify({'success': True, 'count': len(items), 'items': items})

        except Exception as e:
            logger.write_log(f"获取最新结果失败: {str(e)}", 'ERROR')
            return jsonify({'success': False, 'message': f'获取失败: {str(e)}'}), 500

    @staticmethod
    def clear_data():
        """清空改名饰品数据"""
        try:
            from src.units.execution_db import DatabaseManager
            data = request.get_json() or {}
            data_type = data.get('dataType', 'rename')
            config_id = data.get('configId')

            db = DatabaseManager()
            table_name = AutoSearchWeaponModel.get_table_name()

            where_parts = ["data_type = ?"]
            params = [data_type]

            if config_id:
                try:
                    where_parts.append("config_id = ?")
                    params.append(int(config_id))
                except (ValueError, TypeError):
                    pass

            where_clause = " AND ".join(where_parts)
            count_result = db.execute_query(f"SELECT COUNT(*) FROM {table_name} WHERE {where_clause}", tuple(params))
            count = count_result[0][0] if count_result else 0
            db.execute_update(f"DELETE FROM {table_name} WHERE {where_clause}", tuple(params))

            return jsonify({'success': True, 'count': count, 'message': f'清空成功，删除了{count}条记录'})

        except Exception as e:
            logger.write_log(f"清空数据失败: {str(e)}", 'ERROR')
            return jsonify({'success': False, 'message': f'清空失败: {str(e)}'}), 500

    @staticmethod
    def cleanup_old_data():
        """清理旧数据"""
        try:
            data = request.get_json() or {}
            days = data.get('days', 7)
            count = AutoSearchWeaponModel.clear_old_records(days)
            return jsonify({'success': True, 'count': count, 'message': f'清理了{count}条记录'})
        except Exception as e:
            logger.write_log(f"清理旧数据失败: {str(e)}", 'ERROR')
            return jsonify({'success': False, 'message': f'清理失败: {str(e)}'}), 500

    @staticmethod
    def get_stats():
        """获取统计信息"""
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
            results = AutoSearchWeaponModel.find_all(where_clause, tuple(params)) if where_clause else AutoSearchWeaponModel.find_all()

            if not results:
                return jsonify({'success': True, 'stats': {
                    'totalItems': 0, 'totalWeapons': 0, 'avgPrice': 0,
                    'avgSpread': 0, 'avgProfit': 0, 'totalProfit': 0
                }})

            weapon_ids = set()
            total_price = total_spread = total_profit = 0
            rename_items = pendant_items = 0

            for r in results:
                weapon_ids.add(r.weapon_id)
                total_price += r.price or 0
                total_spread += r.spread or 0
                if r.price_diff:
                    total_profit += r.price_diff
                if r.data_type == 'rename':
                    rename_items += 1
                elif r.data_type == 'pendant':
                    pendant_items += 1

            count = len(results)
            return jsonify({'success': True, 'stats': {
                'totalItems': count,
                'totalWeapons': len(weapon_ids),
                'avgPrice': round(total_price / count, 2) if count else 0,
                'avgSpread': round(total_spread / count, 2) if count else 0,
                'avgProfit': round(total_profit / count, 2) if count else 0,
                'totalProfit': round(total_profit, 2),
                'renameItems': rename_items,
                'pendantItems': pendant_items
            }})

        except Exception as e:
            logger.write_log(f"获取统计信息失败: {str(e)}", 'ERROR')
            return jsonify({'success': False, 'message': f'获取统计失败: {str(e)}'}), 500
