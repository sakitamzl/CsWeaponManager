"""
Inventory 页面价格查询模块
提供通过 steam_hash_name 查询悠悠有品底价、挂件价格及批量挂件数据功能
"""
from flask import jsonify, request
from src.db_manager.index.model.weapon_classID import WeaponClassIDModel


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
            steam_hash_name = data.get('steamHashName', '').strip()

            if not steam_hash_name:
                return jsonify({
                    "success": False,
                    "message": "steamHashName 参数不能为空"
                }), 400

            where_clause = "[steam_hash_name] = ?"
            params = (steam_hash_name,)

            records = WeaponClassIDModel.find_all(
                where=where_clause,
                params=params
            )

            if not records:
                return jsonify({
                    "success": False,
                    "message": f"未找到数据: {steam_hash_name}"
                }), 404

            record = records[0]
            result = {
                'yyyp_Price': record.yyyp_Price,
                'yyyp_Rent': record.yyyp_Rent,
                'weapon_name': record.weapon_name
            }

            return jsonify({
                "success": True,
                "data": result
            }), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                "success": False,
                "message": f"获取挂件价格失败: {str(e)}"
            }), 500

    @staticmethod
    def get_all_pendants():
        """
        获取所有挂件数据（用于预加载到内存字典）
        返回: 所有 weapon_type='挂件' 或 '挂件（纪念品）' 的数据
        """
        try:
            where_clause = "[weapon_type] IN (?, ?)"
            params = ('挂件', '挂件（纪念品）')

            records = WeaponClassIDModel.find_all(
                where=where_clause,
                params=params
            )

            results = []
            filtered_count = 0
            for record in records:
                if record.steam_hash_name:
                    results.append({
                        'steam_hash_name': record.steam_hash_name,
                        'weapon_name': record.weapon_name,
                        'yyyp_Price': record.yyyp_Price,
                        'yyyp_Rent': record.yyyp_Rent
                    })
                else:
                    filtered_count += 1

            return jsonify({
                "success": True,
                "data": results,
                "count": len(results)
            }), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                "success": False,
                "message": f"获取挂件数据失败: {str(e)}"
            }), 500

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
            steam_hash_name = data.get('steamHashName', '').strip()

            if not steam_hash_name:
                return jsonify({
                    "success": False,
                    "message": "steamHashName 参数不能为空"
                }), 400

            records = WeaponClassIDModel.find_by_steam_hash_name(steam_hash_name)

            if not records:
                return jsonify({
                    "success": False,
                    "message": f"未找到数据: {steam_hash_name}"
                }), 404

            record = records[0]

            result = {
                'yyyp_Price': record.yyyp_Price or '0',
                'yyyp_Rent': record.yyyp_Rent or '0',
                'yyyp_OnSaleCount': record.yyyp_OnSaleCount or '0',
                'yyyp_OnLeaseCount': record.yyyp_OnLeaseCount or '0',
                'yyyp_id': str(record.yyyp_id) if record.yyyp_id else None,
                'weapon_name': record.weapon_name,
                'item_name': record.item_name,
                'weapon_type': record.weapon_type,
                'float_range': record.float_range
            }

            return jsonify({
                "success": True,
                "data": result
            }), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                "success": False,
                "message": f"查询悠悠有品底价失败: {str(e)}"
            }), 500
