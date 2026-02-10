import os
import sys
import requests
import zipfile
import shutil
import hashlib
from flask import Blueprint, jsonify, request, Response, stream_with_context

version_update_bp = Blueprint('version_update', __name__)

# 更新服务器配置
# 生产环境使用域名，开发环境可以使用本地地址
UPDATE_SERVER_URL = 'http://makurochan.com:9004'
# UPDATE_SERVER_URL = 'http://127.0.0.1:9004'  # 本地开发

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


# ============================================
# 更新系统 API
# ============================================

def get_current_version():
    """获取当前应用版本"""
    try:
        # 从 package.json 读取版本号
        base_dir = get_base_dir()
        package_json_path = os.path.join(base_dir, 'WebSite', 'package.json')

        if os.path.exists(package_json_path):
            import json
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
                return package_data.get('version', '0.0.0')

        return '0.0.0'
    except Exception as e:
        print(f"❌ 获取当前版本失败: {e}")
        return '0.0.0'


@version_update_bp.route('/api/update/check', methods=['GET'])
def check_update():
    """
    检查更新

    返回：
    {
        "success": true,
        "has_update": true/false,
        "data": {
            "current_version": "2.3.5",
            "latest_version": "2.3.6",
            "release_date": "2026-02-10",
            "file_size": "125.5 MB",
            "changelog": ["新增：...", "优化：...", "修复：..."],
            "required": false
        }
    }
    """
    try:
        # 获取当前版本
        current_version = get_current_version()

        # 请求更新服务器
        response = requests.get(
            f'{UPDATE_SERVER_URL}/api/update/check',
            params={'current_version': current_version},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            return jsonify(data)
        else:
            return jsonify({
                'success': False,
                'error': '更新服务器响应异常'
            }), response.status_code

    except requests.exceptions.ConnectionError:
        return jsonify({
            'success': False,
            'error': '无法连接到更新服务器，请检查网络或服务器是否运行'
        }), 503

    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'error': '连接更新服务器超时'
        }), 504

    except Exception as e:
        print(f"❌ 检查更新失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@version_update_bp.route('/api/update/download-stream', methods=['GET'])
def download_update_stream():
    """
    下载更新包（流式传输）

    返回：二进制流
    """
    try:
        def generate():
            # 请求更新服务器下载更新包
            response = requests.get(
                f'{UPDATE_SERVER_URL}/api/update/download',
                stream=True,
                timeout=300
            )

            if response.status_code != 200:
                yield b''
                return

            # 流式传输
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk

        return Response(
            stream_with_context(generate()),
            mimetype='application/zip',
            headers={
                'Content-Disposition': 'attachment; filename=update.zip'
            }
        )

    except Exception as e:
        print(f"❌ 下载更新包失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@version_update_bp.route('/api/update/download', methods=['POST'])
def download_update():
    """
    下载更新包到本地

    返回：
    {
        "success": true,
        "data": {
            "file_path": "/path/to/update.zip",
            "file_size": "125.5 MB",
            "md5": "abc123..."
        }
    }
    """
    try:
        base_dir = get_base_dir()
        temp_dir = os.path.join(base_dir, 'temp')
        os.makedirs(temp_dir, exist_ok=True)

        update_file_path = os.path.join(temp_dir, 'update.zip')

        # 下载更新包
        print("📥 开始下载更新包...")
        response = requests.get(
            f'{UPDATE_SERVER_URL}/api/update/download',
            stream=True,
            timeout=300
        )

        if response.status_code != 200:
            return jsonify({
                'success': False,
                'error': '更新服务器返回错误'
            }), response.status_code

        # 保存文件
        total_size = 0
        with open(update_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    total_size += len(chunk)

        print(f"✅ 下载完成，文件大小: {total_size} 字节")

        # 计算MD5
        md5_hash = hashlib.md5()
        with open(update_file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        md5_value = md5_hash.hexdigest()

        # 格式化文件大小
        size = total_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                file_size = f"{size:.1f} {unit}"
                break
            size /= 1024.0
        else:
            file_size = f"{size:.1f} TB"

        return jsonify({
            'success': True,
            'data': {
                'file_path': update_file_path,
                'file_size': file_size,
                'md5': md5_value
            }
        })

    except requests.exceptions.ConnectionError:
        return jsonify({
            'success': False,
            'error': '无法连接到更新服务器'
        }), 503

    except Exception as e:
        print(f"❌ 下载更新包失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@version_update_bp.route('/api/update/extract', methods=['POST'])
def extract_update():
    """
    解压更新包

    请求体：
    {
        "file_path": "/path/to/update.zip",
        "verify_md5": "abc123..."
    }

    返回：
    {
        "success": true,
        "message": "更新包解压完成，请重启应用"
    }
    """
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        expected_md5 = data.get('verify_md5')

        if not file_path or not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': '更新包文件不存在'
            }), 400

        # 验证MD5（可选）
        if expected_md5:
            print("🔍 验证文件完整性...")
            md5_hash = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    md5_hash.update(chunk)
            actual_md5 = md5_hash.hexdigest()

            if actual_md5 != expected_md5:
                return jsonify({
                    'success': False,
                    'error': 'MD5 校验失败，文件可能已损坏'
                }), 400
            print("✅ MD5 校验通过")

        # 备份当前版本（可选）
        base_dir = get_base_dir()
        backup_dir = os.path.join(base_dir, 'backup')
        os.makedirs(backup_dir, exist_ok=True)

        print("📦 开始解压更新包...")

        # 解压到临时目录
        temp_extract_dir = os.path.join(base_dir, 'temp', 'update_extract')
        if os.path.exists(temp_extract_dir):
            shutil.rmtree(temp_extract_dir)
        os.makedirs(temp_extract_dir, exist_ok=True)

        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(temp_extract_dir)

        print("✅ 解压完成")
        print("📝 准备应用更新...")

        # 复制文件到程序目录
        for item in os.listdir(temp_extract_dir):
            src = os.path.join(temp_extract_dir, item)
            dst = os.path.join(base_dir, item)

            # 跳过某些目录/文件
            skip_items = ['conf.ini', 'csweaponmanager.db', 'log', 'backup', 'temp', 'UpdateServer']
            if item in skip_items:
                print(f"⏭️  跳过: {item}")
                continue

            try:
                if os.path.isdir(src):
                    # 备份旧目录
                    if os.path.exists(dst):
                        backup_path = os.path.join(backup_dir, f"{item}_backup")
                        if os.path.exists(backup_path):
                            shutil.rmtree(backup_path)
                        shutil.copytree(dst, backup_path)
                        shutil.rmtree(dst)

                    shutil.copytree(src, dst)
                    print(f"✅ 更新目录: {item}")
                else:
                    # 备份旧文件
                    if os.path.exists(dst):
                        backup_path = os.path.join(backup_dir, f"{item}_backup")
                        shutil.copy2(dst, backup_path)
                        os.remove(dst)

                    shutil.copy2(src, dst)
                    print(f"✅ 更新文件: {item}")
            except Exception as e:
                print(f"⚠️  更新 {item} 失败: {e}")

        # 清理临时文件
        print("🧹 清理临时文件...")
        shutil.rmtree(temp_extract_dir)
        os.remove(file_path)

        print("✅ 更新完成！")

        return jsonify({
            'success': True,
            'message': '更新包已解压并应用，请重启应用生效'
        })

    except zipfile.BadZipFile:
        return jsonify({
            'success': False,
            'error': '更新包文件损坏，无法解压'
        }), 400

    except Exception as e:
        print(f"❌ 解压更新包失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@version_update_bp.route('/api/update/current-version', methods=['GET'])
def get_version():
    """
    获取当前版本号

    返回：
    {
        "success": true,
        "data": {
            "version": "2.3.5"
        }
    }
    """
    try:
        version = get_current_version()
        return jsonify({
            'success': True,
            'data': {
                'version': version
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
