"""
BUFF buy 写入模块
提供 Spider 所需的购买记录插入与状态更新接口
"""
import json
from flask import jsonify, request
from src.db_manager.index.model.buy import BuyModel
from src.db_manager.index.model.weapon_classID import WeaponClassIDModel


def _process_accessory_data(accessory_json_str, accessory_type):
    """
    处理饰品数据（印花/挂件），为每个饰品添加 steam_hash_name
    :param accessory_json_str: 饰品 JSON 字符串
    :param accessory_type: 饰品类型 '印花' 或 '挂件'
    :return: 处理后的 JSON 字符串
    """
    if not accessory_json_str:
        return None
    try:
        accessories = json.loads(accessory_json_str)
        if not isinstance(accessories, list):
            return accessory_json_str

        for accessory in accessories:
            accessory_name = accessory.get('name')
            if accessory_name:
                if accessory_type == '印花':
                    search_name = f'印花 | {accessory_name}'
                elif accessory_type == '挂件':
                    search_name = f'挂件 | {accessory_name}'
                else:
                    search_name = accessory_name

                records = WeaponClassIDModel.find_by_market_listing_item_name(search_name)
                steam_hash_name = None
                for record in records:
                    if record.weapon_type == accessory_type:
                        steam_hash_name = record.steam_hash_name
                        break

                if accessory_type == '印花' and steam_hash_name:
                    if steam_hash_name.startswith('Sticker | '):
                        steam_hash_name = steam_hash_name[len('Sticker | '):]

                accessory['steam_hash_name'] = steam_hash_name
                if not steam_hash_name:
                    print(f"警告: 未找到{accessory_type}的steam_hash_name: 原名={accessory_name}, 查询名={search_name}")
            else:
                accessory['steam_hash_name'] = None

        return json.dumps(accessories, ensure_ascii=False)
    except Exception as e:
        print(f"处理{accessory_type}数据失败: {e}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        return accessory_json_str


class BuyInsert:

    @staticmethod
    def insert_db():
        """插入 BUFF 购买记录到 buy 表"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': '无效的JSON数据'}), 400

            item_id = data['item_id']
            weapon_type = data['weapon_type']
            item_name = data['item_name']
            weaponitem_name = data['weaponitem_name']
            float_range = data['float_range']
            price = data['price']
            state = data['state']
            state_sub = data['state_sub']
            created_at = data['created_at']
            pay_method_text = data['pay_method_text']
            steam_price_cny = data.get('steam_price_cny')
            seller_id = data['seller_id']
            weapon_float = data['weapon_float']
            data_user = data['data_user']
            sticker = data.get('sticker')
            pendant = data.get('pendant')
            rename = data.get('rename')
            market_hash_name = data.get('market_hash_name')
            img_url = data.get('img_url')

            if sticker:
                sticker = _process_accessory_data(sticker, '印花')
            if pendant:
                pendant = _process_accessory_data(pendant, '挂件')

            steam_hash_name = market_hash_name if market_hash_name else None
            if steam_hash_name is None and img_url:
                steam_hash_name = img_url
                print(f"market_hash_name为空,使用img_url作为steam_hash_name: {img_url}")

            print(f"插入BUFF购买记录到buy表，ID: {item_id}, from: buff")
            buy_record = BuyModel()
            buy_record.ID = item_id
            buy_record.weapon_name = weaponitem_name
            buy_record.weapon_type = weapon_type
            buy_record.item_name = item_name
            buy_record.weapon_float = weapon_float
            buy_record.float_range = float_range
            buy_record.price = price
            buy_record.seller_name = seller_id
            buy_record.status = state
            buy_record.order_time = created_at
            buy_record.payment = pay_method_text
            buy_record.data_user = data_user
            buy_record.status_sub = state_sub
            buy_record.sticker = sticker
            buy_record.pendant = pendant
            buy_record.rename = rename
            buy_record.steam_hash_name = steam_hash_name
            setattr(buy_record, 'from', 'buff')
            buy_saved = buy_record.save()
            print(f"buy表保存结果: {buy_saved}")

            if buy_saved:
                return jsonify({
                    'success': True,
                    'message': 'BUFF购买数据插入成功',
                    'data': {'id': item_id, 'weapon_name': weaponitem_name, 'item_name': item_name, 'price': price}
                }), 200
            else:
                return jsonify({'success': False, 'error': '数据插入失败'}), 500

        except Exception as e:
            print(f"BUFF购买数据插入错误: {str(e)}")
            import traceback
            print(f"详细错误信息: {traceback.format_exc()}")
            return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500

    @staticmethod
    def update_order_status():
        """更新 BUFF 购买订单状态"""
        try:
            data = request.get_json()
            item_id = data['item_id']
            status = data['state']
            status_sub = data.get('state_sub')

            buy_record = BuyModel.find_by_id(ID=item_id, **{'from': 'buff'})
            if buy_record:
                buy_record.status = status
                buy_record.status_sub = status_sub
                buy_record.save()
                return jsonify({'success': True, 'message': '更新成功'}), 200
            else:
                return jsonify({'success': False, 'error': '未找到对应的BUFF购买订单'}), 404
        except Exception as e:
            print(f"更新订单状态失败: {e}")
            import traceback
            print(f"详细错误信息: {traceback.format_exc()}")
            return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500
