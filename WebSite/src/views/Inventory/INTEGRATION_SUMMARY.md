# 出租功能集成总结

## ✅ 已完成的工作

### 1. 饰品列表展示 ✨
- [x] 在出租表单中显示选中的饰品列表
- [x] 显示饰品图片、名称、磨损、购入价
- [x] 支持滚动查看多个饰品
- [x] 列表样式精美,带悬停效果

### 2. 解析 init.json 数据 📊
成功解析并使用以下数据:

#### 交易方式 (`tradingMethodDTOList`)
- 自动过滤出"租赁"和"可租可售"选项
- 动态渲染交易方式按钮

#### 出租天数 (`leaseDayList`)
- 从 init 数据读取: [8, 15, 30]
- 动态生成天数选项按钮
- 支持自定义天数输入(带范围验证)

#### 饰品系数配置 (`coefficientMap`)
- 最小/最大租金验证
- 最小/最大押金验证
- 最小/最大租赁天数限制

#### 零CD活动提示 (`zeroRentMap`)
- 租金提示: "租金<=0.89更快出租"
- 押金提示: "押金<=1299，优先展示"

#### 押金赔付费率 (`depositProtectFeeConfigMap`)
- 显示服务费率: 25%
- 显示VIP费率: 20% (删除线)

#### 租送活动 (`activityCustomConfigDTOList`)
- 显示"满9送1、满30送3"
- 支持选择是否参加活动

#### 0CD出租支持 (`zeroCDRentSupportTempateMap`)
- 根据饰品判断是否支持0CD出租
- 动态显示/隐藏0CD选项

### 3. 表单验证 🛡️
实现完整的前端验证:
- ✅ 租赁天数验证 (8-100天)
- ✅ 租金范围验证 (0.01-100.00)
- ✅ 押金范围验证 (根据配置)
- ✅ 必填项验证
- ✅ 数字格式验证

### 4. 数据传递 🔄
从 Inventory.vue 传递到 RentFormYYYP:

```javascript
// 饰品数据
formattedSelectedItems: [
  {
    assetid: "xxx",
    name: "加利尔 AR | 警告！（崭新出厂）",
    steam_hash_name: "Galil AR | CAUTION! (Factory New)",
    image: "图片URL",
    float: "0.052507744",
    buyPrice: "868.99"
  }
]

// init 数据
rentInitData: {
  tradingMethodDTOList: [...],
  leaseDayList: [8, 15, 30],
  coefficientMap: {...},
  zeroRentMap: {...},
  depositProtectFeeConfigMap: {...},
  activityCustomConfigDTOList: [...],
  zeroCDRentSupportTempateMap: {...}
}
```

## 📁 修改的文件

### 1. RentFormYYYP.vue (完全重写)
**新增功能:**
- 接收 `items` 和 `initData` props
- 显示饰品列表(带图片、名称、磨损、价格)
- 根据 init 数据动态渲染表单选项
- 根据饰品配置进行验证
- 自动读取并显示各种提示信息

**关键改进:**
```vue
<!-- 饰品列表展示 -->
<div class="items-list">
  <div v-for="(item, index) in items" class="item-card">
    <div class="item-image">
      <img :src="item.image" />
    </div>
    <div class="item-info">
      <div class="item-name">{{ item.name }}</div>
      <div class="item-details">
        <span>磨损: {{ item.float }}</span>
        <span>购入: ¥{{ item.buyPrice }}</span>
      </div>
    </div>
  </div>
</div>

<!-- 动态交易方式 -->
<div v-for="method in tradeMethods" @click="formData.tradeMode = method.type">
  {{ method.name }}
</div>

<!-- 动态出租天数 -->
<div v-for="days in rentDaysOptions" @click="formData.rentDays = days">
  {{ days }}天
</div>
```

### 2. Inventory.vue
**新增:**
- `rentInitData` 状态变量
- `formattedSelectedItems` 计算属性
- 传递 props 到 RentFormYYYP

**修改位置:**
```javascript
// Line 1460: 添加状态
const rentInitData = ref(null)

// Line 3377-3386: 添加计算属性
const formattedSelectedItems = computed(() => {
  return selectedItems.value.map(item => ({
    assetid: item.assetid,
    name: getCardTitle(item),
    steam_hash_name: item.steam_hash_name || item.item_name,
    image: getWeaponImage(item.steam_hash_name),
    float: item.weapon_float,
    buyPrice: item.buy_price ? parseFloat(item.buy_price).toFixed(2) : null
  }))
})

// Line 1341-1342: 传递 props
<RentFormYYYP
  :items="formattedSelectedItems"
  :initData="rentInitData"
  @cancel="rentFormVisible = false"
  @submit="handleRentFormSubmit"
/>

// Line 3624-3625: 导出变量
rentInitData,
formattedSelectedItems,
```

## 🔌 下一步: API 对接

### 需要实现的功能:

#### 1. 获取 init 数据
```javascript
const handlePlatformSelect = async (platform) => {
  selectedRentPlatform.value = platform

  if (platform === 'yyyp') {
    // 调用 init API
    try {
      const response = await axios.post(
        `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/rentInit`,
        {
          steamId: selectedSteamId.value,
          assetIds: selectedItems.value.map(item => item.assetid)
        }
      )

      if (response.data.code === 0) {
        rentInitData.value = response.data.data
        rentFormVisible.value = true
      } else {
        ElMessage.error(response.data.msg || '获取配置失败')
      }
    } catch (error) {
      console.error('获取出租配置失败:', error)
      ElMessage.error('获取配置失败，请重试')
    }
  }
}
```

#### 2. 提交出租请求
```javascript
const handleRentFormSubmit = async (formData) => {
  console.log('出租表单提交:', formData)
  console.log('选中的物品:', selectedItems.value)

  try {
    // 逐个上架
    let successCount = 0
    let failCount = 0

    for (const item of selectedItems.value) {
      try {
        const response = await axios.post(
          `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/rentInventoryItem`,
          {
            steamId: selectedSteamId.value,
            assetId: item.assetid,
            tradingMethod: formData.tradeMode, // 1=租赁, 2=可租可售
            rentDays: formData.rentDays,
            shortRentPrice: formData.shortRentPrice,
            depositPrice: formData.depositPrice,
            zeroCooldown: formData.services.zeroCooldown,
            rentActivity: formData.services.rentActivity
          }
        )

        if (response.data.success) {
          successCount++
          console.log(`✓ 出租成功: ${getCardTitle(item)}`)
        } else {
          failCount++
          console.error(`✗ 出租失败: ${getCardTitle(item)} - ${response.data.message}`)
        }

        // 延迟避免请求过快
        if (i < selectedItems.value.length - 1) {
          await new Promise(resolve => setTimeout(resolve, 1000))
        }
      } catch (error) {
        failCount++
        console.error(`✗ 出租异常: ${getCardTitle(item)}`, error)
      }
    }

    // 显示结果
    if (failCount === 0) {
      ElMessage.success(`全部出租成功！共${successCount}件物品`)
      rentFormVisible.value = false
    } else if (successCount === 0) {
      ElMessage.error(`全部出租失败！共${failCount}件物品`)
    } else {
      ElMessage.warning(`出租完成：成功${successCount}件，失败${failCount}件`)
    }

    // 刷新库存
    await loadInventoryData()
  } catch (error) {
    console.error('出租失败:', error)
    ElMessage.error(error.message || '出租失败')
  }
}
```

### API 端点 (需要后端提供):
1. **POST** `/youping898SpiderV1/rentInit` - 获取出租配置
   - 参数: `{ steamId, assetIds }`
   - 返回: init.json 格式的数据

2. **POST** `/youping898SpiderV1/rentInventoryItem` - 出租单个饰品
   - 参数: `{ steamId, assetId, tradingMethod, rentDays, shortRentPrice, depositPrice, zeroCooldown, rentActivity }`
   - 返回: `{ success, message }`

## 🎨 UI 特性

### 饰品列表卡片
- 深色主题 (#1a1a1a, #2a2a2a)
- 最大高度 200px,超出滚动
- 悬停效果
- 序号标记 (#1, #2, ...)

### 动态表单
- 所有选项从 init 数据读取
- 实时验证
- 友好的错误提示
- 范围限制显示

### 响应式设计
- 桌面端: 4列布局
- 移动端: 2列布局
- 自适应图片大小

## 📊 数据流程图

```
用户选择饰品
    ↓
点击"出租"
    ↓
选择平台(悠悠有品)
    ↓
调用 rentInit API → 获取配置数据
    ↓
显示出租表单
    ├─ 显示饰品列表
    ├─ 根据配置显示选项
    └─ 根据配置设置验证规则
    ↓
用户填写表单
    ↓
表单验证
    ↓
提交出租请求 (逐个上架)
    ↓
显示结果 & 刷新库存
```

## 🧪 测试建议

1. **单个饰品出租**: 选择1个饰品测试
2. **多个饰品出租**: 选择多个饰品测试
3. **表单验证**: 测试各种非法输入
4. **自定义天数**: 测试边界值(8, 100)
5. **服务选项**: 测试0CD和租送活动
6. **取消操作**: 测试取消流程
7. **响应式**: 测试移动端显示

## 📝 注意事项

1. **图片加载**: 确保 `getWeaponImage()` 返回正确的图片 URL
2. **Hash Name**: 需要使用 `steam_hash_name` 匹配 coefficientMap
3. **数据格式**: init API 返回的数据格式必须与 init.json 一致
4. **错误处理**: 需要处理网络错误、API 错误
5. **加载状态**: 建议添加 loading 状态提示

## 🚀 部署清单

- [x] PlatformSelectDialog.vue - 平台选择对话框
- [x] RentFormYYYP.vue - 出租表单组件
- [x] Inventory.vue 集成 - 主页面集成
- [ ] API 对接 - 后端接口对接
- [ ] 测试 - 功能测试
- [ ] 上线 - 生产环境部署

---

**当前状态**: ✅ 前端完成，等待 API 对接

**下一步**: 实现 `handlePlatformSelect` 和 `handleRentFormSubmit` 中的 API 调用逻辑
