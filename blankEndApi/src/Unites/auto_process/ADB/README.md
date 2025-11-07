# ADB 安卓调试模块

## 简介

这是一个用于向安卓设备（包括模拟器）安装和管理 Charles SSL 代理证书的工具模块。

参考文档: [MuMu模拟器 - 如何安装证书&抓包](https://mumu.163.com/mac/tutorials/certificates-and-packet-capture.html)

## 功能特性

- ✅ 自动检测 ADB 工具
- ✅ 检查设备连接状态
- ✅ 启用 Root 权限
- ✅ 自动转换证书格式
- ✅ 安装/更新 Charles 证书到系统目录
- ✅ 列出已安装的系统证书
- ✅ 移除指定证书
- ✅ 支持 Windows/macOS/Linux
- ✅ 完整的日志记录

## 前置要求

### 1. ADB 工具

**Windows:**
- 下载 [Android SDK Platform Tools](https://developer.android.com/studio/releases/platform-tools)
- 或者安装 Android Studio

**macOS:**
```bash
brew install android-platform-tools
```

**Linux:**
```bash
sudo apt-get install adb  # Ubuntu/Debian
sudo yum install android-tools  # CentOS/RHEL
```

### 2. OpenSSL

**Windows:**
- 下载 [Win32/Win64 OpenSSL](https://slproweb.com/products/Win32OpenSSL.html)

**macOS:**
```bash
brew install openssl
```

**Linux:**
```bash
sudo apt-get install openssl  # Ubuntu/Debian
```

### 3. Root 权限的安卓设备或模拟器

支持的模拟器:
- MuMu 模拟器（推荐）
- 夜神模拟器
- 雷电模拟器
- BlueStacks（部分版本）

## 使用方法

### 方式一: 在 Python 代码中使用

```python
from src.Unites.auto_process.ADB import CharlesCertManager

# 初始化管理器（自动检测 ADB）
manager = CharlesCertManager()

# 或者指定 ADB 路径
# manager = CharlesCertManager(adb_path='/path/to/adb')

# 检查 ADB 连接
success, msg = manager.check_adb_connection()
print(msg)

# 安装 Charles 证书
cert_file = 'D:/charles-ssl-proxying-certificate.pem'
success, msg = manager.install_charles_cert(cert_file)
print(msg)

# 强制安装（覆盖已存在的证书）
success, msg = manager.install_charles_cert(cert_file, force=True)
print(msg)

# 列出已安装的证书
success, cert_list = manager.list_installed_certs()
print(cert_list)

# 移除证书
success, msg = manager.remove_cert('9a5ba575.0')
print(msg)

# 重启设备
success, msg = manager.reboot_device()
print(msg)
```

### 方式二: 命令行使用

```bash
# 进入模块目录
cd D:\Project\CsWeaponManager\blankEndApi\src\Unites\auto_process\ADB

# 检查 ADB 连接
python charles_cert_manager.py check

# 安装证书
python charles_cert_manager.py install --cert "D:/charles-ssl-proxying-certificate.pem"

# 强制安装（覆盖已存在）
python charles_cert_manager.py install --cert "D:/charles-ssl-proxying-certificate.pem" --force

# 列出已安装的证书
python charles_cert_manager.py list

# 移除证书
python charles_cert_manager.py remove --hash "9a5ba575.0"

# 重启设备
python charles_cert_manager.py reboot

# 指定 ADB 路径
python charles_cert_manager.py check --adb "C:/Android/platform-tools/adb.exe"
```

## Charles 证书导出步骤

### Windows / macOS

1. 打开 Charles
2. 菜单栏: Help → SSL Proxying → Save Charles Root Certificate...
3. 保存为 `.pem` 格式（如 `charles-ssl-proxying-certificate.pem`）

## 完整安装流程

### 1. 启动模拟器

以 MuMu 模拟器为例:
- 启动 MuMu 模拟器
- 确保模拟器已开启 Root 权限

### 2. 检查 ADB 连接

```bash
adb devices
```

应该能看到连接的设备列表:
```
List of devices attached
127.0.0.1:7555  device
```

### 3. 导出 Charles 证书

按照上述步骤从 Charles 导出 `.pem` 格式的证书。

### 4. 安装证书

```python
from src.Unites.auto_process.ADB import CharlesCertManager

manager = CharlesCertManager()
success, msg = manager.install_charles_cert('charles-ssl-proxying-certificate.pem')
print(msg)
```

### 5. 重启模拟器

```python
manager.reboot_device()
```

或手动重启模拟器。

### 6. 配置 Charles 代理

在模拟器中:
1. 设置 → WLAN → 长按当前网络 → 修改网络
2. 代理: 手动
3. 主机名: 你的电脑 IP（如 `192.168.1.100`）
4. 端口: `8888`（Charles 默认端口）
5. 绕过代理: `10.0.2.2`（模拟器内部网络）

### 7. 配置 Charles SSL 代理

在 Charles 中:
1. Proxy → SSL Proxying Settings
2. 勾选 "Enable SSL Proxying"
3. Add location: Host `*`, Port `*`

## 常见问题

### Q1: 提示"未找到 ADB 工具"

**解决方法:**
- 确保已安装 Android SDK Platform Tools
- 将 ADB 添加到系统 PATH
- 或者在代码中指定 ADB 路径

### Q2: 提示"启用 root 权限失败"

**解决方法:**
- 确保使用支持 Root 的模拟器（如 MuMu 模拟器）
- 在模拟器设置中开启 Root 权限
- 真机需要先 Root

### Q3: 提示"未检测到连接的设备"

**解决方法:**
- 确保模拟器或设备已启动
- 运行 `adb devices` 检查连接
- 如果看不到设备，尝试 `adb kill-server` 然后 `adb start-server`

### Q4: 证书安装成功但 HTTPS 仍然无法抓包

**解决方法:**
- 确保已重启设备/模拟器
- 检查 Charles 的 SSL Proxying 设置是否正确
- 确认模拟器代理设置正确
- 某些 App 可能使用了证书固定（Certificate Pinning），需要额外处理

### Q5: MuMu 模拟器 ADB 连接端口

不同版本的 MuMu 模拟器端口可能不同:
- MuMu 模拟器 12: `16384` 起（第一个实例: 16384, 第二个: 16416...）
- MuMu 模拟器 6: `7555`

查看端口:
```bash
adb devices
```

手动连接:
```bash
adb connect 127.0.0.1:16384
```

## API 参考

### CharlesCertManager 类

#### `__init__(adb_path: Optional[str] = None)`
初始化证书管理器
- `adb_path`: ADB 工具路径，默认自动检测

#### `check_adb_connection() -> Tuple[bool, str]`
检查 ADB 连接状态
- 返回: (成功标志, 设备列表信息)

#### `install_charles_cert(cert_file: str, force: bool = False) -> Tuple[bool, str]`
安装 Charles 证书
- `cert_file`: 证书文件路径
- `force`: 是否强制覆盖已存在的证书
- 返回: (成功标志, 详细消息)

#### `list_installed_certs() -> Tuple[bool, str]`
列出已安装的系统证书
- 返回: (成功标志, 证书列表)

#### `remove_cert(cert_hash: str) -> Tuple[bool, str]`
移除指定证书
- `cert_hash`: 证书哈希文件名（如 "9a5ba575.0"）
- 返回: (成功标志, 消息)

#### `reboot_device() -> Tuple[bool, str]`
重启设备
- 返回: (成功标志, 消息)

## 日志

所有操作都会记录到项目日志系统中，日志级别:
- `debug`: 详细的命令执行信息
- `info`: 一般操作信息
- `warning`: 警告信息
- `error`: 错误信息

查看日志:
```
D:\Project\CsWeaponManager\blankEndApi\log\<date>_blankEndApi.log
```

## 许可证

本模块是 CsWeaponManager 项目的一部分。

## 参考资料

- [MuMu模拟器 - 如何安装证书&抓包](https://mumu.163.com/mac/tutorials/certificates-and-packet-capture.html)
- [Android 开发者文档 - ADB](https://developer.android.com/studio/command-line/adb)
- [Charles Proxy 官方文档](https://www.charlesproxy.com/documentation/)

