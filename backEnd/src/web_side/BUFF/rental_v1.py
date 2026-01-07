from flask import jsonify, request, Blueprint
from src.log import Log
from src.execution_db import Date_base
from src.now_time import today
from src.db_manager.manager import RentalModel
import requests

buff163RentalV1 = Blueprint('buff163RentalV1', __name__)

@buff163RentalV1.route('/countData/<data_user>', methods=['GET'])
def countData(data_user):
    """统计指定用户的BUFF租入订单数量"""
    try:
        sql = f"SELECT COUNT(*) FROM rental WHERE data_user = '{data_user}' AND \"from\" = 'buff'"
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag and len(data) > 0:
                count = data[0][0]
                return jsonify({"count": count}), 200
        return jsonify({"count": 0}), 200
    except Exception as e:
        print(f"统计BUFF租入订单数量失败: {e}")
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": "统计失败"}), 500


@buff163RentalV1.route('/insert_db', methods=['POST'])
def insert_db():
    """插入BUFF租入订单数据到rental表"""
    try:
        data = request.get_json()
        
        # 提取数据 - ID是主键，必须提供
        order_id = data.get('order_id', '')  # 订单ID (主键)
        item_id = data.get('item_id', '')
        assetid = data.get('assetid', '')  # Steam资产ID
        classid = data.get('classid', '')  # Steam类别ID
        weapon_type = data.get('weapon_type', '')
        item_name = data.get('item_name', '')
        weapon_name = data.get('weaponitem_name', '')
        float_range = data.get('float_range', '')
        weapon_float = data.get('weapon_float', None)
        rent_unit_price = data.get('rent_unit_price', '')  # 租金/天
        security_price = data.get('security_price', '')  # 押金
        total_rent_price = data.get('total_rent_price', '')  # 总租金
        state = data.get('state', '')
        state_sub = data.get('state_sub', '')
        created_at = data.get('created_at', '')  # 下单时间
        rent_start_time = data.get('rent_start_time', '')  # 租赁开始时间
        rent_end_time = data.get('rent_end_time', '')  # 租赁结束时间
        pay_method_text = data.get('pay_method_text', '')
        steam_price_cny = data.get('steam_price_cny', '')
        seller_id = data.get('seller_id', '')  # 出租人ID
        rent_in_day = data.get('rent_in_day', 0)  # 已租天数
        rented_day = data.get('rented_day', 0)  # 实际租赁天数
        min_rent_out_day = data.get('min_rent_out_day', 0)  # 最小租期
        max_rent_out_day = data.get('max_rent_out_day', 0)  # 最大租期
        data_user = data.get('data_user', '')
        
        # 新增字段
        sticker = data.get('sticker', None)
        pendant = data.get('pendant', None)
        rename = data.get('rename', None)
        market_hash_name = data.get('market_hash_name', '')
        img_url = data.get('img_url', '')
        
        # 查询steam_hash_name - 使用当前服务器地址
        steam_hash_name = None
        if market_hash_name:
            try:
                # 使用request.host_url获取当前backend地址
                from flask import request as flask_request
                base_url = flask_request.host_url.rstrip('/')
                steam_hash_name_url = f"{base_url}/api/weaponV1/getSteamHashName/{market_hash_name}"
                response = requests.get(steam_hash_name_url, timeout=5)
                if response.status_code == 200:
                    result = response.json()
                    steam_hash_name = result.get('steam_hash_name', None)
            except Exception as e:
                print(f"查询steam_hash_name失败: {e}")
                steam_hash_name = None
        
        # 如果查询不到steam_hash_name，使用market_hash_name
        if not steam_hash_name:
            steam_hash_name = market_hash_name
        
        # 插入数据到rental表
        rental_data = {
            'ID': order_id,  # 主键ID
            'item_id': item_id,
            'assetid': assetid,  # Steam资产ID
            'classid': classid,  # Steam类别ID
            'weapon_name': weapon_name,
            'weapon_type': weapon_type,
            'item_name': item_name,
            'weapon_float': weapon_float,
            'float_range': float_range,
            'price': rent_unit_price,  # 日租金
            'security_price': security_price,  # 押金
            'lessor_name': seller_id,  # 出租人ID
            'status': state,
            'last_status': state_sub,
            'from': 'buff',
            'lean_start_time': rent_start_time,
            'lean_end_time': rent_end_time,
            'total_Lease_Days': max_rent_out_day,  # 租期天数 (rent_out_day)
            'max_Lease_Days': max_rent_out_day,  # 最大租期（预留，与total_Lease_Days相同）
            'steam_hash_name': steam_hash_name,
            'sticker': sticker,
            'pendant': pendant,
            'rename': rename,
            'data_user': data_user,
        }
        
        # 使用save()方法而不是insert()
        rental_model = RentalModel(**rental_data)
        result = rental_model.save()
        
        if result:
            return jsonify({"success": True, "message": "数据插入成功"}), 200
        else:
            return jsonify({"success": False, "message": "数据插入失败"}), 500
            
    except Exception as e:
        print(f"插入BUFF租入数据失败: {e}")
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500


@buff163RentalV1.route('/getLatestData/<data_user>', methods=['GET'])
def getLatestData(data_user):
    """获取指定用户最新的BUFF租入订单数据"""
    try:
        sql = f"""
        SELECT ID, lean_start_time 
        FROM rental 
        WHERE data_user = '{data_user}' AND \"from\" = 'buff'
        ORDER BY lean_start_time DESC 
        LIMIT 1
        """
        result = Date_base().select(sql)
        
        if result and len(result) == 2:
            flag, data = result
            if flag and len(data) > 0:
                return jsonify({
                    "ID": data[0][0],
                    "order_time": data[0][1]
                }), 200
        
        return jsonify({"message": "数据库为空，请先执行全量采集"}), 200
        
    except Exception as e:
        print(f"获取最新BUFF租入数据失败: {e}")
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@buff163RentalV1.route('/selectNotEnd/<data_user>', methods=['GET'])
def selectNotEnd(data_user):
    """查询指定用户未结束的BUFF租入订单（状态不是'已完成'和'已取消'）"""
    try:
        sql = f"""
        SELECT ID 
        FROM rental 
        WHERE data_user = '{data_user}' 
            AND \"from\" = 'buff'
            AND status NOT IN ('已完成', '已取消')
        ORDER BY lean_start_time DESC
        """
        result = Date_base().select(sql)
        
        if result and len(result) == 2:
            flag, data = result
            if flag:
                order_ids = [row[0] for row in data]
                return jsonify({"not_end_orders": order_ids}), 200
        
        return jsonify({"not_end_orders": []}), 200
        
    except Exception as e:
        print(f"查询未结束BUFF租入订单失败: {e}")
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@buff163RentalV1.route('/updateOrderStatus', methods=['POST'])
def updateOrderStatus():
    """更新BUFF租入订单状态"""
    try:
        data = request.get_json()
        order_id = data.get('order_id', '')  # 使用order_id作为主键
        state = data.get('state', '')
        state_sub = data.get('state_sub', '')
        
        if not order_id:
            return jsonify({"success": False, "error": "订单ID不能为空"}), 400
        
        sql = f"""
        UPDATE rental 
        SET status = '{state}', last_status = '{state_sub}'
        WHERE ID = '{order_id}' AND \"from\" = 'buff'
        """
        
        result = Date_base().update(sql)
        
        if result:
            return jsonify({"success": True, "message": "状态更新成功"}), 200
        else:
            return jsonify({"success": False, "error": "状态更新失败"}), 500
            
    except Exception as e:
        print(f"更新BUFF租入订单状态失败: {e}")
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500
