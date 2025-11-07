# ADB 安卓调试模块

用于向安卓设备安装/更新 Charles 证书的自动化工具。

## 功能特性

- ✅ 使用纯Python实现，无需外部ADB程序
- ✅ 自动连接和管理Android设备
- ✅ 自动安装Charles代理证书到系统证书目录
- ✅ 支持证书的安装、卸载和状态检查
- ✅ 支持root权限检查
- ✅ 详细的操作日志和错误提示

## 安装依赖

```bash
pip install pure-python-adb
```

## 使用方法

### 方法一: 使用示例脚本（推荐）

```python
# 运行交互式示例
python example.py
```

交互式示例会引导你完成以下步骤：
1. 连接ADB服务器
2. 列出所有设备
3. 选择要操作的设备
4. 显示设备信息
5. 检查root权限
6. 安装/更新/卸载证书

### 方法二: 快速安装

```python
from example import quick_install, quick_uninstall

# 快速安装证书（自动选择第一个设备）
quick_install()

# 快速卸载证书
quick_uninstall()
```

### 方法三: 自定义使用

```python
from adb_manager import ADBManager
from charles_cert_manager import CharlesCertManager

# 1. 创建ADB管理器
adb = ADBManager()

# 2. 连接ADB服务器
adb.connect()

# 3. 选择设备（不指定serial则选择第一个设备）
adb.select_device()

# 4. 创建证书管理器
cert_manager = CharlesCertManager(adb)

# 5. 安装证书
cert_manager.install_cert()

# 6. 检查证书状态
cert_manager.check_cert_installed()

# 7. 卸载证书
cert_manager.uninstall_cert()
```

## 前置条件

### 1. 启动ADB服务器

对于MuMu模拟器：
```bash
# MuMu 12模拟器默认ADB端口: 16384
# 使用pure-python-adb会自动连接本地ADB服务器
```

对于其他设备：
```bash
# 确保ADB服务器正在运行
adb start-server

# 查看已连接的设备
adb devices
```

### 2. 设备要求

- Android设备必须开启USB调试
- 设备必须已获得root权限（MuMu模拟器默认具有root权限）
- 设备已授权此电脑进行调试

### 3. MuMu模拟器配置

参考官方文档: https://mumu.163.com/mac/tutorials/certificates-and-packet-capture.html

1. 打开MuMu模拟器设置
2. 开启开发者选项和USB调试
3. 连接时授权电脑调试权限

## 证书信息

使用的Charles代理证书信息：
- 颁发者: Charles Proxy CA (6 Nov 2025, MAKURO-DESKTOP)
- 有效期: 2025-11-05 至 2026-11-05
- 用途: SSL/HTTPS流量抓包

## API文档

### ADBManager

ADB设备管理器，负责设备连接和命令执行。

#### 方法

- `connect()`: 连接到ADB服务器
- `get_devices()`: 获取所有已连接的设备列表
- `select_device(serial=None)`: 选择要操作的设备
- `execute_shell(command)`: 执行shell命令
- `push_file(local_path, remote_path)`: 推送文件到设备
- `pull_file(remote_path, local_path)`: 从设备拉取文件
- `get_device_info()`: 获取设备信息
- `is_root()`: 检查设备是否已root

### CharlesCertManager

Charles证书管理器，负责证书的安装和管理。

#### 方法

- `check_cert_installed()`: 检查证书是否已安装
- `install_cert(force=False)`: 安装证书（force=True时强制重新安装）
- `uninstall_cert()`: 卸载证书
- `get_cert_info()`: 获取证书信息

## 工作原理

1. **证书Hash计算**: 根据证书内容计算hash值，生成系统证书文件名
2. **文件推送**: 将证书推送到设备的临时目录
3. **系统挂载**: 以root权限将系统分区重新挂载为可写
4. **证书安装**: 将证书移动到 `/system/etc/security/cacerts/` 目录
5. **权限设置**: 设置证书文件权限为644，所有者为root
6. **系统还原**: 将系统分区重新挂载为只读

## 常见问题

### Q: 提示"未找到设备"怎么办？

A: 请检查：
1. 设备是否已连接到电脑
2. 设备是否已开启USB调试
3. 是否已授权此电脑进行调试
4. 运行 `adb devices` 查看设备是否被识别

### Q: 提示"设备没有root权限"怎么办？

A: 
1. 对于MuMu模拟器，默认具有root权限
2. 对于真实设备，需要先root设备
3. 某些设备需要在开发者选项中开启"root权限"

### Q: 安装后证书不生效怎么办？

A: 
1. 重启设备
2. 在设备的"设置 -> 安全 -> 信任的凭据 -> 系统"中查看证书
3. 确保Charles代理服务器正在运行
4. 确保设备网络代理配置正确

### Q: 提示"挂载失败"怎么办？

A:
1. 某些设备的系统分区无法重新挂载
2. 可能需要先禁用SELinux
3. 对于较新的Android版本（10+），可能需要其他方法

## 注意事项

⚠️ **重要提醒**：

1. 此工具需要root权限，仅用于开发和测试环境
2. 修改系统证书存在一定风险，请谨慎操作
3. 建议在模拟器或测试机上使用
4. 安装证书后建议重启设备
5. 不再需要时应及时卸载证书

## 技术参考

- [MuMu模拟器 - 抓包配置教程](https://mumu.163.com/mac/tutorials/certificates-and-packet-capture.html)
- [pure-python-adb文档](https://github.com/Swind/pure-python-adb)
- [Android证书管理](https://source.android.com/docs/security/features/keystore)

## 许可证

本模块为项目内部工具，仅供开发使用。

