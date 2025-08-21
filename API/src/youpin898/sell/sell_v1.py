from flask import jsonify, request, Blueprint
from src.log import Log
from src.execution_db import Date_base
import requests

youpin898SellV1 = Blueprint('youpin898SellV1/<data_user>', __name__)

@youpin898SellV1.route('/selectApexTime', methods=['get'])
def selectApexTime(data_user):
    sql = f"SELECT order_time FROM `yyyp_Sell` WHERE data_user = '{data_user}' ORDER BY order_time DESC LIMIT 1"
    flag, data = Date_base().select(sql)
    data = str(data[0][0])
    return jsonify(data), 200


@youpin898SellV1.route('/insert_webside_selldata', methods=['post'])
def insert_webside_selldata():
    data = request.get_json()
    ID = data['ID']
    weapon_name = data['weapon_name']
    weapon_type = data['weapon_type']
    item_name = data['item_name']
    weapon_float = data['weapon_float']
    float_range = data['float_range']
    price = data['price']
    buyer_user_name = data['buyer_user_name']
    status = data['status']
    data_from = data['from']
    order_time = data['order_time']
    steamid = data['steam_id']
    data_user = data['data_user']
    try:
        sell_number = int(data['sell_number'])
    except TypeError:
        sell_number = "None"
    try:
        err_number = int(data['err_number'])
    except TypeError:
        err_number = "None"

    price_all = data['price_all']


    sql =  (f"INSERT INTO `{data_from}_Sell` "
            f"(`ID`, `weapon_name`, `weapon_type`, `item_name`, `weapon_float`, `float_range`, `price`,"
            f" `buyer_name`, `status`, `from`, `order_time`, `steam_id`, `sell_number`, `err_number`, `price_all`, `data_user`)"
            f" VALUES "
            f"('{ID}','{weapon_name}','{weapon_type}','{item_name}',{weapon_float},'{float_range}',{price},"
            f" '{buyer_user_name}', '{status}', '{data_from}', '{order_time}', '{steamid}',"
            f" '{sell_number}', '{err_number}', {price_all}, '{data_user}');")
    a_status = Date_base().insert(sql)

    if sell_number == 1:
        sql =  (f"INSERT INTO `Sell` "
                f"(`ID`, `weapon_name`, `weapon_type`, `item_name`, `weapon_float`, `float_range`, `price`,"
                f" `buyer_name`,  `status`, `from`, `order_time`, `steam_id`,"
                f" `sell_number`, `err_number`, `price_all` , `data_user`)"
                f" VALUES "
                f"('{ID}','{weapon_name}','{weapon_type}','{item_name}',{weapon_float},'{float_range}',{price},"
                f" '{buyer_user_name}',  '{status}', '{data_from}', '{order_time}', '{steamid}',"
                f" '{sell_number}', '{err_number}', {price_all}, '{data_user}');")
        Date_base().insert(sql)
        
    if a_status == '重复数据':
        insert_status = "重复数据"
    elif a_status:
        insert_status = '写入成功'
    else:
        insert_status = '写入失败'
    return insert_status, 200

@youpin898SellV1.route('/insert_main_selldata', methods=['post'])
def insert_main_selldata():
    data = request.get_json()
    ID = data['ID']
    weapon_name = data['weapon_name']
    weapon_type = data['weapon_type']
    item_name = data['item_name']
    weapon_float = data['weapon_float']
    float_range = data['float_range']
    price = data['price']
    buyer_user_name = data['buyer_user_name']
    status = data['status']
    data_from = data['from']
    order_time = data['order_time']
    steamid = data['steam_id']
    data_user = data['data_user']
    try:
        sell_number = int(data['sell_number'])
    except TypeError:
        sell_number = "None"
    try:
        err_number = int(data['err_number'])
    except TypeError:
        err_number = "None"
    price_all = data['price_all']

    sql =  (f"INSERT INTO `Sell` "
        f"(`ID`, `weapon_name`, `weapon_type`, `item_name`, `weapon_float`, `float_range`, `price`,"
        f" `buyer_name`, `status`, `from`, `order_time`, `steam_id`,"
        f" `sell_number`, `err_number`, `price_all`, `data_user`)"
        f" VALUES "
        f"('{ID}','{weapon_name}','{weapon_type}','{item_name}',{weapon_float},'{float_range}',{price},"
        f" '{buyer_user_name}', '{status}', '{data_from}', '{order_time}', '{steamid}',"
        f" '{sell_number}', '{err_number}', {price_all}, '{data_user}');")
    a_status = Date_base().insert(sql)
    
    if a_status is True:
        insert_status = "写入成功"
    elif a_status == '重复数据':
        insert_status = '重复数据'
    else:
        insert_status = '写入失败'
    return insert_status, 200

@youpin898SellV1.route('/countSellNumber', methods=['get'])
def countSellNumber():
    sql = "SELECT COUNT(*) FROM `sell`"
    result = Date_base().select(sql)
    if result and len(result) == 2:
        flag, data = result
        if flag:
            return jsonify({"count": data[0][0]}), 200
    return "查询失败", 500

@youpin898SellV1.route('/getSellData/<int:min>/<int:max>', methods=['get'])
def getSellData(min, max):
    sql = f"SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, `from`, order_time, status FROM `sell` ORDER BY order_time DESC LIMIT {min}, {max};"
    result = Date_base().select(sql)
    if result and len(result) == 2:
        flag, data = result
        if flag:
            return jsonify(data), 200
    return "查询失败", 500

@youpin898SellV1.route('/selectSellWeaponName/<itemName>', methods=['get'])
def selectSellWeaponName(itemName):
    sql = f"SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, `from`, order_time, status FROM `sell` WHERE item_name LIKE '%{itemName}%' OR weapon_name LIKE '%{itemName}%';"
    result = Date_base().select(sql)
    if result and len(result) == 2:
        flag, data = result
        if flag:
            return jsonify(data), 200
    return "查询失败", 500

@youpin898SellV1.route('/getSellDataByStatus/<status>/<int:min>/<int:max>', methods=['get'])
def getSellDataByStatus(status, min, max):
    if status == 'all':
        sql = f"SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, `from`, order_time, status FROM `sell` ORDER BY order_time DESC LIMIT {min}, {max};"
    else:
        sql = f"SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, `from`, order_time, status FROM `sell` WHERE status = '{status}' ORDER BY order_time DESC LIMIT {min}, {max};"
    result = Date_base().select(sql)
    if result and len(result) == 2:
        flag, data = result
        if flag:
            return jsonify(data), 200
    return "查询失败", 500

