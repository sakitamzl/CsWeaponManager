from flask import jsonify, request, Blueprint
from src.db_manager.database import DatabaseManager
import requests
import json

webOnSaleV1 = Blueprint('webOnSaleV1', __name__)

# Spider服务地址（硬编码，因为后端配置文件中没有这个配置项）
SPIDER_API_ADDRESS = "http://127.0.0.1:9002"


@webOnSaleV1.route('/getYYYPAccounts', methods=['GET'])
def get_yyyp_accounts():
    """获取悠悠有品账号列表"""
    try:
        db = DatabaseManager()
        
        # 查询 config 表中 key1='youpin' AND key2='config' 的记录
        sql = """
        SELECT dataID, dataName, steamID
        FROM config 
        WHERE key1 = 'youpin' AND key2 = 'config'
        ORDER BY dataID
        """
        results = db.execute_query(sql)
        
        accounts = []
        for row in results:
            data_id = row[0]
            data_name = row[1] if row[1] else f"账号{data_id}"
            steam_id = row[2] if len(row) > 2 else None
            
            if not steam_id:
                continue
            
            # 调用Spider服务获取在售数量
            item_count = 0
            try:
                spider_url = f"{SPIDER_API_ADDRESS}/youping898SpiderV1/getSellList"
                spider_response = requests.post(
                    spider_url,
                    json={
                        'steamId': steam_id,
                        'page': 1,
                        'pageSize': 1  # 只获取第一页来统计数量
                    },
                    timeout=10
                )
                
                if spider_response.status_code == 200:
                    spider_data = spider_response.json()
                    if spider_data.get('success'):
                        data = spider_data.get('data', {})
                        statistical_data = data.get('statisticalData', {})
                        item_count = statistical_data.get('quantity', 0)
            except Exception as e:
                print(f"获取账号 {data_id} 在售数量失败: {str(e)}")
                item_count = 0
            
            accounts.append({
                'id': data_id,
                'name': data_name,
                'steam_id': steam_id,
                'item_count': item_count
            })
        
        return jsonify({
            'success': True,
            'data': accounts
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'获取悠悠有品账号列表失败: {str(e)}'
        }), 500


@webOnSaleV1.route('/getBuffAccounts', methods=['GET'])
def get_buff_accounts():
    """获取BUFF账号列表"""
    try:
        db = DatabaseManager()
        
        # 查询 config 表中 key1='buff' AND key2='config' 的记录
        sql = """
        SELECT dataID, dataName, steamID
        FROM config 
        WHERE key1 = 'buff' AND key2 = 'config'
        ORDER BY dataID
        """
        results = db.execute_query(sql)
        
        accounts = []
        for row in results:
            data_id = row[0]
            data_name = row[1] if row[1] else f"账号{data_id}"
            steam_id = row[2] if len(row) > 2 else None
            
            if not steam_id:
                continue
            
            # TODO: 查询该账号在售商品数量（需要根据实际表结构调整）
            # 这里暂时返回0，等待实际表结构确定后补充
            item_count = 0
            
            accounts.append({
                'id': data_id,
                'name': data_name,
                'steam_id': steam_id,
                'item_count': item_count
            })
        
        return jsonify({
            'success': True,
            'data': accounts
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取BUFF账号列表失败: {str(e)}'
        }), 500


@webOnSaleV1.route('/getOnSaleItems', methods=['GET'])
def get_on_sale_items():
    """获取在售商品列表"""
    try:
        platform = request.args.get('platform', '')
        account_id = request.args.get('account_id', '')
        
        if not platform or not account_id:
            return jsonify({
                'success': False,
                'message': '缺少必要参数: platform 和 account_id'
            }), 400
        
        # 只支持悠悠有品平台
        if platform != 'yyyp':
            return jsonify({
                'success': False,
                'message': f'暂不支持 {platform} 平台'
            }), 400
        
        db = DatabaseManager()
        
        # 获取账号配置信息
        config_sql = """
        SELECT steamID
        FROM config 
        WHERE key1 = 'youpin' AND key2 = 'config' AND dataID = ?
        """
        config_result = db.execute_query(config_sql, (account_id,))
        
        if not config_result or len(config_result) == 0:
            return jsonify({
                'success': False,
                'message': '未找到账号配置'
            }), 404
        
        steam_id = config_result[0][0]
        
        # 调用Spider服务获取出售列表
        try:
            spider_url = f"{SPIDER_API_ADDRESS}/youping898SpiderV1/getSellList"
            spider_response = requests.post(
                spider_url,
                json={
                    'steamId': steam_id,
                    'page': 1,
                    'pageSize': 100
                },
                timeout=30
            )
            
            if spider_response.status_code != 200:
                return jsonify({
                    'success': False,
                    'message': f'Spider服务请求失败: HTTP {spider_response.status_code}'
                }), 500
            
            spider_data = spider_response.json()
            
            if not spider_data.get('success'):
                return jsonify({
                    'success': False,
                    'message': spider_data.get('message', '获取出售列表失败')
                }), 500
            
            # 转换数据格式
            data = spider_data.get('data', {})
            commodity_list = data.get('commodityInfoList', [])
            
            items = []
            for commodity in commodity_list:
                steam_asset_id = commodity.get('steamAssetId')
                
                # 通过 steamAssetId 查询购入价格
                buy_price = None
                if steam_asset_id:
                    try:
                        buy_price_sql = """
                        SELECT buy_price
                        FROM steam_inventory
                        WHERE assetid = ?
                        LIMIT 1
                        """
                        buy_price_result = db.execute_query(buy_price_sql, (str(steam_asset_id),))
                        if buy_price_result and len(buy_price_result) > 0:
                            buy_price = buy_price_result[0][0]
                    except Exception as e:
                        print(f"查询购入价格失败 - assetid: {steam_asset_id}, 错误: {str(e)}")
                
                # 获取售价（使用 sellAmountDesc，已经是元为单位）
                sell_amount_desc = commodity.get('sellAmountDesc', '')
                sale_price_str = sell_amount_desc.replace('¥', '').strip() if sell_amount_desc else '0'
                
                try:
                    # sellAmountDesc 格式如 "¥5000"，表示5000元
                    sale_price = float(sale_price_str)
                except:
                    sale_price = 0.0
                
                item = {
                    'id': commodity.get('id'),
                    'item_name': commodity.get('name'),
                    'steam_hash_name': commodity.get('commodityHashName'),
                    'weapon_type': commodity.get('typeName'),
                    'weapon_float': commodity.get('abrade'),
                    'float_range': commodity.get('exteriorName'),
                    'sale_price': sale_price,  # 直接使用 sellAmountDesc，不转换
                    'buy_price': buy_price,  # 从 steam_inventory 表查询
                    'platform': 'yyyp',
                    'account_id': int(account_id),
                    'sticker': json.dumps(commodity.get('stickers', [])),
                    'pendant': json.dumps(commodity.get('pendants', [])) if commodity.get('havePendant') else None,
                    'rename': None,
                    'on_sale_time': None,
                    'steam_asset_id': steam_asset_id,
                    'template_id': commodity.get('templateId'),
                    'img_url': commodity.get('imgUrl'),
                    'status': commodity.get('status'),
                    'paintseed': commodity.get('paintseed')
                }
                
                items.append(item)
            
            return jsonify({
                'success': True,
                'data': items,
                'total': data.get('statisticalData', {}).get('quantity', len(items))
            })
            
        except requests.exceptions.Timeout:
            return jsonify({
                'success': False,
                'message': 'Spider服务请求超时'
            }), 500
        except requests.exceptions.RequestException as e:
            return jsonify({
                'success': False,
                'message': f'Spider服务请求失败: {str(e)}'
            }), 500
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'获取在售商品列表失败: {str(e)}'
        }), 500


@webOnSaleV1.route('/updateSalePrice', methods=['POST'])
def update_sale_price():
    """修改售价"""
    try:
        data = request.get_json()
        item_id = data.get('id')
        new_price = data.get('new_price')
        
        if not item_id or not new_price:
            return jsonify({
                'success': False,
                'message': '缺少必要参数: id 和 new_price'
            }), 400
        
        # TODO: 根据实际的在售商品表结构实现更新
        # 这里暂时返回成功，等待实际表结构确定后补充
        
        return jsonify({
            'success': True,
            'message': '改价成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'改价失败: {str(e)}'
        }), 500


@webOnSaleV1.route('/removeFromSale', methods=['POST'])
def remove_from_sale():
    """下架商品"""
    try:
        data = request.get_json()
        item_id = data.get('id')  # 商品ID（commodity_id）
        account_id = data.get('account_id')  # 账号ID（可选，用于获取steamId）
        
        if not item_id:
            return jsonify({
                'success': False,
                'message': '缺少必要参数: id'
            }), 400
        
        # 如果提供了account_id，从config表获取steamId
        steam_id = None
        if account_id:
            db = DatabaseManager()
            config_sql = """
            SELECT steamID
            FROM config 
            WHERE key1 = 'youpin' AND key2 = 'config' AND dataID = ?
            """
            config_result = db.execute_query(config_sql, (account_id,))
            
            if config_result and len(config_result) > 0:
                steam_id = config_result[0][0]
        
        # 调用Spider服务下架商品
        try:
            spider_url = f"{SPIDER_API_ADDRESS}/youping898SpiderV1/offShelfItems"
            spider_response = requests.post(
                spider_url,
                json={
                    'steamId': steam_id if steam_id else '',
                    'ids': str(item_id)  # 单个ID
                },
                timeout=30
            )
            
            if spider_response.status_code != 200:
                return jsonify({
                    'success': False,
                    'message': f'Spider服务请求失败: HTTP {spider_response.status_code}'
                }), 500
            
            spider_data = spider_response.json()
            
            if spider_data.get('success'):
                return jsonify({
                    'success': True,
                    'message': '下架成功'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': spider_data.get('message', '下架失败')
                }), 400
                
        except requests.exceptions.Timeout:
            return jsonify({
                'success': False,
                'message': 'Spider服务请求超时'
            }), 500
        except requests.exceptions.RequestException as e:
            return jsonify({
                'success': False,
                'message': f'Spider服务请求失败: {str(e)}'
            }), 500
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'下架失败: {str(e)}'
        }), 500
