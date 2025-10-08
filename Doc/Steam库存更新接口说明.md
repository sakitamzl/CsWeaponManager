# Steam库存更新接口说明

## 功能概述
新增了一个接口，可以根据 `steamID` 自动从数据库 `config` 表中查询对应的 Steam Cookie，然后更新该用户的库存数据。

## 接口架构

### 1. Spider 服务接口
**URL:** `POST /steamSpiderV1/updateInventoryBySteamID`

**请求参数:**
```json
{
    "steamID": "76561198xxxxxx"
}
```

**功能说明:**
- 接收 `steamID` 参数
- 调用后端 API 查询 config 表获取 cookie
- 返回库存更新结果

**响应示例:**
```json
{
    "message": "库存更新成功",
    "data": {
        "success": true,
        "message": "Steam库存更新成功",
        "data": {...}
    }
}
```

### 2. 后端 API 接口
**URL:** `POST /api/v1/steam/select_vaule`

**请求参数:**
```json
{
    "steamID": "76561198xxxxxx",
    "spider_url": "http://127.0.0.1:5001/steamSpiderV1/getInventory"  // 可选，默认值
}
```

**功能说明:**
1. 从 config 表查询 `key1='steam'` 且 `key2=steamID` 的记录
2. 获取该记录的 `value` 字段（即 Steam Cookie）
3. 调用 Spider 服务的 `/steamSpiderV1/getInventory` 接口更新库存
4. 返回更新结果

**响应示例:**
```json
{
    "success": true,
    "message": "Steam库存更新成功",
    "data": {...}
}
```

**错误响应:**
```json
{
    "success": false,
    "error": "未找到 steamID 76561198xxxxxx 的配置信息"
}
```

## 数据库配置

### config 表结构
更新库存时会查询以下条件的记录：
- `key1 = 'steam'`
- `key2 = steamID`（例如：'76561198xxxxxx'）
- `value` 字段存储 Steam Cookie

### 配置示例
| dataID | dataName | key1 | key2 | value | status |
|--------|----------|------|------|-------|--------|
| 1 | Steam账号1 | steam | 76561198xxxxxx | sessionid=xxx;steamLoginSecure=xxx | 1 |

## 调用流程

```
前端/页面
    ↓ POST steamID
Spider: /steamSpiderV1/updateInventoryBySteamID
    ↓ 调用后端API
Backend: /api/v1/steam/select_vaule
    ↓ 查询config表获取cookie
    ↓ 回调Spider服务
Spider: /steamSpiderV1/getInventory (使用cookie)
    ↓ 获取Steam库存
    ↓ 保存到数据库
Backend: /api/v1/steam/inventory (保存库存数据)
    ↓ 返回结果
前端/页面
```

## 使用示例

### 使用 Spider 接口（推荐）
```python
import requests

url = "http://127.0.0.1:5001/steamSpiderV1/updateInventoryBySteamID"
data = {
    "steamID": "76561198xxxxxx"
}

response = requests.post(url, json=data)
print(response.json())
```

### 使用后端 API 接口
```python
import requests

url = "http://127.0.0.1:9001/api/v1/steam/select_vaule"
data = {
    "steamID": "76561198xxxxxx"
}

response = requests.post(url, json=data)
print(response.json())
```

## 注意事项

1. **Cookie 有效性**: 确保 config 表中的 Steam Cookie 是有效的，否则更新会失败
2. **超时时间**: 库存数据较多时可能需要较长时间，接口设置了 120 秒的超时时间
3. **服务依赖**: 
   - Spider 服务需要运行在端口 5001
   - 后端 API 服务需要运行在端口 9001
4. **数据覆盖**: 每次更新会先删除该用户的旧库存记录，然后插入新记录

## 错误处理

可能的错误情况：
- `steamID 参数缺失` - 未提供 steamID
- `未找到 steamID xxx 的配置信息` - config 表中没有对应记录
- `steamID xxx 的 cookie 值为空` - config 表中 value 为空
- `请求Spider服务超时` - Spider 服务响应超时
- `无法连接到Spider服务` - Spider 服务未运行
- `Steam cookie 失效需要重新获取` - Cookie 已过期

