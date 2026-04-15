"""
武器数据查询模块
迁移自 web_side/webSide/web/select_weapon.py
统一使用 DatabaseManager + 参数化 SQL（行映射为 SimpleNamespace，兼容原 record.xxx 访问）
"""
from types import SimpleNamespace
from flask import jsonify, request
from src.db_manager.database import DatabaseManager
from src.units.log import Log

logger = Log()

WEAPON_TABLE = "weapon_classID"

_DETAIL_FIELDS = (
    "steam_hash_name", "market_listing_item_name", "csqaq_id", "yyyp_id", "buff_id", "steam_id",
    "yyyp_class_name", "buff_class_name", "weapon_type", "weapon_name", "item_name",
    "float_range", "Rarity", "yyyp_Price", "buff_Price", "yyyp_OnSaleCount", "buff_OnSaleCount",
)
_DETAIL_SELECT = "SELECT " + ", ".join(
    "[Rarity]" if f == "Rarity" else f"[{f}]" for f in _DETAIL_FIELDS
)


def _rows_to_records(rows):
    if not rows:
        return []
    return [SimpleNamespace(**dict(zip(_DETAIL_FIELDS, r))) for r in rows]


def _query_weapons(where_clause: str, params: tuple, order_by: str = None, limit: int = None):
    db = DatabaseManager()
    sql = f"{_DETAIL_SELECT} FROM {WEAPON_TABLE}"
    if where_clause:
        sql += f" WHERE {where_clause}"
    if order_by:
        sql += f" ORDER BY {order_by}"
    if limit is not None:
        sql += f" LIMIT {int(limit)}"
    return _rows_to_records(db.execute_query(sql, params))


class WeaponQuery:

    @staticmethod
    def search_weapon():
        try:
            keyword = request.args.get("keyword", "")

            if not keyword or len(keyword.strip()) == 0:
                return jsonify({"success": True, "data": []}), 200

            where_clause = "([market_listing_item_name] LIKE ? OR [steam_hash_name] LIKE ?)"
            params = (f"%{keyword}%", f"%{keyword}%")
            records = _query_weapons(where_clause, params, limit=20)

            results = []
            seen = set()
            for record in records:
                name = record.market_listing_item_name
                if name and name not in seen:
                    results.append(name)
                    seen.add(name)

            return jsonify({"success": True, "data": results}), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"success": False, "error": str(e), "data": []}), 500

    @staticmethod
    def get_weapon_names():
        try:
            weapon_type = request.args.get("weaponType", "")
            db = DatabaseManager()

            if weapon_type and len(weapon_type.strip()) > 0:
                sql = """
                SELECT DISTINCT [weapon_name] FROM weapon_classID
                WHERE [weapon_type] = ? AND [weapon_name] IS NOT NULL AND TRIM([weapon_name]) != ''
                """
                rows = db.execute_query(sql, (weapon_type.strip(),))
            else:
                sql = """
                SELECT DISTINCT [weapon_name] FROM weapon_classID
                WHERE [weapon_name] IS NOT NULL AND TRIM([weapon_name]) != ''
                """
                rows = db.execute_query(sql, ())

            weapon_names_list = sorted({r[0].strip() for r in rows if r and r[0]})

            return jsonify({"success": True, "data": weapon_names_list}), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"success": False, "error": str(e), "data": []}), 500

    @staticmethod
    def search_weapon_detail():
        try:
            platform_type = request.args.get("platformType", "youpin")
            keyword = request.args.get("keyword", "")
            exact_match = request.args.get("exactMatch", "false").lower() == "true"
            weapon_type = request.args.get("weaponType", "")
            weapon_name = request.args.get("weaponName", "")
            rarity = request.args.get("rarity", "")
            price_min = request.args.get("priceMin", "")
            price_max = request.args.get("priceMax", "")
            min_on_sale_count = request.args.get("minOnSaleCount", "")
            page = int(request.args.get("page", 1))
            limit = int(request.args.get("limit", 50))

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

            where_clause = " AND ".join(where_clauses) if where_clauses else ""

            if platform_type == "steam":
                extra = "[steam_hash_name] IS NOT NULL AND [steam_hash_name] <> ''"
                where_clause = f"{where_clause} AND {extra}" if where_clause else extra

            price_field = "yyyp_Price" if platform_type == "youpin" else "buff_Price"
            order_by = f"CAST([{price_field}] AS REAL) DESC"

            records = _query_weapons(where_clause, tuple(params), order_by=order_by)

            if platform_type == "steam":
                price_field = "yyyp_Price"
                on_sale_count_field = "yyyp_OnSaleCount"
            else:
                price_field = "yyyp_Price" if platform_type == "youpin" else "buff_Price"
                on_sale_count_field = (
                    "yyyp_OnSaleCount" if platform_type == "youpin" else "buff_OnSaleCount"
                )

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
                    "steam_hash_name": record.steam_hash_name,
                    "market_listing_item_name": record.market_listing_item_name,
                    "yyyp_id": record.yyyp_id,
                    "buff_id": record.buff_id,
                    "steam_id": record.steam_id,
                    "yyyp_class_name": record.yyyp_class_name,
                    "buff_class_name": record.buff_class_name,
                    "weapon_type": record.weapon_type,
                    "weapon_name": record.weapon_name,
                    "item_name": record.item_name,
                    "float_range": record.float_range,
                    "Rarity": record.Rarity,
                    "yyyp_Price": record.yyyp_Price,
                    "buff_Price": record.buff_Price,
                    "yyyp_OnSaleCount": record.yyyp_OnSaleCount,
                    "buff_OnSaleCount": record.buff_OnSaleCount,
                })

            return jsonify({
                "success": True,
                "data": results,
                "count": len(results),
                "total": total_count,
                "page": page,
                "limit": limit,
            }), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                "success": False,
                "error": str(e),
                "data": [],
                "count": 0,
            }), 500

    @staticmethod
    def get_reference_prices():
        try:
            data = request.get_json() or {}
            steam_hash_names = data.get("steamHashNames", [])
            reference_price_source = data.get("referencePriceSource", "youpin")
            reference_price_source = (reference_price_source or "").strip().lower()
            if reference_price_source not in ("youpin", "buff"):
                reference_price_source = "youpin"

            if not steam_hash_names:
                return jsonify({"success": True, "data": {}})

            placeholders = ",".join(["?"] * len(steam_hash_names))
            where_clause = f"[steam_hash_name] IN ({placeholders})"
            records = _query_weapons(where_clause, tuple(steam_hash_names))

            price_field = "yyyp_Price" if reference_price_source == "youpin" else "buff_Price"
            price_map = {}
            for record in records:
                hash_name = record.steam_hash_name
                if not hash_name:
                    continue
                raw_value = getattr(record, price_field, None)
                if raw_value in (None, "", "None"):
                    price_map[hash_name] = 0
                    continue
                try:
                    price_map[hash_name] = float(raw_value)
                except (ValueError, TypeError):
                    price_map[hash_name] = 0

            logger.write_log(
                f"批量查询参考价({reference_price_source}): 请求{len(steam_hash_names)}个，找到{len(price_map)}个",
                "INFO",
            )

            return jsonify({"success": True, "data": price_map})

        except Exception as e:
            logger.write_log(f"批量查询参考价失败: {str(e)}", "ERROR")
            import traceback
            traceback.print_exc()
            return jsonify({"success": False, "error": str(e), "data": {}}), 500

    @staticmethod
    def get_csqaq_id():
        try:
            data = request.get_json() or {}
            market_listing_item_name = data.get("market_listing_item_name", "").strip()

            if not market_listing_item_name:
                return jsonify({
                    "success": False,
                    "message": "market_listing_item_name 参数不能为空",
                }), 400

            records = _query_weapons(
                "[market_listing_item_name] = ?", (market_listing_item_name,)
            )

            if not records:
                logger.write_log(f"[get_csqaq_id] 未找到数据: {market_listing_item_name}", "WARNING")
                return jsonify({
                    "success": False,
                    "message": f"未找到数据: {market_listing_item_name}",
                }), 404

            record = records[0]

            if not record.csqaq_id:
                return jsonify({
                    "success": False,
                    "message": "该武器没有对应的 CSQAQ ID",
                }), 404

            logger.write_log(
                f"[get_csqaq_id] 查询成功: {market_listing_item_name} -> csqaq_id={record.csqaq_id}",
                "INFO",
            )

            return jsonify({"success": True, "csqaq_id": record.csqaq_id}), 200

        except Exception as e:
            logger.write_log(f"获取 csqaq_id 失败: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return jsonify({"success": False, "message": f"获取 csqaq_id 失败: {str(e)}"}), 500

    @staticmethod
    def query_weapons_by_price_range():
        try:
            price_min = request.args.get("price_min", "")
            price_max = request.args.get("price_max", "")
            weapon_types_str = request.args.get("weapon_types", "")
            min_on_sale_count_str = request.args.get("min_on_sale_count", "100")

            where_clauses = []
            params = []

            if weapon_types_str and len(weapon_types_str.strip()) > 0:
                weapon_types_list = [wt.strip() for wt in weapon_types_str.split(",") if wt.strip()]
                if weapon_types_list:
                    placeholders = ",".join(["?"] * len(weapon_types_list))
                    where_clauses.append(f"[weapon_type] IN ({placeholders})")
                    params.extend(weapon_types_list)

            where_clause = " AND ".join(where_clauses) if where_clauses else ""

            try:
                min_on_sale_count = int(min_on_sale_count_str) if min_on_sale_count_str else 100
            except (ValueError, TypeError):
                min_on_sale_count = 100

            records = _query_weapons(
                where_clause,
                tuple(params),
                order_by="CAST([yyyp_Price] AS REAL) ASC",
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
                    "id": str(record.yyyp_id),
                    "name": record.market_listing_item_name or record.weapon_name or "未知饰品",
                }
                for record in filtered_records
            ]

            logger.write_log(
                f"[queryWeaponsByPriceRange] 查询成功 - 返回 {len(results)} 个饰品",
                "INFO",
            )

            return jsonify({"success": True, "data": results, "total": len(results)}), 200

        except Exception as e:
            logger.write_log(f"[queryWeaponsByPriceRange] 查询失败: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return jsonify({
                "success": False,
                "message": f"查询失败: {str(e)}",
                "data": [],
                "total": 0,
            }), 500
