"""
ADB工具API接口
用于管理安卓设备和Charles证书安装
"""

from flask import jsonify, request, Blueprint
from src.log import Log
import traceback

adbToolsPage = Blueprint('adbToolsPage', __name__)

# 全局ADB管理器实例（避免每次请求都创建新实例导致连接断开）
_global_adb_manager = None

def get_adb_manager():
    """获取全局ADB管理器实例"""
    global _global_adb_manager
    if _global_adb_manager is None:
        from src.Unites.auto_process.ADB import ADBManager
        _global_adb_manager = ADBManager()
        _global_adb_manager.connect()
    return _global_adb_manager


@adbToolsPage.route('/api/adb/scan', methods=['POST'])
def scan_lan_devices():
    """扫描局域网内的ADB设备"""
    try:
        from src.Unites.auto_process.ADB import ADBManager
        
        data = request.get_json() or {}
        timeout = data.get('timeout', 0.5)
        max_workers = data.get('max_workers', 50)
        
        Log().write_log(f"开始扫描局域网ADB设备，超时: {timeout}s", 'info')
        
        # 扫描设备
        discovered = ADBManager.scan_lan_devices(timeout=timeout, max_workers=max_workers)
        
        if discovered:
            Log().write_log(f"扫描完成，发现 {len(discovered)} 个设备: {discovered}", 'info')
            return jsonify({
                'success': True,
                'data': discovered,
                'message': f'发现 {len(discovered)} 个设备'
            }), 200
        else:
            return jsonify({
                'success': True,
                'data': [],
                'message': '未发现任何设备'
            }), 200
            
    except Exception as e:
        Log().write_log(f"扫描局域网设备失败: {str(e)}", 'error')
        Log().write_log(traceback.format_exc(), 'error')
        return jsonify({
            'success': False,
            'message': f'扫描失败: {str(e)}'
        }), 500


@adbToolsPage.route('/api/adb/connect', methods=['POST'])
def connect_device():
    """连接到指定地址的设备"""
    try:
        data = request.get_json()
        address = data.get('address')
        
        if not address:
            return jsonify({
                'success': False,
                'message': '设备地址不能为空'
            }), 400
        
        adb = get_adb_manager()
        
        # 连接设备
        if adb.connect_device(address):
            Log().write_log(f"成功连接到设备: {address}", 'info')
            return jsonify({
                'success': True,
                'message': f'已连接到设备: {address}'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': f'连接设备失败: {address}'
            }), 500
            
    except Exception as e:
        Log().write_log(f"连接设备失败: {str(e)}", 'error')
        return jsonify({
            'success': False,
            'message': f'连接失败: {str(e)}'
        }), 500


@adbToolsPage.route('/api/adb/devices', methods=['GET'])
def get_adb_devices():
    """获取所有已连接的ADB设备"""
    try:
        # 获取查询参数
        auto_scan = request.args.get('auto_scan', 'false').lower() == 'true'
        
        adb = get_adb_manager()
        
        # 获取设备列表（可选自动扫描）
        devices = adb.get_devices(auto_scan=auto_scan)
        
        if not devices:
            return jsonify({
                'success': True,
                'data': [],
                'message': '未找到任何设备'
            }), 200
        
        # 获取设备详细信息
        device_list = []
        for device_dict in devices:
            serial = device_dict.get('serial')
            state = device_dict.get('state', 'unknown')
            
            if state == 'device' and adb.device and adb.device_address == serial:
                # 当前连接的设备，获取详细信息
                try:
                    device_info = adb.get_device_info()
                    device_list.append(device_info)
                except Exception as e:
                    Log().write_log(f"获取设备 {serial} 信息失败: {str(e)}", 'warning')
                    device_list.append({
                        'serial': serial,
                        'connection': serial,
                        'android_version': '未知',
                        'model': '未知',
                        'sdk_version': '未知',
                        'is_root': False
                    })
            else:
                # 未连接的设备，只显示基本信息
                device_list.append({
                    'serial': serial,
                    'connection': serial,
                    'android_version': '未连接',
                    'model': '未连接',
                    'sdk_version': '未知',
                    'is_root': False
                })
        
        return jsonify({
            'success': True,
            'data': device_list,
            'message': f'找到 {len(device_list)} 个设备'
        }), 200
        
    except ImportError as e:
        Log().write_log(f"导入ADB模块失败: {str(e)}", 'error')
        return jsonify({
            'success': False,
            'message': '系统缺少必要的依赖库，请安装 pure-python-adb: pip install pure-python-adb'
        }), 500
    except Exception as e:
        Log().write_log(f"获取ADB设备列表失败: {str(e)}", 'error')
        Log().write_log(traceback.format_exc(), 'error')
        return jsonify({
            'success': False,
            'message': f'获取设备列表失败: {str(e)}'
        }), 500


@adbToolsPage.route('/api/adb/disconnect', methods=['POST'])
def disconnect_device():
    """断开当前设备连接"""
    try:
        adb = get_adb_manager()
        
        if adb.disconnect():
            return jsonify({
                'success': True,
                'message': '设备已断开连接'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '断开连接失败'
            }), 500
            
    except Exception as e:
        Log().write_log(f"断开设备连接失败: {str(e)}", 'error')
        return jsonify({
            'success': False,
            'message': f'断开连接失败: {str(e)}'
        }), 500


@adbToolsPage.route('/api/adb/device/<serial>/info', methods=['GET'])
def get_device_info(serial):
    """获取指定设备的详细信息"""
    try:
        adb = get_adb_manager()
        
        if not adb.select_device(serial):
            return jsonify({
                'success': False,
                'message': f'未找到设备: {serial}'
            }), 404
        
        device_info = adb.get_device_info()
        
        return jsonify({
            'success': True,
            'data': device_info,
            'message': '获取设备信息成功'
        }), 200
        
    except Exception as e:
        Log().write_log(f"获取设备信息失败: {str(e)}", 'error')
        return jsonify({
            'success': False,
            'message': f'获取设备信息失败: {str(e)}'
        }), 500


@adbToolsPage.route('/api/adb/cert/status', methods=['POST'])
def check_cert_status():
    """检查Charles证书安装状态"""
    try:
        data = request.get_json()
        serial = data.get('serial')
        
        if not serial:
            return jsonify({
                'success': False,
                'message': '设备序列号不能为空'
            }), 400
        
        from src.Unites.auto_process.ADB import CharlesCertManager
        
        adb = get_adb_manager()
        
        if not adb.select_device(serial):
            return jsonify({
                'success': False,
                'message': f'未找到设备: {serial}'
            }), 404
        
        # 创建证书管理器
        cert_manager = CharlesCertManager(adb)
        
        # 检查证书状态
        is_installed = cert_manager.check_cert_installed()
        cert_info = cert_manager.get_cert_info()
        
        return jsonify({
            'success': True,
            'data': {
                'installed': is_installed,
                'cert_info': cert_info
            },
            'message': '证书已安装' if is_installed else '证书未安装'
        }), 200
        
    except Exception as e:
        Log().write_log(f"检查证书状态失败: {str(e)}", 'error')
        Log().write_log(traceback.format_exc(), 'error')
        return jsonify({
            'success': False,
            'message': f'检查证书状态失败: {str(e)}'
        }), 500


@adbToolsPage.route('/api/adb/cert/install', methods=['POST'])
def install_cert():
    """安装Charles证书到设备"""
    try:
        data = request.get_json()
        serial = data.get('serial')
        force = data.get('force', False)
        
        if not serial:
            return jsonify({
                'success': False,
                'message': '设备序列号不能为空'
            }), 400
        
        from src.Unites.auto_process.ADB import CharlesCertManager
        
        adb = get_adb_manager()
        
        # 先断开连接
        adb.disconnect()
        
        # 重新连接设备
        if not adb.connect_device(serial):
            return jsonify({
                'success': False,
                'message': f'无法连接到设备: {serial}'
            }), 500
        
        # 检查root权限
        if not adb.is_root():
            return jsonify({
                'success': False,
                'message': '设备没有root权限，无法安装系统证书'
            }), 403
        
        # 创建证书管理器
        cert_manager = CharlesCertManager(adb)
        
        Log().write_log(f"开始安装Charles证书到设备: {serial}, force={force}", 'info')
        
        # 安装证书
        success = cert_manager.install_cert(force=force)
        
        if success:
            Log().write_log(f"Charles证书安装成功: {serial}，准备重新连接", 'info')
            
            # 断开连接，准备重启
            adb.disconnect()
            
            return jsonify({
                'success': True,
                'message': 'Charles证书安装成功！请重启模拟器/设备以使证书生效，然后重新连接设备'
            }), 200
        else:
            Log().write_log(f"Charles证书安装失败: {serial}", 'error')
            return jsonify({
                'success': False,
                'message': '证书安装失败，请查看日志获取详细信息'
            }), 500
        
    except Exception as e:
        Log().write_log(f"安装证书失败: {str(e)}", 'error')
        Log().write_log(traceback.format_exc(), 'error')
        return jsonify({
            'success': False,
            'message': f'安装证书失败: {str(e)}'
        }), 500


@adbToolsPage.route('/api/adb/cert/uninstall', methods=['POST'])
def uninstall_cert():
    """卸载Charles证书"""
    try:
        data = request.get_json()
        serial = data.get('serial')
        
        if not serial:
            return jsonify({
                'success': False,
                'message': '设备序列号不能为空'
            }), 400
        
        from src.Unites.auto_process.ADB import CharlesCertManager
        
        adb = get_adb_manager()
        
        if not adb.select_device(serial):
            return jsonify({
                'success': False,
                'message': f'未找到设备: {serial}'
            }), 404
        
        # 检查root权限
        if not adb.is_root():
            return jsonify({
                'success': False,
                'message': '设备没有root权限，无法卸载系统证书'
            }), 403
        
        # 创建证书管理器
        cert_manager = CharlesCertManager(adb)
        
        Log().write_log(f"开始卸载Charles证书: {serial}", 'info')
        
        # 卸载证书
        success = cert_manager.uninstall_cert()
        
        if success:
            Log().write_log(f"Charles证书卸载成功: {serial}", 'info')
            return jsonify({
                'success': True,
                'message': 'Charles证书卸载成功'
            }), 200
        else:
            Log().write_log(f"Charles证书卸载失败: {serial}", 'error')
            return jsonify({
                'success': False,
                'message': '证书卸载失败，请查看日志获取详细信息'
            }), 500
        
    except Exception as e:
        Log().write_log(f"卸载证书失败: {str(e)}", 'error')
        Log().write_log(traceback.format_exc(), 'error')
        return jsonify({
            'success': False,
            'message': f'卸载证书失败: {str(e)}'
        }), 500


@adbToolsPage.route('/api/adb/device/<serial>/shell', methods=['POST'])
def execute_shell_command(serial):
    """在设备上执行shell命令"""
    try:
        data = request.get_json()
        command = data.get('command')
        
        if not command:
            return jsonify({
                'success': False,
                'message': '命令不能为空'
            }), 400
        
        from src.Unites.auto_process.ADB import ADBManager
        
        adb = ADBManager()
        
        if not adb.connect():
            return jsonify({
                'success': False,
                'message': 'ADB服务器连接失败'
            }), 500
        
        if not adb.select_device(serial):
            return jsonify({
                'success': False,
                'message': f'未找到设备: {serial}'
            }), 404
        
        # 执行命令
        success, output = adb.execute_shell(command)
        
        if success:
            return jsonify({
                'success': True,
                'data': {
                    'output': output
                },
                'message': '命令执行成功'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': f'命令执行失败: {output}'
            }), 500
        
    except Exception as e:
        Log().write_log(f"执行shell命令失败: {str(e)}", 'error')
        return jsonify({
            'success': False,
            'message': f'执行命令失败: {str(e)}'
        }), 500


@adbToolsPage.route('/api/adb/cert/info', methods=['GET'])
def get_cert_info():
    """获取Charles证书信息"""
    try:
        from src.Unites.auto_process.ADB import CharlesCertManager
        
        # 创建临时证书管理器（不需要连接设备）
        cert_manager = CharlesCertManager()
        cert_info = cert_manager.get_cert_info()
        
        return jsonify({
            'success': True,
            'data': cert_info,
            'message': '获取证书信息成功'
        }), 200
        
    except Exception as e:
        Log().write_log(f"获取证书信息失败: {str(e)}", 'error')
        return jsonify({
            'success': False,
            'message': f'获取证书信息失败: {str(e)}'
        }), 500


@adbToolsPage.route('/api/adb/cert/verify', methods=['POST'])
def verify_cert_installation():
    """验证证书安装情况（调试用）"""
    try:
        data = request.get_json()
        serial = data.get('serial')
        
        if not serial:
            return jsonify({
                'success': False,
                'message': '设备序列号不能为空'
            }), 400
        
        from src.Unites.auto_process.ADB import ADBManager, CharlesCertManager
        
        adb = ADBManager()
        
        if not adb.connect():
            return jsonify({
                'success': False,
                'message': 'ADB服务器连接失败'
            }), 500
        
        if not adb.select_device(serial):
            return jsonify({
                'success': False,
                'message': f'未找到设备: {serial}'
            }), 404
        
        # 创建证书管理器
        cert_manager = CharlesCertManager(adb)
        cert_hash = cert_manager._calculate_cert_hash()
        cert_filename = f"{cert_hash}.0"
        
        # 检查所有可能的位置
        cert_locations = [
            "/system/etc/security/cacerts/",
            "/apex/com.android.conscrypt/cacerts/",
            "/data/misc/user/0/cacerts-added/",
        ]
        
        verification_result = {
            "cert_hash": cert_hash,
            "cert_filename": cert_filename,
            "locations": []
        }
        
        for location in cert_locations:
            cert_path = f"{location}{cert_filename}"
            success, result = adb.execute_shell(f"ls -la {cert_path}")
            
            location_info = {
                "path": cert_path,
                "exists": success and "No such file" not in result,
                "details": result.strip() if success else ""
            }
            
            verification_result["locations"].append(location_info)
        
        # 列出系统证书目录的所有证书
        success, result = adb.execute_shell("ls /system/etc/security/cacerts/ | head -10")
        verification_result["system_certs_sample"] = result.strip() if success else ""
        
        # 检查证书内容的前几行
        for location_info in verification_result["locations"]:
            if location_info["exists"]:
                cert_path = location_info["path"]
                success, content = adb.execute_shell(f"head -3 {cert_path}")
                location_info["content_preview"] = content.strip() if success else ""
        
        return jsonify({
            'success': True,
            'data': verification_result,
            'message': '证书验证完成'
        }), 200
        
    except Exception as e:
        Log().write_log(f"验证证书失败: {str(e)}", 'error')
        Log().write_log(traceback.format_exc(), 'error')
        return jsonify({
            'success': False,
            'message': f'验证失败: {str(e)}'
        }), 500

