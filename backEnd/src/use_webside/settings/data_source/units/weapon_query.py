"""
武器数据查询模块
迁移自 web_side/webSide/web/select_weapon.py
提供武器搜索、详情查询、参考价、csqaq_id、按价格区间查询等功能
"""
from flask import jsonify, request
from src.db_manager.index.model.weapon_classID import WeaponClassIDModel
from src.units.log import Log

logger = Log()


class WeaponQuery:

    @staticmethod
    def search_weapon():
        """
        根据 market_listing_item_name 或 steam_hash_name 模糊搜索武器（用于自动完成下拉框）
        参数: keyword - 搜索关键词
        返回: 匹配的武器名称列表（仅 market_listing_item_name 字段，限制20条）
        """
        try:
            keyword = request.args.get('keyword', '')

            if not keyword or len(keyword.strip()) == 0:
                return jsonify({
                    "success": True,
                    "data": []
                }), 200

            where_clause = "([market_listing_item_name] LIKE ? OR [steam_hash_name] LIKE ?)"
            params = (f"%{keyword}%", f"%{keyword}%")

            records = WeaponClassIDModel.find_all(
                where=where_clause,
                params=params,
                limit=20
            )

            results = []
            seen = set()
            for record in records:
                name = record.market_listing_item_name
                if name and name not in seen:
                    results.append(name)
                    seen.add(name)

            return jsonify({
                "success": True,
                "data": results
            }), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                "success": False,
                "error": str(e),
                "data": []
            }), 500

    @staticmethod
    def get_weapon_names():
        """
        根据武器类型获取该类型下的所有武器名称（去重）
        参数: weaponType - 武器类型（可选，不传则返回所有武器名称）
        返回: 武器名称列表
        """
        try:
            weapon_type = request.args.get('weaponType', '')

            if weapon_type and len(weapon_type.strip()) > 0:
                where_clause = "[weapon_type] = ?"
                params = (weapon_type.strip(),)
                records = WeaponClassIDModel.find_all(
                    where=where_clause,
                    params=params
                )
            else:
                records = WeaponClassIDModel.find_all()

            weapon_names = set()
            for record in records:
                if record.weapon_name and record.weapon_name.strip():
                    weapon_names.add(record.weapon_name.strip())

            weapon_names_list = sorted(list(weapon_names))

            return jsonify({
                "success": True,
                "data": weapon_names_list
            }), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                "success": False,
                "error": str(e),
                "data": []
            }), 500

    @staticmethod
    def search_weapon_detail():
        """
        根据 market_listing_item_name 搜索武器详细信息（用于表格展示）
        参数:
            platformType - 平台类型：youpin 或 buff（必填）
            keyword - 搜索关键词（可选）
            exactMatch - 是否精确匹配（可选，默认false）
            weaponType - 武器类型筛选（可选）
            weaponName - 武器名称筛选（可选）
            rarity - 稀有度筛选（可选）
            priceMin - 最低价格（可选）
            priceMax - 最高价格（可选）
            minOnSaleCount - 最小在售数量（可选）
            page - 页码（可选，默认1）
            limit - 每页数量（可选，默认50）
        """
        try:
            platform_type = request.args.get('platformType', 'youpin')
            keyword = request.args.get('keyword', '')
            exact_match = request.args.get('exactMatch', 'false').lower() == 'true'
            weapon_type = request.args.get('weaponType', '')
            weapon_name = request.args.get('weaponName', '')
            rarity = request.args.get('rarity', '')
            price_min = request.args.get('priceMin', '')
            price_max = request.args.get('priceMax', '')
            min_on_sale_count = request.args.get('minOnSaleCount', '')
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 50))

            where_clauses = []
            params = []

            if keyword and len(keyword.strip()) > 0:
                if exact_match:
                    where_clauses.append("([market_listing_item_name] = ? OR [steam_hash_name] = ?)")
                    params.append(keyword.strip())
                    params.append(keyword.strip())
                else:
                    where_clauses.append("([market_listing_item_name] LIKE ? OR [steam_hash_name] LIKE ?)")
                    params.append(f"%{keyword.strip()}%")
                    params.append(f"%{keyword.strip()}%")

            if weapon_type and len(weapon_type.strip()) > 0:
                where_clauses.append("[weapon_type] = ?")
                params.append(weapon_type.strip())

            if weapon_name and len(weapon_name.strip()) > 0:
                where_clauses.append("[weapon_name] = ?")
                params.append(weapon_name.strip())

            if rarity and len(rarity.strip()) > 0:
                where_clauses.append("[Rarity] = ?")
                params.append(rarity.strip())

            where_clause = " AND ".join(where_clauses) if where_clauses else None

            if platform_type == 'steam':
                extra_clause = "[steam_hash_name] IS NOT NULL AND [steam_hash_name] <> ''"
                where_clause = f"{where_clause} AND {extra_clause}" if where_clause else extra_clause

            price_field = 'yyyp_Price' if platform_type == 'youpin' else 'buff_Price'

            records = WeaponClassIDModel.find_all(
                where=where_clause,
                params=tuple(params) if params else None,
                order_by=f"CAST([{price_field}] AS REAL) DESC"
            )

            if platform_type == 'steam':
                price_field = 'yyyp_Price'
                on_sale_count_field = 'yyyp_OnSaleCount'
            else:
                price_field = 'yyyp_Price' if platform_type == 'youpin' else 'buff_Price'
                on_sale_count_field = 'yyyp_OnSaleCount' if platform_type == 'youpin' else 'buff_OnSaleCount'

            filtered_records = []
            for record in records:
                price_str = getattr(record, price_field, None)
                if price_str:
                    try:
                        price = float(price_str)
                        if price < 1:
                            continue
                    except (ValueError, TypeError):
                        continue
                else:
                    continue

                on_sale_count_str = getattr(record, on_sale_count_field, None)
                if on_sale_count_str:
                    try:
                        on_sale_count = int(on_sale_count_str)
                        if on_sale_count < 10:
                            continue
                    except (ValueError, TypeError):
                        continue
                else:
                    continue

                if price_min or price_max:
                    if price_min and price < float(price_min):
                        continue
                    if price_max and price > float(price_max):
                        continue

                if min_on_sale_count:
                    if on_sale_count < int(min_on_sale_count):
                        continue

                filtered_records.append(record)

            total_count = len(filtered_records)
            start_index = (page - 1) * limit
            paginated_records = filtered_records[start_index:start_index + limit]

            results = []
            for record in paginated_records:
                results.append({
                    'steam_hash_name': record.steam_hash_name,
                    'market_listing_item_name': record.market_listing_item_name,
                    'yyyp_id': record.yyyp_id,
                    'buff_id': record.buff_id,
                    'steam_id': record.steam_id,
                    'yyyp_class_name': record.yyyp_class_name,
                    'buff_class_name': record.buff_class_name,
                    'weapon_type': record.weapon_type,
                    'weapon_name': record.weapon_name,
                    'item_name': record.item_name,
                    'float_range': record.float_range,
                    'Rarity': record.Rarity,
                    'yyyp_Price': record.yyyp_Price,
                    'buff_Price': record.buff_Price,
                    'yyyp_OnSaleCount': record.yyyp_OnSaleCount,
                    'buff_OnSaleCount': record.buff_OnSaleCount
                })

            return jsonify({
                "success": True,
                "data": results,
                "count": len(results),
                "total": total_count,
                "page": page,
                "limit": limit
            }), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                "success": False,
                "error": str(e),
                "data": [],
                "count": 0
            }), 500

    @staticmethod
    def get_reference_prices():
        """
        批量查询参考价（通过 steam_hash_name 列表）
        请求体: {"steamHashNames": [...], "referencePriceSource": "youpin"|"buff"}
        返回: {"success": true, "data": {"steam_hash_name": price, ...}}
        """
        try:
            data = request.get_json() or {}
            steam_hash_names = data.get('steamHashNames', [])
            reference_price_source = data.get('referencePriceSource', 'youpin')
            reference_price_source = (reference_price_source or '').strip().lower()
            if reference_price_source not in ('youpin', 'buff'):
                reference_price_source = 'youpin'

            if not steam_hash_names:
                return jsonify({'success': True, 'data': {}})

            placeholders = ','.join(['?' for _ in steam_hash_names])
            where_clause = f"[steam_hash_name] IN ({placeholders})"

            records = WeaponClassIDModel.find_all(
                where=where_clause,
                params=tuple(steam_hash_names)
            )

            price_field = 'yyyp_Price' if reference_price_source == 'youpin' else 'buff_Price'
            price_map = {}
            for record in records:
                hash_name = record.steam_hash_name
                if not hash_name:
                    continue
                raw_value = getattr(record, price_field, None)
                if raw_value in (None, '', 'None'):
                    price_map[hash_name] = 0
                    continue
                try:
                    price_map[hash_name] = float(raw_value)
                except (ValueError, TypeError):
                    price_map[hash_name] = 0

            logger.write_log(
                f"批量查询参考价({reference_price_source}): 请求{len(steam_hash_names)}个，找到{len(price_map)}个",
                'INFO'
            )

            return jsonify({'success': True, 'data': price_map})

        except Exception as e:
            logger.write_log(f"批量查询参考价失败: {str(e)}", 'ERROR')
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': str(e),
                'data': {}
            }), 500

    @staticmethod
    def get_csqaq_id():
        """
        通过 market_listing_item_name 查询 csqaq_id
        请求体: {"market_listing_item_name": "P2000 | Dispatch (Factory New)"}
        返回: {"success": true, "csqaq_id": 16550}
        """
        try:
            data = request.get_json() or {}
            market_listing_item_name = data.get('market_listing_item_name', '').strip()

            if not market_listing_item_name:
                return jsonify({
                    "success": False,
                    "message": "market_listing_item_name 参数不能为空"
                }), 400

            records = WeaponClassIDModel.find_by_market_listing_item_name(market_listing_item_name)

            if not records:
                logger.write_log(f"[get_csqaq_id] 未找到数据: {market_listing_item_name}", 'WARNING')
                return jsonify({
                    "success": False,
                    "message": f"未找到数据: {market_listing_item_name}"
                }), 404

            record = records[0]

            if not record.csqaq_id:
                return jsonify({
                    "success": False,
                    "message": "该武器没有对应的 CSQAQ ID"
                }), 404

            logger.write_log(
                f"[get_csqaq_id] 查询成功: {market_listing_item_name} -> csqaq_id={record.csqaq_id}",
                'INFO'
            )

            return jsonify({
                "success": True,
                "csqaq_id": record.csqaq_id
            }), 200

        except Exception as e:
            logger.write_log(f"获取 csqaq_id 失败: {e}", 'ERROR')
            import traceback
            traceback.print_exc()
            return jsonify({
                "success": False,
                "message": f"获取 csqaq_id 失败: {str(e)}"
            }), 500

    @staticmethod
    def query_weapons_by_price_range():
        """
        根据价格区间和武器类型查询武器ID列表（用于挂件搜索的按价格区间查询模式）
        参数:
            price_min - 最低价格（可选）
            price_max - 最高价格（可选）
            weapon_types - 武器类型列表，逗号分隔（可选）
            min_on_sale_count - 最小在售数量（可选，默认100）
        返回: {"success": true, "data": [{"id": "61490", "name": "AK-47 | 红线"}, ...], "total": 100}
        """
        try:
            price_min = request.args.get('price_min', '')
            price_max = request.args.get('price_max', '')
            weapon_types_str = request.args.get('weapon_types', '')
            min_on_sale_count_str = request.args.get('min_on_sale_count', '100')

            where_clauses = []
            params = []

            if weapon_types_str and len(weapon_types_str.strip()) > 0:
                weapon_types_list = [wt.strip() for wt in weapon_types_str.split(',') if wt.strip()]
                if weapon_types_list:
                    placeholders = ','.join(['?' for _ in weapon_types_list])
                    where_clauses.append(f"[weapon_type] IN ({placeholders})")
                    params.extend(weapon_types_list)

            where_clause = " AND ".join(where_clauses) if where_clauses else None

            try:
                min_on_sale_count = int(min_on_sale_count_str) if min_on_sale_count_str else 100
            except (ValueError, TypeError):
                min_on_sale_count = 100

            records = WeaponClassIDModel.find_all(
                where=where_clause,
                params=tuple(params) if params else None,
                order_by="CAST([yyyp_Price] AS REAL) ASC"
            )

            filtered_records = []
            for record in records:
                price_str = record.yyyp_Price
                if price_str:
                    try:
                        price = float(price_str)
                        if price < 1:
                            continue
                    except (ValueError, TypeError):
                        continue
                else:
                    continue

                if price_min:
                    try:
                        if price < float(price_min):
                            continue
                    except (ValueError, TypeError):
                        pass

                if price_max:
                    try:
                        if price > float(price_max):
                            continue
                    except (ValueError, TypeError):
                        pass

                on_sale_count_str = record.yyyp_OnSaleCount
                if on_sale_count_str:
                    try:
                        on_sale_count = int(on_sale_count_str)
                        if on_sale_count < min_on_sale_count:
                            continue
                    except (ValueError, TypeError):
                        continue
                else:
                    continue

                if not record.yyyp_id:
                    continue

                filtered_records.append(record)

            results = [
                {
                    'id': str(record.yyyp_id),
                    'name': record.market_listing_item_name or record.weapon_name or '未知饰品'
                }
                for record in filtered_records
            ]

            logger.write_log(
                f"[queryWeaponsByPriceRange] 查询成功 - 返回 {len(results)} 个饰品",
                'INFO'
            )

            return jsonify({
                "success": True,
                "data": results,
                "total": len(results)
            }), 200

        except Exception as e:
            logger.write_log(f"[queryWeaponsByPriceRange] 查询失败: {e}", 'ERROR')
            import traceback
            traceback.print_exc()
            return jsonify({
                "success": False,
                "message": f"查询失败: {str(e)}",
                "data": [],
                "total": 0
            }), 500
