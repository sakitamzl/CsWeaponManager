# CSQAQ映射文件上传功能

## 功能说明

该功能用于上传CSQAQ平台的饰品ID映射文件，将CSQAQ的商品ID存储到数据库的`weapon_classID`表中。

## 数据库变更

在`weapon_classID`表中新增了字段：
- `csqaq_id` (INTEGER): 存储CSQAQ平台的商品ID

## 文件格式要求

上传的文件必须是`.txt`格式，内容为JSON数组，每个对象包含以下字段：

```json
[
  {
    "id": 1,
    "name": "运动手套（★） | 迈阿密风云 (略有磨损)",
    "market_hash_name": "★ Sport Gloves | Vice (Minimal Wear)"
  },
  ...
]
```

### 字段说明

- `id`: CSQAQ平台的商品ID（必填）
- `name`: 商品的中文名称（可选，用于新增记录时填充`market_listing_item_name`）
- `market_hash_name`: Steam市场的英文名称（必填，用于匹配数据库中的`steam_hash_name`字段）

## 处理逻辑

1. 解析上传的JSON文件
2. 遍历每条记录：
   - 通过`market_hash_name`在数据库中查找对应的`steam_hash_name`记录
   - **如果找到记录**：更新该记录的`csqaq_id`字段
   - **如果未找到记录**：新增一条记录，填充`steam_hash_name`、`market_listing_item_name`和`csqaq_id`字段
3. 返回处理结果统计

## API端点

**POST** `/csqaqApiV1/api/csqaq/upload-mapping`

### 请求参数

- `file`: 上传的文件（multipart/form-data）

### 响应格式

```json
{
  "success": true,
  "message": "处理完成：总计 100 条，更新 80 条，新增 15 条，失败 5 条",
  "total": 100,
  "updated": 80,
  "inserted": 15,
  "failed": 5
}
```

## 前端使用

在开发工具页面（DevTool.vue）的"平台饰品映射"区域：

1. 点击"选择CSQAQ映射文件"按钮，选择`.txt`文件
2. 点击"提交上传"按钮开始处理
3. 查看处理结果统计

## 注意事项

1. 文件大小限制：最大50MB
2. 文件格式：必须是`.txt`文件，内容为有效的JSON格式
3. 必填字段：`id`和`market_hash_name`缺一不可
4. 匹配规则：使用`market_hash_name`精确匹配数据库中的`steam_hash_name`字段
5. 新增记录时，只填充必要字段，其他字段保持为NULL
