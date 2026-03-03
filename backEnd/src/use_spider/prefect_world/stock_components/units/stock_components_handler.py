# -*- coding: utf-8 -*-
"""
完美世界 stock_components 处理模块
提供 Spider 所需的库存组件数据插入、更新与删除接口
逻辑完整迁移自 web_side/prefectWorld/stock_components_api.py
"""
import traceback
from flask import request, jsonify
from src.db_manager.steam.model import SteamStockComponentsModel


class StockComponentsHandler:

    @staticmethod
    def batch():
        """批量插入或更新库存组件数据"""
        try:
            data = request.get_json()
            if not data or 'items' not in data:
                return jsonify({'code': 400, 'message': '缺少必要参数 items', 'result': None}), 400

            items = data.get('items', [])
            if not isinstance(items, list):
                return jsonify({'code': 400, 'message': 'items 必须是数组类型', 'result': None}), 400
            if len(items) == 0:
                return jsonify({'code': 400, 'message': 'items 不能为空', 'result': None}), 400

            db_fields = set(SteamStockComponentsModel.get_fields().keys())
            total_count = len(items)
            success_count = failed_count = insert_count = update_count = 0
            failed_items = []

            for item_index, item in enumerate(items):
                try:
                    filtered_item = {k: (str(v) if v is not None else None) for k, v in item.items() if k in db_fields}

                    if 'goods_assetid' not in filtered_item or not filtered_item['goods_assetid']:
                        failed_count += 1
                        failed_items.append({'index': item_index, 'error': '缺少主键 goods_assetid'})
                        continue

                    goods_assetid = filtered_item['goods_assetid']
                    existing_record = SteamStockComponentsModel.find_by_id(goods_assetid=goods_assetid)

                    if existing_record:
                        for k, v in filtered_item.items():
                            setattr(existing_record, k, v)
                        if existing_record.save():
                            success_count += 1
                            update_count += 1
                        else:
                            failed_count += 1
                            failed_items.append({'index': item_index, 'goods_assetid': goods_assetid, 'error': '更新记录失败'})
                    else:
                        new_record = SteamStockComponentsModel(**filtered_item)
                        if new_record.save():
                            success_count += 1
                            insert_count += 1
                        else:
                            failed_count += 1
                            failed_items.append({'index': item_index, 'goods_assetid': goods_assetid, 'error': '插入记录失败'})

                except Exception as e:
                    failed_count += 1
                    failed_items.append({'index': item_index, 'error': str(e)})

            return jsonify({'code': 0, 'message': 'success', 'result': {'total': total_count, 'success': success_count, 'failed': failed_count, 'insert_count': insert_count, 'update_count': update_count, 'failed_items': failed_items[:20] if failed_items else []}})

        except Exception as e:
            return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}', 'result': None}), 500

    @staticmethod
    def single():
        """插入单条库存组件数据"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'code': 400, 'message': '缺少请求数据', 'result': None}), 400

            db_fields = set(SteamStockComponentsModel.get_fields().keys())
            filtered_data = {k: (str(v) if v is not None else None) for k, v in data.items() if k in db_fields}

            if 'goods_assetid' not in filtered_data or not filtered_data['goods_assetid']:
                return jsonify({'code': 400, 'message': '缺少主键 goods_assetid', 'result': None}), 400

            goods_assetid = filtered_data['goods_assetid']
            existing_record = SteamStockComponentsModel.find_by_id(goods_assetid=goods_assetid)

            if existing_record:
                for k, v in filtered_data.items():
                    setattr(existing_record, k, v)
                if existing_record.save():
                    return jsonify({'code': 0, 'message': '记录更新成功', 'result': {'goods_assetid': goods_assetid, 'action': 'update'}})
                return jsonify({'code': 500, 'message': '更新记录失败', 'result': None}), 500
            else:
                new_record = SteamStockComponentsModel(**filtered_data)
                if new_record.save():
                    return jsonify({'code': 0, 'message': '记录插入成功', 'result': {'goods_assetid': goods_assetid, 'action': 'insert'}})
                return jsonify({'code': 500, 'message': '插入记录失败', 'result': None}), 500

        except Exception as e:
            return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}', 'result': None}), 500

    @staticmethod
    def delete(goods_assetid):
        """删除指定 goods_assetid 的库存组件记录"""
        try:
            record = SteamStockComponentsModel.find_by_id(goods_assetid=goods_assetid)
            if not record:
                return jsonify({'code': 404, 'message': '记录不存在', 'result': None}), 404
            if record.delete():
                return jsonify({'code': 0, 'message': '删除成功', 'result': None})
            return jsonify({'code': 500, 'message': '删除失败', 'result': None}), 500
        except Exception as e:
            return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}', 'result': None}), 500

    @staticmethod
    def delete_by_assetid_steam(assetid, steam_id):
        """删除指定 assetid 和 steam_id（data_user）的库存组件记录"""
        try:
            from src.db_manager.database import DatabaseManager
            db = DatabaseManager()

            check_result = db.execute_query(
                "SELECT COUNT(*) FROM steam_stockComponents WHERE assetid = ? AND data_user = ?",
                (assetid, steam_id)
            )
            count = check_result[0][0] if check_result else 0

            if count == 0:
                return jsonify({'code': 0, 'message': '记录不存在或已删除', 'result': {'deleted_count': 0}})

            db.execute_update(
                "DELETE FROM steam_stockComponents WHERE assetid = ? AND data_user = ?",
                (assetid, steam_id)
            )
            print(f"✅ 删除成功 - assetid: {assetid}, steam_id: {steam_id}, 删除数量: {count}")
            return jsonify({'code': 0, 'message': '删除成功', 'result': {'deleted_count': count}})

        except Exception as e:
            print(f"❌ 删除失败 - assetid: {assetid}, steam_id: {steam_id}, 错误: {str(e)}\n{traceback.format_exc()}")
            return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}', 'result': None}), 500

    @staticmethod
    def auto_fill_prices(steam_id):
        """自动将 buy 表中的购入价格同步填充到 steam_stockComponents 表
        根据 steam_hash_name 匹配，将 buy.price 写入 stockComponents.buy_price
        POST /stock_components/auto_fill_prices/<steam_id>
        """
        try:
            from src.db_manager.database import DatabaseManager
            db = DatabaseManager()

            # 查询该 steam_id 下所有 buy_price 为空的库存组件
            components = db.execute_query(
                """SELECT goods_assetid, steam_hash_name
                   FROM steam_stockComponents
                   WHERE data_user = ? AND (buy_price IS NULL OR buy_price = '')""",
                (steam_id,)
            )

            total_count = len(components) if components else 0
            filled_count = 0

            for row in (components or []):
                goods_assetid = row[0]
                steam_hash_name = row[1]
                if not steam_hash_name:
                    continue

                # 从 buy 表按 steam_hash_name 取最新一条购入价格
                buy_row = db.execute_query(
                    """SELECT price FROM buy
                       WHERE steam_hash_name = ? AND price IS NOT NULL
                       ORDER BY order_time DESC LIMIT 1""",
                    (steam_hash_name,)
                )
                if not buy_row:
                    continue

                price = buy_row[0][0]
                affected = db.execute_update(
                    "UPDATE steam_stockComponents SET buy_price = ? WHERE goods_assetid = ?",
                    (price, goods_assetid)
                )
                if affected > 0:
                    filled_count += 1

            return jsonify({
                'success': True,
                'data': {'total_count': total_count, 'filled_count': filled_count}
            }), 200

        except Exception as e:
            print(f"auto_fill_prices 失败: {e}\n{traceback.format_exc()}")
            return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'}), 500
