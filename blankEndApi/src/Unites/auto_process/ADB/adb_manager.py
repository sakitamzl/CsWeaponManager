"""
ADB管理器
使用pure-python-adb库进行ADB操作，无需外部ADB程序
"""

import time
from typing import List, Optional, Tuple
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
        
    def connect(self) -> bool:
        """
        连接到ADB服务器
        
        Returns:
            bool: 连接是否成功
        """
        try:
            self.client = AdbClient(host=self.host, port=self.port)
            return True
        except Exception as e:
            print(f"连接ADB服务器失败: {e}")
            return False
    
    def get_devices(self) -> List[Device]:
        """
        获取所有已连接的设备
        
        Returns:
            List[Device]: 设备列表
        """
        if not self.client:
            if not self.connect():
                return []
        
        try:
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
            "serial": self.device.serial,
        }
        
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

