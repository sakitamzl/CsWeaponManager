"""
武器图片读取API
提供武器图片的后端访问接口
"""
import os
import sys
from flask import Blueprint, send_file, jsonify
from pathlib import Path

readImagesV1 = Blueprint('readImagesV1', __name__)

def get_base_dir():
    """获取程序运行的基础目录"""
    if getattr(sys, 'frozen', False):
        # 打包后的可执行文件，返回 exe 所在目录
        return Path(sys.executable).parent
    else:
        # 开发环境，返回项目根目录
        return Path(__file__).resolve().parent.parent.parent.parent

# 获取图片文件夹路径
BASE_DIR = get_base_dir()
WEAPON_IMGS_DIR = BASE_DIR / 'weapon_imgs'
@readImagesV1.route('/weapon_image/<path:image_name>', methods=['GET'])
def get_weapon_image(image_name):
    """
    获取武器图片
    :param image_name: 图片文件名（包含.png后缀）
    :return: 图片文件或404错误
    """
    try:
        # 构建完整的图片路径
        image_path = WEAPON_IMGS_DIR / image_name
        
        # 检查文件是否存在
        if not image_path.exists() or not image_path.is_file():
            return jsonify({
                'error': 'Image not found',
                'message': f'图片 {image_name} 不存在'
            }), 404
        
        # 返回图片文件
        return send_file(
            image_path,
            mimetype='image/png',
            as_attachment=False,
            download_name=image_name
        )
    
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@readImagesV1.route('/weapon_image/check/<path:image_name>', methods=['GET'])
def check_weapon_image(image_name):
    """
    检查武器图片是否存在
    :param image_name: 图片文件名（包含.png后缀）
    :return: JSON响应，包含exists字段
    """
    try:
        image_path = WEAPON_IMGS_DIR / image_name
        exists = image_path.exists() and image_path.is_file()
        
        return jsonify({
            'exists': exists,
            'image_name': image_name,
            'path': str(image_path) if exists else None
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500
