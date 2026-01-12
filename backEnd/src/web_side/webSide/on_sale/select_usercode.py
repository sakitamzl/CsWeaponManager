from flask import jsonify, request, Blueprint
from src.db_manager.database import DatabaseManager

webOnSaleV1 = Blueprint('webOnSaleV1', __name__)


@webOnSaleV1.route('/getYYYPAccounts', methods=['GET'])
def get_yyyp_accounts():
    """获取悠悠有品账号列表"""
    try:
        db = DatabaseManager()
        
        # 查询 config 表中 key1='yyyp' AND key2='config' 的记录
        sql = """
        SELECT dataID, dataName, steamID
        FROM config 
        WHERE key1 = 'yyyp' AND key2 = 'config'
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
        
        # TODO: 根据实际的在售商品表结构实现查询
        # 这里返回空数组，等待实际表结构确定后补充
        
        return jsonify({
            'success': True,
            'data': []
        })
    except Exception as e:
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
        item_id = data.get('id')
        
        if not item_id:
            return jsonify({
                'success': False,
                'message': '缺少必要参数: id'
            }), 400
        
        # TODO: 根据实际的在售商品表结构实现下架
        # 这里暂时返回成功，等待实际表结构确定后补充
        
        return jsonify({
            'success': True,
            'message': '下架成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'下架失败: {str(e)}'
        }), 500
