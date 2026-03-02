"""
BUFF select_weapon 写入模块
提供 Spider 所需的 BUFF 武器数据批量更新接口
"""
from flask import jsonify, request
from src.db_manager.index.model.weapon_classID import WeaponClassIDModel


class WeaponInsert:

    @staticmethod
    def batch_insert_or_update():
        """
        BUFF 专用：批量更新或插入 BUFF 武器数据
        通过 steam_hash_name 匹配已有记录，更新 buff_id 等 BUFF 相关字段
        """
        try:
            data = request.get_json()
            if not data or not isinstance(data, list):
                return jsonify({'success': False, 'error': '无效的JSON数据，需要数组格式'}), 400

            success_count = WeaponClassIDModel.batch_update_buff_id(data)

            return jsonify({
                'success': True,
                'message': f'成功更新 {success_count}/{len(data)} 条BUFF数据的buff_id',
                'success_count': success_count,
                'total_count': len(data)
            }), 200
        except Exception as e:
            print(f"批量更新BUFF buff_id失败: {e}")
            import traceback
            print(f"详细错误信息: {traceback.format_exc()}")
            return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500
