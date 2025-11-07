"""
Charles证书管理器
用于安装和管理Charles代理证书
"""

import os
import hashlib
import tempfile
from typing import Optional
from .adb_manager import ADBManager


class CharlesCertManager:
    """Charles证书管理器"""
    
    # Charles证书内容
    CHARLES_CERT = """-----BEGIN CERTIFICATE-----
MIIFQjCCBCqgAwIBAgIGAZpYklggMA0GCSqGSIb3DQEBCwUAMIGlMTYwNAYDVQQDDC1DaGFybGVz
IFByb3h5IENBICg2IE5vdiAyMDI1LCBNQUtVUk8tREVTS1RPUCkxJTAjBgNVBAsMHGh0dHBzOi8v
Y2hhcmxlc3Byb3h5LmNvbS9zc2wxETAPBgNVBAoMCFhLNzIgTHRkMREwDwYDVQQHDAhBdWNrbGFu
ZDERMA8GA1UECAwIQXVja2xhbmQxCzAJBgNVBAYTAk5aMB4XDTI1MTEwNTA5NDkzN1oXDTI2MTEw
NTA5NDkzN1owgaUxNjA0BgNVBAMMLUNoYXJsZXMgUHJveHkgQ0EgKDYgTm92IDIwMjUsIE1BS1VS
Ty1ERVNLVE9QKTElMCMGA1UECwwcaHR0cHM6Ly9jaGFybGVzcHJveHkuY29tL3NzbDERMA8GA1UE
CgwIWEs3MiBMdGQxETAPBgNVBAcMCEF1Y2tsYW5kMREwDwYDVQQIDAhBdWNrbGFuZDELMAkGA1UE
BhMCTlowggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDLFmGPr6cVfOcf1g7jv3ZT4rsS
QsGSaQqecCa3FVotYrI3IJcg34sU5vyuljLLjW3s2qVckksUkLC/KCMDs0RI8uwV7T26PdARCYXx
7j7nV+tSAdr12KLALRgnsNt6IdzNRBek7vdORFcO3fFTQrprqUXXzpaEquKwkvRzvfX8MoE4/pZg
i1JyHlloRn/Dm20jQOKvEmir0empGv4YQLXoOQvUMuK2VfcACrIkiHq//OsTXn81zYSrTpun7P6s
6jJ/aa3KLB19CqJde/fxB5J/+Aok0Z1iDcfjzgk673CPQspyStfE4RRa/j3SNsAyIf6Z1AO0seXJ
Tau2Kn9hwSAfAgMBAAGjggF0MIIBcDAPBgNVHRMBAf8EBTADAQH/MIIBLAYJYIZIAYb4QgENBIIB
HROCARlUaGlzIFJvb3QgY2VydGlmaWNhdGUgd2FzIGdlbmVyYXRlZCBieSBDaGFybGVzIFByb3h5
IGZvciBTU0wgUHJveHlpbmcuIElmIHRoaXMgY2VydGlmaWNhdGUgaXMgcGFydCBvZiBhIGNlcnRp
ZmljYXRlIGNoYWluLCB0aGlzIG1lYW5zIHRoYXQgeW91J3JlIGJyb3dzaW5nIHRocm91Z2ggQ2hh
cmxlcyBQcm94eSB3aXRoIFNTTCBQcm94eWluZyBlbmFibGVkIGZvciB0aGlzIHdlYnNpdGUuIFBs
ZWFzZSBzZWUgaHR0cDovL2NoYXJsZXNwcm94eS5jb20vc3NsIGZvciBtb3JlIGluZm9ybWF0aW9u
LjAOBgNVHQ8BAf8EBAMCAgQwHQYDVR0OBBYEFNjO5CCh0Rec14BBtrn3uovqWyjnMA0GCSqGSIb3
DQEBCwUAA4IBAQAGSpNUx8eysNMbmZsQ+pTyfAOjM8wxYNVC7OlIUxeTStUn6pkYgBNvh9gznrU4
2GTO3Z35isKJOiu7pN4uJRZ59fff5vgEup5AvjJaU6urM6Z9f5VTb/+ca0L/zjX/hzoWYjbcMTmv
s3QVRz0P1REdKjgInMitAV4HsdZYu+Zc4LX6KNBeY81LDIm5Ou3p5a5bQaVpY3B0BZsBH/+x2HI2
YST/MxU4rvsps28Vt8SCSPLYx8jlF9WbZOik4wlYN33qXlVMjTdvmYjAb7Ws4P3YkrYcLMFS5UJL
8xFey1XRuxXN0zYCRVn0LzpIRxstVaF37f6lPrdjfUIbRX55qaZV
-----END CERTIFICATE-----"""
    
    def __init__(self, adb_manager: Optional[ADBManager] = None):
        """
        初始化证书管理器
        
        Args:
            adb_manager: ADB管理器实例，如果为None则创建新实例
        """
        self.adb = adb_manager if adb_manager else ADBManager()
        self.cert_hash = None
        self.temp_cert_path = None
        
    def _calculate_cert_hash(self) -> str:
        """
        计算证书的hash值（Android系统证书命名规则）
        使用OpenSSL的subject_hash_old算法
        
        Returns:
            str: 证书hash值
        """
        try:
            from cryptography import x509
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives import hashes
            
            # 解析证书
            cert = x509.load_pem_x509_certificate(
                self.CHARLES_CERT.encode(),
                default_backend()
            )
            
            # 获取Subject DN
            subject = cert.subject
            
            # 构建Subject字符串（按OpenSSL格式）
            subject_str = ""
            for attr in subject:
                subject_str += f"/{attr.oid._name}={attr.value}"
            
            # 计算MD5 hash（OpenSSL subject_hash_old使用MD5）
            hash_obj = hashlib.md5(subject_str.encode())
            hash_bytes = hash_obj.digest()
            
            # 转换为OpenSSL的hash格式（取前4字节，小端序）
            hash_value = int.from_bytes(hash_bytes[:4], byteorder='little')
            return f"{hash_value:08x}"
            
        except Exception as e:
            print(f"使用cryptography计算hash失败: {e}")
            # 备用方法：使用固定的hash（从设备实际安装的证书得出）
            # 这个hash是从你的设备日志中看到的实际值
            return "fdfa4fd9"  # Charles证书的实际hash值
    
    def _create_temp_cert_file(self) -> str:
        """
        创建临时证书文件
        
        Returns:
            str: 临时文件路径
        """
        if self.temp_cert_path and os.path.exists(self.temp_cert_path):
            return self.temp_cert_path
        
        # 计算证书hash
        self.cert_hash = self._calculate_cert_hash()
        
        # 创建临时文件
        temp_dir = tempfile.gettempdir()
        cert_filename = f"{self.cert_hash}.0"
        self.temp_cert_path = os.path.join(temp_dir, cert_filename)
        
        # 写入证书内容
        with open(self.temp_cert_path, 'w', encoding='utf-8') as f:
            f.write(self.CHARLES_CERT)
        
        print(f"临时证书文件已创建: {self.temp_cert_path}")
        return self.temp_cert_path
    
    def _cleanup_temp_file(self):
        """清理临时证书文件"""
        if self.temp_cert_path and os.path.exists(self.temp_cert_path):
            try:
                os.remove(self.temp_cert_path)
                print(f"临时证书文件已删除: {self.temp_cert_path}")
            except Exception as e:
                print(f"删除临时文件失败: {e}")
    
    def check_cert_installed(self) -> bool:
        """
        检查证书是否已安装
        
        Returns:
            bool: 证书是否已安装
        """
        if not self.adb.device:
            print("未选择设备")
            return False
        
        self.cert_hash = self._calculate_cert_hash()
        cert_filename = f"{self.cert_hash}.0"
        
        # 可能的证书目录列表（不同Android版本可能不同）
        cert_paths = [
            f"/system/etc/security/cacerts/{cert_filename}",
            f"/apex/com.android.conscrypt/cacerts/{cert_filename}",  # Android 14+
            f"/data/misc/user/0/cacerts-added/{cert_filename}",  # 用户证书
        ]
        
        for cert_path in cert_paths:
            # 使用 test 命令检查文件是否存在（更可靠）
            success, result = self.adb.execute_shell(f"test -f {cert_path} && echo 'EXISTS' || echo 'NOT_EXISTS'")
            
            if success and 'EXISTS' in result and 'NOT_EXISTS' not in result:
                print(f"证书已安装: {cert_filename} (位置: {cert_path})")
                return True
        
        print(f"证书未安装")
        return False
    
    def install_cert(self, force: bool = False) -> bool:
        """
        安装Charles证书到Android设备
        
        Args:
            force: 是否强制重新安装
            
        Returns:
            bool: 是否安装成功
        """
        if not self.adb.device:
            print("错误: 未选择设备")
            return False
        
        # 检查设备信息
        device_info = self.adb.get_device_info()
        print(f"设备信息: {device_info}")
        
        # 检查是否已安装
        if self.check_cert_installed():
            if not force:
                print("证书已存在，跳过安装。如需重新安装，请使用 force=True")
                return True
            else:
                print("证书已存在，但设置了force=True，将强制重新安装...")
        
        try:
            # 1. 创建临时证书文件
            local_cert_path = self._create_temp_cert_file()
            cert_filename = f"{self.cert_hash}.0"
            
            # 2. 挂载系统分区为可写（需要root权限）
            print("尝试重新挂载系统分区为可写...")
            success, result = self.adb.execute_shell("su -c 'mount -o remount,rw /system'")
            if not success:
                print(f"挂载失败: {result}")
                print("提示: 某些设备可能需要先授予root权限")
                return False
            
            # 3. 推送证书到临时目录
            temp_remote_path = f"/sdcard/{cert_filename}"
            print(f"推送证书到设备...")
            if not self.adb.push_file(local_cert_path, temp_remote_path):
                return False
            
            # 4. 移动证书到系统证书目录
            print("移动证书到系统目录...")
            success, result = self.adb.execute_shell(
                f"su -c 'mv {temp_remote_path} /system/etc/security/cacerts/{cert_filename}'"
            )
            if not success:
                print(f"移动证书失败: {result}")
                return False
            
            # 5. 设置证书权限
            print("设置证书权限...")
            success, result = self.adb.execute_shell(
                f"su -c 'chmod 644 /system/etc/security/cacerts/{cert_filename}'"
            )
            if not success:
                print(f"设置权限失败: {result}")
            
            # 6. 设置证书所有者
            success, result = self.adb.execute_shell(
                f"su -c 'chown root:root /system/etc/security/cacerts/{cert_filename}'"
            )
            if not success:
                print(f"设置所有者失败: {result}")
            
            # 7. 重新挂载系统分区为只读
            print("重新挂载系统分区为只读...")
            self.adb.execute_shell("su -c 'mount -o remount,ro /system'")
            
            # 8. 验证安装
            if self.check_cert_installed():
                print("✓ Charles证书安装成功!")
                
                # 9. 自动重启网络使证书生效
                print("正在重启网络以使证书生效...")
                if self.adb.restart_network():
                    print("✓ 网络已重启，证书已生效")
                else:
                    print("⚠ 网络重启失败，建议手动重启设备")
                
                return True
            else:
                print("✗ 证书安装验证失败")
                return False
                
        except Exception as e:
            print(f"安装证书时发生错误: {e}")
            return False
        finally:
            # 清理临时文件
            self._cleanup_temp_file()
    
    def uninstall_cert(self) -> bool:
        """
        卸载Charles证书
        
        Returns:
            bool: 是否卸载成功
        """
        if not self.adb.device:
            print("错误: 未选择设备")
            return False
        
        if not self.check_cert_installed():
            print("证书未安装，无需卸载")
            return True
        
        try:
            cert_filename = f"{self.cert_hash}.0"
            cert_path = f"/system/etc/security/cacerts/{cert_filename}"
            
            # 1. 挂载系统分区为可写
            print("重新挂载系统分区为可写...")
            success, result = self.adb.execute_shell("su -c 'mount -o remount,rw /system'")
            if not success:
                print(f"挂载失败: {result}")
                return False
            
            # 2. 检查文件是否存在
            success, result = self.adb.execute_shell(f"su -c 'ls -la {cert_path}'")
            print(f"删除前文件状态: {result}")
            
            # 3. 删除证书文件（使用 -f 参数强制删除）
            print("删除证书文件...")
            success, result = self.adb.execute_shell(
                f"su -c 'rm -f {cert_path}'"
            )
            print(f"删除命令执行结果: success={success}, output={result}")
            
            # 4. 再次检查文件是否还存在
            success, result = self.adb.execute_shell(f"su -c 'ls -la {cert_path}'")
            print(f"删除后文件状态: {result}")
            
            # 如果文件仍然存在，说明删除失败
            if "No such file" not in result and cert_filename in result:
                print(f"警告: 文件仍然存在，尝试其他删除方式")
                # 尝试使用 busybox rm
                self.adb.execute_shell(f"su -c 'busybox rm -f {cert_path}'")
                # 或者直接清空文件
                self.adb.execute_shell(f"su -c 'echo \"\" > {cert_path}'")
                self.adb.execute_shell(f"su -c 'rm -f {cert_path}'")
            
            # 5. 重新挂载系统分区为只读
            print("重新挂载系统分区为只读...")
            self.adb.execute_shell("su -c 'mount -o remount,ro /system'")
            
            # 6. 等待一下确保操作生效
            import time
            time.sleep(1)
            
            # 7. 验证卸载
            if not self.check_cert_installed():
                print("✓ Charles证书卸载成功!")
                return True
            else:
                print("✗ 证书卸载验证失败")
                print(f"提示: 某些设备可能需要重启才能完全删除证书")
                return False
                
        except Exception as e:
            print(f"卸载证书时发生错误: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # 确保系统分区恢复为只读
            try:
                self.adb.execute_shell("su -c 'mount -o remount,ro /system'")
            except:
                pass
    
    def get_cert_info(self) -> dict:
        """
        获取证书信息
        
        Returns:
            dict: 证书信息字典
        """
        self.cert_hash = self._calculate_cert_hash()
        
        return {
            "cert_hash": self.cert_hash,
            "cert_filename": f"{self.cert_hash}.0",
            "installed": self.check_cert_installed(),
            "cert_length": len(self.CHARLES_CERT)
        }

