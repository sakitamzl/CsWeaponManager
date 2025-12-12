import os
import sys
from flask import Blueprint, jsonify, request

version_update_bp = Blueprint('version_update', __name__)

def get_base_dir():
    """获取程序运行的基础目录"""
    if getattr(sys, 'frozen', False):
        # 打包后的可执行文件，返回 exe 所在目录
        return os.path.dirname(sys.executable)
    else:
        # 开发环境，返回项目根目录
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

def get_documents_dir():
    """获取 Documents 目录路径"""
    docs_dir = os.path.join(get_base_dir(), 'Documents')
    print(f"📁 Documents 目录路径: {docs_dir}")
    print(f"📁 Documents 目录是否存在: {os.path.exists(docs_dir)}")
    return docs_dir

def scan_directory(path, base_path):
    """递归扫描目录，返回文件树结构"""
    items = []
    try:
        entries = os.listdir(path)
        for entry in sorted(entries):
            # 跳过隐藏文件和 imges 文件夹
            if entry.startswith('.') or entry.lower() in ['imges', 'images']:
                continue

            full_path = os.path.join(path, entry)
            relative_path = os.path.relpath(full_path, base_path)

            if os.path.isdir(full_path):
                # 递归获取子目录
                children = scan_directory(full_path, base_path)
                # 只添加有内容的目录
                if children:
                    items.append({
                        'name': entry,
                        'type': 'directory',
                        'path': relative_path.replace('\\', '/'),
                        'children': children
                    })
            elif entry.endswith('.md'):
                # 只包含 markdown 文件
                items.append({
                    'name': entry,
                    'type': 'file',
                    'path': relative_path.replace('\\', '/')
                })
    except Exception as e:
        print(f"扫描目录失败: {path}, 错误: {str(e)}")

    return items

@version_update_bp.route('/api/version/documents/tree', methods=['GET'])
def get_documents_tree():
    """获取 Documents 目录的文件树结构"""
    try:
        docs_dir = get_documents_dir()

        if not os.path.exists(docs_dir):
            return jsonify({
                'success': False,
                'error': 'Documents 目录不存在'
            }), 404

        tree = scan_directory(docs_dir, docs_dir)

        return jsonify({
            'success': True,
            'data': tree
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@version_update_bp.route('/api/version/documents/file', methods=['GET'])
def get_document_file():
    """读取指定的 markdown 文件内容"""
    try:
        file_path = request.args.get('path', '')

        if not file_path:
            return jsonify({
                'success': False,
                'error': '未指定文件路径'
            }), 400

        # 安全检查：确保路径不包含 ../ 等危险路径
        if '..' in file_path or file_path.startswith('/') or file_path.startswith('\\'):
            return jsonify({
                'success': False,
                'error': '无效的文件路径'
            }), 400

        # 构建完整路径
        docs_dir = get_documents_dir()
        full_path = os.path.normpath(os.path.join(docs_dir, file_path))

        # 确保文件在 Documents 目录下
        if not full_path.startswith(os.path.normpath(docs_dir)):
            return jsonify({
                'success': False,
                'error': '无权访问该文件'
            }), 403

        if not os.path.exists(full_path):
            return jsonify({
                'success': False,
                'error': '文件不存在'
            }), 404

        if not os.path.isfile(full_path):
            return jsonify({
                'success': False,
                'error': '指定路径不是文件'
            }), 400

        # 读取文件内容
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return jsonify({
            'success': True,
            'data': {
                'path': file_path,
                'content': content
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@version_update_bp.route('/api/version/documents/image', methods=['GET'])
def get_document_image():
    """获取文档中的图片"""
    try:
        from flask import send_file
        
        file_path = request.args.get('path', '')

        if not file_path:
            return jsonify({
                'success': False,
                'error': '未指定图片路径'
            }), 400

        # 安全检查：确保路径不包含危险路径
        if '..' in file_path or file_path.startswith('/') or file_path.startswith('\\'):
            return jsonify({
                'success': False,
                'error': '无效的图片路径'
            }), 400

        # 构建完整路径
        docs_dir = get_documents_dir()
        full_path = os.path.normpath(os.path.join(docs_dir, file_path))

        # 确保文件在 Documents 目录下
        if not full_path.startswith(os.path.normpath(docs_dir)):
            return jsonify({
                'success': False,
                'error': '无权访问该文件'
            }), 403

        if not os.path.exists(full_path):
            return jsonify({
                'success': False,
                'error': '图片不存在'
            }), 404

        if not os.path.isfile(full_path):
            return jsonify({
                'success': False,
                'error': '指定路径不是文件'
            }), 400

        # 检查文件扩展名
        allowed_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp']
        file_ext = os.path.splitext(full_path)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({
                'success': False,
                'error': '不支持的图片格式'
            }), 400

        # 返回图片文件
        return send_file(full_path, mimetype=f'image/{file_ext[1:]}')

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@version_update_bp.route('/api/version/update-log', methods=['GET'])
def get_update_log():
    """读取 updateLog.md 文件内容（保持向后兼容）"""
    try:
        # 获取项目根目录下 Documents 目录的 updateLog.md 文件路径
        base_dir = get_base_dir()
        update_log_path = os.path.join(base_dir, 'Documents', 'updateLog.md')

        if not os.path.exists(update_log_path):
            return jsonify({
                'success': False,
                'error': '更新日志文件不存在'
            }), 404

        # 读取文件内容
        with open(update_log_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return jsonify({
            'success': True,
            'data': {
                'content': content
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
