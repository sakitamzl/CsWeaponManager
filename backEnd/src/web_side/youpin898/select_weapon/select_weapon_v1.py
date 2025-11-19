from flask import jsonify, request, Blueprint
from src.db_manager.index.weapon_classID import WeaponClassIDModel
import requests
import base64
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

ICON_DOWNLOAD_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/119.0.0.0 Safari/537.36"),
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://www.youpin898.com/",
    "Origin": "https://www.youpin898.com",
    "Connection": "keep-alive"
}

youpin898SelectWeaponV1 = Blueprint('youpin898SelectWeaponV1', __name__)

@youpin898SelectWeaponV1.route('/getWeaponList', methods=['GET'])
def getWeaponList():
    """获取所有武器列表"""
    try:
        records = WeaponClassIDModel.find_all()
        data = [record.to_dict() for record in records]
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data)
        }), 200
    except Exception as e:
        print(f"获取武器列表失败: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@youpin898SelectWeaponV1.route('/getWeaponByYyypId/<int:yyyp_id>', methods=['GET'])
def getWeaponByYyypId(yyyp_id):
    """根据悠悠有品ID获取武器信息"""
    try:
        records = WeaponClassIDModel.find_by_yyyp_id(yyyp_id)
        if records:
            return jsonify({
                'success': True,
                'data': records[0].to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '武器不存在'
            }), 404
    except Exception as e:
        print(f"根据悠悠有品ID获取武器失败: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@youpin898SelectWeaponV1.route('/getWeaponByBuffId/<int:buff_id>', methods=['GET'])
def getWeaponByBuffId(buff_id):
    """根据BUFF ID获取武器信息"""
    try:
        records = WeaponClassIDModel.find_by_buff_id(buff_id)
        if records:
            return jsonify({
                'success': True,
                'data': records[0].to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '武器不存在'
            }), 404
    except Exception as e:
        print(f"根据BUFF ID获取武器失败: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@youpin898SelectWeaponV1.route('/getWeaponBySteamId/<int:steam_id>', methods=['GET'])
def getWeaponBySteamId(steam_id):
    """根据Steam ID获取武器信息"""
    try:
        records = WeaponClassIDModel.find_by_steam_id(steam_id)
        if records:
            return jsonify({
                'success': True,
                'data': records[0].to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '武器不存在'
            }), 404
    except Exception as e:
        print(f"根据Steam ID获取武器失败: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@youpin898SelectWeaponV1.route('/getWeaponByType/<weapon_type>', methods=['GET'])
def getWeaponByType(weapon_type):
    """根据武器类型获取武器列表"""
    try:
        records = WeaponClassIDModel.find_by_weapon_info(weapon_type=weapon_type)
        data = [record.to_dict() for record in records]
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data)
        }), 200
    except Exception as e:
        print(f"根据类型获取武器列表失败: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@youpin898SelectWeaponV1.route('/getWeaponByRarity/<rarity>', methods=['GET'])
def getWeaponByRarity(rarity):
    """根据稀有度获取武器列表"""
    try:
        records = WeaponClassIDModel.find_by_rarity(rarity)
        data = [record.to_dict() for record in records]
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data)
        }), 200
    except Exception as e:
        print(f"根据稀有度获取武器列表失败: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@youpin898SelectWeaponV1.route('/getWeaponByFloatRange/<float_range>', methods=['GET'])
def getWeaponByFloatRange(float_range):
    """根据品质范围获取武器列表"""
    try:
        records = WeaponClassIDModel.find_by_float_range(float_range)
        data = [record.to_dict() for record in records]
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data)
        }), 200
    except Exception as e:
        print(f"根据品质范围获取武器列表失败: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@youpin898SelectWeaponV1.route('/getWeaponByEnName/<en_weapon_name>', methods=['GET'])
def getWeaponByEnName(en_weapon_name):
    """根据英文武器名称获取武器列表"""
    try:
        records = WeaponClassIDModel.find_by_en_weapon_name(en_weapon_name)
        data = [record.to_dict() for record in records]
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data)
        }), 200
    except Exception as e:
        print(f"根据英文武器名称获取武器列表失败: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@youpin898SelectWeaponV1.route('/getIconStatus', methods=['POST'])
def getIconStatus():
    """批量获取icon_base64状态"""
    try:
        data = request.get_json() or {}
        steam_hash_names = data.get('steam_hash_names') or data.get('hash_names') or []

        if not isinstance(steam_hash_names, list):
            return jsonify({
                'success': False,
                'error': 'steam_hash_names需要数组格式'
            }), 400

        status_map = WeaponClassIDModel.get_icon_status_map(steam_hash_names)
        resp_data = {}
        for name in steam_hash_names:
            if not name:
                continue
            resp_data[name] = {
                'has_icon': status_map.get(name, False)
            }

        return jsonify({
            'success': True,
            'data': resp_data
        }), 200
    except Exception as e:
        print(f"获取icon状态失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@youpin898SelectWeaponV1.route('/fetchWeaponIcons', methods=['POST'])
def fetchWeaponIcons():
    """批量下载饰品图片并写入Base64"""
    try:
        data = request.get_json() or {}
        limit = int(data.get('limit', 50))
        force = bool(data.get('force', False))
        limit = max(1, min(limit, 200))

        records = WeaponClassIDModel.get_records_for_icon_batch(limit=limit, force=force)

        if not records:
            return jsonify({
                'success': True,
                'message': '没有需要处理的饰品',
                'processed': 0,
                'success_count': 0,
                'failed_count': 0
            }), 200

        success_count = 0
        failed_items = []

        for record in records:
            steam_hash_name = record.get('steam_hash_name')
            icon_url = record.get('icon_url')

            if not icon_url:
                failed_items.append({
                    'steam_hash_name': steam_hash_name,
                    'reason': '缺少icon_url'
                })
                continue

            try:
                response = requests.get(icon_url, headers=ICON_DOWNLOAD_HEADERS, timeout=20)
                if response.status_code == 403:
                    retry_headers = ICON_DOWNLOAD_HEADERS.copy()
                    retry_headers["Referer"] = icon_url
                    response = requests.get(icon_url, headers=retry_headers, timeout=20)
                if response.status_code == 403 and response.text.strip().startswith('<'):
                    redirected_url = _resolve_oss_url(icon_url, response.text)
                    if redirected_url:
                        response = requests.get(redirected_url, headers=ICON_DOWNLOAD_HEADERS, timeout=20)
                response.raise_for_status()
                icon_base64 = base64.b64encode(response.content).decode('utf-8')
                if WeaponClassIDModel.update_icon_data(steam_hash_name, icon_base64=icon_base64):
                    success_count += 1
                else:
                    failed_items.append({
                        'steam_hash_name': steam_hash_name,
                        'reason': '数据库更新失败'
                    })
            except Exception as e:
                failed_items.append({
                    'steam_hash_name': steam_hash_name,
                    'reason': str(e)
                })

        return jsonify({
            'success': True,
            'message': '批量获取饰品图片完成',
            'processed': len(records),
            'success_count': success_count,
            'failed_count': len(failed_items),
            'failed_items': failed_items[:10],  # 仅返回前10条失败信息
            'force': force
        }), 200

    except Exception as e:
        print(f"批量获取饰品图片失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


def _resolve_oss_url(original_url: str, xml_text: str):
    """根据OSS错误XML中的endpoint/bucket重写下载地址"""
    try:
        root = ET.fromstring(xml_text)
        endpoint = root.findtext('Endpoint')
        bucket = root.findtext('Bucket')
        if not endpoint or not bucket:
            return None

        parsed = urlparse(original_url)
        path = parsed.path or ''
        prefix = f'/{bucket}'
        if path.startswith(prefix):
            path = path[len(prefix):]
        if not path.startswith('/'):
            path = '/' + path
        return f"https://{bucket}.{endpoint}{path}"
    except Exception as e:
        print(f"解析OSS跳转地址失败: {e}")
        return None


@youpin898SelectWeaponV1.route('/searchWeapon', methods=['POST'])
def searchWeapon():
    """搜索武器(支持多条件查询)"""
    try:
        data = request.get_json()
        weapon_type = data.get('weapon_type')
        weapon_name = data.get('weapon_name')
        item_name = data.get('item_name')
        
        records = WeaponClassIDModel.find_by_weapon_info(
            weapon_type=weapon_type,
            weapon_name=weapon_name,
            item_name=item_name
        )
        
        result_data = [record.to_dict() for record in records]
        return jsonify({
            'success': True,
            'data': result_data,
            'count': len(result_data)
        }), 200
    except Exception as e:
        print(f"搜索武器失败: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@youpin898SelectWeaponV1.route('/batchInsertOrUpdate', methods=['POST'])
def batchInsertOrUpdate():
    """批量插入或更新武器数据"""
    try:
        data = request.get_json()
        if not data or not isinstance(data, list):
            return jsonify({
                'success': False,
                'error': '无效的JSON数据，需要数组格式'
            }), 400
        
        # 获取平台参数，默认为yyyp
        platform = request.args.get('platform', 'yyyp')
        
        success_count = WeaponClassIDModel.batch_insert_or_update(data, platform=platform)
        
        return jsonify({
            'success': True,
            'message': f'成功处理 {success_count}/{len(data)} 条数据',
            'success_count': success_count,
            'total_count': len(data),
            'platform': platform
        }), 200
    except Exception as e:
        print(f"批量插入或更新武器数据失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@youpin898SelectWeaponV1.route('/insertWeapon', methods=['POST'])
def insertWeapon():
    """插入单个武器数据"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '无效的JSON数据'
            }), 400
        
        # 获取平台参数，默认为yyyp
        platform = request.args.get('platform', 'yyyp')
        id_field_map = {
            'yyyp': 'yyyp_id',
            'buff': 'buff_id',
            'steam': 'steam_id'
        }
        id_field = id_field_map.get(platform, 'yyyp_id')
        
        # 兼容旧数据：如果传入的是'Id'字段，映射到对应字段
        if 'Id' in data and id_field not in data:
            data[id_field] = data.pop('Id')
        
        platform_id = data.get(id_field)
        if not platform_id:
            return jsonify({
                'success': False,
                'error': f'缺少{id_field}字段'
            }), 400
        
        # 检查是否已存在
        existing_list = None
        if platform == 'yyyp':
            existing_list = WeaponClassIDModel.find_by_yyyp_id(platform_id)
        elif platform == 'buff':
            existing_list = WeaponClassIDModel.find_by_buff_id(platform_id)
        elif platform == 'steam':
            existing_list = WeaponClassIDModel.find_by_steam_id(platform_id)
        
        if existing_list:
            return jsonify({
                'success': False,
                'error': f'武器{id_field}已存在，请使用更新接口'
            }), 400
        
        # 创建新记录
        weapon = WeaponClassIDModel(**data)
        if weapon.save():
            return jsonify({
                'success': True,
                'message': '武器数据插入成功',
                'data': weapon.to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '数据插入失败'
            }), 500
    except Exception as e:
        print(f"插入武器数据失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@youpin898SelectWeaponV1.route('/updateWeaponByYyypId/<int:yyyp_id>', methods=['PUT'])
def updateWeaponByYyypId(yyyp_id):
    """根据悠悠有品ID更新武器数据"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '无效的JSON数据'
            }), 400
        
        # 查找记录
        records = WeaponClassIDModel.find_by_yyyp_id(yyyp_id)
        if not records:
            return jsonify({
                'success': False,
                'error': '武器不存在'
            }), 404
        
        weapon = records[0]
        
        # 更新字段
        for key, value in data.items():
            if key not in ['yyyp_id', 'buff_id', 'steam_id'] and hasattr(weapon, key):
                setattr(weapon, key, value)
        
        if weapon.save():
            return jsonify({
                'success': True,
                'message': '武器数据更新成功',
                'data': weapon.to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '数据更新失败'
            }), 500
    except Exception as e:
        print(f"更新武器数据失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@youpin898SelectWeaponV1.route('/deleteWeaponByYyypId/<int:yyyp_id>', methods=['DELETE'])
def deleteWeaponByYyypId(yyyp_id):
    """根据悠悠有品ID删除武器数据"""
    try:
        records = WeaponClassIDModel.find_by_yyyp_id(yyyp_id)
        if not records:
            return jsonify({
                'success': False,
                'error': '武器不存在'
            }), 404
        
        weapon = records[0]
        if weapon.delete():
            return jsonify({
                'success': True,
                'message': '武器数据删除成功'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '数据删除失败'
            }), 500
    except Exception as e:
        print(f"删除武器数据失败: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@youpin898SelectWeaponV1.route('/getWeaponCount', methods=['GET'])
def getWeaponCount():
    """获取武器总数"""
    try:
        count = WeaponClassIDModel.count()
        return jsonify({
            'success': True,
            'count': count
        }), 200
    except Exception as e:
        print(f"获取武器总数失败: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500

