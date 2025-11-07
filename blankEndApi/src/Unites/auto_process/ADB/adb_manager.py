"""
ADB管理器
使用pure-python-adb库进行ADB操作，无需外部ADB程序
"""

import time
import subprocess
import os
import socket
import concurrent.futures
from typing import List, Optional, Tuple, Set
from ppadb.client import Client as AdbClient
from ppadb.device import Device


class ADBManager:
    """ADB管理器类"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 5037):
        """
        初始化ADB管理器
        
        Args:
            host: ADB服务器地址
            port: ADB服务器端口
        """
        self.host = host
        self.port = port
        self.client = None
        self.device = None
        
    def _start_adb_server(self) -> bool:
        """
        尝试启动ADB服务器
        
        Returns:
            bool: 是否成功启动
        """
        try:
            # 尝试通过命令启动ADB服务器
            result = subprocess.run(
                ['adb', 'start-server'],
                capture_output=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            if result.returncode == 0:
                print("ADB服务器已启动")
                time.sleep(2)  # 等待服务器启动
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            print(f"无法启动ADB服务器: {e}")
        return False
    
    def connect(self) -> bool:
        """
        连接到ADB服务器，如果连接失败会尝试启动服务器
        
        Returns:
            bool: 连接是否成功
        """
        try:
            self.client = AdbClient(host=self.host, port=self.port)
            # 测试连接
            try:
                self.client.version()
                return True
            except:
                # 连接失败，尝试启动ADB服务器
                print("ADB服务器未响应，尝试启动...")
                if self._start_adb_server():
                    self.client = AdbClient(host=self.host, port=self.port)
                    self.client.version()
                    return True
                return False
        except Exception as e:
            print(f"连接ADB服务器失败: {e}")
            # 最后尝试启动服务器
            if self._start_adb_server():
                try:
                    self.client = AdbClient(host=self.host, port=self.port)
                    self.client.version()
                    return True
                except:
                    pass
            return False
    
    def get_devices(self, auto_scan: bool = False) -> List[Device]:
        """
        获取所有已连接的设备
        
        Args:
            auto_scan: 是否在没有设备时自动扫描局域网
        
        Returns:
            List[Device]: 设备列表
        """
        if not self.client:
            if not self.connect():
                return []
        
        try:
            devices = self.client.devices()
            
            # 如果没有设备且开启了自动扫描
            if not devices and auto_scan:
                print("未发现已连接设备，开始扫描局域网...")
                discovered = self.scan_lan_devices()
                
                # 尝试连接发现的设备
                for address in discovered[:3]:  # 限制最多连接3个设备
                    self.connect_device(address)
                
                # 重新获取设备列表
                time.sleep(1)
                devices = self.client.devices()
            
            return devices
        except Exception as e:
            print(f"获取设备列表失败: {e}")
            return []
    
    def select_device(self, serial: Optional[str] = None) -> bool:
        """
        选择要操作的设备
        
        Args:
            serial: 设备序列号，如果为None则选择第一个设备
            
        Returns:
            bool: 是否成功选择设备
        """
        devices = self.get_devices()
        
        if not devices:
            print("未找到任何设备")
            return False
        
        if serial:
            for device in devices:
                if device.serial == serial:
                    self.device = device
                    print(f"已选择设备: {device.serial}")
                    return True
            print(f"未找到序列号为 {serial} 的设备")
            return False
        else:
            self.device = devices[0]
            print(f"已选择设备: {self.device.serial}")
            return True
    
    def execute_shell(self, command: str) -> Tuple[bool, str]:
        """
        执行shell命令
        
        Args:
            command: 要执行的shell命令
            
        Returns:
            Tuple[bool, str]: (是否成功, 命令输出)
        """
        if not self.device:
            return False, "未选择设备"
        
        try:
            result = self.device.shell(command)
            return True, result
        except Exception as e:
            return False, f"执行命令失败: {e}"
    
    def push_file(self, local_path: str, remote_path: str) -> bool:
        """
        推送文件到设备
        
        Args:
            local_path: 本地文件路径
            remote_path: 设备上的目标路径
            
        Returns:
            bool: 是否成功
        """
        if not self.device:
            print("未选择设备")
            return False
        
        try:
            self.device.push(local_path, remote_path)
            print(f"文件已推送: {local_path} -> {remote_path}")
            return True
        except Exception as e:
            print(f"推送文件失败: {e}")
            return False
    
    def pull_file(self, remote_path: str, local_path: str) -> bool:
        """
        从设备拉取文件
        
        Args:
            remote_path: 设备上的文件路径
            local_path: 本地目标路径
            
        Returns:
            bool: 是否成功
        """
        if not self.device:
            print("未选择设备")
            return False
        
        try:
            self.device.pull(remote_path, local_path)
            print(f"文件已拉取: {remote_path} -> {local_path}")
            return True
        except Exception as e:
            print(f"拉取文件失败: {e}")
            return False
    
    def get_device_info(self) -> dict:
        """
        获取设备信息
        
        Returns:
            dict: 设备信息字典
        """
        if not self.device:
            return {}
        
        info = {
            "connection": self.device.serial,  # 连接地址（IP:端口）
        }
        
        # 获取真实设备序列号
        success, result = self.execute_shell("getprop ro.serialno")
        if success and result.strip():
            info["serial"] = result.strip()
        else:
            # 如果获取不到，使用连接地址作为序列号
            info["serial"] = self.device.serial
        
        # 获取Android版本
        success, result = self.execute_shell("getprop ro.build.version.release")
        if success:
            info["android_version"] = result.strip()
        
        # 获取设备型号
        success, result = self.execute_shell("getprop ro.product.model")
        if success:
            info["model"] = result.strip()
        
        # 获取SDK版本
        success, result = self.execute_shell("getprop ro.build.version.sdk")
        if success:
            info["sdk_version"] = result.strip()
        
        return info
    
    def is_root(self) -> bool:
        """
        检查设备是否已root
        
        Returns:
            bool: 是否已root
        """
        success, result = self.execute_shell("su -c 'id'")
        return success and "uid=0" in result
    
    def restart_as_root(self) -> bool:
        """
        以root权限重启adb
        
        Returns:
            bool: 是否成功
        """
        success, result = self.execute_shell("su -c 'id'")
        if success and "uid=0" in result:
            print("设备已具有root权限")
            return True
        else:
            print("设备没有root权限或root失败")
            return False
    
    def restart_network(self) -> bool:
        """
        重启网络连接，使证书生效
        
        Returns:
            bool: 是否成功
        """
        if not self.device:
            print("未选择设备")
            return False
        
        try:
            print("正在重启网络...")
            
            # 方法1: 切换飞行模式
            # 开启飞行模式
            success1, result1 = self.execute_shell("su -c 'settings put global airplane_mode_on 1'")
            self.execute_shell("su -c 'am broadcast -a android.intent.action.AIRPLANE_MODE --ez state true'")
            
            # 等待1秒
            import time
            time.sleep(1)
            
            # 关闭飞行模式
            success2, result2 = self.execute_shell("su -c 'settings put global airplane_mode_on 0'")
            self.execute_shell("su -c 'am broadcast -a android.intent.action.AIRPLANE_MODE --ez state false'")
            
            if success1 and success2:
                print("✓ 网络重启成功")
                return True
            else:
                print("⚠ 网络重启可能不完整，建议手动重启设备")
                return False
                
        except Exception as e:
            print(f"重启网络失败: {e}")
            return False
    
    @staticmethod
    def _check_adb_port(ip: str, port: int = 5555, timeout: float = 0.5) -> bool:
        """
        检查指定IP和端口是否有ADB服务
        
        Args:
            ip: IP地址
            port: 端口号，默认5555
            timeout: 超时时间（秒）
            
        Returns:
            bool: 是否有ADB服务
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False
    
    @staticmethod
    def scan_lan_devices(timeout: float = 0.5, max_workers: int = 50) -> List[str]:
        """
        扫描局域网内开启ADB的设备
        
        Args:
            timeout: 每个IP的扫描超时时间
            max_workers: 最大并发扫描线程数
            
        Returns:
            List[str]: 发现的设备IP地址列表
        """
        devices = []
        
        # 获取本机IP
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except:
            local_ip = "192.168.1.1"  # 默认值
        
        # 解析网络段
        ip_parts = local_ip.split('.')
        network = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}"
        
        print(f"开始扫描局域网: {network}.0/24")
        print(f"本机IP: {local_ip}")
        
        # 常见的ADB端口
        common_ports = [5555, 5556, 5557, 16384, 7555]  # 包括MuMu模拟器的16384端口
        
        # 要扫描的IP列表
        ips_to_scan = []
        
        # 优先扫描常见端口和本机
        for port in common_ports:
            # 本机
            if ADBManager._check_adb_port("127.0.0.1", port, timeout):
                address = f"127.0.0.1:{port}"
                if address not in devices:
                    devices.append(address)
                    print(f"✓ 发现设备: {address}")
        
        # 扫描局域网其他设备（多个常见端口）
        scan_targets = []
        for i in range(1, 255):
            ip = f"{network}.{i}"
            if ip != local_ip and ip != "127.0.0.1":
                # 为每个IP创建多个端口扫描任务
                for port in [5555, 16384]:  # 主要端口
                    scan_targets.append((ip, port))
        
        # 并发扫描
        def scan_ip_port(target):
            ip, port = target
            if ADBManager._check_adb_port(ip, port, timeout):
                return f"{ip}:{port}"
            return None
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(scan_ip_port, target) for target in scan_targets]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result and result not in devices:
                    devices.append(result)
                    print(f"✓ 发现设备: {result}")
        
        print(f"扫描完成，共发现 {len(devices)} 个设备")
        return devices
    
    def connect_device(self, address: str) -> bool:
        """
        连接到指定地址的设备
        
        Args:
            address: 设备地址，格式为 "ip:port"
            
        Returns:
            bool: 是否成功连接
        """
        try:
            result = subprocess.run(
                ['adb', 'connect', address],
                capture_output=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            if result.returncode == 0:
                print(f"已连接到设备: {address}")
                time.sleep(1)
                return True
        except Exception as e:
            print(f"连接设备失败 {address}: {e}")
        return False
    
    def connect_mumu_emulator(self, port: int = 16384) -> bool:
        """
        连接到MuMu模拟器
        
        Args:
            port: MuMu模拟器的ADB端口，默认16384
            
        Returns:
            bool: 是否成功连接
        """
        try:
            # 尝试使用ADB命令连接
            result = subprocess.run(
                ['adb', 'connect', f'127.0.0.1:{port}'],
                capture_output=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            if result.returncode == 0:
                print(f"已连接到MuMu模拟器 (端口:{port})")
                time.sleep(1)
                return True
        except Exception as e:
            print(f"连接MuMu模拟器失败: {e}")
        return False
    
    @staticmethod
    def get_adb_download_info() -> dict:
        """
        获取ADB下载信息
        
        Returns:
            dict: 包含下载链接和说明的字典
        """
        import platform
        system = platform.system()
        
        info = {
            "required": True,
            "message": "需要安装ADB工具",
            "downloads": {}
        }
        
        if system == "Windows":
            info["downloads"] = {
                "platform_tools": {
                    "name": "Android SDK Platform-Tools (Windows)",
                    "url": "https://dl.google.com/android/repository/platform-tools-latest-windows.zip",
                    "description": "官方ADB工具包，解压后将platform-tools目录添加到系统PATH"
                },
                "mumu": {
                    "name": "使用MuMu模拟器自带的ADB",
                    "path": "C:\\Program Files\\Netease\\MuMu Player 12\\shell\\adb.exe",
                    "description": "如果已安装MuMu模拟器，可以使用其自带的ADB工具"
                }
            }
        elif system == "Darwin":  # macOS
            info["downloads"] = {
                "platform_tools": {
                    "name": "Android SDK Platform-Tools (Mac)",
                    "url": "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip",
                    "description": "官方ADB工具包"
                },
                "homebrew": {
                    "name": "通过Homebrew安装",
                    "command": "brew install android-platform-tools",
                    "description": "推荐使用Homebrew安装"
                }
            }
        else:  # Linux
            info["downloads"] = {
                "platform_tools": {
                    "name": "Android SDK Platform-Tools (Linux)",
                    "url": "https://dl.google.com/android/repository/platform-tools-latest-linux.zip",
                    "description": "官方ADB工具包"
                },
                "apt": {
                    "name": "通过APT安装",
                    "command": "sudo apt-get install adb",
                    "description": "Debian/Ubuntu系统推荐"
                }
            }
        
        return info

