"""
Charles证书管理器使用示例
"""

from adb_manager import ADBManager
from charles_cert_manager import CharlesCertManager


def main():
    """主函数 - 演示如何使用Charles证书管理器"""
    
    print("=" * 60)
    print("Charles证书管理器 - 使用示例")
    print("=" * 60)
    
    # 1. 创建ADB管理器
    print("\n[步骤 1] 创建ADB管理器...")
    adb = ADBManager()
    
    # 2. 连接ADB服务器
    print("\n[步骤 2] 连接ADB服务器...")
    if not adb.connect():
        print("错误: 无法连接到ADB服务器")
        print("请确保:")
        print("  1. 已安装pure-python-adb: pip install pure-python-adb")
        print("  2. ADB服务器正在运行")
        print("  3. 设备已通过USB连接或网络连接")
        return
    
    # 3. 获取设备列表
    print("\n[步骤 3] 获取已连接的设备...")
    devices = adb.get_devices()
    if not devices:
        print("错误: 未找到任何设备")
        print("请确保:")
        print("  1. 设备已连接到电脑")
        print("  2. 设备已开启USB调试")
        print("  3. 已授权此电脑进行调试")
        return
    
    print(f"找到 {len(devices)} 个设备:")
    for i, device in enumerate(devices):
        print(f"  [{i}] {device.serial}")
    
    # 4. 选择设备
    print("\n[步骤 4] 选择设备...")
    if not adb.select_device():
        print("错误: 无法选择设备")
        return
    
    # 5. 显示设备信息
    print("\n[步骤 5] 获取设备信息...")
    device_info = adb.get_device_info()
    print("设备信息:")
    for key, value in device_info.items():
        print(f"  {key}: {value}")
    
    # 6. 检查root权限
    print("\n[步骤 6] 检查设备root权限...")
    if adb.is_root():
        print("✓ 设备已获得root权限")
    else:
        print("✗ 设备没有root权限")
        print("警告: 安装系统证书需要root权限!")
        print("对于MuMu模拟器，默认具有root权限")
        return
    
    # 7. 创建证书管理器
    print("\n[步骤 7] 创建Charles证书管理器...")
    cert_manager = CharlesCertManager(adb)
    
    # 8. 显示证书信息
    print("\n[步骤 8] 获取证书信息...")
    cert_info = cert_manager.get_cert_info()
    print("证书信息:")
    for key, value in cert_info.items():
        print(f"  {key}: {value}")
    
    # 9. 检查证书是否已安装
    print("\n[步骤 9] 检查证书安装状态...")
    is_installed = cert_manager.check_cert_installed()
    
    if is_installed:
        print("证书已安装")
        
        # 询问是否要重新安装
        response = input("\n是否要重新安装证书? (y/n): ")
        if response.lower() == 'y':
            print("\n[步骤 10] 重新安装证书...")
            if cert_manager.install_cert(force=True):
                print("✓ 证书重新安装成功!")
            else:
                print("✗ 证书重新安装失败!")
        
        # 询问是否要卸载证书
        response = input("\n是否要卸载证书? (y/n): ")
        if response.lower() == 'y':
            print("\n[步骤 11] 卸载证书...")
            if cert_manager.uninstall_cert():
                print("✓ 证书卸载成功!")
            else:
                print("✗ 证书卸载失败!")
    else:
        print("证书未安装")
        
        # 询问是否要安装证书
        response = input("\n是否要安装证书? (y/n): ")
        if response.lower() == 'y':
            print("\n[步骤 10] 安装证书...")
            if cert_manager.install_cert():
                print("✓ 证书安装成功!")
                print("\n提示:")
                print("  1. 建议重启设备以确保证书生效")
                print("  2. 在设备的 设置 -> 安全 -> 信任的凭据 中可以查看已安装的证书")
                print("  3. 现在可以使用Charles抓取HTTPS流量了")
            else:
                print("✗ 证书安装失败!")
                print("\n可能的原因:")
                print("  1. 设备没有root权限")
                print("  2. 系统分区无法重新挂载")
                print("  3. SELinux策略阻止了操作")
    
    print("\n" + "=" * 60)
    print("操作完成!")
    print("=" * 60)


def quick_install():
    """快速安装 - 自动选择第一个设备并安装证书"""
    
    print("Charles证书快速安装")
    print("-" * 60)
    
    # 创建管理器
    adb = ADBManager()
    
    # 连接并选择设备
    if not adb.connect():
        print("错误: 无法连接到ADB服务器")
        return False
    
    if not adb.select_device():
        print("错误: 未找到设备")
        return False
    
    # 检查root权限
    if not adb.is_root():
        print("错误: 设备没有root权限")
        return False
    
    # 安装证书
    cert_manager = CharlesCertManager(adb)
    return cert_manager.install_cert()


def quick_uninstall():
    """快速卸载 - 自动选择第一个设备并卸载证书"""
    
    print("Charles证书快速卸载")
    print("-" * 60)
    
    # 创建管理器
    adb = ADBManager()
    
    # 连接并选择设备
    if not adb.connect():
        print("错误: 无法连接到ADB服务器")
        return False
    
    if not adb.select_device():
        print("错误: 未找到设备")
        return False
    
    # 卸载证书
    cert_manager = CharlesCertManager(adb)
    return cert_manager.uninstall_cert()


if __name__ == "__main__":
    # 运行交互式示例
    main()
    
    # 或者使用快速安装/卸载:
    # quick_install()
    # quick_uninstall()

