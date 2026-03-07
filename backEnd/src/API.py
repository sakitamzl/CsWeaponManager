"""
backEND V2 API 根模块
层级蓝图注册：
- 从 backEnd.py 接收前缀 /backENDV2
- 向下传递给 use_webside 模块，添加 /src 路径段
- 向下传递给 use_spider 聚合模块，添加 /src 路径段
最终形成完整路径示例：
/backENDV2/src/use_webside/...
/backENDV2/src/use_spider/youpin/...
/backENDV2/src/use_spider/buff/...
/backENDV2/src/use_spider/csfloat/...
"""
from flask import Blueprint, jsonify
from .use_webside.API import web_display_blueprint
from .use_spider.API import use_spider_blueprint
from .units.API import unites_blueprint

backendV2_blueprint = Blueprint('backendV2_src', __name__)


def _health():
    """健康检查，用于更新后轮询确认 Backend 已启动"""
    return jsonify({'status': 'ok', 'service': 'backEnd'})


backendV2_blueprint.route('/health', methods=['GET'])(_health)
backendV2_blueprint.register_blueprint(web_display_blueprint, url_prefix='/src')
backendV2_blueprint.register_blueprint(use_spider_blueprint,  url_prefix='/src')
backendV2_blueprint.register_blueprint(unites_blueprint,      url_prefix='/src')