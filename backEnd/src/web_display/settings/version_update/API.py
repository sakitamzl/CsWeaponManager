"""
VersionUpdate API 模块
层级蓝图注册：
- 从 settings/API.py 接收前缀 /backENDV2/src/web_display/settings
- 注册所有 VersionUpdate 路由，添加 /version_update/units/xxx 路径段
"""
from flask import Blueprint
from .units.version_update_data import VersionUpdateData

version_update_blueprint = Blueprint('version_update_v2', __name__)

# 文档系统
version_update_blueprint.route('/version_update/units/docs/getDocumentTree', methods=['GET'])(VersionUpdateData.get_document_tree)
version_update_blueprint.route('/version_update/units/docs/getDocumentFile', methods=['GET'])(VersionUpdateData.get_document_file)
version_update_blueprint.route('/version_update/units/docs/getDocumentImage', methods=['GET'])(VersionUpdateData.get_document_image)

# 更新系统
version_update_blueprint.route('/version_update/units/update/getCurrentVersion', methods=['GET'])(VersionUpdateData.get_current_version)
version_update_blueprint.route('/version_update/units/update/checkUpdate', methods=['GET'])(VersionUpdateData.check_update)
version_update_blueprint.route('/version_update/units/update/downloadUpdate', methods=['POST'])(VersionUpdateData.download_update)
version_update_blueprint.route('/version_update/units/update/checkLocalUpdate', methods=['GET'])(VersionUpdateData.check_local_update)
version_update_blueprint.route('/version_update/units/update/applyUpdate', methods=['POST'])(VersionUpdateData.apply_update)
