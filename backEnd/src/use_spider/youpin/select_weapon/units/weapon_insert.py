"""
select_weapon 写入模块
提供 Spider 所需的武器数据插入、更新与图标状态管理接口
"""
from flask import jsonify, request
from src.db_manager.index.model.weapon_classID import WeaponClassIDModel
from src.db_manager.youpin.model.yyyp_weapon_price_history import YyypWeaponPriceHistoryModel
from datetime import datetime


class WeaponInsert:

    @staticmethod
    def batch_insert_or_update():
        """批量插入或更新武器数据（Spider 同步武器模板时调用）"""
        try:
            data = request.get_json()
            if not data or not isinstance(data, list):
                return jsonify({'success': False, 'error': '无效的JSON数据，需要数组格式'}), 400

            platform = request.args.get('platform', 'yyyp')
            success_count = WeaponClassIDModel.batch_insert_or_update(data, platform=platform)

            return jsonify({
                'success': True,
                'message': f'成功处理 {success_count}/{len(data)} 条数据',
                'success_count': success_count,
                'total_count': len(data),
                'platform': platform
            }), 200
        except Exception as e:
            print(f"批量插入或更新武器数据失败: {e}")
            import traceback
            print(f"详细错误信息: {traceback.format_exc()}")
            return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500

    @staticmethod
    def insert_weapon():
        """插入单个武器数据"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': '无效的JSON数据'}), 400

            platform = request.args.get('platform', 'yyyp')
            id_field_map = {'yyyp': 'yyyp_id', 'buff': 'buff_id', 'steam': 'steam_id'}
            id_field = id_field_map.get(platform, 'yyyp_id')

            if 'Id' in data and id_field not in data:
                data[id_field] = data.pop('Id')

            platform_id = data.get(id_field)
            if not platform_id:
                return jsonify({'success': False, 'error': f'缺少{id_field}字段'}), 400

            existing_list = None
            if platform == 'yyyp':
                existing_list = WeaponClassIDModel.find_by_yyyp_id(platform_id)
            elif platform == 'buff':
                existing_list = WeaponClassIDModel.find_by_buff_id(platform_id)
            elif platform == 'steam':
                existing_list = WeaponClassIDModel.find_by_steam_id(platform_id)

            if existing_list:
                return jsonify({'success': False, 'error': f'武器{id_field}已存在，请使用更新接口'}), 400

            weapon = WeaponClassIDModel(**data)
            if weapon.save():
                return jsonify({'success': True, 'message': '武器数据插入成功', 'data': weapon.to_dict()}), 200
            else:
                return jsonify({'success': False, 'error': '数据插入失败'}), 500
        except Exception as e:
            print(f"插入武器数据失败: {e}")
            import traceback
            print(f"详细错误信息: {traceback.format_exc()}")
            return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500

    @staticmethod
    def update_weapon_by_yyyp_id(yyyp_id):
        """根据悠悠有品 ID 更新武器数据"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': '无效的JSON数据'}), 400

            records = WeaponClassIDModel.find_by_yyyp_id(yyyp_id)
            if not records:
                return jsonify({'success': False, 'error': '武器不存在'}), 404

            weapon = records[0]
            for key, value in data.items():
                if key not in ['yyyp_id', 'buff_id', 'steam_id'] and hasattr(weapon, key):
                    setattr(weapon, key, value)

            if weapon.save():
                return jsonify({'success': True, 'message': '武器数据更新成功', 'data': weapon.to_dict()}), 200
            else:
                return jsonify({'success': False, 'error': '数据更新失败'}), 500
        except Exception as e:
            print(f"更新武器数据失败: {e}")
            import traceback
            print(f"详细错误信息: {traceback.format_exc()}")
            return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500

    @staticmethod
    def update_icon_status():
        """批量更新图标下载状态"""
        try:
            data = request.get_json(silent=True) or {}
            items = data.get('items', [])

            if not isinstance(items, list):
                return jsonify({'success': False, 'error': 'items 需要为数组'}), 400

            if not items:
                return jsonify({'success': True, 'updated': 0}), 200

            table_name = WeaponClassIDModel.get_table_name()
            sql = f"UPDATE {table_name} SET [if_down] = ? WHERE [steam_hash_name] = ?"
            db = WeaponClassIDModel().db

            updated = 0
            for item in items:
                steam_hash_name = item.get('steam_hash_name')
                status = item.get('status')

                if not steam_hash_name or status is None:
                    continue

                try:
                    normalized_status = int(status)
                except (TypeError, ValueError):
                    normalized_status = 0

                normalized_status = max(-1, min(normalized_status, 1))
                affected = db.execute_update(sql, (normalized_status, steam_hash_name))
                if affected:
                    updated += 1

            return jsonify({'success': True, 'updated': updated}), 200
        except Exception as e:
            print(f"更新图标状态失败: {e}")
            import traceback
            print(f"详细错误信息: {traceback.format_exc()}")
            return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500

    @staticmethod
    def record_price_history():
        """记录当前所有饰品的价格到历史表（Spider 完成全量更新后调用）"""
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            all_weapons = WeaponClassIDModel.find_all()

            price_records = []
            for weapon in all_weapons:
                if hasattr(weapon, 'yyyp_id') and weapon.yyyp_id:
                    price_records.append({
                        'yyyp_id': weapon.yyyp_id,
                        'yyyp_price': weapon.yyyp_Price if hasattr(weapon, 'yyyp_Price') else None,
                        'yyyp_rent': weapon.yyyp_Rent if hasattr(weapon, 'yyyp_Rent') else None,
                        'yyyp_on_sale_count': weapon.yyyp_OnSaleCount if hasattr(weapon, 'yyyp_OnSaleCount') else None,
                        'yyyp_on_lease_count': weapon.yyyp_OnLeaseCount if hasattr(weapon, 'yyyp_OnLeaseCount') else None,
                        'record_time': current_time
                    })

            if price_records:
                history_count = YyypWeaponPriceHistoryModel.batch_insert_price_records(price_records)
                print(f"✅ 成功记录 {history_count} 条价格历史数据")
                return jsonify({
                    'success': True,
                    'message': f'成功记录 {history_count} 条价格历史数据',
                    'count': history_count,
                    'record_time': current_time
                }), 200
            else:
                print("⚠️  没有找到需要记录的价格数据")
                return jsonify({'success': True, 'message': '没有找到需要记录的价格数据', 'count': 0}), 200

        except Exception as e:
            print(f"记录价格历史失败: {e}")
            import traceback
            print(f"详细错误信息: {traceback.format_exc()}")
            return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500
