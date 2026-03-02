# ADB 工具 API 文档

## 概述

ADB工具API提供了完整的Android设备管理和Charles证书安装功能，支持通过Web界面远程管理安卓设备。

## 基础信息

- **Base URL**: `http://localhost:9001/adbToolsV1`
- **Content-Type**: `application/json`
- **所有响应格式**: 

```json
{
  "success": true/false,
  "message": "操作消息",
  "data": {} // 可选，根据接口返回不同数据
}
```

## API 端点

### 1. 获取设备列表

获取所有已连接的ADB设备。

**端点**: `GET /api/adb/devices`

**响应示例**:
```json
{
  "success": true,
  "message": "找到 1 个设备",
  "data": [
    {
      "serial": "127.0.0.1:16384",
      "android_version": "9",
      "model": "MuMu",
      "sdk_version": "28",
      "is_root": true
    }
  ]
}
```

**错误响应**:
```json
{
  "success": false,
  "message": "ADB服务器连接失败，请确保ADB服务器正在运行"
}
```

---

### 2. 获取设备详细信息

获取指定设备的详细信息。

**端点**: `GET /api/adb/device/{serial}/info`

**路径参数**:
- `serial`: 设备序列号

**响应示例**:
```json
{
  "success": true,
  "message": "获取设备信息成功",
  "data": {
    "serial": "127.0.0.1:16384",
    "android_version": "9",
    "model": "MuMu",
    "sdk_version": "28",
    "is_root": true
  }
}
```

---

### 3. 检查证书状态

检查Charles证书是否已安装到设备。

**端点**: `POST /api/adb/cert/status`

**请求体**:
```json
{
  "serial": "127.0.0.1:16384"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "证书已安装",
  "data": {
    "installed": true,
    "cert_info": {
      "cert_hash": "a1b2c3d4",
      "cert_filename": "a1b2c3d4.0",
      "installed": true,
      "cert_length": 1234
    }
  }
}
```

---

### 4. 安装证书

安装Charles证书到Android系统证书目录。

**端点**: `POST /api/adb/cert/install`

**请求体**:
```json
{
  "serial": "127.0.0.1:16384",
  "force": false  // 可选，是否强制重新安装
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "Charles证书安装成功，建议重启设备以确保证书生效"
}
```

**错误响应**:
```json
{
  "success": false,
  "message": "设备没有root权限，无法安装系统证书"
}
```

**注意事项**:
- 需要设备具有root权限
- 安装后建议重启设备
- 如果证书已存在且`force=false`，将跳过安装

---

### 5. 卸载证书

从设备卸载Charles证书。

**端点**: `POST /api/adb/cert/uninstall`

**请求体**:
```json
{
  "serial": "127.0.0.1:16384"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "Charles证书卸载成功"
}
```

---

### 6. 获取证书信息

获取Charles证书的基本信息（不需要连接设备）。

**端点**: `GET /api/adb/cert/info`

**响应示例**:
```json
{
  "success": true,
  "message": "获取证书信息成功",
  "data": {
    "cert_hash": "a1b2c3d4",
    "cert_filename": "a1b2c3d4.0",
    "installed": false,
    "cert_length": 1234
  }
}
```

---

### 7. 执行Shell命令

在设备上执行自定义shell命令。

**端点**: `POST /api/adb/device/{serial}/shell`

**路径参数**:
- `serial`: 设备序列号

**请求体**:
```json
{
  "command": "ls /system/etc/security/cacerts/"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "命令执行成功",
  "data": {
    "output": "a1b2c3d4.0\nb2c3d4e5.0\n..."
  }
}
```

---

## 使用示例

### JavaScript/Axios 示例

```javascript
import axios from 'axios'

const API_BASE = 'http://localhost:9001/adbToolsV1'

// 1. 获取设备列表
async function getDevices() {
  try {
    const response = await axios.get(`${API_BASE}/api/adb/devices`)
    console.log('设备列表:', response.data.data)
    return response.data.data
  } catch (error) {
    console.error('获取设备失败:', error)
  }
}

// 2. 检查证书状态
async function checkCertStatus(serial) {
  try {
    const response = await axios.post(`${API_BASE}/api/adb/cert/status`, {
      serial: serial
    })
    console.log('证书状态:', response.data.data)
    return response.data.data
  } catch (error) {
    console.error('检查证书状态失败:', error)
  }
}

// 3. 安装证书
async function installCert(serial) {
  try {
    const response = await axios.post(`${API_BASE}/api/adb/cert/install`, {
      serial: serial,
      force: false
    })
    console.log('安装结果:', response.data.message)
    return response.data
  } catch (error) {
    console.error('安装证书失败:', error)
  }
}

// 完整流程示例
async function setupCertificate() {
  // 1. 获取设备
  const devices = await getDevices()
  if (!devices || devices.length === 0) {
    console.error('未找到设备')
    return
  }
  
  const device = devices[0]
  console.log('选择设备:', device.serial)
  
  // 2. 检查root权限
  if (!device.is_root) {
    console.error('设备没有root权限')
    return
  }
  
  // 3. 检查证书状态
  const certStatus = await checkCertStatus(device.serial)
  if (certStatus.installed) {
    console.log('证书已安装')
    return
  }
  
  // 4. 安装证书
  const result = await installCert(device.serial)
  if (result.success) {
    console.log('证书安装成功!')
  }
}
```

### Python 示例

```python
import requests

API_BASE = 'http://localhost:9001/adbToolsV1'

# 1. 获取设备列表
def get_devices():
    response = requests.get(f'{API_BASE}/api/adb/devices')
    data = response.json()
    if data['success']:
        return data['data']
    return []

# 2. 安装证书
def install_cert(serial):
    response = requests.post(
        f'{API_BASE}/api/adb/cert/install',
        json={'serial': serial, 'force': False}
    )
    return response.json()

# 完整流程
def main():
    # 获取设备
    devices = get_devices()
    if not devices:
        print('未找到设备')
        return
    
    device = devices[0]
    print(f"设备: {device['model']} ({device['serial']})")
    
    # 检查root权限
    if not device['is_root']:
        print('设备没有root权限')
        return
    
    # 安装证书
    result = install_cert(device['serial'])
    if result['success']:
        print('证书安装成功!')
    else:
        print(f"安装失败: {result['message']}")

if __name__ == '__main__':
    main()
```

---

## 错误码说明

| HTTP状态码 | 说明 |
|-----------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 403 | 权限不足（如设备没有root权限） |
| 404 | 资源不存在（如设备未找到） |
| 500 | 服务器内部错误 |

---

## 常见问题

### Q1: 为什么获取不到设备？

**A**: 请检查：
1. ADB服务器是否正在运行
2. 设备是否已连接（USB或网络）
3. 设备是否已开启USB调试
4. 是否已授权此电脑进行调试
5. 是否安装了 `pure-python-adb` 依赖

### Q2: 安装证书失败怎么办？

**A**: 常见原因：
1. 设备没有root权限
2. 系统分区无法重新挂载（部分新版Android）
3. SELinux策略阻止了操作
4. 系统分区空间不足

### Q3: MuMu模拟器如何连接？

**A**: 
1. MuMu 12模拟器默认ADB端口为 16384
2. 序列号通常为 `127.0.0.1:16384`
3. MuMu模拟器默认具有root权限

### Q4: 证书安装后不生效？

**A**: 
1. 重启设备
2. 检查"设置 -> 安全 -> 信任的凭据 -> 系统"
3. 确保Charles代理正在运行
4. 检查设备的代理设置

---

## 技术架构

```
前端 (Vue.js)
    ↓ HTTP请求
后端 API (Flask)
    ↓ 调用
ADB管理器 (ADBManager)
    ↓ 使用
pure-python-adb库
    ↓ 连接
ADB服务器
    ↓ 控制
Android设备
```

---

## 安全建议

1. **仅在开发/测试环境使用** - 不要在生产设备上安装自定义证书
2. **网络隔离** - API服务应只监听本地或内网
3. **不再需要时卸载** - 及时卸载证书
4. **备份设备** - 修改系统前备份重要数据

---

## 更新日志

### v1.0.0 (2025-11-07)
- 初始版本发布
- 支持设备列表获取
- 支持Charles证书安装/卸载
- 支持证书状态检查
- 支持Shell命令执行

