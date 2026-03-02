"""
buy 写入模块
提供 Spider 所需的购买记录插入与状态更新接口
"""
from flask import jsonify, request
from src.db_manager.youpin.model.yyyp_buy import YyypBuyModel
from src.db_manager.index.model.buy import BuyModel


class BuyInsert:

    @staticmethod
    def insert_webside_buydata():
        """插入悠悠有品购买记录（同时写入 yyyp_buy 表；buy_number==1 时也写入 buy 主表）"""
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
            seller_name = data['seller_name']
            status = data['status']
            status_sub = data['status_sub']
            data_from = data['from']
            order_time = data['order_time']
            steamid = data['steam_id']
            data_user = data['data_user']
            try:
                buy_number = int(data['buy_number'])
            except (TypeError, ValueError):
                buy_number = None
            try:
                err_number = int(data['err_number'])
            except (TypeError, ValueError):
                err_number = None
            price_all = data['price_all']
            payment = data['payment']
            tradeType = data['tradeType']
            steam_hash_name = data.get('steam_hash_name')
            sticker = data.get('sticker')
            pendant = data.get('pendant')
            rename = data.get('rename')

            # 插入到 yyyp_buy 表
            print(f"插入悠悠有品购买记录到yyyp_buy表，ID: {ID}")
            yyyp_buy_record = YyypBuyModel()
            yyyp_buy_record.ID = ID
            yyyp_buy_record.weapon_name = weapon_name
            yyyp_buy_record.weapon_type = weapon_type
            yyyp_buy_record.item_name = item_name
            yyyp_buy_record.weapon_float = weapon_float
            yyyp_buy_record.float_range = float_range
            yyyp_buy_record.price = price
            yyyp_buy_record.seller_name = seller_name
            yyyp_buy_record.order_time = order_time
            yyyp_buy_record.status = status
            yyyp_buy_record.status_sub = status_sub
            yyyp_buy_record.steam_id = steamid
            yyyp_buy_record.buy_number = buy_number
            yyyp_buy_record.err_number = err_number
            yyyp_buy_record.price_all = price_all
            yyyp_buy_record.payment = payment
            yyyp_buy_record.trade_type = tradeType
            yyyp_buy_record.data_user = data_user
            setattr(yyyp_buy_record, 'from', 'yyyp')
            yyyp_saved = yyyp_buy_record.save()
            print(f"yyyp_buy表保存结果: {yyyp_saved}")

            # buy_number==1 时同步写入 buy 主表
            buy_saved = True
            if buy_number == 1:
                print(f"插入购买记录到buy表，ID: {ID}")
                buy_record = BuyModel()
                buy_record.ID = ID
                buy_record.weapon_name = weapon_name
                buy_record.weapon_type = weapon_type
                buy_record.item_name = item_name
                buy_record.weapon_float = weapon_float
                buy_record.float_range = float_range
                buy_record.price = price
                buy_record.seller_name = seller_name
                buy_record.status = status
                buy_record.status_sub = status_sub
                buy_record.steam_id = steamid
                buy_record.order_time = order_time
                buy_record.payment = payment
                buy_record.trade_type = tradeType
                buy_record.data_user = data_user
                buy_record.steam_hash_name = steam_hash_name
                buy_record.sticker = sticker
                buy_record.pendant = pendant
                buy_record.rename = rename
                setattr(buy_record, 'from', 'yyyp')
                buy_saved = buy_record.save()
                print(f"buy表保存结果: {buy_saved}")

            if yyyp_saved and buy_saved:
                return jsonify({
                    'success': True,
                    'message': '悠悠有品购买数据插入成功',
                    'data': {'id': ID, 'weapon_name': weapon_name, 'item_name': item_name, 'price': price}
                }), 200
            else:
                return jsonify({'success': False, 'error': '数据插入失败'}), 500

        except Exception as e:
            print(f"悠悠有品购买数据插入错误: {str(e)}")
            import traceback
            print(f"详细错误信息: {traceback.format_exc()}")
            return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500

    @staticmethod
    def insert_main_buydata():
        """插入购买主表记录（仅写入 buy 主表，用于多件订单的子商品）"""
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
            seller_name = data['seller_name']
            status = data['status']
            status_sub = data['status_sub']
            data_from = data['from']
            order_time = data['order_time']
            steamid = data['steam_id']
            payment = data['payment']
            tradeType = data['tradeType']
            data_user = data['data_user']
            steam_hash_name = data.get('steam_hash_name')
            sticker = data.get('sticker')
            pendant = data.get('pendant')
            rename = data.get('rename')

            print(f"插入主购买记录到buy表，ID: {ID}")
            buy_record = BuyModel()
            buy_record.ID = ID
            buy_record.weapon_name = weapon_name
            buy_record.weapon_type = weapon_type
            buy_record.item_name = item_name
            buy_record.weapon_float = weapon_float
            buy_record.float_range = float_range
            buy_record.price = price
            buy_record.seller_name = seller_name
            buy_record.order_time = order_time
            buy_record.status = status
            buy_record.status_sub = status_sub
            buy_record.steam_id = steamid
            buy_record.payment = payment
            buy_record.trade_type = tradeType
            buy_record.data_user = data_user
            buy_record.steam_hash_name = steam_hash_name
            buy_record.sticker = sticker
            buy_record.pendant = pendant
            buy_record.rename = rename
            setattr(buy_record, 'from', 'yyyp')

            buy_saved = buy_record.save()
            print(f"buy表保存结果: {buy_saved}")

            if buy_saved:
                return jsonify({
                    'success': True,
                    'message': '主购买数据插入成功',
                    'data': {'id': ID, 'weapon_name': weapon_name, 'item_name': item_name, 'price': price}
                }), 200
            else:
                return jsonify({'success': False, 'error': '数据插入失败'}), 500

        except Exception as e:
            print(f"主购买数据插入错误: {str(e)}")
            import traceback
            print(f"详细错误信息: {traceback.format_exc()}")
            return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500

    @staticmethod
    def update_buy_data():
        """更新购买订单状态（同时更新 yyyp_buy 和 buy 主表）"""
        try:
            data = request.get_json()
            weapon_ID = data['ID']
            weapon_status = data['weapon_status']
            weapon_status_sub = data.get('weapon_status_sub')

            yyyp_record = YyypBuyModel.find_by_id(ID=weapon_ID)
            if yyyp_record:
                yyyp_record.status = weapon_status
                if weapon_status_sub:
                    yyyp_record.status_sub = weapon_status_sub
                yyyp_saved = yyyp_record.save()
            else:
                return "记录不存在", 404

            buy_records = BuyModel.find_all("ID LIKE ? AND [from] = 'yyyp'", (f"{weapon_ID}%",))
            for buy_record in buy_records:
                buy_record.status = weapon_status
                if weapon_status_sub:
                    buy_record.status_sub = weapon_status_sub
                buy_record.save()

            if yyyp_saved:
                return jsonify({'success': True, 'message': '更新成功'}), 200
            else:
                return jsonify({'success': False, 'error': '更新失败'}), 500

        except Exception as e:
            print(f"更新购买数据失败: {e}")
            return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500

    @staticmethod
    def update_sale_after_withdrawal():
        """检测到卖家报价撤回时更新订单状态（同时更新 yyyp_buy 和 buy 主表）"""
        try:
            data = request.get_json()
            order_no = data.get('orderNo')
            status = data.get('status', '已取消')
            status_sub = data.get('status_sub', '卖家报价撤回')

            if not order_no:
                return jsonify({'success': False, 'error': 'orderNo is required'}), 400

            updated_count = 0

            yyyp_record = YyypBuyModel.find_by_id(ID=order_no)
            if yyyp_record:
                yyyp_record.status = status
                yyyp_record.status_sub = status_sub
                if yyyp_record.save():
                    updated_count += 1
                    print(f"Updated yyyp_buy: {order_no}")

            buy_records = BuyModel.find_all("ID LIKE ? AND [from] = 'yyyp'", (f"{order_no}%",))
            for buy_record in buy_records:
                buy_record.status = status
                buy_record.status_sub = status_sub
                if buy_record.save():
                    updated_count += 1
                    print(f"Updated buy: {buy_record.ID}")

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
