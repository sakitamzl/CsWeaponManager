"""
Images API 模块
层级蓝图注册：
- 从 web_display/API.py 接收前缀 /backENDV2/src/web_display
- 注册所有图片读取路由，添加 /units/images/xxx 路径段
最终路径示例：
  /backENDV2/src/web_display/units/images/weapon_image/<image_name>
  /backENDV2/src/web_display/units/images/weapon_image/check/<image_name>
"""
from flask import Blueprint
from .image_handler import ImageHandler

images_blueprint = Blueprint('images_v2', __name__)

images_blueprint.route('/units/images/weapon_image/<path:image_name>', methods=['GET'])(ImageHandler.get_weapon_image)
images_blueprint.route('/units/images/weapon_image/check/<path:image_name>', methods=['GET'])(ImageHandler.check_weapon_image)
