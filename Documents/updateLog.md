# 更新日志 已更新Ver2.x  Ver1.x.x 大部分数据将不通用

## 📋 目录

- [2025-12-9](#2025-12-9)
  - [v2.0.2](#v202)
- [2025-12-08](#2025-12-08)
  - [V2.0.1](#v201)
  - [v2.0.0 发布](#v200-发布)
- [2025-12-03](#2025-12-03)
  - [v1.2.11](#v1211)
- [2025-12-02](#2025-12-02)
  - [v1.2.10](#v1210)


---

## 2025-12-9
### v2.0.2
1. 优化库存组件 steam库存的显示
2. 页面添加更新日志显 添加使用文档

## 2025-12-08
### V2.0.1
1. 库存组件添加组合显示
2. 修复胶囊 武器箱等冗余显示
3. 修改lent 状态下拉BUG 优化页面加载
4. 添加 库存组件 steam库存 组合显示逻辑

## 2025-12-08
### v2.0.0 发布
#### 已更新Ver2.x Ver1.x.x 大部分数据将不通用
1. 从1.0更新到2.0版本 需要先执行下面sql
```sql
ALTER TABLE steam_stockComponents RENAME COLUMN instanceid TO goods_assetid;
DELETE FROM steam_stockComponents;
```

2. 如果需要重新获取历史数据 以便显示印花 改名 挂件的信息的 需要删除数据后重新获取数据
```sql
DELETE FROM "main"."sell" WHERE "from" = 'SMK';
DELETE FROM "main"."buy" WHERE "from" = 'SMK';
DELETE FROM steam_market;
DELETE FROM yyyp_messagebox;
DELETE FROM steam_inventoryhistory_index;
DELETE FROM steam_inventoryhistory;
DELETE FROM weapon_classID;
DELETE FROM "main"."sell" WHERE "from" = 'buff';
DELETE FROM "main"."buy" WHERE "from" = 'buff';
DELETE FROM buff_sell;
DELETE FROM buff_buy;
DELETE FROM "main"."sell" WHERE "from" = 'csfloat';
DELETE FROM "main"."buy" WHERE "from" = 'csfloat';
DELETE FROM csfloat_sell;
DELETE FROM csfloat_buy;
DELETE FROM "main"."sell" WHERE "from" = 'yyyp';
DELETE FROM "main"."buy" WHERE "from" = 'yyyp';
DELETE FROM yyyp_sell;
DELETE FROM yyyp_buy;
```
## 2025-12-03

### v1.2.11

## 2025-12-02
1. 添加steam cookie自动刷新 需要在自动化管理中开启
2. 更新了出租列表的图片显示

```sql
DELETE FROM yyyp_lent;
```
### v1.2.10

1、添加库存组件 图片 印花等获取

```sql
ALTER TABLE steam_stockComponents RENAME COLUMN instanceid TO goods_assetid;
DELETE FROM steam_stockComponents;
```

## 2025-12-01

### v1.2.9

1. 添加 Steam 市场、Steam 交易历史的 `steam_hash_name` 获取
2. 添加 Steam 库存交易的详细信息获取
3. 添加 Steam 库存组件的详细信息获取
4、添加 在steam中获取hashname

**数据库清理语句：**

```sql
DELETE FROM "main"."sell" WHERE "from" = 'SMK';
DELETE FROM "main"."buy" WHERE "from" = 'SMK';
DELETE FROM steam_market;
DELETE FROM yyyp_messagebox;
DELETE FROM steam_inventoryhistory_index;
DELETE FROM steam_inventoryhistory;
DELETE FROM weapon_classID;
```

---

## 2025-11-30

### v1.2.8

1. 添加 sell、buy 列表的贴纸、挂件、改名的显示
2. 完成 CSFloat 饰品、印花、挂件获取

**数据库清理语句：**

```sql
DELETE FROM "main"."sell" WHERE "from" = 'buff';
DELETE FROM "main"."buy" WHERE "from" = 'buff';
DELETE FROM buff_sell;
DELETE FROM buff_buy;
DELETE FROM "main"."sell" WHERE "from" = 'csfloat';
DELETE FROM "main"."buy" WHERE "from" = 'csfloat';
DELETE FROM csfloat_sell;
DELETE FROM csfloat_buy;
```

---

## 2025-11-29

### v1.2.7

1. 表 `buy`、`sell`、`steam_stockComponents`、`steam_inventory`、`steam_buy`、`steam_sell` 新增字段 `steam_hash_name`
2. Steam 库存表添加详细信息的获取
3. 修改 Steam 库存、sell、buy 页面的显示样式
4. 修改 yyyp 获取商品详情时，添加获取贴纸信息、挂件信息
5. 更新执行语句

**数据库清理语句：**

```sql
DELETE FROM "main"."sell" WHERE "from" = 'yyyp';
DELETE FROM "main"."buy" WHERE "from" = 'yyyp';
DELETE FROM yyyp_sell;
DELETE FROM yyyp_buy;
```

---

## 2025-11-28

### v1.2.6

1. auto-manager 自动化管理页面添加"启动全部"、"停止全部"按钮
2. 修改 CSFloat 的订单查询状态限制
3. 添加使用 yyyp 的 URL 进行 ICON 的下载，脱离在线图片库的依赖

---

## 2025-11-27

### v1.2.5

- 爬取改名中的 Steam 市场类型添加搜索参数
