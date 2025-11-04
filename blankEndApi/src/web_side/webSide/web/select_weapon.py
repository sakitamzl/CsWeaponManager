from flask import jsonify, request, Blueprint
from src.db_manager.index.weapon_classID import WeaponClassIDModel

webSelectWeaponV1 = Blueprint('webSelectWeaponV1', __name__)

@webSelectWeaponV1.route('/searchWeapon', methods=['GET'])
def searchWeapon():
    """
    根据market_listing_item_name模糊搜索武器（用于自动完成下拉框）
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
        
        # 使用LIKE进行模糊查询
        where_clause = "[market_listing_item_name] LIKE ?"
        params = (f"%{keyword}%",)
        
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
    参数: weaponType - 武器类型
    返回: 武器名称列表
    """
    try:
        weapon_type = request.args.get('weaponType', '')
        
        if not weapon_type or len(weapon_type.strip()) == 0:
            return jsonify({
                "success": True,
                "data": []
            }), 200
        
        # 查询该武器类型下的所有记录
        where_clause = "[weapon_type] = ?"
        params = (weapon_type.strip(),)
        
        records = WeaponClassIDModel.find_all(
            where=where_clause, 
            params=params
        )
        
        # 提取并去重武器名称
        weapon_names = set()
        for record in records:
            if record.weapon_name and record.weapon_name.strip():
                weapon_names.add(record.weapon_name.strip())
        
        # 转换为排序列表
        weapon_names_list = sorted(list(weapon_names))
        
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
    根据market_listing_item_name模糊搜索武器详细信息（用于表格展示）
    参数: 
        platformType - 平台类型：youpin 或 buff（必填）
        keyword - 搜索关键词（可选）
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
        
        # 如果提供了关键词
        if keyword and len(keyword.strip()) > 0:
            where_clauses.append("[market_listing_item_name] LIKE ?")
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
        
        # 查询数据库，返回所有匹配的记录
        records = WeaponClassIDModel.find_all(
            where=where_clause, 
            params=tuple(params) if params else None
        )
        
        # 价格筛选、在售数量筛选以及自动过滤在售数量为0的数据
        # 根据平台类型选择对应的价格字段和在售数量字段
        price_field = 'yyyp_Price' if platform_type == 'youpin' else 'buff_Price'
        on_sale_count_field = 'yyyp_OnSaleCount' if platform_type == 'youpin' else 'buff_OnSaleCount'
        
        filtered_records = []
        for record in records:
            # 自动过滤在售数量为0的数据
            on_sale_count_str = getattr(record, on_sale_count_field, None)
            if on_sale_count_str:
                try:
                    on_sale_count = int(on_sale_count_str)
                    if on_sale_count == 0:
                        continue  # 跳过在售数量为0的记录
                except (ValueError, TypeError):
                    pass  # 无法解析的数据保留
            
            # 价格筛选
            if price_min or price_max:
                price_str = getattr(record, price_field, None)
                
                if not price_str:
                    continue
                
                try:
                    price = float(price_str)
                    
                    # 检查价格区间
                    if price_min and price < float(price_min):
                        continue
                    if price_max and price > float(price_max):
                        continue
                except (ValueError, TypeError):
                    # 价格转换失败，跳过
                    continue
            
            # 在售数量筛选（最小在售数量）
            if min_on_sale_count:
                on_sale_count_str = getattr(record, on_sale_count_field, None)
                
                if not on_sale_count_str:
                    continue
                
                try:
                    on_sale_count = int(on_sale_count_str)
                    
                    # 检查在售数量
                    if on_sale_count < int(min_on_sale_count):
                        continue
                except (ValueError, TypeError):
                    # 在售数量转换失败，跳过
                    continue
            
            filtered_records.append(record)
        
        records = filtered_records
        
        # 根据平台类型确定价格字段，并按价格正序排序
        price_field = 'yyyp_Price' if platform_type == 'youpin' else 'buff_Price'
        
        # 对结果按价格正序排序
        sorted_records = []
        for record in records:
            price_str = getattr(record, price_field, None)
            try:
                price = float(price_str) if price_str else float('inf')
            except (ValueError, TypeError):
                price = float('inf')
            sorted_records.append((record, price))
        
        # 按价格排序（正序：从低到高）
        sorted_records.sort(key=lambda x: x[1])
        
        # 分页处理
        total_count = len(sorted_records)
        start_index = (page - 1) * limit
        end_index = start_index + limit
        paginated_records = sorted_records[start_index:end_index]
        
        # 返回完整的武器信息
        results = []
        for record, price in paginated_records:
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

