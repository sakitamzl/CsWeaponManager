# 出租功能集成说明

## 📦 已完成的集成

### 1. 创建的组件

#### PlatformSelectDialog.vue
平台选择对话框组件,用于用户选择要上架的平台。

**特性:**
- ✅ 悠悠有品平台(已启用)
- 🚧 BUFF 平台(预留接口,显示"开发中")
- 显示已选择的饰品数量
- 精美的 UI 设计

#### RentFormYYYP.vue
悠悠有品出租表单组件,基于你提供的截图设计。

**表单项:**
- 交易方式: 租赁 / 可租可售
- 出租天数: 10天 / 21天 / 30天 / 自定义
- 短租租金
- 押金赔付信息
- 商品押金
- 增值服务(0CD出租、租送活动)

### 2. 集成到 Inventory.vue

#### 修改内容:
1. **导入组件**
   - 导入 `PlatformSelectDialog`
   - 导入 `RentFormYYYP`

2. **添加状态管理**
   ```javascript
   platformSelectVisible     // 平台选择对话框显示状态
   rentFormVisible          // 出租表单对话框显示状态
   selectedRentPlatform     // 选中的平台
   ```

3. **修改 showRentDialog() 函数**
   - 原来直接打开出租弹窗
   - 现在先打开平台选择对话框

4. **新增函数**
   - `handlePlatformSelect()` - 处理平台选择
   - `handlePlatformSelectCancel()` - 取消平台选择
   - `handleRentFormClosed()` - 表单关闭处理
   - `handleRentFormSubmit()` - 表单提交处理(待对接 API)

## 🎯 使用流程

### 用户操作流程:

1. **选择饰品**
   - 在库存页面选择要出租的饰品(支持多选)

2. **点击"出租"按钮**
   - 触发平台选择对话框

3. **选择平台**
   - 当前只有"悠悠有品"可用
   - BUFF 显示"开发中"

4. **填写出租表单**
   - 选择交易方式
   - 设置出租天数
   - 输入短租租金
   - 输入商品押金
   - 选择增值服务

5. **提交表单**
   - 点击"确认上架"
   - 表单验证通过后提交

## 🔌 API 对接点

在 `handleRentFormSubmit()` 函数中对接悠悠有品出租 API:

```javascript
// 位置: Inventory.vue:2796
const handleRentFormSubmit = async (formData) => {
  console.log('出租表单提交:', formData)
  console.log('选中的物品:', selectedItems.value)

  // TODO: 这里对接悠悠有品出租 API
  // formData 结构:
  // {
  //   tradeMode: 'rent' | 'rentOrSale',
  //   rentDays: number,
  //   shortRentPrice: number,
  //   depositPrice: number,
  //   services: {
  //     zeroCooldown: boolean
  //   }
  // }

  // selectedItems.value 包含所有选中的饰品信息

  ElMessage.info('出租功能API对接开发中...')
}
```

### 需要对接的数据:

**发送到后端:**
- `steamId` - Steam 账号 ID
- `assetIds` - 饰品资产 ID 数组
- `tradeMode` - 交易方式
- `rentDays` - 出租天数
- `shortRentPrice` - 短租租金
- `depositPrice` - 押金
- `zeroCooldown` - 是否 0CD 出租

**示例 API 调用:**
```javascript
const response = await axios.post(
  apiUrls.yyypRentItems(),
  {
    steamId: selectedSteamId.value,
    items: selectedItems.value.map(item => ({
      assetId: item.assetid,
      tradeMode: formData.tradeMode,
      rentDays: formData.rentDays,
      shortRentPrice: formData.shortRentPrice,
      depositPrice: formData.depositPrice,
      zeroCooldown: formData.services.zeroCooldown
    }))
  }
)
```

## 📝 待办事项

- [ ] 对接悠悠有品出租 API
- [ ] 添加出租进度显示(类似出售功能)
- [ ] 添加出租成功/失败的状态反馈
- [ ] 刷新库存数据(出租成功后)
- [ ] 支持批量出租
- [ ] 为 BUFF 平台实现出租功能(未来)

## 🎨 样式特点

- 深色主题设计
- 响应式布局
- 平滑动画过渡
- 清晰的视觉反馈

## 🔍 文件位置

```
WebSite/src/views/
├── Inventory.vue                           # 主库存页面(已集成)
└── Inventory/
    ├── PlatformSelectDialog.vue           # 平台选择对话框
    ├── RentFormYYYP.vue                   # 悠悠有品出租表单
    ├── RentFormYYYPExample.vue            # 表单示例页面
    └── README_RENT.md                      # 本文档
```

## 🚀 测试建议

1. 选择单个饰品,点击出租
2. 选择多个饰品,点击出租
3. 测试表单验证(空值、非法值)
4. 测试自定义天数输入
5. 测试取消操作
6. 测试 BUFF 平台提示

## 💡 注意事项

1. 表单组件 `RentFormYYYP.vue` 已实现完整的前端验证
2. 暂未对接真实 API,提交时会显示"开发中"提示
3. BUFF 平台选项已预留,选择后会提示"开发中"
4. 所有组件都支持响应式设计,适配移动端

## 📞 下一步

对接完 API 后,建议测试以下场景:
- 单个饰品出租
- 批量饰品出租
- 网络错误处理
- 部分成功/部分失败的情况
- 出租后的库存更新
