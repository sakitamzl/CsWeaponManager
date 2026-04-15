# -*- coding: utf-8 -*-
"""
改名饰品搜索结果 Handler
对应前端页面：SearchWeaponRename
数据库访问统一为参数化 SQL（DatabaseManager）。
"""
from datetime import datetime, timedelta
from flask import request, jsonify
from src.units.log import Log
from src.db_manager.database import DatabaseManager
from .auto_search_sql import (
    AUTO_SEARCH_TABLE,
    SELECT_AUTO_SEARCH_SQL,
    insert_from_search_result,
    select_rows_to_api_dicts,
    count_rows,
    select_one_by_id,
    row_tuple_to_api_dict,
)

logger = Log()


class SearchRenameHandler:

    @staticmethod
    def add_item():
        """添加单个搜索结果"""
        try:
            data = request.get_json()
            steam_id = data.get("steamId")
            weapon_id = data.get("weaponId")
            weapon_name = data.get("weaponName")
            item_data = data.get("item")
            data_type = data.get("dataType", "rename")
            config_id = data.get("configId")
            pendants = data.get("pendants")
            pendant_count = data.get("pendantCount")
            pendant_total_price = data.get("pendantTotalPrice")
            price_diff_percentage = data.get("priceDiffPercentage")
            total_count = data.get("totalCount")

            if not all([steam_id, weapon_id, weapon_name, item_data]):
                return jsonify({"success": False, "message": "缺少必要参数"}), 400

            config_id_int = None
            if config_id is not None:
                try:
                    config_id_int = int(config_id)
                except (ValueError, TypeError):
                    config_id_int = None

            db = DatabaseManager()
            new_id = insert_from_search_result(
                db,
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
                total_count=total_count,
            )

            if new_id:
                logger.write_log(
                    f"添加搜索结果: Weapon={weapon_name}, Price={item_data.get('price')}, NameTag={item_data.get('nameTag')}",
                    "INFO",
                )
                return jsonify({"success": True, "itemId": new_id, "message": "添加成功"})
            return jsonify({"success": False, "message": "保存失败"}), 500

        except Exception as e:
            logger.write_log(f"添加搜索结果失败: {str(e)}", "ERROR")
            import traceback

            logger.write_log(f"详细错误: {traceback.format_exc()}", "ERROR")
            return jsonify({"success": False, "message": f"添加失败: {str(e)}"}), 500

    @staticmethod
    def get_item(item_id):
        """根据ID获取单个商品信息"""
        try:
            db = DatabaseManager()
            row = select_one_by_id(db, item_id)
            if not row:
                return jsonify({"success": False, "message": f"未找到ID为 {item_id} 的商品"}), 404
            return jsonify({"success": True, "data": row})
        except Exception as e:
            logger.write_log(f"获取商品信息失败: {str(e)}", "ERROR")
            return jsonify({"success": False, "message": f"获取商品信息失败: {str(e)}"}), 500

    @staticmethod
    def update_item_status():
        """更新商品状态"""
        try:
            data = request.get_json()
            commodity_id = data.get("commodityId")
            new_status = data.get("status")

            if not commodity_id or not new_status:
                return jsonify(
                    {"success": False, "message": "缺少必要参数：commodityId 和 status"}
                ), 400

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db = DatabaseManager()
            n = db.execute_update(
                f"UPDATE {AUTO_SEARCH_TABLE} SET status = ?, updated_at = ? "
                "WHERE commodity_id = ? AND status = 'active'",
                (new_status, now, str(commodity_id)),
            )

            if n and n > 0:
                return jsonify(
                    {"success": True, "message": f"状态更新成功，更新了{n}条记录"}
                ), 200
            return jsonify({"success": False, "message": "未找到对应的商品记录"}), 404

        except Exception as e:
            logger.write_log(f"更新商品状态失败: {str(e)}", "ERROR")
            return jsonify({"success": False, "message": f"更新失败: {str(e)}"}), 500

    @staticmethod
    def add_items_batch():
        """批量添加搜索结果"""
        try:
            data = request.get_json()
            steam_id = data.get("steamId")
            items = data.get("items", [])
            data_type = data.get("dataType", "rename")
            config_id = data.get("configId")

            if not all([steam_id, items]):
                return jsonify({"success": False, "message": "缺少必要参数"}), 400

            config_id_int = None
            if config_id is not None:
                try:
                    config_id_int = int(config_id)
                except (ValueError, TypeError):
                    config_id_int = None

            db = DatabaseManager()
            success_count = 0
            for item_wrapper in items:
                try:
                    new_id = insert_from_search_result(
                        db,
                        steam_id=steam_id,
                        weapon_id=item_wrapper.get("weaponId"),
                        weapon_name=item_wrapper.get("weaponName"),
                        item_data=item_wrapper.get("item"),
                        data_type=data_type,
                        config_id=config_id_int,
                        pendant_details=item_wrapper.get("pendants"),
                        pendant_count=item_wrapper.get("pendantCount"),
                        pendant_total_price=item_wrapper.get("pendantTotalPrice"),
                        price_diff_percentage=item_wrapper.get("priceDiffPercentage"),
                    )
                    if new_id:
                        success_count += 1
                except Exception as e:
                    logger.write_log(f"批量添加单项失败: {str(e)}", "WARNING")
                    continue

            return jsonify(
                {
                    "success": True,
                    "count": success_count,
                    "total": len(items),
                    "message": f"批量添加完成，成功{success_count}条",
                }
            )

        except Exception as e:
            logger.write_log(f"批量添加失败: {str(e)}", "ERROR")
            return jsonify({"success": False, "message": f"批量添加失败: {str(e)}"}), 500

    @staticmethod
    def get_items_list():
        """获取搜索结果列表（支持轮询）"""
        try:
            data_type = request.args.get("dataType", "rename")
            steam_id = request.args.get("steamId")
            config_id = request.args.get("configId")
            status = request.args.get("status", "active")
            limit = request.args.get("limit")
            offset = request.args.get("offset")

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

            if data_type == "rename":
                where_clause_parts.append("name_tag IS NOT NULL")

            where_and_order = " AND ".join(where_clause_parts) + " ORDER BY spread ASC, id DESC"
            list_limit = int(limit) if limit else None
            list_offset = int(offset) if offset else None

            db = DatabaseManager()
            results = select_rows_to_api_dicts(
                db, where_and_order, tuple(params), limit=list_limit, offset=list_offset
            )
            return jsonify({"success": True, "count": len(results), "items": results})

        except Exception as e:
            logger.write_log(f"查询搜索结果失败: {str(e)}", "ERROR")
            return jsonify({"success": True, "count": 0, "items": [], "error": str(e)})

    @staticmethod
    def get_items_count():
        """获取搜索结果数量"""
        try:
            data_type = request.args.get("dataType", "rename")
            steam_id = request.args.get("steamId")
            status = request.args.get("status", "active")

            where_clause_parts = ["data_type = ?"]
            params: list = [data_type]

            if steam_id:
                where_clause_parts.append("steam_id = ?")
                params.append(steam_id)
            if status:
                where_clause_parts.append("status = ?")
                params.append(status)
            if data_type == "rename":
                where_clause_parts.append("name_tag IS NOT NULL")

            where_sql = " AND ".join(where_clause_parts)
            db = DatabaseManager()
            cnt = count_rows(db, where_sql, tuple(params))
            return jsonify({"success": True, "count": cnt})

        except Exception as e:
            logger.write_log(f"统计搜索结果失败: {str(e)}", "ERROR")
            return jsonify({"success": False, "message": f"统计失败: {str(e)}"}), 500

    @staticmethod
    def get_latest_items():
        """获取最新的搜索结果"""
        try:
            data_type = request.args.get("dataType", "rename")
            steam_id = request.args.get("steamId")
            limit = int(request.args.get("limit", 20))
            since_id = request.args.get("sinceId")
            status = request.args.get("status", "active")

            where_clause_parts = ["data_type = ?"]
            params: list = [data_type]

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

            where_and_order = " AND ".join(where_clause_parts) + order_clause
            db = DatabaseManager()
            sql = f"{SELECT_AUTO_SEARCH_SQL} WHERE {where_and_order} LIMIT ?"
            rows = db.execute_query(sql, tuple(params) + (limit,))
            items = [row_tuple_to_api_dict(r) for r in rows] if rows else []

            return jsonify({"success": True, "count": len(items), "items": items})

        except Exception as e:
            logger.write_log(f"获取最新结果失败: {str(e)}", "ERROR")
            return jsonify({"success": False, "message": f"获取失败: {str(e)}"}), 500

    @staticmethod
    def clear_data():
        """清空改名饰品数据"""
        try:
            data = request.get_json() or {}
            data_type = data.get("dataType", "rename")
            config_id = data.get("configId")

            db = DatabaseManager()

            where_parts = ["data_type = ?"]
            params: list = [data_type]

            if config_id:
                try:
                    where_parts.append("config_id = ?")
                    params.append(int(config_id))
                except (ValueError, TypeError):
                    pass

            where_clause = " AND ".join(where_parts)
            count_result = db.execute_query(
                f"SELECT COUNT(*) FROM {AUTO_SEARCH_TABLE} WHERE {where_clause}",
                tuple(params),
            )
            count = count_result[0][0] if count_result else 0
            db.execute_update(
                f"DELETE FROM {AUTO_SEARCH_TABLE} WHERE {where_clause}", tuple(params)
            )

            return jsonify(
                {"success": True, "count": count, "message": f"清空成功，删除了{count}条记录"}
            )

        except Exception as e:
            logger.write_log(f"清空数据失败: {str(e)}", "ERROR")
            return jsonify({"success": False, "message": f"清空失败: {str(e)}"}), 500

    @staticmethod
    def cleanup_old_data():
        """清理旧数据（软删除）"""
        try:
            data = request.get_json() or {}
            days = data.get("days", 7)
            cutoff_date = (datetime.now() - timedelta(days=int(days))).strftime("%Y-%m-%d")
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db = DatabaseManager()
            n = db.execute_update(
                f"UPDATE {AUTO_SEARCH_TABLE} SET status = 'deleted', updated_at = ? "
                "WHERE created_at < ? AND status = 'active'",
                (now, cutoff_date),
            )
            count = n if n and n > 0 else 0
            return jsonify(
                {"success": True, "count": count, "message": f"清理了{count}条记录"}
            )
        except Exception as e:
            logger.write_log(f"清理旧数据失败: {str(e)}", "ERROR")
            return jsonify({"success": False, "message": f"清理失败: {str(e)}"}), 500

    @staticmethod
    def get_stats():
        """获取统计信息"""
        try:
            data_type = request.args.get("dataType")
            steam_id = request.args.get("steamId")
            status = request.args.get("status", "active")

            where_clause_parts = []
            params: list = []

            if status:
                where_clause_parts.append("status = ?")
                params.append(status)
            if data_type:
                where_clause_parts.append("data_type = ?")
                params.append(data_type)
            if steam_id:
                where_clause_parts.append("steam_id = ?")
                params.append(steam_id)

            where_sql = " AND ".join(where_clause_parts) if where_clause_parts else "1=1"
            db = DatabaseManager()
            sql = f"""
            SELECT
                COUNT(*) AS total_items,
                COUNT(DISTINCT weapon_id) AS total_weapons,
                COALESCE(AVG(price), 0) AS avg_price,
                COALESCE(AVG(spread), 0) AS avg_spread,
                COALESCE(
                    SUM(CASE WHEN price_diff IS NOT NULL AND price_diff != 0 THEN price_diff ELSE 0 END),
                    0
                ) AS total_profit,
                SUM(CASE WHEN data_type = 'rename' THEN 1 ELSE 0 END) AS rename_items,
                SUM(CASE WHEN data_type = 'pendant' THEN 1 ELSE 0 END) AS pendant_items
            FROM {AUTO_SEARCH_TABLE}
            WHERE {where_sql}
            """
            rows = db.execute_query(sql, tuple(params))
            if not rows or not rows[0]:
                return jsonify(
                    {
                        "success": True,
                        "stats": {
                            "totalItems": 0,
                            "totalWeapons": 0,
                            "avgPrice": 0,
                            "avgSpread": 0,
                            "avgProfit": 0,
                            "totalProfit": 0,
                            "renameItems": 0,
                            "pendantItems": 0,
                        },
                    }
                )

            row = rows[0]
            total_items, total_weapons, avg_price, avg_spread, total_profit, rename_items, pendant_items = row
            total_items = int(total_items or 0)
            total_profit_f = float(total_profit or 0)

            return jsonify(
                {
                    "success": True,
                    "stats": {
                        "totalItems": total_items,
                        "totalWeapons": int(total_weapons or 0),
                        "avgPrice": round(float(avg_price or 0), 2),
                        "avgSpread": round(float(avg_spread or 0), 2),
                        "avgProfit": round(
                            total_profit_f / total_items, 2
                        )
                        if total_items
                        else 0,
                        "totalProfit": round(total_profit_f, 2),
                        "renameItems": int(rename_items or 0),
                        "pendantItems": int(pendant_items or 0),
                    },
                }
            )

        except Exception as e:
            logger.write_log(f"获取统计信息失败: {str(e)}", "ERROR")
            return jsonify({"success": False, "message": f"获取统计失败: {str(e)}"}), 500
