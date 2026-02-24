"""
VersionUpdate Data 模块
提供版本更新和文档查看的端点
"""
import os
import sys
import hashlib
import requests
import json
import time
from flask import jsonify, request, Response, stream_with_context, send_file

# GitHub 仓库配置
GITHUB_REPO = 'henntaidesu/CsWeaponManager'
GITHUB_API_URL = f'https://api.github.com/repos/{GITHUB_REPO}/releases/latest'


def _get_base_dir():
    """获取程序运行的基础目录（项目根目录）"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        # 从当前文件向上 7 级到项目根目录
        # units/ → version_update/ → settings/ → web_display/ → src/ → backEnd/ → 项目根
        base = os.path.dirname(os.path.abspath(__file__))
        for _ in range(6):
            base = os.path.dirname(base)
        return base


def _get_documents_dir():
    """获取 Documents 目录路径"""
    return os.path.join(_get_base_dir(), 'Documents')


def _compare_versions(current, latest):
    """比较两个语义化版本号，返回 True 表示 latest 更新"""
    def parse_version(v):
        v = v.lstrip('v')
        return [int(x) for x in v.split('.')]
    try:
        return parse_version(latest) > parse_version(current)
    except (ValueError, AttributeError):
        return False


def _format_file_size(size_bytes):
    """格式化文件大小"""
    size = size_bytes
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def _scan_directory(path, base_path):
    """递归扫描目录，返回文件树结构"""
    items = []
    try:
        entries = os.listdir(path)
        for entry in sorted(entries):
            if entry.startswith('.') or entry.lower() in ['imges', 'images']:
                continue
            full_path = os.path.join(path, entry)
            relative_path = os.path.relpath(full_path, base_path)
            if os.path.isdir(full_path):
                children = _scan_directory(full_path, base_path)
                if children:
                    items.append({
                        'name': entry,
                        'type': 'directory',
                        'path': relative_path.replace('\\', '/'),
                        'children': children
                    })
            elif entry.endswith('.md'):
                items.append({
                    'name': entry,
                    'type': 'file',
                    'path': relative_path.replace('\\', '/')
                })
    except Exception as e:
        print(f"扫描目录失败: {path}, 错误: {str(e)}")
    return items


class VersionUpdateData:

    @staticmethod
    def get_document_tree():
        """获取 Documents 目录的文件树结构"""
        try:
            docs_dir = _get_documents_dir()
            if not os.path.exists(docs_dir):
                return jsonify({'success': False, 'error': 'Documents 目录不存在'}), 404
            tree = _scan_directory(docs_dir, docs_dir)
            return jsonify({'success': True, 'data': tree})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @staticmethod
    def get_document_file():
        """读取指定的 markdown 文件内容"""
        try:
            file_path = request.args.get('path', '')
            if not file_path:
                return jsonify({'success': False, 'error': '未指定文件路径'}), 400
            if '..' in file_path or file_path.startswith('/') or file_path.startswith('\\'):
                return jsonify({'success': False, 'error': '无效的文件路径'}), 400

            docs_dir = _get_documents_dir()
            full_path = os.path.normpath(os.path.join(docs_dir, file_path))
            if not full_path.startswith(os.path.normpath(docs_dir)):
                return jsonify({'success': False, 'error': '无权访问该文件'}), 403
            if not os.path.exists(full_path):
                return jsonify({'success': False, 'error': '文件不存在'}), 404
            if not os.path.isfile(full_path):
                return jsonify({'success': False, 'error': '指定路径不是文件'}), 400

            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({'success': True, 'data': {'path': file_path, 'content': content}})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @staticmethod
    def get_document_image():
        """获取文档中的图片"""
        try:
            file_path = request.args.get('path', '')
            if not file_path:
                return jsonify({'success': False, 'error': '未指定图片路径'}), 400
            if '..' in file_path or file_path.startswith('/') or file_path.startswith('\\'):
                return jsonify({'success': False, 'error': '无效的图片路径'}), 400

            docs_dir = _get_documents_dir()
            full_path = os.path.normpath(os.path.join(docs_dir, file_path))
            if not full_path.startswith(os.path.normpath(docs_dir)):
                return jsonify({'success': False, 'error': '无权访问该文件'}), 403
            if not os.path.exists(full_path):
                return jsonify({'success': False, 'error': '图片不存在'}), 404
            if not os.path.isfile(full_path):
                return jsonify({'success': False, 'error': '指定路径不是文件'}), 400

            allowed_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp']
            file_ext = os.path.splitext(full_path)[1].lower()
            if file_ext not in allowed_extensions:
                return jsonify({'success': False, 'error': '不支持的图片格式'}), 400

            return send_file(full_path, mimetype=f'image/{file_ext[1:]}')
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @staticmethod
    def get_current_version():
        """获取当前版本号"""
        try:
            from backEnd import CURRENT_VERSION
            return jsonify({'success': True, 'data': {'version': CURRENT_VERSION}})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @staticmethod
    def check_update():
        """通过 GitHub Releases 检查是否有新版本"""
        try:
            from backEnd import CURRENT_VERSION
            current_version = CURRENT_VERSION

            headers = {'Accept': 'application/vnd.github.v3+json'}
            response = requests.get(GITHUB_API_URL, headers=headers, timeout=15)

            if response.status_code == 200:
                release_data = response.json()
                latest_version = release_data.get('tag_name', '').lstrip('v')
                has_update = _compare_versions(current_version, latest_version)

                published_at = release_data.get('published_at', '')
                release_date = published_at[:10] if published_at else ''

                body = release_data.get('body', '') or ''
                changelog = [line.strip() for line in body.split('\n') if line.strip()]

                download_url = ''
                file_size = ''
                assets = release_data.get('assets', [])
                for asset in assets:
                    if asset.get('name', '').endswith('.zip'):
                        download_url = asset.get('browser_download_url', '')
                        file_size = _format_file_size(asset.get('size', 0))
                        break
                if not download_url:
                    download_url = release_data.get('zipball_url', '')

                return jsonify({
                    'success': True,
                    'has_update': has_update,
                    'data': {
                        'current_version': current_version,
                        'latest_version': latest_version,
                        'release_date': release_date,
                        'file_size': file_size,
                        'changelog': changelog,
                        'download_url': download_url
                    }
                })

            elif response.status_code == 404:
                return jsonify({
                    'success': True,
                    'has_update': False,
                    'data': {
                        'current_version': current_version,
                        'latest_version': current_version,
                        'message': '暂无发布版本'
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'GitHub API 响应异常: {response.status_code}'
                }), response.status_code

        except requests.exceptions.ConnectionError:
            return jsonify({'success': False, 'error': '无法连接到 GitHub，请检查网络连接或代理设置'}), 503
        except requests.exceptions.Timeout:
            return jsonify({'success': False, 'error': '连接 GitHub 超时，请检查网络连接或代理设置'}), 504
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @staticmethod
    def download_update():
        """从 GitHub 下载更新包到本地（SSE 流式返回下载进度）"""
        data = request.get_json()
        download_url = data.get('download_url', '') if data else ''

        if not download_url:
            return jsonify({'success': False, 'error': '未提供下载地址'}), 400

        def generate():
            try:
                base_dir = _get_base_dir()
                update_file_path = os.path.join(base_dir, 'CsWeaponManager.zip')

                resp = requests.get(
                    download_url,
                    stream=True,
                    timeout=300,
                    headers={'Accept': 'application/octet-stream'}
                )

                if resp.status_code != 200:
                    yield f"data: {json.dumps({'type': 'error', 'error': f'下载失败，HTTP 状态码: {resp.status_code}'})}\n\n"
                    return

                total = int(resp.headers.get('content-length', 0))
                downloaded = 0
                start_time = time.time()
                last_report_time = start_time

                with open(update_file_path, 'wb') as f:
                    for chunk in resp.iter_content(chunk_size=65536):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            now = time.time()
                            if now - last_report_time >= 0.3 or downloaded == total:
                                elapsed = now - start_time
                                speed = downloaded / elapsed if elapsed > 0 else 0
                                progress = int(downloaded * 100 / total) if total > 0 else 0
                                yield f"data: {json.dumps({'type': 'progress', 'downloaded': downloaded, 'total': total, 'progress': progress, 'speed': _format_file_size(int(speed)) + '/s'})}\n\n"
                                last_report_time = now

                md5_hash = hashlib.md5()
                with open(update_file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        md5_hash.update(chunk)
                md5_value = md5_hash.hexdigest()

                yield f"data: {json.dumps({'type': 'complete', 'file_size': _format_file_size(downloaded), 'md5': md5_value})}\n\n"

            except requests.exceptions.ConnectionError:
                yield f"data: {json.dumps({'type': 'error', 'error': '无法连接到 GitHub，请检查网络连接或代理设置'})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

        return Response(stream_with_context(generate()), mimetype='text/event-stream', headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        })

    @staticmethod
    def check_local_update():
        """检查本地是否存在已下载的更新包"""
        try:
            base_dir = _get_base_dir()
            update_file_path = os.path.join(base_dir, 'CsWeaponManager.zip')
            if os.path.exists(update_file_path):
                file_size = os.path.getsize(update_file_path)
                return jsonify({'success': True, 'data': {'exists': True, 'file_size': _format_file_size(file_size)}})
            else:
                return jsonify({'success': True, 'data': {'exists': False}})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @staticmethod
    def apply_update():
        """调用 update.bat 执行更新"""
        try:
            import subprocess
            base_dir = _get_base_dir()
            update_bat = os.path.join(base_dir, 'update.bat')
            update_zip = os.path.join(base_dir, 'CsWeaponManager.zip')

            if not os.path.exists(update_zip):
                return jsonify({'success': False, 'error': '更新包不存在，请先下载更新'}), 400
            if not os.path.exists(update_bat):
                return jsonify({'success': False, 'error': 'update.bat 不存在'}), 400

            subprocess.Popen(
                ['cmd.exe', '/c', 'start', '', update_bat],
                cwd=base_dir,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            return jsonify({'success': True, 'message': '更新程序已启动'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
