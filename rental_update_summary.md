# Rental（借入）功能更新总结

## ✅ 已完成的工作

### 1. 数据库模型
- ✅ 创建 `backEnd/src/db_manager/index/rental.py` - rental 主表模型
- ✅ 更新 `backEnd/src/db_manager/index/__init__.py` - 导出 RentalModel
- ✅ 更新 `backEnd/src/db_manager/manager.py` - 注册 RentalModel

### 2. 后端 API
- ✅ 创建 `backEnd/src/web_side/youpin898/rental/rental_v1.py` - rental API 接口
- ✅ 创建 `backEnd/src/web_side/youpin898/rental/__init__.py`
- ✅ 更新 `backEnd/backEnd.py` - 注册 rental Blueprint

### 3. 爬虫代码
- ✅ 修改 `Spider/src/web_site/youping/get_trade/rental.py`
  - ✅ 类名改为 `yyypRental`
  - ✅ API 接口改为 `/api/youpin/bff/order/lease-record-list`
  - ✅ 字段改为 `lessor_name` 和 `lessor_id`（出租人）
  - ✅ 所有接口调用改为 `youpin898RentalV1`
  - ✅ 删除不需要的方法：`updateLentStatus`、`sync_lent_buyout_to_sell`
  - ✅ 删除兼容函数 `get_lent`

## 📋 Rental 与 Lent 的主要区别

| 项目 | Lent（出租） | Rental（借入） |
|------|-------------|---------------|
| 类名 | `yyypLent` | `yyypRental` |
| API接口 | `/api/youpin/bff/order/rent-out-record-list` | `/api/youpin/bff/order/lease-record-list` |
| 数据库表 | `yyyp_lent` + `lent` | 仅 `rental` |
| 人员字段 | `lenter_name`（承租人） | `lessor_name`（出租人） |
| 后端路由 | `/youpin898LentV1` | `/youpin898RentalV1` |

## 🔧 Rental 可用的方法

```python
class yyypRental:
    def get_rent_records()          # 获取借入订单列表
    def get_rental_detail()         # 获取借入订单详情
    def getNewRentalData()          # 获取新的借入数据
    def getNotRentalData()          # 获取所有未同步的借入数据
    def updateRentalStatus()        # 更新借入订单状态
    def post_API()                  # 批量提交借入数据
    def _parse_order_data()         # 解析订单数据
```

## 🌐 后端 API 接口

```
GET  /youpin898RentalV1/getNowRentalList          # 获取需要更新状态的借入订单
GET  /youpin898RentalV1/getTimeOutRental          # 获取超时的借入订单
GET  /youpin898RentalV1/selectApexTime/<steamId>  # 获取最新借入订单时间
GET  /youpin898RentalV1/getCount/<steamId>        # 获取借入订单总数
POST /youpin898RentalV1/updateRentalData          # 更新借入订单状态
POST /youpin898RentalV1/insert_rental_data        # 插入借入订单数据
```

## ✅ 验证结果

- ✅ 所有文件无语法错误
- ✅ 所有 lent 相关引用已清除
- ✅ 所有接口调用已更新为 youpin898RentalV1
- ✅ 数据库模型已正确注册
- ✅ Blueprint 已正确注册

## 🚀 使用示例

```python
from Spider.src.web_site.youping.get_trade.rental import yyypRental

config = {
    'Sessionid': 'xxx',
    'app_version': 'xxx',
    'steamId': 'xxx',
    # ... 其他配置
}

rental_client = yyypRental(config)

# 获取历史数据
rental_client.getNotRentalData()

# 获取新数据
rental_client.getNewRentalData()

# 更新订单状态
rental_client.updateRentalStatus()
```

## 📝 注意事项

1. **rental 不需要源表**：直接使用主表 `rental`，不需要 `yyyp_rental`
2. **字段命名**：使用 `lessor_name` 和 `lessor_id` 表示出租人
3. **API 接口**：使用 `/api/youpin/bff/order/lease-record-list`
4. **首次运行**：会自动创建 rental 表
