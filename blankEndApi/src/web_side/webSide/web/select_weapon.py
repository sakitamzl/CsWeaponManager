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
        keyword - 搜索关键词（可选）
        weaponType - 武器类型筛选（可选）
        weaponName - 武器名称筛选（可选）
        rarity - 稀有度筛选（可选）
        如果所有参数都为空，则返回全部数据
    返回: 匹配的武器完整信息列表（所有字段，不限制数量，不去重）
    """
    try:
        keyword = request.args.get('keyword', '')
        weapon_type = request.args.get('weaponType', '')
        weapon_name = request.args.get('weaponName', '')
        rarity = request.args.get('rarity', '')
        
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
        
        # 返回完整的武器信息
        results = []
        for record in records:
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
                'Rarity': record.Rarity
            }
            results.append(weapon_data)
        
        return jsonify({
            "success": True,
            "data": results,
            "count": len(results)
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

