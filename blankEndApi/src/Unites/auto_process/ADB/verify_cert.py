"""
验证Charles证书安装情况
"""

from adb_manager import ADBManager
from charles_cert_manager import CharlesCertManager


def main():
    print("=" * 60)
    print("Charles证书安装验证工具")
    print("=" * 60)
    
    # 连接设备
    adb = ADBManager()
    if not adb.connect():
        print("✗ 无法连接ADB服务器")
        return
    
    if not adb.select_device():
        print("✗ 未找到设备")
        return
    
    print(f"\n✓ 已连接设备: {adb.device.serial}")
    
    # 获取设备信息
    device_info = adb.get_device_info()
    print(f"设备: {device_info.get('model', '未知')}")
    print(f"Android版本: {device_info.get('android_version', '未知')}")
    
    # 创建证书管理器
    cert_manager = CharlesCertManager(adb)
    cert_hash = cert_manager._calculate_cert_hash()
    cert_filename = f"{cert_hash}.0"
    
    print(f"\n证书Hash: {cert_hash}")
    print(f"证书文件名: {cert_filename}")
    
    # 检查所有可能的证书位置
    print("\n检查证书安装位置:")
    cert_locations = [
        "/system/etc/security/cacerts/",
        "/apex/com.android.conscrypt/cacerts/",
        "/data/misc/user/0/cacerts-added/",
    ]
    
    found = False
    for location in cert_locations:
        cert_path = f"{location}{cert_filename}"
        success, result = adb.execute_shell(f"ls -la {cert_path}")
        if success and "No such file" not in result:
            print(f"  ✓ 找到: {cert_path}")
            print(f"    {result.strip()}")
            found = True
        else:
            print(f"  ✗ 不存在: {cert_path}")
    
    if not found:
        print("\n⚠ 警告: 未在任何位置找到证书文件!")
    
    # 列出实际存在的证书
    print("\n实际安装的系统证书:")
    success, result = adb.execute_shell("ls -la /system/etc/security/cacerts/ | head -20")
    if success:
        print(result)
    
    # 检查证书内容
    if found:
        print(f"\n检查证书内容:")
        for location in cert_locations:
            cert_path = f"{location}{cert_filename}"
            success, result = adb.execute_shell(f"cat {cert_path} 2>/dev/null | head -5")
            if success and result.strip():
                print(f"\n{cert_path} 内容:")
                print(result[:200])
                break
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()

