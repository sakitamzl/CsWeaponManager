"""
Charles 证书管理器使用示例
"""

import os
import sys

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
sys.path.insert(0, project_root)

from src.Unites.auto_process.ADB import CharlesCertManager


def example_check_connection():
    """示例: 检查 ADB 连接"""
    print("\n" + "="*60)
    print("示例 1: 检查 ADB 连接")
    print("="*60)
    
    try:
        manager = CharlesCertManager()
        success, msg = manager.check_adb_connection()
        
        if success:
            print(f"✓ {msg}")
        else:
            print(f"✗ {msg}")
            print("\n提示:")
            print("1. 确保模拟器或设备已启动")
            print("2. 运行 'adb devices' 检查连接")
            
    except Exception as e:
        print(f"✗ 错误: {str(e)}")


def example_install_cert():
    """示例: 安装 Charles 证书"""
    print("\n" + "="*60)
    print("示例 2: 安装 Charles 证书")
    print("="*60)
    
    # 这里需要替换为你的证书路径
    cert_file = input("请输入 Charles 证书文件路径（.pem 格式）: ").strip()
    
    if not cert_file:
        print("✗ 未输入证书路径")
        return
    
    if not os.path.exists(cert_file):
        print(f"✗ 证书文件不存在: {cert_file}")
        return
    
    try:
        manager = CharlesCertManager()
        success, msg = manager.install_charles_cert(cert_file)
        
        if success:
            print(f"\n✓ {msg}")
            
            # 询问是否重启设备
            reboot = input("\n是否立即重启设备以使证书生效？(y/n): ").strip().lower()
            if reboot == 'y':
                success, msg = manager.reboot_device()
                print(f"✓ {msg}")
        else:
            print(f"\n✗ {msg}")
            
    except Exception as e:
        print(f"✗ 错误: {str(e)}")


def example_list_certs():
    """示例: 列出已安装的证书"""
    print("\n" + "="*60)
    print("示例 3: 列出已安装的系统证书")
    print("="*60)
    
    try:
        manager = CharlesCertManager()
        success, cert_list = manager.list_installed_certs()
        
        if success:
            print("\n已安装的系统证书:")
            print(cert_list)
        else:
            print(f"✗ {cert_list}")
            
    except Exception as e:
        print(f"✗ 错误: {str(e)}")


def example_remove_cert():
    """示例: 移除证书"""
    print("\n" + "="*60)
    print("示例 4: 移除证书")
    print("="*60)
    
    # 先列出已安装的证书
    try:
        manager = CharlesCertManager()
        success, cert_list = manager.list_installed_certs()
        
        if success:
            print("\n当前已安装的证书:")
            print(cert_list)
            
            cert_hash = input("\n请输入要移除的证书文件名（如 9a5ba575.0）: ").strip()
            
            if not cert_hash:
                print("✗ 未输入证书文件名")
                return
            
            confirm = input(f"确认要移除证书 {cert_hash} 吗？(y/n): ").strip().lower()
            if confirm != 'y':
                print("✗ 操作已取消")
                return
            
            success, msg = manager.remove_cert(cert_hash)
            
            if success:
                print(f"\n✓ {msg}")
            else:
                print(f"\n✗ {msg}")
        else:
            print(f"✗ 无法列出证书: {cert_list}")
            
    except Exception as e:
        print(f"✗ 错误: {str(e)}")


def example_auto_install():
    """示例: 自动化安装流程（从 Charles 导出到安装）"""
    print("\n" + "="*60)
    print("示例 5: 自动化安装流程")
    print("="*60)
    
    print("\n步骤说明:")
    print("1. 从 Charles 导出证书")
    print("2. 检查 ADB 连接")
    print("3. 自动转换并安装证书")
    print("4. 重启设备")
    
    cert_file = input("\n请输入 Charles 证书文件路径: ").strip()
    
    if not cert_file or not os.path.exists(cert_file):
        print("✗ 证书文件不存在")
        return
    
    try:
        manager = CharlesCertManager()
        
        # 步骤 1: 检查连接
        print("\n[1/3] 检查 ADB 连接...")
        success, msg = manager.check_adb_connection()
        if not success:
            print(f"✗ {msg}")
            return
        print(f"✓ {msg}")
        
        # 步骤 2: 安装证书
        print("\n[2/3] 安装证书...")
        success, msg = manager.install_charles_cert(cert_file, force=True)
        if not success:
            print(f"✗ {msg}")
            return
        print(f"✓ {msg}")
        
        # 步骤 3: 重启设备
        print("\n[3/3] 重启设备...")
        reboot = input("是否立即重启设备？(y/n): ").strip().lower()
        if reboot == 'y':
            success, msg = manager.reboot_device()
            print(f"✓ {msg}")
            print("\n✓ 证书安装完成！设备重启后即可使用 Charles 抓包")
        else:
            print("\n✓ 证书安装完成！请手动重启设备以使证书生效")
        
    except Exception as e:
        print(f"✗ 错误: {str(e)}")


def main():
    """主菜单"""
    print("\n" + "="*60)
    print("Charles 证书管理器 - 使用示例")
    print("="*60)
    
    while True:
        print("\n请选择操作:")
        print("1. 检查 ADB 连接")
        print("2. 安装 Charles 证书")
        print("3. 列出已安装的证书")
        print("4. 移除证书")
        print("5. 自动化安装流程（推荐）")
        print("0. 退出")
        
        choice = input("\n请输入选项 (0-5): ").strip()
        
        if choice == '0':
            print("\n再见！")
            break
        elif choice == '1':
            example_check_connection()
        elif choice == '2':
            example_install_cert()
        elif choice == '3':
            example_list_certs()
        elif choice == '4':
            example_remove_cert()
        elif choice == '5':
            example_auto_install()
        else:
            print("✗ 无效的选项，请重新输入")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
    except Exception as e:
        print(f"\n发生错误: {str(e)}")

