from flask import jsonify, request, Blueprint
from src.db_manager.index.model.weapon_classID import WeaponClassIDModel
from src.log import Log

logger = Log()
webSelectWeaponV1 = Blueprint('webSelectWeaponV1', __name__)

@webSelectWeaponV1.route('/getPendantPrice', methods=['POST'])
def getPendantPrice():
    """
    通过 steam_hash_name 获取单个挂件价格（悠悠有品平台专用）
    请求体: {"steamHashName": "Charm | Baby's AK"}
    返回: {"success": true, "data": {"yyyp_Price": "10.5", "yyyp_Rent": "5.2", "weapon_name": "宝宝AK"}}
    注意: 使用完全匹配查询，不限制 weapon_type
    """
    try:
        data = request.get_json() or {}
        steam_hash_name = data.get('steamHashName', '').strip()
        
        if not steam_hash_name:
            return jsonify({
                "success": False,
                "message": "steamHashName 参数不能为空"
            }), 400
        
        # 只通过 steam_hash_name 完全匹配查询，不限制 weapon_type
        where_clause = "[steam_hash_name] = ?"
        params = (steam_hash_name,)
        
        records = WeaponClassIDModel.find_all(
            where=where_clause, 
            params=params
        )
        
        if not records:
            logger.write_log(f"[getPendantPrice] 未找到数据: {steam_hash_name}", 'WARNING')
            return jsonify({
                "success": False,
                "message": f"未找到数据: {steam_hash_name}"
            }), 404
        
        # 取第一条记录
        record = records[0]
        
        result = {
            'yyyp_Price': record.yyyp_Price,
            'yyyp_Rent': record.yyyp_Rent,
            'weapon_name': record.weapon_name
        }
        
        logger.write_log(f"[getPendantPrice] 查询成功: {steam_hash_name} -> yyyp_Price={result['yyyp_Price']}, yyyp_Rent={result['yyyp_Rent']}", 'INFO')
        
        return jsonify({
            "success": True,
            "data": result
        }), 200
        
    except Exception as e:
        logger.write_log(f"获取挂件价格失败: {e}", 'ERROR')
        import traceback
        logger.write_log(f"错误堆栈: {traceback.format_exc()}", 'ERROR')
        return jsonify({
            "success": False,
            "message": f"获取挂件价格失败: {str(e)}"
        }), 500


@webSelectWeaponV1.route('/getYYYPLowestPrice', methods=['POST'])
def getYYYPLowestPrice():
    """
    通过 steam_hash_name 获取悠悠有品在售底价
    
    请求体: {"steamHashName": "AK-47 | 红线 (久经沙场)"}
    返回: {
        "success": true, 
        "data": {
            "yyyp_Price": "150.5",  # 在售底价
            "yyyp_Rent": "10.2",    # 租赁底价
            "yyyp_OnSaleCount": "123",  # 在售数量
            "yyyp_OnLeaseCount": "45",  # 出租数量
            "yyyp_id": "12345",     # 悠悠有品ID
            "weapon_name": "AK-47",
            "item_name": "红线"
        }
    }
    
    逻辑：
    1. 通过 steam_hash_name 在 weapon_classID 表中查询
    2. 获取 yyyp_id
    3. 返回 yyyp_Price (在售底价) 和其他相关信息
    """
    try:
        data = request.get_json() or {}
        steam_hash_name = data.get('steamHashName', '').strip()
        
        if not steam_hash_name:
            return jsonify({
                "success": False,
                "message": "steamHashName 参数不能为空"
            }), 400
        
        # 通过 steam_hash_name 查询
        records = WeaponClassIDModel.find_by_steam_hash_name(steam_hash_name)
        
        if not records:
            logger.write_log(f"[getYYYPLowestPrice] 未找到数据: {steam_hash_name}", 'WARNING')
            return jsonify({
                "success": False,
                "message": f"未找到数据: {steam_hash_name}"
            }), 404
        
        # 取第一条记录
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
        
        logger.write_log(
            f"[getYYYPLowestPrice] 查询成功: {steam_hash_name} -> "
            f"yyyp_id={result['yyyp_id']}, "
            f"yyyp_Price={result['yyyp_Price']}, "
            f"在售数量={result['yyyp_OnSaleCount']}", 
            'INFO'
        )
        
        return jsonify({
            "success": True,
            "data": result
        }), 200
        
    except Exception as e:
        logger.write_log(f"获取悠悠在售底价失败: {e}", 'ERROR')
        import traceback
        logger.write_log(f"错误堆栈: {traceback.format_exc()}", 'ERROR')
        return jsonify({
            "success": False,
            "message": f"获取悠悠在售底价失败: {str(e)}"
        }), 500


@webSelectWeaponV1.route('/getAllPendants', methods=['GET'])
def getAllPendants():
    """
    获取所有挂件数据（用于预加载到内存字典）
    返回: 所有 weapon_type='挂件' 或 '挂件（纪念品）' 的数据，包含 steam_hash_name, weapon_name, yyyp_Price, yyyp_Rent
    """
    try:
        # 查询所有挂件数据（包括普通挂件和纪念品挂件）
        where_clause = "[weapon_type] IN (?, ?)"
        params = ('挂件', '挂件（纪念品）')
        
        print(f"[getAllPendants] 开始查询挂件数据: where={where_clause}, params={params}")
        
        records = WeaponClassIDModel.find_all(
            where=where_clause, 
            params=params
        )
        
        print(f"[getAllPendants] 查询到 {len(records)} 条记录（包含普通挂件和纪念品挂件）")
        
        # 构建返回数据
        results = []
        filtered_count = 0
        
        for record in records:
            if record.steam_hash_name:  # 必须有 steam_hash_name
                results.append({
                    'steam_hash_name': record.steam_hash_name,
                    'weapon_name': record.weapon_name,
                    'yyyp_Price': record.yyyp_Price,
                    'yyyp_Rent': record.yyyp_Rent
                })
            else:
                filtered_count += 1
        
        print(f"[getAllPendants] 返回 {len(results)} 条数据，过滤掉 {filtered_count} 条无 steam_hash_name 的数据")
        
        # 打印前3条数据作为示例
        for i, item in enumerate(results[:3]):
            print(f"[getAllPendants] 示例 {i+1}: {item}")
        
        return jsonify({
            "success": True,
            "data": results,
            "count": len(results)
        }), 200
        
    except Exception as e:
        print(f"获取挂件数据失败: {e}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": f"获取挂件数据失败: {str(e)}"
        }), 500

@webSelectWeaponV1.route('/searchWeapon', methods=['GET'])
def searchWeapon():
    """
    根据market_listing_item_name或steam_hash_name模糊搜索武器（用于自动完成下拉框）
    参数: keyword - 搜索关键词
    返回: 匹配的武器名称列表（仅market_listing_item_name字段，限制20条）
    """
    try:
        keyword = request.args.get('keyword', '')

        if not keyword or len(keyword.strip()) == 0:
            return jsonify({
                "success": True,
                "data": []
            }), 200

        # 使用LIKE进行模糊查询，同时搜索 market_listing_item_name 和 steam_hash_name
        where_clause = "([market_listing_item_name] LIKE ? OR [steam_hash_name] LIKE ?)"
        params = (f"%{keyword}%", f"%{keyword}%")
        
        # 查询数据库，限制返回20条用于下拉建议
        records = WeaponClassIDModel.find_all(
            where=where_clause, 
            params=params,
            limit=20
        )
        
        # 提取market_listing_item_name字段
        results = []
        seen = set()  # 下拉框去重，避免重复显示
        for record in records:
            name = record.market_listing_item_name
            if name and name not in seen:
                results.append(name)
                seen.add(name)
        
        return jsonify({
            "success": True,
            "data": results
        }), 200
        
    except Exception as e:
        print(f"搜索武器失败: {e}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "error": str(e),
            "data": []
        }), 500


@webSelectWeaponV1.route('/getWeaponNames', methods=['GET'])
def getWeaponNames():
    """
    根据武器类型获取该类型下的所有武器名称（去重）
    参数: weaponType - 武器类型（可选，不传则返回所有武器名称）
    返回: 武器名称列表
    """
    try:
        weapon_type = request.args.get('weaponType', '')
        
        # 如果指定了武器类型，查询该类型；否则查询所有
        if weapon_type and len(weapon_type.strip()) > 0:
            # 查询该武器类型下的所有记录
            where_clause = "[weapon_type] = ?"
            params = (weapon_type.strip(),)
            
            records = WeaponClassIDModel.find_all(
                where=where_clause, 
                params=params
            )
        else:
            # 查询所有武器名称
            records = WeaponClassIDModel.find_all()
        
        # 提取并去重武器名称
        weapon_names = set()
        for record in records:
            if record.weapon_name and record.weapon_name.strip():
                weapon_names.add(record.weapon_name.strip())
        
        # 转换为排序列表
        weapon_names_list = sorted(list(weapon_names))
        
        print(f"[getWeaponNames] 武器类型: {weapon_type or '全部'}, 返回 {len(weapon_names_list)} 个武器名称")
        
        return jsonify({
            "success": True,
            "data": weapon_names_list
        }), 200
        
    except Exception as e:
        print(f"获取武器名称失败: {e}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "error": str(e),
            "data": []
        }), 500


@webSelectWeaponV1.route('/searchWeaponDetail', methods=['GET'])
def searchWeaponDetail():
    """
    根据market_listing_item_name搜索武器详细信息（用于表格展示）
    参数:
        platformType - 平台类型：youpin 或 buff（必填）
        keyword - 搜索关键词（可选）
        exactMatch - 是否精确匹配（可选，默认false，true时使用=，false时使用LIKE）
        weaponType - 武器类型筛选（可选）
        weaponName - 武器名称筛选（可选）
        rarity - 稀有度筛选（可选）
        priceMin - 最低价格（可选）
        priceMax - 最高价格（可选）
        minOnSaleCount - 最小在售数量（可选）
        page - 页码（可选，默认1）
        limit - 每页数量（可选，默认50）
        如果所有参数都为空，则返回全部数据
    返回: 匹配的武器完整信息列表（按价格正序排序）
    """
    try:
        platform_type = request.args.get('platformType', 'youpin')
        keyword = request.args.get('keyword', '')
        exact_match = request.args.get('exactMatch', 'false').lower() == 'true'
        weapon_type = request.args.get('weaponType', '')
        weapon_name = request.args.get('weaponName', '')
        rarity = request.args.get('rarity', '')
        price_min = request.args.get('priceMin', '')
        price_max = request.args.get('priceMax', '')
        min_on_sale_count = request.args.get('minOnSaleCount', '')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))

        # 构建查询条件
        where_clauses = []
        params = []

        # 如果提供了关键词，根据 exactMatch 参数选择查询方式
        if keyword and len(keyword.strip()) > 0:
            if exact_match:
                # 精确匹配（用于URL参数跳转）
                where_clauses.append("([market_listing_item_name] = ? OR [steam_hash_name] = ?)")
                params.append(keyword.strip())
                params.append(keyword.strip())
            else:
                # 模糊匹配（用于输入框搜索）
                where_clauses.append("([market_listing_item_name] LIKE ? OR [steam_hash_name] LIKE ?)")
                params.append(f"%{keyword.strip()}%")
                params.append(f"%{keyword.strip()}%")
        
        # 如果指定了武器类型
        if weapon_type and len(weapon_type.strip()) > 0:
            where_clauses.append("[weapon_type] = ?")
            params.append(weapon_type.strip())
        
        # 如果指定了武器名称
        if weapon_name and len(weapon_name.strip()) > 0:
            where_clauses.append("[weapon_name] = ?")
            params.append(weapon_name.strip())
        
        # 如果指定了稀有度
        if rarity and len(rarity.strip()) > 0:
            where_clauses.append("[Rarity] = ?")
            params.append(rarity.strip())
        
        # 组合查询条件（如果没有任何条件，where_clause为None，返回全部数据）
        where_clause = " AND ".join(where_clauses) if where_clauses else None
        
        # 如果是Steam平台，要求必须存在hash name
        if platform_type == 'steam':
            extra_clause = "[steam_hash_name] IS NOT NULL AND [steam_hash_name] <> ''"
            if where_clause:
                where_clause = f"{where_clause} AND {extra_clause}"
            else:
                where_clause = extra_clause
        
        # 根据平台类型确定价格字段用于排序
        price_field = 'yyyp_Price' if platform_type == 'youpin' else 'buff_Price'
        
        # 查询数据库，返回所有匹配的记录，并按价格降序排序（价格高的在前）
        records = WeaponClassIDModel.find_all(
            where=where_clause, 
            params=tuple(params) if params else None,
            order_by=f"CAST([{price_field}] AS REAL) DESC"
        )
        
        # 价格筛选、在售数量筛选以及自动过滤
        # 根据平台类型选择对应的价格字段和在售数量字段
        if platform_type == 'steam':
            price_field = 'yyyp_Price'
            on_sale_count_field = 'yyyp_OnSaleCount'
        else:
            price_field = 'yyyp_Price' if platform_type == 'youpin' else 'buff_Price'
            on_sale_count_field = 'yyyp_OnSaleCount' if platform_type == 'youpin' else 'buff_OnSaleCount'
        
        filtered_records = []
        for record in records:
            # 1. 默认过滤：价格 < 1 的数据不查询
            price_str = getattr(record, price_field, None)
            if price_str:
                try:
                    price = float(price_str)
                    if price < 1:
                        continue  # 跳过价格小于1的记录
                except (ValueError, TypeError):
                    continue  # 价格无法解析的跳过
            else:
                continue  # 没有价格的跳过
            
            # 2. 默认过滤：在售数量 < 10 的数据不查询
            on_sale_count_str = getattr(record, on_sale_count_field, None)
            if on_sale_count_str:
                try:
                    on_sale_count = int(on_sale_count_str)
                    if on_sale_count < 10:
                        continue  # 跳过在售数量小于10的记录
                except (ValueError, TypeError):
                    continue  # 在售数量无法解析的跳过
            else:
                continue  # 没有在售数量的跳过
            
            # 3. 用户指定的价格筛选（价格已在步骤1中获取）
            if price_min or price_max:
                # 检查价格区间
                if price_min and price < float(price_min):
                    continue
                if price_max and price > float(price_max):
                    continue
            
            # 4. 用户指定的在售数量筛选（在售数量已在步骤2中获取）
            if min_on_sale_count:
                # 检查在售数量是否满足用户指定的最小值
                if on_sale_count < int(min_on_sale_count):
                    continue
            
            filtered_records.append(record)
        
        records = filtered_records
        
        # 分页处理
        total_count = len(records)
        start_index = (page - 1) * limit
        end_index = start_index + limit
        paginated_records = records[start_index:end_index]
        
        # 返回完整的武器信息
        results = []
        for record in paginated_records:
            weapon_data = {
                'steam_hash_name': record.steam_hash_name,
                'market_listing_item_name': record.market_listing_item_name,
                'yyyp_id': record.yyyp_id,
                'buff_id': record.buff_id,
                'steam_id': record.steam_id,
                'yyyp_class_name': record.yyyp_class_name,
                'buff_class_name': record.buff_class_name,
                'weapon_type': record.weapon_type,
                'weapon_name': record.weapon_name,
                'item_name': record.item_name,
                'float_range': record.float_range,
                'Rarity': record.Rarity,
                'yyyp_Price': record.yyyp_Price,
                'buff_Price': record.buff_Price,
                'yyyp_OnSaleCount': record.yyyp_OnSaleCount,
                'buff_OnSaleCount': record.buff_OnSaleCount
            }
            results.append(weapon_data)
        
        return jsonify({
            "success": True,
            "data": results,
            "count": len(results),
            "total": total_count,
            "page": page,
            "limit": limit
        }), 200
        
    except Exception as e:
        print(f"搜索武器详情失败: {e}")
        import traceback
        print(f"错误堆栈: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "error": str(e),
            "data": [],
            "count": 0
        }), 500


@webSelectWeaponV1.route('/getReferencePrices', methods=['POST'])
def get_reference_prices():
    """
    批量查询参考价（通过 steam_hash_name 列表）
    
    请求体:
    {
        "steamHashNames": ["AK-47 | Redline (Field-Tested)", ...]
    }
    
    返回:
    {
        "success": true,
        "data": {
            "steam_hash_name_1": "120.00",
            "steam_hash_name_2": "150.00",
            ...
        }
    }
    """
    try:
        data = request.get_json() or {}
        steam_hash_names = data.get('steamHashNames', [])
        reference_price_source = data.get('referencePriceSource', 'youpin')
        reference_price_source = (reference_price_source or '').strip().lower()
        if reference_price_source not in ('youpin', 'buff'):
            reference_price_source = 'youpin'
        
        if not steam_hash_names:
            return jsonify({
                'success': True,
                'data': {}
            })
        
        # 构建查询条件
        placeholders = ','.join(['?' for _ in steam_hash_names])
        where_clause = f"[steam_hash_name] IN ({placeholders})"
        
        # 查询记录
        records = WeaponClassIDModel.find_all(
            where=where_clause,
            params=tuple(steam_hash_names)
        )
        
        # 构建返回数据：steam_hash_name -> yyyp_Price 的映射
        price_field = 'yyyp_Price' if reference_price_source == 'youpin' else 'buff_Price'

        price_map = {}
        for record in records:
            hash_name = record.steam_hash_name
            if not hash_name:
                continue
            raw_value = getattr(record, price_field, None)
            if raw_value in (None, '', 'None'):
                price_map[hash_name] = 0
                continue
            try:
                price_value = float(raw_value)
            except (ValueError, TypeError):
                price_value = 0
            price_map[hash_name] = price_value
        
        logger.write_log(
            f"批量查询参考价({reference_price_source}): 请求{len(steam_hash_names)}个，找到{len(price_map)}个",
            'INFO'
        )
        
        return jsonify({
            'success': True,
            'data': price_map
        })
    
    except Exception as e:
        logger.write_log(f"批量查询参考价失败: {str(e)}", 'ERROR')
        import traceback
        logger.write_log(f"详细错误: {traceback.format_exc()}", 'ERROR')
        return jsonify({
            'success': False,
            'error': str(e),
            'data': {}
        }), 500



@webSelectWeaponV1.route('/csqaq_id', methods=['POST'])
def get_csqaq_id():
    """
    通过 market_listing_item_name 查询 csqaq_id

    请求体: {"market_listing_item_name": "P2000 | Dispatch (Factory New)"}
    返回: {
        "success": true,
        "csqaq_id": 16550
    }
    """
    try:
        data = request.get_json() or {}
        market_listing_item_name = data.get('market_listing_item_name', '').strip()

        if not market_listing_item_name:
            return jsonify({
                "success": False,
                "message": "market_listing_item_name 参数不能为空"
            }), 400

        # 通过 market_listing_item_name 查询
        records = WeaponClassIDModel.find_by_market_listing_item_name(market_listing_item_name)

        if not records:
            logger.write_log(f"[get_csqaq_id] 未找到数据: {market_listing_item_name}", 'WARNING')
            return jsonify({
                "success": False,
                "message": f"未找到数据: {market_listing_item_name}"
            }), 404

        # 取第一条记录
        record = records[0]

        if not record.csqaq_id:
            logger.write_log(f"[get_csqaq_id] 该武器没有 csqaq_id: {market_listing_item_name}", 'WARNING')
            return jsonify({
                "success": False,
                "message": f"该武器没有对应的 CSQAQ ID"
            }), 404

        logger.write_log(
            f"[get_csqaq_id] 查询成功: {market_listing_item_name} -> csqaq_id={record.csqaq_id}",
            'INFO'
        )

        return jsonify({
            "success": True,
            "csqaq_id": record.csqaq_id
        }), 200

    except Exception as e:
        logger.write_log(f"获取 csqaq_id 失败: {e}", 'ERROR')
        import traceback
        logger.write_log(f"错误堆栈: {traceback.format_exc()}", 'ERROR')
        return jsonify({
            "success": False,
            "message": f"获取 csqaq_id 失败: {str(e)}"
        }), 500


@webSelectWeaponV1.route('/queryWeaponsByPriceRange', methods=['GET'])
def queryWeaponsByPriceRange():
    """
    根据价格区间和武器类型查询武器ID列表（用于挂件搜索的按价格区间查询模式）

    参数:
        price_min - 最低价格（可选，使用yyyp_price字段）
        price_max - 最高价格（可选，使用yyyp_price字段）
        weapon_types - 武器类型列表，逗号分隔（可选，例如: "手枪,步枪,冲锋枪"）
        min_on_sale_count - 最小在售数量（可选，默认10）

    返回:
        {
            "success": true,
            "data": [
                {"id": "61490", "name": "AK-47 | 红线 (久经沙场)"},
                ...
            ],
            "total": 100
        }

    逻辑：
        1. 根据price_min和price_max过滤yyyp_price字段
        2. 根据weapon_types过滤weapon_type字段（手枪、步枪、冲锋枪、散弹枪、机枪）
        3. 自动过滤：价格 >= 1 且在售数量 >= min_on_sale_count（默认10）
        4. 返回 yyyp_id 和 market_listing_item_name
    """
    try:
        price_min = request.args.get('price_min', '')
        price_max = request.args.get('price_max', '')
        weapon_types_str = request.args.get('weapon_types', '')
        min_on_sale_count_str = request.args.get('min_on_sale_count', '100')

        # 构建查询条件
        where_clauses = []
        params = []

        # 武器类型过滤（多选）
        if weapon_types_str and len(weapon_types_str.strip()) > 0:
            weapon_types_list = [wt.strip() for wt in weapon_types_str.split(',') if wt.strip()]
            if weapon_types_list:
                placeholders = ','.join(['?' for _ in weapon_types_list])
                where_clauses.append(f"[weapon_type] IN ({placeholders})")
                params.extend(weapon_types_list)

        # 组合查询条件
        where_clause = " AND ".join(where_clauses) if where_clauses else None

        # 解析最小在售数量参数
        try:
            min_on_sale_count = int(min_on_sale_count_str) if min_on_sale_count_str else 100
        except (ValueError, TypeError):
            min_on_sale_count = 100

        logger.write_log(
            f"[queryWeaponsByPriceRange] 开始查询 - "
            f"price_min={price_min}, price_max={price_max}, "
            f"weapon_types={weapon_types_str}, min_on_sale_count={min_on_sale_count}",
            'INFO'
        )

        # 查询数据库
        records = WeaponClassIDModel.find_all(
            where=where_clause,
            params=tuple(params) if params else None,
            order_by="CAST([yyyp_Price] AS REAL) ASC"  # 按价格升序
        )

        logger.write_log(f"[queryWeaponsByPriceRange] 初步查询到 {len(records)} 条记录", 'INFO')

        # 价格区间过滤和自动过滤
        filtered_records = []
        for record in records:
            # 1. 自动过滤：价格 >= 1
            price_str = record.yyyp_Price
            if price_str:
                try:
                    price = float(price_str)
                    if price < 1:
                        continue
                except (ValueError, TypeError):
                    continue
            else:
                continue

            # 2. 用户指定的价格区间过滤
            if price_min:
                try:
                    if price < float(price_min):
                        continue
                except (ValueError, TypeError):
                    pass

            if price_max:
                try:
                    if price > float(price_max):
                        continue
                except (ValueError, TypeError):
                    pass

            # 3. 用户指定的在售数量过滤（最小在售数量）
            on_sale_count_str = record.yyyp_OnSaleCount
            if on_sale_count_str:
                try:
                    on_sale_count = int(on_sale_count_str)
                    if on_sale_count < min_on_sale_count:
                        continue
                except (ValueError, TypeError):
                    continue
            else:
                continue

            # 4. 必须有yyyp_id
            if not record.yyyp_id:
                continue

            filtered_records.append(record)

        logger.write_log(
            f"[queryWeaponsByPriceRange] 过滤后剩余 {len(filtered_records)} 条记录",
            'INFO'
        )

        # 构建返回数据
        results = []
        for record in filtered_records:
            results.append({
                'id': str(record.yyyp_id),
                'name': record.market_listing_item_name or record.weapon_name or '未知饰品'
            })

        logger.write_log(
            f"[queryWeaponsByPriceRange] 查询成功 - 返回 {len(results)} 个饰品",
            'INFO'
        )

        return jsonify({
            "success": True,
            "data": results,
            "total": len(results)
        }), 200

    except Exception as e:
        logger.write_log(f"[queryWeaponsByPriceRange] 查询失败: {e}", 'ERROR')
        import traceback
        logger.write_log(f"错误堆栈: {traceback.format_exc()}", 'ERROR')
        return jsonify({
            "success": False,
            "message": f"查询失败: {str(e)}",
            "data": [],
            "total": 0
        }), 500
