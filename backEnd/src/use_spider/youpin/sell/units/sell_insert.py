"""
sell 写入模块
提供 Spider 所需的销售记录插入与状态更新接口
"""
from flask import jsonify, request
from src.db_manager.youpin.model.yyyp_sell import YyypSellModel
from src.db_manager.index.model.sell import SellModel


class SellInsert:

    @staticmethod
    def insert_webside_selldata():
        """插入悠悠有品销售记录（同时写入 yyyp_sell 表；sell_number==1 时也写入 sell 主表）"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': '无效的JSON数据'}), 400

            ID = data['ID']
            weapon_name = data['weapon_name']
            weapon_type = data['weapon_type']
            item_name = data['item_name']
            weapon_float = data['weapon_float']
            float_range = data['float_range']
            price = data['price']
            price_original = data['price_original']
            buyer_user_name = data['buyer_user_name']
            status = data['status']
            status_sub = data['status_sub']
            data_from = data['from']
            order_time = data['order_time']
            steamid = data['steam_id']
            data_user = data['data_user']

            # 处理 weapon_float 字符串 'NULL' 转换为 None
            if weapon_float == 'NULL':
                weapon_float = None
            elif weapon_float is not None:
                try:
                    weapon_float = float(weapon_float)
                except (ValueError, TypeError):
                    weapon_float = None

            try:
                sell_number = int(data['sell_number'])
            except (TypeError, ValueError):
                sell_number = None
            try:
                err_number = int(data['err_number'])
            except (TypeError, ValueError):
                err_number = None
            price_all = data['price_all']
            steam_hash_name = data.get('steam_hash_name')
            sticker = data.get('sticker')
            pendant = data.get('pendant')
            rename = data.get('rename')

            # 插入到 yyyp_sell 表
            print(f"插入悠悠有品销售记录到yyyp_sell表，ID: {ID}")
            yyyp_sell_record = YyypSellModel()
            yyyp_sell_record.ID = ID
            yyyp_sell_record.weapon_name = weapon_name
            yyyp_sell_record.weapon_type = weapon_type
            yyyp_sell_record.item_name = item_name
            yyyp_sell_record.weapon_float = weapon_float
            yyyp_sell_record.float_range = float_range
            yyyp_sell_record.price = price
            yyyp_sell_record.price_original = price_original
            yyyp_sell_record.buyer_name = buyer_user_name
            yyyp_sell_record.status = status
            yyyp_sell_record.status_sub = status_sub
            yyyp_sell_record.order_time = order_time
            yyyp_sell_record.steam_id = steamid
            yyyp_sell_record.sell_number = sell_number
            yyyp_sell_record.err_number = err_number
            yyyp_sell_record.price_all = price_all
            yyyp_sell_record.data_user = data_user
            setattr(yyyp_sell_record, 'from', 'yyyp')

            yyyp_saved = yyyp_sell_record.save()
            print(f"yyyp_sell表保存结果: {yyyp_saved}")

            # sell_number==1 时同步写入 sell 主表
            sell_saved = True
            if sell_number == 1:
                print(f"插入销售记录到sell表，ID: {ID}")
                sell_record = SellModel()
                sell_record.ID = ID
                sell_record.weapon_name = weapon_name
                sell_record.weapon_type = weapon_type
                sell_record.item_name = item_name
                sell_record.weapon_float = weapon_float
                sell_record.float_range = float_range
                sell_record.price = price
                sell_record.price_original = price_original
                sell_record.buyer_name = buyer_user_name
                sell_record.status = status
                sell_record.status_sub = status_sub
                sell_record.order_time = order_time
                sell_record.steam_id = steamid
                sell_record.data_user = data_user
                sell_record.steam_hash_name = steam_hash_name
                sell_record.sticker = sticker
                sell_record.pendant = pendant
                sell_record.rename = rename
                setattr(sell_record, 'from', 'yyyp')

                sell_saved = sell_record.save()
                print(f"sell表保存结果: {sell_saved}")

            if yyyp_saved and sell_saved:
                return jsonify({
                    'success': True,
                    'message': '悠悠有品销售数据插入成功',
                    'data': {
                        'id': ID, 'weapon_name': weapon_name,
                        'item_name': item_name, 'price': price, 'price_original': price_original
                    }
                }), 200
            else:
                return jsonify({'success': False, 'error': '数据插入失败'}), 500

        except Exception as e:
            print(f"悠悠有品销售数据插入错误: {str(e)}")
            import traceback
            print(f"详细错误信息: {traceback.format_exc()}")
            return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500

    @staticmethod
    def insert_main_selldata():
        """插入销售主表记录（仅写入 sell 主表，用于多件订单的子商品）"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': '无效的JSON数据'}), 400

            ID = data['ID']
            weapon_name = data['weapon_name']
            weapon_type = data['weapon_type']
            item_name = data['item_name']
            weapon_float = data['weapon_float']
            float_range = data['float_range']
            price = data['price']
            price_original = data['price_original']
            buyer_user_name = data['buyer_user_name']
            status = data['status']
            status_sub = data['status_sub']
            data_from = data['from']
            order_time = data['order_time']
            steamid = data['steam_id']
            data_user = data['data_user']
            steam_hash_name = data.get('steam_hash_name')
            sticker = data.get('sticker')
            pendant = data.get('pendant')
            rename = data.get('rename')

            # 处理 weapon_float 字符串 'NULL' 转换为 None
            if weapon_float == 'NULL':
                weapon_float = None
            elif weapon_float is not None:
                try:
                    weapon_float = float(weapon_float)
                except (ValueError, TypeError):
                    weapon_float = None

            print(f"插入主销售记录到sell表，ID: {ID}")
            sell_record = SellModel()
            sell_record.ID = ID
            sell_record.weapon_name = weapon_name
            sell_record.weapon_type = weapon_type
            sell_record.item_name = item_name
            sell_record.weapon_float = weapon_float
            sell_record.float_range = float_range
            sell_record.price = price
            sell_record.price_original = price_original
            sell_record.buyer_name = buyer_user_name
            sell_record.status = status
            sell_record.status_sub = status_sub
            sell_record.order_time = order_time
            sell_record.steam_id = steamid
            sell_record.data_user = data_user
            sell_record.steam_hash_name = steam_hash_name
            sell_record.sticker = sticker
            sell_record.pendant = pendant
            sell_record.rename = rename
            setattr(sell_record, 'from', data_from)

            sell_saved = sell_record.save()
            print(f"sell表保存结果: {sell_saved}")

            if sell_saved:
                return jsonify({
                    'success': True,
                    'message': '主销售数据插入成功',
                    'data': {
                        'id': ID, 'weapon_name': weapon_name,
                        'item_name': item_name, 'price': price, 'price_original': price_original
                    }
                }), 200
            else:
                return jsonify({'success': False, 'error': '数据插入失败'}), 500

        except Exception as e:
            print(f"主销售数据插入错误: {str(e)}")
            import traceback
            print(f"详细错误信息: {traceback.format_exc()}")
            return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500

    @staticmethod
    def update_sell_data():
        """更新销售订单状态（同时更新 yyyp_sell 和 sell 主表）"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': '无效的JSON数据'}), 400

            weapon_ID = data.get('ID')
            weapon_status = data.get('weapon_status')
            weapon_status_sub = data.get('weapon_status_sub')

            if not weapon_ID or not weapon_status:
                return jsonify({'success': False, 'error': '缺少必需参数ID或weapon_status'}), 400

            yyyp_record = YyypSellModel.find_by_id(ID=weapon_ID)
            if yyyp_record:
                yyyp_record.status = weapon_status
                if weapon_status_sub is not None:
                    yyyp_record.status_sub = weapon_status_sub
                yyyp_saved = yyyp_record.save()
                print(f"更新yyyp_sell表成功: ID={weapon_ID}, status={weapon_status}")
            else:
                print(f"yyyp_sell表中未找到记录: ID={weapon_ID}")
                return jsonify({'success': False, 'error': 'yyyp_sell表中记录不存在'}), 404

            sell_records = SellModel.find_all("ID LIKE ? AND \"from\" = 'yyyp'", (f"{weapon_ID}%",))
            sell_updated_count = 0
            for sell_record in sell_records:
                sell_record.status = weapon_status
                if weapon_status_sub is not None:
                    sell_record.status_sub = weapon_status_sub
                sell_record.save()
                sell_updated_count += 1
            print(f"更新通用sell表成功: 共更新{sell_updated_count}条记录")

            if yyyp_saved:
                return jsonify({'success': True, 'message': '更新成功'}), 200
            else:
                return jsonify({'success': False, 'error': '更新失败'}), 500

        except Exception as e:
            print(f"更新销售数据失败: {e}")
            return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500

    @staticmethod
    def update_sale_after_withdrawal():
        """检测到买家报价撤回时更新订单状态（同时更新 yyyp_sell 和 sell 主表）"""
        try:
            data = request.get_json()
            order_no = data.get('orderNo')
            status = data.get('status', '已取消')
            status_sub = data.get('status_sub', '买家报价撤回')

            if not order_no:
                return jsonify({'success': False, 'error': 'orderNo is required'}), 400

            updated_count = 0

            yyyp_record = YyypSellModel.find_by_id(ID=order_no)
            if yyyp_record:
                yyyp_record.status = status
                yyyp_record.status_sub = status_sub
                if yyyp_record.save():
                    updated_count += 1
                    print(f"Updated yyyp_sell: {order_no}")

            sell_records = SellModel.find_all("ID LIKE ? AND \"from\" = 'yyyp'", (f"{order_no}%",))
            for sell_record in sell_records:
                sell_record.status = status
                sell_record.status_sub = status_sub
                if sell_record.save():
                    updated_count += 1
                    print(f"Updated sell: {sell_record.ID}")

            if updated_count > 0:
                return jsonify({
                    'success': True,
                    'message': f'Successfully updated {updated_count} records',
                    'updated_count': updated_count
                }), 200
            else:
                return jsonify({'success': False, 'error': 'No records found to update'}), 404

        except Exception as e:
            print(f"Update sale after withdrawal failed: {e}")
            import traceback
            print(f"Detailed error: {traceback.format_exc()}")
            return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500
