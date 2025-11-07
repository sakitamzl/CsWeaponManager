"""
Charles 证书管理模块
用于向安卓设备（模拟器）安装和更新 Charles SSL 代理证书

参考文档: https://mumu.163.com/mac/tutorials/certificates-and-packet-capture.html
"""

import os
import subprocess
import platform
import shutil
from pathlib import Path
from typing import Tuple, Optional
from src.log import Log


class CharlesCertManager:
    """Charles 证书管理器"""
    
    def __init__(self, adb_path: Optional[str] = None):
        """
        初始化证书管理器
        
        Args:
            adb_path: ADB 可执行文件路径，如果为 None 则使用系统 PATH 中的 adb
        """
        self.log = Log()
        self.adb_path = adb_path or self._find_adb()
        self.system_type = platform.system()  # Windows, Darwin(Mac), Linux
        
        if not self.adb_path:
            raise FileNotFoundError("未找到 ADB 工具，请安装 Android SDK 或指定 ADB 路径")
        
        self.log.write_log(f"ADB 路径: {self.adb_path}", 'info')
        self.log.write_log(f"操作系统: {self.system_type}", 'info')
    
    def _find_adb(self) -> Optional[str]:
        """查找系统中的 ADB 工具"""
        # 尝试从系统 PATH 中查找
        adb_cmd = 'adb.exe' if platform.system() == 'Windows' else 'adb'
        adb_path = shutil.which(adb_cmd)
        
        if adb_path:
            return adb_path
        
        # 常见的 ADB 安装路径
        common_paths = []
        
        if platform.system() == 'Windows':
            common_paths = [
                r'C:\Program Files (x86)\Android\android-sdk\platform-tools\adb.exe',
                r'C:\Android\platform-tools\adb.exe',
                os.path.expanduser(r'~\AppData\Local\Android\Sdk\platform-tools\adb.exe'),
            ]
        elif platform.system() == 'Darwin':  # macOS
            common_paths = [
                '/usr/local/bin/adb',
                os.path.expanduser('~/Library/Android/sdk/platform-tools/adb'),
                '/Applications/MuMuPlayer.app/Contents/MacOS/MuMuEmulator.app/Contents/MacOS/tools/adb',
            ]
        else:  # Linux
            common_paths = [
                '/usr/bin/adb',
                '/usr/local/bin/adb',
                os.path.expanduser('~/Android/Sdk/platform-tools/adb'),
            ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def _run_command(self, command: list, check: bool = True, timeout: int = 30) -> Tuple[bool, str]:
        """
        执行命令
        
        Args:
            command: 命令列表
            check: 是否检查返回码
            timeout: 超时时间（秒）
        
        Returns:
            (成功标志, 输出信息)
        """
        try:
            self.log.write_log(f"执行命令: {' '.join(command)}", 'debug')
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=check,
                timeout=timeout,
                encoding='utf-8',
                errors='ignore'
            )
            
            output = result.stdout + result.stderr
            self.log.write_log(f"命令输出: {output[:500]}", 'debug')
            
            return True, output
            
        except subprocess.TimeoutExpired:
            error_msg = f"命令执行超时 ({timeout}秒)"
            self.log.write_log(error_msg, 'error')
            return False, error_msg
            
        except subprocess.CalledProcessError as e:
            error_msg = f"命令执行失败: {e.stderr}"
            self.log.write_log(error_msg, 'error')
            return False, error_msg
            
        except Exception as e:
            error_msg = f"命令执行异常: {str(e)}"
            self.log.write_log(error_msg, 'error')
            return False, error_msg
    
    def check_adb_connection(self) -> Tuple[bool, str]:
        """
        检查 ADB 连接状态
        
        Returns:
            (成功标志, 设备列表信息)
        """
        self.log.write_log("检查 ADB 连接状态", 'info')
        
        success, output = self._run_command([self.adb_path, 'devices'])
        
        if success:
            # 解析设备列表
            lines = output.strip().split('\n')[1:]  # 跳过第一行 "List of devices attached"
            devices = [line.split('\t')[0] for line in lines if '\tdevice' in line]
            
            if devices:
                device_info = f"已连接设备: {', '.join(devices)}"
                self.log.write_log(device_info, 'info')
                return True, device_info
            else:
                msg = "未检测到连接的设备"
                self.log.write_log(msg, 'warning')
                return False, msg
        
        return False, output
    
    def enable_root(self) -> Tuple[bool, str]:
        """
        启用 ADB root 权限
        
        Returns:
            (成功标志, 消息)
        """
        self.log.write_log("尝试启用 root 权限", 'info')
        
        success, output = self._run_command([self.adb_path, 'root'], check=False)
        
        if success or 'already running as root' in output.lower():
            self.log.write_log("Root 权限已启用", 'info')
            return True, "Root 权限已启用"
        else:
            self.log.write_log(f"启用 root 权限失败: {output}", 'error')
            return False, f"启用 root 权限失败: {output}"
    
    def remount_system(self) -> Tuple[bool, str]:
        """
        重新挂载系统分区为可写
        
        Returns:
            (成功标志, 消息)
        """
        self.log.write_log("尝试重新挂载系统分区", 'info')
        
        success, output = self._run_command([self.adb_path, 'remount'], check=False)
        
        if success:
            self.log.write_log("系统分区重新挂载成功", 'info')
            return True, "系统分区重新挂载成功"
        else:
            self.log.write_log(f"重新挂载失败: {output}", 'warning')
            return False, f"重新挂载失败: {output}"
    
    def convert_cert_format(self, cert_file: str, output_dir: Optional[str] = None) -> Tuple[bool, str]:
        """
        将证书转换为安卓系统格式
        
        证书需要重命名为其 subject_hash_old 值 + .0
        
        Args:
            cert_file: 证书文件路径（.pem 或 .crt）
            output_dir: 输出目录，如果为 None 则使用证书文件所在目录
        
        Returns:
            (成功标志, 转换后的证书路径或错误消息)
        """
        if not os.path.exists(cert_file):
            error_msg = f"证书文件不存在: {cert_file}"
            self.log.write_log(error_msg, 'error')
            return False, error_msg
        
        self.log.write_log(f"转换证书格式: {cert_file}", 'info')
        
        # 检查 openssl 是否可用
        openssl_cmd = 'openssl.exe' if platform.system() == 'Windows' else 'openssl'
        openssl_path = shutil.which(openssl_cmd)
        
        if not openssl_path:
            error_msg = "未找到 OpenSSL 工具，请先安装 OpenSSL"
            self.log.write_log(error_msg, 'error')
            return False, error_msg
        
        try:
            # 获取证书的 subject_hash_old
            result = subprocess.run(
                [openssl_path, 'x509', '-subject_hash_old', '-in', cert_file],
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            cert_hash = result.stdout.strip().split('\n')[0].strip()
            self.log.write_log(f"证书哈希值: {cert_hash}", 'info')
            
            # 确定输出目录
            if output_dir is None:
                output_dir = os.path.dirname(cert_file)
            
            # 生成新的证书文件名
            new_cert_path = os.path.join(output_dir, f"{cert_hash}.0")
            
            # 复制证书文件
            shutil.copy2(cert_file, new_cert_path)
            
            self.log.write_log(f"证书已转换: {new_cert_path}", 'info')
            return True, new_cert_path
            
        except subprocess.CalledProcessError as e:
            error_msg = f"OpenSSL 执行失败: {e.stderr}"
            self.log.write_log(error_msg, 'error')
            return False, error_msg
            
        except Exception as e:
            error_msg = f"证书转换失败: {str(e)}"
            self.log.write_log(error_msg, 'error')
            return False, error_msg
    
    def push_cert_to_system(self, cert_file: str) -> Tuple[bool, str]:
        """
        将证书推送到安卓系统证书目录
        
        Args:
            cert_file: 已转换格式的证书文件路径（格式: hash.0）
        
        Returns:
            (成功标志, 消息)
        """
        if not os.path.exists(cert_file):
            error_msg = f"证书文件不存在: {cert_file}"
            self.log.write_log(error_msg, 'error')
            return False, error_msg
        
        cert_filename = os.path.basename(cert_file)
        target_path = f"/system/etc/security/cacerts/{cert_filename}"
        
        self.log.write_log(f"推送证书到设备: {cert_file} -> {target_path}", 'info')
        
        # 推送证书
        success, output = self._run_command([self.adb_path, 'push', cert_file, target_path])
        
        if not success:
            return False, f"推送证书失败: {output}"
        
        self.log.write_log("证书推送成功", 'info')
        
        # 设置证书权限 (644)
        self.log.write_log("设置证书权限", 'info')
        success, output = self._run_command(
            [self.adb_path, 'shell', f'chmod 644 {target_path}'],
            check=False
        )
        
        if success:
            self.log.write_log("证书权限设置成功", 'info')
            return True, "证书安装成功"
        else:
            self.log.write_log(f"设置权限失败: {output}", 'warning')
            return True, "证书已推送，但权限设置可能失败"
    
    def install_charles_cert(self, cert_file: str, force: bool = False) -> Tuple[bool, str]:
        """
        完整的 Charles 证书安装流程
        
        Args:
            cert_file: Charles 证书文件路径（.pem 或 .crt 格式）
            force: 是否强制安装（即使已存在）
        
        Returns:
            (成功标志, 详细消息)
        """
        self.log.write_log("=" * 60, 'info')
        self.log.write_log("开始安装 Charles 证书", 'info')
        self.log.write_log("=" * 60, 'info')
        
        # 步骤 1: 检查 ADB 连接
        success, msg = self.check_adb_connection()
        if not success:
            return False, f"ADB 连接检查失败: {msg}"
        
        # 步骤 2: 启用 root 权限
        success, msg = self.enable_root()
        if not success:
            return False, f"启用 root 权限失败: {msg}\n提示: 请确保设备已 root 或使用支持 root 的模拟器（如 MuMu 模拟器）"
        
        # 步骤 3: 重新挂载系统分区
        success, msg = self.remount_system()
        if not success:
            self.log.write_log(f"重新挂载警告: {msg}，尝试继续...", 'warning')
        
        # 步骤 4: 转换证书格式
        success, result = self.convert_cert_format(cert_file)
        if not success:
            return False, f"证书格式转换失败: {result}"
        
        converted_cert_path = result
        cert_filename = os.path.basename(converted_cert_path)
        
        # 步骤 5: 检查证书是否已存在
        if not force:
            target_path = f"/system/etc/security/cacerts/{cert_filename}"
            success, output = self._run_command(
                [self.adb_path, 'shell', f'ls {target_path}'],
                check=False
            )
            
            if success and target_path in output:
                msg = f"证书已存在: {target_path}，使用 force=True 强制更新"
                self.log.write_log(msg, 'warning')
                return True, msg
        
        # 步骤 6: 推送证书到系统
        success, msg = self.push_cert_to_system(converted_cert_path)
        
        if success:
            self.log.write_log("=" * 60, 'info')
            self.log.write_log("Charles 证书安装完成！", 'info')
            self.log.write_log("请重启设备或模拟器以使证书生效", 'info')
            self.log.write_log("=" * 60, 'info')
            return True, f"证书安装成功: {cert_filename}\n请重启设备使证书生效"
        else:
            return False, msg
    
    def list_installed_certs(self) -> Tuple[bool, str]:
        """
        列出已安装的系统证书
        
        Returns:
            (成功标志, 证书列表或错误消息)
        """
        self.log.write_log("查询已安装的系统证书", 'info')
        
        success, output = self._run_command(
            [self.adb_path, 'shell', 'ls -l /system/etc/security/cacerts/'],
            check=False
        )
        
        if success:
            return True, output
        else:
            return False, "查询证书列表失败"
    
    def remove_cert(self, cert_hash: str) -> Tuple[bool, str]:
        """
        移除指定的证书
        
        Args:
            cert_hash: 证书哈希值（文件名，如 "9a5ba575.0"）
        
        Returns:
            (成功标志, 消息)
        """
        self.log.write_log(f"移除证书: {cert_hash}", 'info')
        
        # 启用 root 权限
        success, msg = self.enable_root()
        if not success:
            return False, f"启用 root 权限失败: {msg}"
        
        # 重新挂载系统分区
        self.remount_system()
        
        # 删除证书
        target_path = f"/system/etc/security/cacerts/{cert_hash}"
        success, output = self._run_command(
            [self.adb_path, 'shell', f'rm {target_path}'],
            check=False
        )
        
        if success:
            self.log.write_log(f"证书已移除: {cert_hash}", 'info')
            return True, f"证书已移除: {cert_hash}"
        else:
            return False, f"移除证书失败: {output}"
    
    def reboot_device(self) -> Tuple[bool, str]:
        """
        重启设备
        
        Returns:
            (成功标志, 消息)
        """
        self.log.write_log("重启设备", 'info')
        
        success, output = self._run_command([self.adb_path, 'reboot'], check=False)
        
        if success:
            return True, "设备重启命令已发送"
        else:
            return False, f"重启失败: {output}"


def main():
    """命令行测试入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Charles 证书管理工具')
    parser.add_argument('action', choices=['install', 'list', 'remove', 'check', 'reboot'],
                        help='操作: install-安装证书, list-列出证书, remove-移除证书, check-检查连接, reboot-重启设备')
    parser.add_argument('--cert', help='证书文件路径（install 操作必需）')
    parser.add_argument('--hash', help='证书哈希值（remove 操作必需）')
    parser.add_argument('--adb', help='ADB 工具路径')
    parser.add_argument('--force', action='store_true', help='强制安装（覆盖已存在的证书）')
    
    args = parser.parse_args()
    
    try:
        manager = CharlesCertManager(adb_path=args.adb)
        
        if args.action == 'check':
            success, msg = manager.check_adb_connection()
            print(msg)
            
        elif args.action == 'list':
            success, msg = manager.list_installed_certs()
            print(msg)
            
        elif args.action == 'install':
            if not args.cert:
                print("错误: 安装证书需要指定 --cert 参数")
                return
            success, msg = manager.install_charles_cert(args.cert, force=args.force)
            print(msg)
            
        elif args.action == 'remove':
            if not args.hash:
                print("错误: 移除证书需要指定 --hash 参数")
                return
            success, msg = manager.remove_cert(args.hash)
            print(msg)
            
        elif args.action == 'reboot':
            success, msg = manager.reboot_device()
            print(msg)
        
    except Exception as e:
        print(f"错误: {str(e)}")


if __name__ == '__main__':
    main()

