from flask import Blueprint, request, jsonify
from src.log import Log
from backEnd.src.db_manager.index.model.config import ConfigModel
import json


search_pendant_config_bp = Blueprint(
    'search_pendant_config',
    __name__,
    url_prefix='/searchPendantConfigV1'
)

logger = Log()


@search_pendant_config_bp.route('/saveConfig', methods=['POST'])
def save_pendant_config():
    """
    保存挂件搜索进度到配置表

    前端请求体（来自 SearchPendant 页面）：
    {
        "id": 70,                 # 配置ID（必填）
        "crawlProgress": { ... }  # 进度数据（必填）
        ...  其它配置字段忽略
    }

    实现：
    - 将进度数据以 key1="search_pendant_progress", key2=str(config_id)
      的形式写入 config 表（与 spider 端保持一致的存储方式）。
    """
    try:
        data = request.get_json() or {}
        config_id = data.get('id') or data.get('configId')
        progress = data.get('crawlProgress')

        if not config_id:
            return jsonify({
                'success': False,
                'message': '缺少配置ID'
            }), 400

        if progress is None:
            # 如果没有提供进度数据，则视为清除进度：写入一个空对象
            progress = {}

        try:
            config_id_str = str(int(config_id))
        except (TypeError, ValueError):
            return jsonify({
                'success': False,
                'message': '配置ID必须为整数'
            }), 400

        # 序列化进度数据
        try:
            value = json.dumps(progress, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            return jsonify({
                'success': False,
                'message': f'进度数据格式错误: {e}'
            }), 400

        # 使用 ConfigModel 写入 config 表（与 ConfigAPI.set_value 逻辑一致）
        ok = ConfigModel.set_value(
            key1='search_pendant_progress',
            key2=config_id_str,
            value=value,
            data_name=f'search_pendant_progress_{config_id_str}'
        )

        if not ok:
            return jsonify({
                'success': False,
                'message': '保存失败'
            }), 500

        logger.write_log(
            f"[SearchPendantConfig] 保存进度成功: config_id={config_id_str}, data={value}",
            'info'
        )

        return jsonify({
            'success': True,
            'message': '保存成功'
        }), 200

    except Exception as e:
        logger.write_log(f"[SearchPendantConfig] 保存进度异常: {str(e)}", 'error')
        import traceback
        logger.write_log(traceback.format_exc(), 'error')
        return jsonify({
            'success': False,
            'message': f'保存失败: {str(e)}'
        }), 500

