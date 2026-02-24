"""
Inventory 页面价格查询模块
提供通过 steam_hash_name 查询悠悠有品底价功能
"""
from flask import jsonify, request
from src.db_manager.index.model.weapon_classID import WeaponClassIDModel


class InventoryPrice:

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
