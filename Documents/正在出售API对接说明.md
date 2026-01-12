# 正在出售API对接说明

## 完成时间
2025年1月

## 完成内容

### 1. 前端API配置
已在 `WebSite/src/config/api.js` 中添加以下API端点：

```javascript
// 正在出售相关
ON_SALE_YYYP_ACCOUNTS: '/webOnSaleV1/getYYYPAccounts',  // 获取悠悠有品账号列表
ON_SALE_BUFF_ACCOUNTS: '/webOnSaleV1/getBuffAccounts',  // 获取BUFF账号列表
ON_SALE_ITEMS: '/webOnSaleV1/getOnSaleItems',  // 获取在售商品列表
ON_SALE_UPDATE_PRICE: '/webOnSaleV1/updateSalePrice',  // 修改售价
ON_SALE_REMOVE: '/webOnSaleV1/removeFromSale',  // 下架商品
```

快捷方法：
```javascript
getYYYPAccounts: () => getApiUrl(API_CONFIG.ENDPOINTS.ON_SALE_YYYP_ACCOUNTS),
getBuffAccounts: () => getApiUrl(API_CONFIG.ENDPOINTS.ON_SALE_BUFF_ACCOUNTS),
getOnSaleItems: () => getApiUrl(API_CONFIG.ENDPOINTS.ON_SALE_ITEMS),
updateSalePrice: () => getApiUrl(API_CONFIG.ENDPOINTS.ON_SALE_UPDATE_PRICE),
removeFromSale: () => getApiUrl(API_CONFIG.ENDPOINTS.ON_SALE_REMOVE),
```

### 2. 后端API实现
已创建 `backEnd/src/web_side/webSide/on_sale/select_usercode.py`

#### API端点列表

1. **获取悠悠有品账号列表**
   ```
   GET /webOnSaleV1/getYYYPAccounts
   
   返回格式：
   {
     "success": true,
     "data": [
       {
         "id": 1,
         "name": "账号名称",
         "steam_id": "76561198XXXXXXXX",
         "item_count": 0
       }
     ]
   }
   ```
   
   实现逻辑：
   - 查询 `config` 表
   - 条件：`key1='yyyp' AND key2='config'`
   - 返回字段：`dataID`, `dataName`, `steamID`

2. **获取BUFF账号列表**
   ```
   GET /webOnSaleV1/getBuffAccounts
   
   返回格式：
   {
     "success": true,
     "data": [
       {
         "id": 1,
         "name": "账号名称",
         "steam_id": "76561198XXXXXXXX",
         "item_count": 0
       }
     ]
   }
   ```
   
   实现逻辑：
   - 查询 `config` 表
   - 条件：`key1='buff' AND key2='config'`
   - 返回字段：`dataID`, `dataName`, `steamID`

3. **获取在售商品列表**
   ```
   GET /webOnSaleV1/getOnSaleItems?platform=yyyp&account_id=1
   
   参数：
   - platform: 平台标识 (yyyp/buff)
   - account_id: 账号ID
   
   返回格式：
   {
     "success": true,
     "data": []  // 暂时返回空数组
   }
   ```
   
   **注意**：此接口需要根据实际的在售商品表结构补充实现

4. **修改售价**
   ```
   POST /webOnSaleV1/updateSalePrice
   
   请求体：
   {
     "id": 1,
     "new_price": 100.00
   }
   
   返回格式：
   {
     "success": true,
     "message": "改价成功"
   }
   ```
   
   **注意**：此接口需要根据实际的在售商品表结构补充实现

5. **下架商品**
   ```
   POST /webOnSaleV1/removeFromSale
   
   请求体：
   {
     "id": 1
   }
   
   返回格式：
   {
     "success": true,
     "message": "下架成功"
   }
   ```
   
   **注意**：此接口需要根据实际的在售商品表结构补充实现

### 3. Blueprint注册
已在 `backEnd/backEnd.py` 中注册：

```python
from src.web_side.webSide.on_sale.select_usercode import webOnSaleV1

# 注册Blueprint
app.register_blueprint(webOnSaleV1, url_prefix='/webOnSaleV1')
```

## 数据库查询说明

### Config表结构
```sql
SELECT dataID, dataName, steamID
FROM config 
WHERE key1 = 'yyyp' AND key2 = 'config'  -- 悠悠有品账号
-- 或
WHERE key1 = 'buff' AND key2 = 'config'  -- BUFF账号
ORDER BY dataID
```

返回字段：
- `dataID`: 账号ID（用作前端的 id）
- `dataName`: 账号名称（用作前端的 name）
- `steamID`: Steam ID（用作前端的 steam_id）

## 待完成工作

### 1. 在售商品表结构
需要确定在售商品的表结构，包含以下字段：
- `id`: 商品ID
- `item_name`: 饰品名称
- `steam_hash_name`: Steam哈希名称
- `weapon_type`: 武器类型
- `weapon_float`: 磨损值
- `float_range`: 磨损等级
- `sale_price`: 售价
- `buy_price`: 购入价
- `platform`: 平台 (yyyp/buff)
- `account_id`: 账号ID（关联config表的dataID）
- `sticker`: 贴纸数据（JSON）
- `pendant`: 挂件数据（JSON）
- `rename`: 改名
- `on_sale_time`: 上架时间

### 2. 补充实现
需要在 `select_usercode.py` 中补充以下功能：

1. **查询在售商品数量**
   在 `get_yyyp_accounts()` 和 `get_buff_accounts()` 中：
   ```python
   # TODO: 查询该账号在售商品数量
   count_sql = """
   SELECT COUNT(*) 
   FROM on_sale_items 
   WHERE platform = ? AND account_id = ?
   """
   count_result = db.execute_query(count_sql, (platform, data_id))
   item_count = count_result[0][0] if count_result else 0
   ```

2. **查询在售商品列表**
   在 `get_on_sale_items()` 中：
   ```python
   sql = """
   SELECT id, item_name, steam_hash_name, weapon_type, weapon_float, 
          float_range, sale_price, buy_price, platform, account_id,
          sticker, pendant, rename, on_sale_time
   FROM on_sale_items 
   WHERE platform = ? AND account_id = ?
   ORDER BY on_sale_time DESC
   """
   results = db.execute_query(sql, (platform, account_id))
   ```

3. **修改售价**
   在 `update_sale_price()` 中：
   ```python
   sql = """
   UPDATE on_sale_items 
   SET sale_price = ? 
   WHERE id = ?
   """
   db.execute_update(sql, (new_price, item_id))
   ```

4. **下架商品**
   在 `remove_from_sale()` 中：
   ```python
   sql = """
   DELETE FROM on_sale_items 
   WHERE id = ?
   """
   db.execute_update(sql, (item_id,))
   ```

## 测试说明

### 1. 测试账号列表接口
```bash
# 测试悠悠有品账号列表
curl http://localhost:5000/webOnSaleV1/getYYYPAccounts

# 测试BUFF账号列表
curl http://localhost:5000/webOnSaleV1/getBuffAccounts
```

### 2. 测试在售商品接口
```bash
# 测试获取在售商品
curl "http://localhost:5000/webOnSaleV1/getOnSaleItems?platform=yyyp&account_id=1"
```

### 3. 测试改价接口
```bash
curl -X POST http://localhost:5000/webOnSaleV1/updateSalePrice \
  -H "Content-Type: application/json" \
  -d '{"id": 1, "new_price": 100.00}'
```

### 4. 测试下架接口
```bash
curl -X POST http://localhost:5000/webOnSaleV1/removeFromSale \
  -H "Content-Type: application/json" \
  -d '{"id": 1}'
```

## 前端使用示例

```javascript
import { apiUrls } from '@/config/api.js'
import axios from 'axios'

// 获取悠悠有品账号列表
const response = await axios.get(apiUrls.getYYYPAccounts())
console.log(response.data)

// 获取BUFF账号列表
const response = await axios.get(apiUrls.getBuffAccounts())
console.log(response.data)

// 获取在售商品
const response = await axios.get(apiUrls.getOnSaleItems(), {
  params: {
    platform: 'yyyp',
    account_id: 1
  }
})
console.log(response.data)

// 修改售价
const response = await axios.post(apiUrls.updateSalePrice(), {
  id: 1,
  new_price: 100.00
})
console.log(response.data)

// 下架商品
const response = await axios.post(apiUrls.removeFromSale(), {
  id: 1
})
console.log(response.data)
```

## 注意事项

1. **账号查询已完成**：可以正常查询悠悠有品和BUFF的账号列表
2. **在售商品功能待完成**：需要确定在售商品表结构后补充实现
3. **错误处理**：所有接口都包含了基本的错误处理
4. **参数验证**：接口会验证必要参数是否存在
5. **数据库连接**：使用 DatabaseManager 统一管理数据库连接

## 相关文档
- [正在出售页面设计.md](./正在出售页面设计.md)
- [正在出售页面更新说明.md](./正在出售页面更新说明.md)
