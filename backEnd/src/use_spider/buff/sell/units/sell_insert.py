"""
BUFF sell 写入模块
提供 Spider 所需的销售记录插入与状态更新接口
"""
import json
from flask import jsonify, request
from src.db_manager.index.model.sell import SellModel
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


class SellInsert:

    @staticmethod
    def insert_db():
        """插入 BUFF 销售记录到 sell 表"""
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
            price_original = data.get('price_original')
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

            print(f"插入BUFF销售记录到sell表，ID: {item_id}, from: buff")
            sell_record = SellModel()
            sell_record.ID = item_id
            sell_record.weapon_name = weaponitem_name
            sell_record.weapon_type = weapon_type
            sell_record.item_name = item_name
            sell_record.weapon_float = weapon_float
            sell_record.float_range = float_range
            sell_record.price = price
            sell_record.price_original = price_original
            sell_record.buyer_name = seller_id
            sell_record.status = state
            sell_record.order_time = created_at
            sell_record.data_user = data_user
            sell_record.status_sub = state_sub
            sell_record.sticker = sticker
            sell_record.pendant = pendant
            sell_record.rename = rename
            sell_record.steam_hash_name = steam_hash_name
            setattr(sell_record, 'from', 'buff')
            sell_saved = sell_record.save()
            print(f"sell表保存结果: {sell_saved}")

            if sell_saved:
                return jsonify({
                    'success': True,
                    'message': 'BUFF销售数据插入成功',
                    'data': {
                        'id': item_id, 'weapon_name': weaponitem_name,
                        'item_name': item_name, 'price': price, 'price_original': price_original
                    }
                }), 200
            else:
                return jsonify({'success': False, 'error': '数据插入失败'}), 500

        except Exception as e:
            print(f"BUFF销售数据插入错误: {str(e)}")
            import traceback
            print(f"详细错误信息: {traceback.format_exc()}")
            return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500

    @staticmethod
    def update_order_status():
        """更新 BUFF 销售订单状态"""
        try:
            data = request.get_json()
            item_id = data['item_id']
            status = data['state']
            status_sub = data.get('state_sub')

            sell_record = SellModel.find_by_id(ID=item_id, **{'from': 'buff'})
            if sell_record:
                sell_record.status = status
                sell_record.status_sub = status_sub
                sell_record.save()
                return jsonify({'success': True, 'message': '更新成功'}), 200
            else:
                return jsonify({'success': False, 'error': '未找到对应的BUFF销售订单'}), 404
        except Exception as e:
            print(f"更新订单状态失败: {e}")
            import traceback
            print(f"详细错误信息: {traceback.format_exc()}")
            return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500
