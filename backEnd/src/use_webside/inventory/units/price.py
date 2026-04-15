"""
Inventory 页面价格查询模块
提供通过 steam_hash_name 查询悠悠有品底价、挂件价格及批量挂件数据功能
数据库访问统一为 DatabaseManager + 参数化 SQL
"""
from flask import jsonify, request
from src.db_manager.database import DatabaseManager

WEAPON_CLASSID_TABLE = "weapon_classID"


class InventoryPrice:

    @staticmethod
    def get_pendant_price():
        """
        通过 steam_hash_name 获取单个挂件价格（悠悠有品平台专用）
        请求体: {"steamHashName": "Charm | Baby's AK"}
        返回: {"success": true, "data": {"yyyp_Price": "10.5", "yyyp_Rent": "5.2", "weapon_name": "宝宝AK"}}
        注意: 使用完全匹配查询，不限制 weapon_type
        """
        try:
            data = request.get_json() or {}
            steam_hash_name = data.get("steamHashName", "").strip()

            if not steam_hash_name:
                return jsonify(
                    {"success": False, "message": "steamHashName 参数不能为空"}
                ), 400

            sql = f"""
            SELECT [yyyp_Price], [yyyp_Rent], [weapon_name]
            FROM {WEAPON_CLASSID_TABLE}
            WHERE [steam_hash_name] = ?
            LIMIT 1
            """
            db = DatabaseManager()
            rows = db.execute_query(sql, (steam_hash_name,))

            if not rows:
                return jsonify(
                    {"success": False, "message": f"未找到数据: {steam_hash_name}"}
                ), 404

            yyyp_price, yyyp_rent, weapon_name = rows[0]
            result = {
                "yyyp_Price": yyyp_price,
                "yyyp_Rent": yyyp_rent,
                "weapon_name": weapon_name,
            }

            return jsonify({"success": True, "data": result}), 200

        except Exception as e:
            import traceback

            traceback.print_exc()
            return jsonify(
                {"success": False, "message": f"获取挂件价格失败: {str(e)}"}
            ), 500

    @staticmethod
    def get_all_pendants():
        """
        获取所有挂件数据（用于预加载到内存字典）
        返回: 所有 weapon_type='挂件' 或 '挂件（纪念品）' 的数据
        """
        try:
            sql = f"""
            SELECT [steam_hash_name], [weapon_name], [yyyp_Price], [yyyp_Rent]
            FROM {WEAPON_CLASSID_TABLE}
            WHERE [weapon_type] IN (?, ?)
              AND [steam_hash_name] IS NOT NULL
              AND TRIM([steam_hash_name]) != ''
            """
            db = DatabaseManager()
            rows = db.execute_query(sql, ("挂件", "挂件（纪念品）"))

            results = []
            for row in rows or []:
                steam_hash_name, weapon_name, yyyp_price, yyyp_rent = row
                results.append(
                    {
                        "steam_hash_name": steam_hash_name,
                        "weapon_name": weapon_name,
                        "yyyp_Price": yyyp_price,
                        "yyyp_Rent": yyyp_rent,
                    }
                )

            return jsonify(
                {"success": True, "data": results, "count": len(results)}
            ), 200

        except Exception as e:
            import traceback

            traceback.print_exc()
            return jsonify(
                {"success": False, "message": f"获取挂件数据失败: {str(e)}"}
            ), 500

    @staticmethod
    def get_yyyp_lowest_price():
        """
        通过 steam_hash_name 获取悠悠有品在售底价

        请求体: {"steamHashName": "AK-47 | 红线 (久经沙场)"}
        返回: {
            "success": true,
            "data": {
                "yyyp_Price": "150.5",
                "yyyp_Rent": "10.2",
                "yyyp_OnSaleCount": "123",
                "yyyp_OnLeaseCount": "45",
                "yyyp_id": "12345",
                "weapon_name": "AK-47",
                "item_name": "红线"
            }
        }
        """
        try:
            data = request.get_json() or {}
            steam_hash_name = data.get("steamHashName", "").strip()

            if not steam_hash_name:
                return jsonify(
                    {"success": False, "message": "steamHashName 参数不能为空"}
                ), 400

            sql = f"""
            SELECT [yyyp_Price], [yyyp_Rent], [yyyp_OnSaleCount], [yyyp_OnLeaseCount],
                   [yyyp_id], [weapon_name], [item_name], [weapon_type], [float_range]
            FROM {WEAPON_CLASSID_TABLE}
            WHERE [steam_hash_name] = ?
            LIMIT 1
            """
            db = DatabaseManager()
            rows = db.execute_query(sql, (steam_hash_name,))

            if not rows:
                return jsonify(
                    {"success": False, "message": f"未找到数据: {steam_hash_name}"}
                ), 404

            (
                yyyp_price,
                yyyp_rent,
                yyyp_on_sale,
                yyyp_on_lease,
                yyyp_id,
                weapon_name,
                item_name,
                weapon_type,
                float_range,
            ) = rows[0]

            result = {
                "yyyp_Price": yyyp_price or "0",
                "yyyp_Rent": yyyp_rent or "0",
                "yyyp_OnSaleCount": yyyp_on_sale or "0",
                "yyyp_OnLeaseCount": yyyp_on_lease or "0",
                "yyyp_id": str(yyyp_id) if yyyp_id is not None else None,
                "weapon_name": weapon_name,
                "item_name": item_name,
                "weapon_type": weapon_type,
                "float_range": float_range,
            }

            return jsonify({"success": True, "data": result}), 200

        except Exception as e:
            import traceback

            traceback.print_exc()
            return jsonify(
                {"success": False, "message": f"查询悠悠有品底价失败: {str(e)}"}
            ), 500
