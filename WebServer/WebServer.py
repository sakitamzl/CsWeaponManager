import os
import sys
import logging
import requests
from flask import Flask, send_from_directory, request, Response
from flask_cors import CORS

def get_base_path():
    """获取程序运行的基础路径"""
    if getattr(sys, 'frozen', False):
        # 打包后的可执行文件
        return os.path.dirname(sys.executable)
    else:
        # 开发环境
        return os.path.dirname(os.path.abspath(__file__))

def get_static_folder():
    """获取静态文件目录路径"""
    base_path = get_base_path()
    
    # 打包后的路径: Releases/v2.x.x/WebSite/dist
    static_folder = os.path.join(base_path, 'WebSite', 'dist')
    
    # 如果不存在，尝试开发环境路径
    if not os.path.exists(static_folder):
        static_folder = os.path.join(base_path, '..', 'WebSite', 'dist')
        static_folder = os.path.abspath(static_folder)
    
    return static_folder

# 初始化 Flask 应用
static_folder = get_static_folder()
# 注意：不设置 static_folder 和 static_url_path，完全由我们自己的路由处理
app = Flask(__name__, static_folder=None, static_url_path=None)
CORS(app)

# 手动设置 static_folder 供我们的路由使用
app.static_folder = static_folder

# API 代理配置
BACKEND_URL = 'http://127.0.0.1:9001'
SPIDER_URL = 'http://127.0.0.1:9002'

# 代理到后端 API
@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy_api(path):
    """代理 /api/* 请求到后端服务器 (9001)"""
    try:
        url = f'{BACKEND_URL}/{path}'

        # 检查是否为流式端点
        is_stream = path in ('api/update/download',)
        timeout = 600 if is_stream else 30

        # 转发请求
        resp = requests.request(
            method=request.method,
            url=url,
            headers={key: value for key, value in request.headers if key.lower() != 'host'},
            data=request.get_data(),
            params=request.args,
            allow_redirects=False,
            timeout=timeout,
            stream=is_stream
        )

        # 返回响应
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for name, value in resp.raw.headers.items()
                  if name.lower() not in excluded_headers]

        if is_stream:
            return Response(resp.iter_content(chunk_size=1024), resp.status_code, headers)

        return Response(resp.content, resp.status_code, headers)
    except Exception as e:
        print(f"API代理错误: {e}")
        return {'error': str(e)}, 500

# 代理到爬虫服务
@app.route('/spider/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy_spider(path):
    """代理 /spider/* 请求到爬虫服务器 (9002)"""
    try:
        url = f'{SPIDER_URL}/{path}'
        
        # 转发请求
        resp = requests.request(
            method=request.method,
            url=url,
            headers={key: value for key, value in request.headers if key.lower() != 'host'},
            data=request.get_data(),
            params=request.args,
            allow_redirects=False,
            timeout=30,
            stream=True  # 支持 SSE (Server-Sent Events)
        )
        
        # 返回响应
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for name, value in resp.raw.headers.items()
                  if name.lower() not in excluded_headers]
        
        return Response(resp.iter_content(chunk_size=1024), resp.status_code, headers)
    except Exception as e:
        print(f"Spider代理错误: {e}")
        return {'error': str(e)}, 500

# 提供静态文件服务
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    """
    提供静态文件服务
    - 如果文件存在，返回文件
    - 如果文件不存在，返回 index.html（用于 SPA 前端路由）
    """
    # print(f"[DEBUG] 请求路径: /{path}")
    
    # 如果是根路径，直接返回 index.html
    if path == '':
        # print(f"[DEBUG] 返回根路径 index.html")
        return send_from_directory(app.static_folder, 'index.html')
    
    # 构建完整的文件路径
    static_file_path = os.path.join(app.static_folder, path)
    # print(f"[DEBUG] 检查文件: {static_file_path}")
    
    # 如果文件存在且是文件（不是目录），返回该文件
    if os.path.exists(static_file_path) and os.path.isfile(static_file_path):
        # print(f"[DEBUG] 文件存在，返回: {path}")
        return send_from_directory(app.static_folder, path)
    
    # SPA fallback - 所有未匹配的路由返回 index.html
    # 这样可以支持前端路由（如 /inventory, /settings 等）
    # print(f"[DEBUG] 文件不存在，返回 index.html (SPA fallback)")
    return send_from_directory(app.static_folder, 'index.html')

def webServer():
    """
    静态文件服务器 - 用于提供 WebSite 前端页面
    端口: 9003
    """
    
    # 检查静态文件目录是否存在
    if not os.path.exists(app.static_folder):
        print(f"❌ 错误: 静态文件目录不存在: {app.static_folder}")
        print(f"📁 程序运行目录: {get_base_path()}")
        print("请确保 WebSite/dist 目录存在")
        input("按任意键退出...")
        return
    
    # 禁用 werkzeug 的 HTTP 请求日志
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    print("=" * 50)
    print("🌐 WebServer 静态文件服务器已启动")
    print("=" * 50)
    print(f"📁 静态文件目录: {os.path.abspath(app.static_folder)}")
    print(f"🔗 访问地址: http://localhost:9003")
    print(f"🔗 访问地址: http://127.0.0.1:9003")
    print("=" * 50)
    
    app.run(debug=False, port=9003, host='0.0.0.0')

if __name__ == '__main__':
    webServer()
