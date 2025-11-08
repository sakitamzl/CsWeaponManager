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
        使用OpenSSL的subject_hash_old算法（纯Python实现）
        
        Returns:
            str: 证书hash值
            
        Raises:
            Exception: 如果计算失败
        """
        try:
            from cryptography import x509
            from cryptography.hazmat.backends import default_backend
            import hashlib
            
            # 解析证书
            cert = x509.load_pem_x509_certificate(
                self.CHARLES_CERT.encode(),
                default_backend()
            )
            
            # 获取Subject的DER编码（这是OpenSSL subject_hash_old使用的）
            subject_der = cert.subject.public_bytes(default_backend())
            
            # 使用MD5计算hash（OpenSSL subject_hash_old使用MD5）
            md5_hash = hashlib.md5(subject_der).digest()
            
            # 转换为OpenSSL格式的hash（取前4字节，小端序）
            hash_value = int.from_bytes(md5_hash[:4], byteorder='little')
            hash_str = f"{hash_value:08x}"
            
            print(f"✓ 计算的证书hash: {hash_str}")
            return hash_str
            
        except Exception as e:
            print(f"计算证书hash失败: {e}")
            import traceback
            print(traceback.format_exc())
            raise Exception(f"计算证书hash失败: {str(e)}")
    
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
            # 对于系统目录，需要使用 su -c 来获取root权限
            if '/system/' in cert_path or '/apex/' in cert_path:
                success, result = self.adb.execute_shell(f"su -c 'test -f {cert_path} && echo EXISTS || echo NOT_EXISTS'")
            else:
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
        
        # 检查并请求root权限
        if not device_info.get('is_root', False):
            print("设备未检测到root权限，尝试主动请求...")
            if not self.adb.request_root():
                print("✗ 无法获取root权限，证书安装需要root权限")
                return False
        else:
            print("✓ 设备已有root权限")
        
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
            
            # 检查当前挂载状态
            success, mount_info = self.adb.execute_shell("su -c 'mount | grep system'")
            print(f"当前系统分区挂载状态:\n{mount_info}")
            
            # 提取实际的设备路径
            device_path = None
            if '/dev/block/' in mount_info:
                import re
                match = re.search(r'(/dev/block/\S+)', mount_info)
                if match:
                    device_path = match.group(1)
                    print(f"检测到设备路径: {device_path}")
            
            # 尝试多种挂载方式（Android 12+可能需要不同的方式）
            mount_commands = [
                "mount -o remount,rw /system",
                "mount -o rw,remount /system",
                "mount -o remount,rw /",
            ]
            
            # 如果检测到设备路径，添加直接挂载设备的命令
            if device_path:
                mount_commands.insert(0, f"mount -o remount,rw {device_path} /system")
                mount_commands.insert(1, f"mount -o rw,remount {device_path}")
            
            # 对于某些设备，可能需要禁用dm-verity
            mount_commands.extend([
                "mount -o remount,rw,hidepid=0 /system",
                "busybox mount -o remount,rw /system",
            ])
            
            mount_success = False
            for cmd in mount_commands:
                success, result = self.adb.execute_shell(f"su -c '{cmd} 2>&1'")
                print(f"尝试挂载命令: {cmd}")
                if result.strip():
                    print(f"结果: {result}")
                
                # 验证是否挂载成功（检查是否可写）
                success, test_result = self.adb.execute_shell(
                    "su -c 'touch /system/etc/security/cacerts/.test 2>&1 && rm /system/etc/security/cacerts/.test 2>&1 && echo WRITABLE || echo READONLY'"
                )
                if 'WRITABLE' in test_result:
                    print("✓ 系统分区已成功挂载为可写")
                    mount_success = True
                    break
            
            if not mount_success:
                print("✗ 无法将系统分区挂载为可写")
                print("\n尝试使用替代方案：通过Magisk覆盖目录安装...")
                
                # 使用Magisk的覆盖目录（如果可用）
                magisk_paths = [
                    "/data/adb/modules/custom_certs/system/etc/security/cacerts",
                    "/sbin/.magisk/modules/custom_certs/system/etc/security/cacerts",
                ]
                
                magisk_success = False
                for magisk_path in magisk_paths:
                    # 检查Magisk目录是否存在
                    success, result = self.adb.execute_shell(f"su -c 'test -d /data/adb/modules && echo EXISTS || echo NOT_EXISTS'")
                    if 'EXISTS' in result:
                        print(f"尝试使用Magisk模块路径: {magisk_path}")
                        
                        # 创建目录结构
                        success, result = self.adb.execute_shell(f"su -c 'mkdir -p {magisk_path}'")
                        if success:
                            print(f"✓ 已创建Magisk模块目录")
                            # 标记使用Magisk方案
                            self._use_magisk_path = magisk_path
                            mount_success = True
                            magisk_success = True
                            break
                
                if not magisk_success:
                    print("\n可能的原因:")
                    print("  1. 设备启用了dm-verity或AVB验证")
                    print("  2. 系统分区被保护为只读")
                    print("  3. Magisk未正确安装")
                    print("\n解决方案:")
                    print("  1. 在Magisk中禁用'Preserve force encryption'")
                    print("  2. 使用'adb disable-verity && adb reboot'命令（需要重启）")
                    print("  3. 手动安装Magisk模块来管理证书")
                    return False
                else:
                    print("✓ 将使用Magisk模块方式安装证书")
            
            # 3. 推送证书到临时目录
            temp_remote_path = f"/sdcard/{cert_filename}"
            print(f"推送证书到设备...")
            if not self.adb.push_file(local_cert_path, temp_remote_path):
                return False
            
            # 验证文件是否成功推送
            success, result = self.adb.execute_shell(f"ls -la {temp_remote_path}")
            print(f"推送后文件状态: {result}")
            if "No such file" in result:
                print("✗ 证书文件推送失败")
                return False
            
            # 4. 复制证书到系统证书目录（使用cp而不是mv，更可靠）
            # 检查是否使用Magisk路径
            if hasattr(self, '_use_magisk_path') and self._use_magisk_path:
                target_path = f"{self._use_magisk_path}/{cert_filename}"
                print(f"复制证书到Magisk模块目录: {target_path}")
            else:
                target_path = f"/system/etc/security/cacerts/{cert_filename}"
                print(f"复制证书到系统目录: {target_path}")
            
            # 先删除旧文件（如果存在）
            self.adb.execute_shell(f"su -c 'rm -f {target_path}'")
            
            # 复制文件
            success, result = self.adb.execute_shell(
                f"su -c 'cp {temp_remote_path} {target_path}'"
            )
            print(f"复制命令执行结果: success={success}, output={result}")
            
            # 验证文件是否已经复制到目标位置
            success, result = self.adb.execute_shell(
                f"su -c 'ls -la {target_path}'"
            )
            print(f"复制后文件状态: {result}")
            
            if "No such file" in result:
                print("✗ 证书文件复制失败")
                # 清理临时文件
                self.adb.execute_shell(f"rm {temp_remote_path}")
                return False
            
            # 清理临时文件
            self.adb.execute_shell(f"rm {temp_remote_path}")
            print(f"已清理临时文件: {temp_remote_path}")
            
            # 如果使用Magisk方案，创建module.prop文件
            if hasattr(self, '_use_magisk_path') and self._use_magisk_path:
                module_dir = "/data/adb/modules/custom_certs"
                print(f"创建Magisk模块配置...")
                
                # 创建module.prop
                module_prop = """id=custom_certs
name=Custom CA Certificates
version=1.0
versionCode=1
author=CsWeaponManager
description=Install custom CA certificates (Charles Proxy)
"""
                # 写入module.prop
                self.adb.execute_shell(f"su -c 'echo \"{module_prop}\" > {module_dir}/module.prop'")
                
                # 创建update标记（告诉Magisk更新模块）
                self.adb.execute_shell(f"su -c 'touch {module_dir}/update'")
                
                print(f"✓ Magisk模块配置已创建")
            
            # 5. 设置证书权限
            print("设置证书权限...")
            success, result = self.adb.execute_shell(
                f"su -c 'chmod 644 {target_path}'"
            )
            if not success:
                print(f"设置权限失败: {result}")
            else:
                print(f"✓ 权限设置成功")
            
            # 6. 设置证书所有者
            print("设置证书所有者...")
            success, result = self.adb.execute_shell(
                f"su -c 'chown root:root {target_path}'"
            )
            if not success:
                print(f"设置所有者失败: {result}")
            else:
                print(f"✓ 所有者设置成功")
            
            # 7. 重新挂载系统分区为只读
            print("重新挂载系统分区为只读...")
            self.adb.execute_shell("su -c 'mount -o remount,ro /system'")
            
            # 8. 等待文件系统同步
            import time
            time.sleep(1)
            
            # 9. 验证安装
            print("开始验证证书安装...")
            
            # 如果使用Magisk方案，需要重启才能验证
            if hasattr(self, '_use_magisk_path') and self._use_magisk_path:
                print("✓ Charles证书已安装到Magisk模块!")
                print("⚠ 重要提示: 必须重启设备才能使Magisk模块生效")
                print("   重启后证书将自动加载到系统证书目录")
                return True
            
            if self.check_cert_installed():
                print("✓ Charles证书安装成功!")
                print("提示: 请重启模拟器/设备以使证书生效")
                return True
            else:
                print("✗ 证书安装验证失败")
                # 额外调试：直接检查文件
                print("尝试直接检查文件...")
                success, result = self.adb.execute_shell(
                    f"su -c 'ls -la /system/etc/security/cacerts/ | grep {self.cert_hash}'"
                )
                print(f"直接检查结果: {result}")
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

