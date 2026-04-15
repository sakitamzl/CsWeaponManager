# -*- coding: utf-8 -*-
"""
饰品搜索处理器
迁移自 backEnd/src/web_side/data_webside/item_search.py
"""

import json
import traceback
import requests as http_requests
from flask import request, jsonify
from src.db_manager.database import DatabaseManager
from src.units.log import Log

logger = Log()


class ItemSearchHandler:

    @staticmethod
    def search_items():
        """
        搜索饰品
        请求体: { "keyword", "weaponType", "weaponName", "rarity" }
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

            conditions = []
            params = []

            if keyword:
                conditions.append("item_name LIKE ?")
                params.append(f"%{keyword}%")
            if weapon_type:
                conditions.append("weapon_type = ?")
                params.append(weapon_type)
            if weapon_name:
                conditions.append("weapon_name = ?")
                params.append(weapon_name)
            if rarity:
                conditions.append("Rarity = ?")
                params.append(rarity)

            if not conditions:
                return jsonify({'success': True, 'data': [], 'message': '请提供搜索条件'}), 200

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
                    CASE WHEN csqaq_id IS NOT NULL THEN 0 ELSE 1 END,
                    yyyp_OnSaleCount DESC,
                    yyyp_Price ASC
                LIMIT 50
            """

            results = DatabaseManager().execute_query(sql, tuple(params))

            items = []
            for row in results:
                items.append({
                    'csqaq_id': row[0],
                    'market_listing_item_name': row[1],
                    'steam_hash_name': row[2],
                    'weapon_type': row[3],
                    'weapon_name': row[4],
                    'item_name': row[5],
                    'rarity': row[6],
                    'yyyp_Price': row[7],
                    'on_sale_count': int(row[8]) if row[8] else 0
                })

            logger.write_log(f"搜索完成，找到 {len(items)} 件饰品", 'info')
            return jsonify({'success': True, 'data': items, 'total': len(items)}), 200

        except Exception as e:
            logger.write_log(f"饰品搜索失败: {str(e)}", 'error')
            logger.write_log(f"详细错误: {traceback.format_exc()}", 'error')
            return jsonify({'success': False, 'message': f'搜索失败: {str(e)}'}), 500

    @staticmethod
    def get_weapon_names():
        """
        获取指定武器类型的所有武器名称列表
        请求体: { "weaponType": "步枪" }
        """
        try:
            data = request.get_json()
            weapon_type = data.get('weaponType', '').strip()

            if not weapon_type:
                return jsonify({'success': False, 'message': '请提供武器类型'}), 400

            sql = """
                SELECT DISTINCT weapon_name
                FROM weapon_classID
                WHERE weapon_type = ? AND weapon_name IS NOT NULL AND weapon_name != ''
                ORDER BY weapon_name
            """

            results = DatabaseManager().execute_query(sql, (weapon_type,))
            weapon_names = [row[0] for row in results if row[0]]

            return jsonify({'success': True, 'data': weapon_names}), 200

        except Exception as e:
            logger.write_log(f"获取武器名称列表失败: {str(e)}", 'error')
            return jsonify({'success': False, 'message': f'获取失败: {str(e)}'}), 500

    @staticmethod
    def get_csqaq_detail():
        """
        获取 CSQAQ 饰品详细信息
        Query 参数: id=<csqaq_id>
        """
        try:
            csqaq_id = request.args.get('id')
            if not csqaq_id:
                return jsonify({'success': False, 'message': '请提供 CSQAQ ID'}), 400

            logger.write_log(f"获取 CSQAQ 详细信息: id={csqaq_id}", 'info')

            cfg_rows = DatabaseManager().execute_query(
                "SELECT [value] FROM config WHERE [key1] = ? AND [key2] = ? LIMIT 1",
                ("csqaq", "config"),
            )
            if not cfg_rows or not cfg_rows[0] or not cfg_rows[0][0]:
                return jsonify({
                    'success': False,
                    'message': 'CSQAQ配置不存在，请先在【设置 > 数据源管理】中添加CSQAQ数据源'
                }), 404

            config_data = json.loads(cfg_rows[0][0])
            api_token = config_data.get('ApiToken', '')

            if not api_token:
                return jsonify({'success': False, 'message': 'CSQAQ ApiToken未配置'}), 400

            response = http_requests.get(
                'https://api.csqaq.com/api/v1/info/good',
                params={'id': csqaq_id},
                headers={'ApiToken': api_token},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 200:
                    logger.write_log(f"CSQAQ 详细信息获取成功: id={csqaq_id}", 'info')
                    return jsonify({'success': True, 'data': data.get('data')}), 200
                else:
                    return jsonify({'success': False, 'message': data.get('msg', 'CSQAQ API 返回错误')}), 400
            else:
                return jsonify({
                    'success': False,
                    'message': f'CSQAQ API 请求失败: {response.status_code}'
                }), response.status_code

        except Exception as e:
            logger.write_log(f"获取 CSQAQ 详细信息失败: {str(e)}", 'error')
            logger.write_log(f"详细错误: {traceback.format_exc()}", 'error')
            return jsonify({'success': False, 'message': f'获取失败: {str(e)}'}), 500

    @staticmethod
    def batch_sticker_prices():
        """
        批量查询印花/挂件价格
        请求体: { "steam_hash_names": [...] }
        """
        try:
            data = request.get_json()
            if not data or 'steam_hash_names' not in data:
                return jsonify({'success': False, 'message': '缺少必需参数: steam_hash_names'}), 400

            steam_hash_names = data['steam_hash_names']

            if not isinstance(steam_hash_names, list):
                return jsonify({'success': False, 'message': 'steam_hash_names 必须是数组'}), 400

            if not steam_hash_names:
                return jsonify({'success': True, 'data': {}})

            logger.write_log(f"批量查询印花价格: 共 {len(steam_hash_names)} 个", 'info')

            db = DatabaseManager()
            placeholders = ",".join(["?"] * len(steam_hash_names))
            sql_batch = f"""
            SELECT [steam_hash_name], [yyyp_Price], [buff_Price], [market_listing_item_name],
                   [icon_url], [weapon_type], [item_name], [yyyp_OnSaleCount], [buff_OnSaleCount]
            FROM weapon_classID
            WHERE [steam_hash_name] IN ({placeholders})
            """
            rows = db.execute_query(sql_batch, tuple(steam_hash_names))
            by_hash = {r[0]: r for r in rows} if rows else {}

            result_map = {}
            for steam_hash_name in steam_hash_names:
                if not steam_hash_name:
                    continue
                row = by_hash.get(steam_hash_name)
                if row:
                    (_, yyyp_p, buff_p, mname, icon, wtype, iname, yyyp_cnt, buff_cnt) = row
                    result_map[steam_hash_name] = {
                        'yyyp_price': yyyp_p if yyyp_p else None,
                        'buff_price': buff_p if buff_p else None,
                        'market_listing_item_name': mname if mname else None,
                        'icon_url': icon if icon else None,
                        'weapon_type': wtype if wtype else None,
                        'item_name': iname if iname else None,
                        'yyyp_on_sale_count': yyyp_cnt if yyyp_cnt else None,
                        'buff_on_sale_count': buff_cnt if buff_cnt else None,
                    }
                else:
                    result_map[steam_hash_name] = None

            logger.write_log(
                f"批量查询完成: 找到 {len([v for v in result_map.values() if v])} 个有价格数据", 'info'
            )
            return jsonify({'success': True, 'data': result_map})

        except Exception as e:
            logger.write_log(f"批量查询印花价格失败: {str(e)}", 'error')
            logger.write_log(f"详细错误: {traceback.format_exc()}", 'error')
            return jsonify({'success': False, 'message': f'查询失败: {str(e)}'}), 500
