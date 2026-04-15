# -*- coding: utf-8 -*-
"""
挂件搜索 Handler
对应前端页面：SearchPendant
数据库访问统一为参数化 SQL（DatabaseManager）。
"""
import json
from flask import request, jsonify
from src.units.log import Log
from src.db_manager.database import DatabaseManager
from .auto_search_sql import (
    AUTO_SEARCH_TABLE,
    insert_from_search_result,
    select_rows_to_api_dicts,
)

logger = Log()


def _save_search_pendant_config_sql(
    db: DatabaseManager, key1: str, key2: str, value: str, data_name: str = None
) -> bool:
    """等价于 ConfigModel.set_value，使用 SQL upsert。"""
    rows = db.execute_query(
        "SELECT [dataID] FROM config WHERE [key1] = ? AND [key2] = ? LIMIT 1",
        (key1, key2),
    )
    if rows:
        data_id = rows[0][0]
        if data_name:
            db.execute_update(
                "UPDATE config SET [value] = ?, [dataName] = ? WHERE [dataID] = ?",
                (value, data_name, data_id),
            )
        else:
            db.execute_update(
                "UPDATE config SET [value] = ? WHERE [dataID] = ?",
                (value, data_id),
            )
        return True
    db.execute_insert(
        "INSERT INTO config ([key1], [key2], [value], [dataName], [status]) VALUES (?, ?, ?, ?, '1')",
        (key1, key2, value, data_name),
    )
    return True


class SearchPendantHandler:

    @staticmethod
    def save_config():
        """
        保存挂件搜索进度到配置表
        请求体：{ "id": 70, "crawlProgress": { ... } }
        """
        try:
            data = request.get_json() or {}
            config_id = data.get("id") or data.get("configId")
            progress = data.get("crawlProgress")

            if not config_id:
                return jsonify({"success": False, "message": "缺少配置ID"}), 400

            if progress is None:
                progress = {}

            try:
                config_id_str = str(int(config_id))
            except (TypeError, ValueError):
                return jsonify({"success": False, "message": "配置ID必须为整数"}), 400

            try:
                value = json.dumps(progress, ensure_ascii=False)
            except (TypeError, ValueError) as e:
                return jsonify({"success": False, "message": f"进度数据格式错误: {e}"}), 400

            db = DatabaseManager()
            ok = _save_search_pendant_config_sql(
                db,
                key1="search_pendant_progress",
                key2=config_id_str,
                value=value,
                data_name=f"search_pendant_progress_{config_id_str}",
            )

            if not ok:
                return jsonify({"success": False, "message": "保存失败"}), 500

            logger.write_log(
                f"[SearchPendant] 保存进度成功: config_id={config_id_str}, data={value}", "info"
            )
            return jsonify({"success": True, "message": "保存成功"}), 200

        except Exception as e:
            logger.write_log(f"[SearchPendant] 保存进度异常: {str(e)}", "error")
            import traceback

            logger.write_log(traceback.format_exc(), "error")
            return jsonify({"success": False, "message": f"保存失败: {str(e)}"}), 500

    @staticmethod
    def add_item():
        """添加单个挂件搜索结果（Spider 调用）"""
        try:
            data = request.get_json()
            steam_id = data.get("steamId")
            weapon_id = data.get("weaponId")
            weapon_name = data.get("weaponName")
            item_data = data.get("item")
            data_type = data.get("dataType", "pendant")
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
                    f"[SearchPendant] 添加结果: Weapon={weapon_name}, Price={item_data.get('price')}",
                    "INFO",
                )
                return jsonify({"success": True, "itemId": new_id, "message": "添加成功"})
            return jsonify({"success": False, "message": "保存失败"}), 500

        except Exception as e:
            logger.write_log(f"[SearchPendant] 添加结果失败: {str(e)}", "ERROR")
            import traceback

            logger.write_log(f"详细错误: {traceback.format_exc()}", "ERROR")
            return jsonify({"success": False, "message": f"添加失败: {str(e)}"}), 500

    @staticmethod
    def get_items_list():
        """获取挂件搜索结果列表（支持轮询）"""
        try:
            data_type = request.args.get("dataType", "pendant")
            steam_id = request.args.get("steamId")
            config_id = request.args.get("configId")
            status = request.args.get("status", "active")
            limit = request.args.get("limit")
            offset = request.args.get("offset")

            where_clause_parts = ["data_type = ?"]
            params: list = [data_type]

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

            where_and_order = " AND ".join(where_clause_parts) + " ORDER BY spread ASC, id DESC"
            list_limit = int(limit) if limit else None
            list_offset = int(offset) if offset else None

            db = DatabaseManager()
            results = select_rows_to_api_dicts(
                db, where_and_order, tuple(params), limit=list_limit, offset=list_offset
            )

            return jsonify({"success": True, "count": len(results), "items": results})

        except Exception as e:
            logger.write_log(f"[SearchPendant] 查询结果失败: {str(e)}", "ERROR")
            return jsonify({"success": True, "count": 0, "items": [], "error": str(e)})

    @staticmethod
    def update_item_status():
        """更新挂件商品状态"""
        try:
            data = request.get_json()
            commodity_id = data.get("commodityId")
            new_status = data.get("status")

            if not commodity_id or not new_status:
                return jsonify(
                    {"success": False, "message": "缺少必要参数：commodityId 和 status"}
                ), 400

            from datetime import datetime

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
            logger.write_log(f"[SearchPendant] 更新状态失败: {str(e)}", "ERROR")
            return jsonify({"success": False, "message": f"更新失败: {str(e)}"}), 500

    @staticmethod
    def clear_data():
        """清空挂件搜索数据"""
        try:
            data = request.get_json() or {}
            data_type = data.get("dataType", "pendant")
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
            logger.write_log(f"[SearchPendant] 清空数据失败: {str(e)}", "ERROR")
            return jsonify({"success": False, "message": f"清空失败: {str(e)}"}), 500
