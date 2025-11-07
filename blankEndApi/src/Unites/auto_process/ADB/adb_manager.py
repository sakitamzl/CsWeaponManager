"""
ADB管理器
使用adb-shell库直接通过TCP连接设备，无需ADB服务器
"""

import time
import socket
import concurrent.futures
from typing import List, Optional, Tuple
from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.auth.sign_pythonrsa import PythonRSASigner


class ADBManager:
    """ADB管理器类 - 使用adb-shell直接连接设备"""
    
    def __init__(self):
        """
        初始化ADB管理器
        """
        self.device = None
        self.device_address = None  # 当前连接的设备地址
        self.signer = None
        
    def _get_signer(self):
        """
        获取RSA签名器（用于ADB认证）
        如果没有密钥，会自动生成
        """
        if self.signer is None:
            try:
                from adb_shell.auth.keygen import keygen
                import os
                import tempfile
                
                # 在临时目录生成密钥
                temp_dir = tempfile.gettempdir()
                adbkey_path = os.path.join(temp_dir, 'adbkey')
                
                # 如果密钥不存在，生成新的
                if not os.path.exists(adbkey_path):
                    keygen(adbkey_path)
                
                # 加载密钥
                with open(adbkey_path, 'rb') as f:
                    priv_key = f.read()
                with open(adbkey_path + '.pub', 'rb') as f:
                    pub_key = f.read()
                
                self.signer = PythonRSASigner(pub_key, priv_key)
                print("✓ ADB密钥已加载")
            except Exception as e:
                print(f"⚠ 加载ADB密钥失败: {e}，将尝试无认证连接")
                self.signer = None
        
        return self.signer
    
    def connect(self) -> bool:
        """
        初始化连接（adb-shell不需要连接到服务器）
        
        Returns:
            bool: 始终返回True
        """
        return True
    
    def get_devices(self, auto_scan: bool = False) -> List[dict]:
        """
        获取所有已连接的设备
        注意：adb-shell需要手动扫描或连接，不能像传统ADB那样列出所有设备
        
        Args:
            auto_scan: 是否自动扫描局域网
        
        Returns:
            List[dict]: 设备列表（仅包含当前连接的设备）
        """
        devices = []
        
        # 如果有当前连接的设备，返回它
        if self.device and self.device_address:
            try:
                # 测试连接是否还活着
                self.device.shell("echo test")
                devices.append({
                    'serial': self.device_address,
                    'state': 'device'
                })
            except:
                # 连接已断开
                self.device = None
                self.device_address = None
        
        # 如果需要自动扫描且没有设备
        if auto_scan and not devices:
            print("自动扫描局域网设备...")
            found_devices = self.scan_lan_devices()
            for addr in found_devices:
                devices.append({
                    'serial': addr,
                    'state': 'offline'  # 未连接状态
                })
        
        return devices
    
    def select_device(self, serial: str) -> bool:
        """
        选择要操作的设备
        
        Args:
            serial: 设备序列号或地址（IP:端口）
            
        Returns:
            bool: 是否成功选择
        """
        # 如果已经连接到这个设备，直接返回
        if self.device and self.device_address == serial:
            try:
                # 测试连接
                self.device.shell("echo test")
                return True
            except:
                # 连接已断开，需要重新连接
                pass
        
        # 连接到指定设备
        return self.connect_device(serial)
    
    def execute_shell(self, command: str) -> Tuple[bool, str]:
        """
        执行shell命令
        
        Args:
            command: 要执行的命令
            
        Returns:
            Tuple[bool, str]: (是否成功, 输出结果)
        """
        if not self.device:
            return False, "未连接设备"
        
        try:
            result = self.device.shell(command)
            return True, result
        except Exception as e:
            return False, str(e)
    
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
            print("未连接设备")
            return False
        
        try:
            with open(local_path, 'rb') as f:
                file_data = f.read()
            
            self.device.push(file_data, remote_path)
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
            print("未连接设备")
            return False
        
        try:
            file_data = self.device.pull(remote_path)
            with open(local_path, 'wb') as f:
                f.write(file_data)
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
            "connection": self.device_address,  # 连接地址（IP:端口）
        }
        
        # 获取真实设备序列号
        success, result = self.execute_shell("getprop ro.serialno")
        if success and result.strip():
            info["serial"] = result.strip()
        else:
            # 如果获取不到，使用连接地址作为序列号
            info["serial"] = self.device_address
        
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
        
        # 检查root权限
        info["is_root"] = self.is_root()
        
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
        以root权限重启adb（对于adb-shell，不需要此操作）
        
        Returns:
            bool: 始终返回当前root状态
        """
        return self.is_root()
    
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
            List[str]: 发现的设备地址列表（格式：IP:端口）
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
        
        # 优先扫描本机常见端口
        for port in common_ports:
            if ADBManager._check_adb_port("127.0.0.1", port, timeout):
                address = f"127.0.0.1:{port}"
                if address not in devices:
                    devices.append(address)
                    print(f"✓ 发现设备: {address}")
        
        # 扫描局域网其他设备
        scan_targets = []
        for i in range(1, 255):
            ip = f"{network}.{i}"
            if ip != local_ip:
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
        连接到指定地址的设备（使用adb-shell直接TCP连接）
        
        Args:
            address: 设备地址，格式为 "ip:port"
            
        Returns:
            bool: 是否成功连接
        """
        try:
            # 解析地址
            if ':' in address:
                ip, port = address.split(':')
                port = int(port)
            else:
                ip = address
                port = 5555
            
            print(f"正在连接到设备: {ip}:{port}")
            
            # 创建设备连接
            device = AdbDeviceTcp(ip, port, default_transport_timeout_s=9.0)
            
            # 尝试连接（先不用认证）
            try:
                device.connect(rsa_keys=[], auth_timeout_s=10.0)
                print(f"✓ 已连接到设备: {address} (无需认证)")
            except Exception as e:
                # 如果需要认证，使用签名器
                print(f"需要认证，尝试使用密钥连接...")
                device.close()
                device = AdbDeviceTcp(ip, port, default_transport_timeout_s=9.0)
                
                signer = self._get_signer()
                if signer:
                    device.connect(rsa_keys=[signer], auth_timeout_s=10.0)
                    print(f"✓ 已连接到设备: {address} (已认证)")
                else:
                    raise Exception("无法进行ADB认证")
            
            # 测试连接
            test_result = device.shell("echo test")
            if "test" not in test_result:
                raise Exception("设备响应异常")
            
            # 保存设备连接
            if self.device:
                try:
                    self.device.close()
                except:
                    pass
            
            self.device = device
            self.device_address = address
            
            print(f"✓ 设备连接成功: {address}")
            return True
            
        except Exception as e:
            print(f"连接设备失败 {address}: {e}")
            import traceback
            print(traceback.format_exc())
            return False
    
    def connect_mumu_emulator(self, port: int = 16384) -> bool:
        """
        连接到MuMu模拟器
        
        Args:
            port: MuMu模拟器的ADB端口，默认16384
            
        Returns:
            bool: 是否成功连接
        """
        return self.connect_device(f"127.0.0.1:{port}")
    
    def disconnect(self) -> bool:
        """
        断开设备连接
        
        Returns:
            bool: 是否成功断开
        """
        if self.device:
            try:
                self.device.close()
                print(f"已断开设备连接: {self.device_address}")
                self.device = None
                self.device_address = None
                return True
            except Exception as e:
                print(f"断开连接失败: {e}")
                return False
        return True
    
    def __del__(self):
        """析构函数，自动断开连接"""
        self.disconnect()
