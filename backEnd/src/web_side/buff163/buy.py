from flask import jsonify, request, Blueprint
from src.execution_db import Date_base
from src.db_manager.index.model.buy import BuyModel
from src.db_manager.index.model.weapon_classID import WeaponClassIDModel
import json

buff163BuyV1 = Blueprint('buff163BuyV1', __name__)

def process_accessory_data(accessory_json_str, accessory_type):
    """
    处理饰品数据(印花/挂件),为每个饰品添加steam_hash_name
    :param accessory_json_str: 饰品JSON字符串
    :param accessory_type: 饰品类型 '印花' 或 '挂件'
    :return: 处理后的JSON字符串
    """
    if not accessory_json_str:
        return None

    try:
        accessories = json.loads(accessory_json_str)
        if not isinstance(accessories, list):
            return accessory_json_str

        # 为每个饰品添加steam_hash_name
        for accessory in accessories:
            accessory_name = accessory.get('name')
            if accessory_name:
                # 根据类型添加前缀
                if accessory_type == '印花':
                    search_name = f'印花 | {accessory_name}'
                elif accessory_type == '挂件':
                    search_name = f'挂件 | {accessory_name}'
                else:
                    search_name = accessory_name

                # 查询weapon_classID表: market_listing_item_name = search_name AND weapon_type = accessory_type
                records = WeaponClassIDModel.find_by_market_listing_item_name(search_name)

                # 在结果中查找weapon_type匹配的记录
                steam_hash_name = None
                for record in records:
                    if record.weapon_type == accessory_type:
                        steam_hash_name = record.steam_hash_name
                        break

                # 如果是印花类型，裁剪steam_hash_name前面的"Sticker | "前缀
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

@buff163BuyV1.route('/selectNotEnd/<user_id>', methods=['get'])
def selectNotEnd(user_id):
    """查询BUFF平台未完成的购买订单"""
    try:
        records = BuyModel.find_all(
            "status NOT IN ('已完成', '已取消') AND data_user = ? AND \"from\" = 'buff'",
            (user_id,)
        )
        not_end_orders = [record.ID for record in records]
        return jsonify({"not_end_orders": not_end_orders}), 200
    except Exception as e:
        print(f"查询未完成订单失败: {e}")
        return jsonify({"not_end_orders": []}), 500


@buff163BuyV1.route('/ApexTimeUrl/<user_id>', methods=['get'])
def ApexTimeUrl(user_id):
    """获取BUFF平台最新订单时间"""
    try:
        records = BuyModel.find_all(
            "data_user = ? AND \"from\" = 'buff' ORDER BY order_time DESC",
            (user_id,),
            limit=1
        )
        last_order_time = records[0].order_time if records else None
        return jsonify({"last_order_time": last_order_time}), 200
    except Exception as e:
        print(f"查询最新订单时间失败: {e}")
        return jsonify({"last_order_time": None}), 500

@buff163BuyV1.route('/getLatestData/<user_id>', methods=['GET'])
def getLatestData(user_id):
    """获取指定用户BUFF平台的最新一条购买记录（ID和订单时间）"""
    try:
        records = BuyModel.find_all(
            "data_user = ? AND \"from\" = 'buff' ORDER BY order_time DESC",
            (user_id,),
            limit=1
        )

        if records and len(records) > 0:
            latest_record = records[0]
            return jsonify({
                "ID": latest_record.ID,
                "order_time": latest_record.order_time
            }), 200
        else:
            return jsonify({"ID": None, "order_time": None}), 200
    except Exception as e:
        print(f"获取最新购买数据失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({"ID": None, "order_time": None}), 500

@buff163BuyV1.route('/updateOrderStatus', methods=['post'])
def updateOrderStatus():
    """更新BUFF购买订单状态"""
    try:
        data = request.get_json()
        item_id = data['item_id']
        status = data['state']
        status_sub = data.get('state_sub')

        # 只更新buy表中from='buff'的记录
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

@buff163BuyV1.route('/insert_db', methods=['post'])
def insert_db():
    """插入BUFF购买记录到buy表"""
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
        # 新增字段
        sticker = data.get('sticker')
        pendant = data.get('pendant')
        rename = data.get('rename')
        market_hash_name = data.get('market_hash_name')
        img_url = data.get('img_url')  # 获取图片URL,但不入库,仅用作备用值

        # 处理印花数据,为每个印花添加steam_hash_name
        if sticker:
            sticker = process_accessory_data(sticker, '印花')

        # 处理挂件数据,为每个挂件添加steam_hash_name
        if pendant:
            pendant = process_accessory_data(pendant, '挂件')

        # steam_hash_name直接使用market_hash_name的值
        steam_hash_name = market_hash_name if market_hash_name else None

        # 如果steam_hash_name为None,则使用img_url的值
        if steam_hash_name is None and img_url:
            steam_hash_name = img_url
            print(f"market_hash_name为空,使用img_url作为steam_hash_name: {img_url}")

        # 只插入到buy表
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
        # 新增字段
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
                'data': {
                    'id': item_id,
                    'weapon_name': weaponitem_name,
                    'item_name': item_name,
                    'price': price
                }
            }), 200
        else:
            return jsonify({'success': False, 'error': '数据插入失败'}), 500

    except Exception as e:
        print(f"BUFF购买数据插入错误: {str(e)}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500

@buff163BuyV1.route('/countData/<user_id>', methods=['get'])
def countData(user_id):
    """统计指定用户BUFF平台的购买记录数量"""
    try:
        records = BuyModel.find_all("data_user = ? AND \"from\" = 'buff'", (user_id,))
        count = len(records)
        print(f"BUFF购买记录数量: {count}")
        return jsonify({"count": count}), 200
    except Exception as e:
        print(f"查询数据数量失败: {e}")
        return jsonify({"count": 0}), 500
    
