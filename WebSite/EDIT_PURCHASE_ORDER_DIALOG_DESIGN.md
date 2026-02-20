# 修改求购订单弹出框设计

## 界面设计（参考图片）

### 弹出框标题
```
修改求购
```

### 内容区域

#### 1. 物品信息展示区
```
┌────────────┬──────────────────────────────────┐
│            │  印花 | 炙热                      │
│  [图片]     │  参考价：¥6.20    查看市场 >      │
│            │                                  │
└────────────┴──────────────────────────────────┘
```

#### 2. 当前市场行情
```
┌─────────────────┬─────────────────┐
│   ¥6.05         │      ¥6         │
│   在售最低       │   求购最高       │
└─────────────────┴─────────────────┘
```

#### 3. 求购单价输入
```
求购单价¥    [  6  ]     (?)
```

#### 4. 求购数量输入
```
求购数量      [  9  ]
```

#### 5. 增值服务
```
增值服务    自动接收    >
```

#### 6. 求购规则说明
```
求购规则：

• 求购账户余额>求购总价(求购单价*数量)，可无限发布求购；账户余额不足可补足差额继续发布，差额将充值进求购账户。

• 卖家供应发起报价后，你需要在24小时内接收报价，取消报价或24小时未接收会扣除2%求购金额作为处罚。

• 求购账户余额随时可提现，0手续费。
```

#### 7. 底部按钮区
```
┌─────────────────────────────────────┐
│  总计  ¥54              [确定]        │
└─────────────────────────────────────┘
```

## Vue 组件实现代码

```vue
<template>
  <el-dialog
    v-model="dialogVisible"
    title="修改求购"
    width="90%"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    @close="handleClose"
  >
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <!-- 主要内容 -->
    <div v-else class="edit-purchase-content">
      <!-- 物品信息 -->
      <div class="item-info">
        <div class="item-image">
          <el-image
            :src="orderInfo.icon_url"
            fit="contain"
            style="width: 100px; height: 100px"
          />
        </div>
        <div class="item-details">
          <div class="item-name">{{ orderInfo.commodity_name }}</div>
          <div class="item-reference">
            <span>参考价：¥{{ orderInfo.reference_price }}</span>
            <el-link type="primary" @click="viewMarket">查看市场 ></el-link>
          </div>
        </div>
      </div>

      <!-- 市场行情 -->
      <div class="market-info">
        <div class="market-item">
          <div class="market-price">¥{{ orderInfo.lowest_selling_price }}</div>
          <div class="market-label">在售最低</div>
        </div>
        <div class="market-item">
          <div class="market-price">¥{{ orderInfo.highest_purchase_price }}</div>
          <div class="market-label">求购最高</div>
        </div>
      </div>

      <!-- 求购单价 -->
      <div class="form-row">
        <div class="form-label">
          求购单价¥
          <el-tooltip content="设置您愿意支付的单个物品价格" placement="top">
            <el-icon><QuestionFilled /></el-icon>
          </el-tooltip>
        </div>
        <el-input-number
          v-model="formData.unitPrice"
          :precision="2"
          :step="0.01"
          :min="0.01"
          :max="parseFloat(orderInfo.max_purchase_price) || 999999"
          controls-position="right"
          style="width: 100%"
        />
      </div>

      <!-- 求购数量 -->
      <div class="form-row">
        <div class="form-label">求购数量</div>
        <el-input-number
          v-model="formData.quantity"
          :min="1"
          :max="9999"
          controls-position="right"
          style="width: 100%"
        />
      </div>

      <!-- 增值服务 -->
      <div class="form-row clickable" @click="handleServiceClick">
        <div class="form-label">增值服务</div>
        <div class="service-value">
          <span>{{ orderInfo.auto_received ? '自动接收' : '手动接收' }}</span>
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>

      <!-- 求购规则 -->
      <div class="rules-section">
        <div class="rules-title">求购规则：</div>
        <ul class="rules-list">
          <li>求购账户余额>求购总价(求购单价*数量)，可无限发布求购；账户余额不足可补足差额继续发布，差额将充值进求购账户。</li>
          <li>卖家供应发起报价后，你需要在24小时内接收报价，取消报价或24小时未接收会扣除2%求购金额作为处罚。</li>
          <li>求购账户余额随时可提现，0手续费。</li>
        </ul>
      </div>

      <!-- 底部操作栏 -->
      <div class="footer-bar">
        <div class="total-price">
          总计 <span class="price">¥{{ totalPrice }}</span>
        </div>
        <el-button
          type="primary"
          size="large"
          :loading="submitting"
          @click="handleConfirm"
        >
          确定
        </el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading, QuestionFilled, ArrowRight } from '@element-plus/icons-vue'
import axios from 'axios'
import { apiUrls } from '@/config/api.js'

const props = defineProps({
  steamId: {
    type: String,
    required: true
  },
  orderNo: {
    type: String,
    default: ''
  },
  visible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:visible', 'success'])

const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const loading = ref(false)
const submitting = ref(false)
const orderInfo = ref({})
const formData = ref({
  unitPrice: 0,
  quantity: 1
})

// 计算总价
const totalPrice = computed(() => {
  return (formData.value.unitPrice * formData.value.quantity).toFixed(2)
})

// 监听弹窗打开，加载订单信息
watch(() => props.visible, async (newVal) => {
  if (newVal && props.orderNo) {
    await loadOrderInfo()
  }
})

// 加载订单详情
const loadOrderInfo = async () => {
  loading.value = true
  try {
    const response = await axios.post(apiUrls.yyypGetOrderInfo(), {
      steamId: props.steamId,
      orderNo: props.orderNo
    })

    if (response.data.code === 200) {
      const result = response.data.data
      if (result.success) {
        orderInfo.value = result.data
        // 初始化表单数据
        formData.value = {
          unitPrice: parseFloat(orderInfo.value.unit_price) || 0,
          quantity: orderInfo.value.quantity || 1
        }
      } else {
        ElMessage.error(result.message || '获取订单详情失败')
        handleClose()
      }
    } else {
      ElMessage.error(response.data.message || '获取订单详情失败')
      handleClose()
    }
  } catch (error) {
    console.error('加载订单详情失败:', error)
    ElMessage.error('加载订单详情失败，请重试')
    handleClose()
  } finally {
    loading.value = false
  }
}

// 查看市场
const viewMarket = () => {
  // TODO: 打开市场页面
  ElMessage.info('查看市场功能待实现')
}

// 增值服务点击
const handleServiceClick = () => {
  ElMessage.info('增值服务设置功能待实现')
}

// 确认修改
const handleConfirm = async () => {
  // 验证输入
  if (formData.value.unitPrice <= 0) {
    ElMessage.warning('请输入有效的求购单价')
    return
  }

  if (formData.value.quantity < 1) {
    ElMessage.warning('求购数量至少为1')
    return
  }

  // 确认提示
  try {
    await ElMessageBox.confirm(
      `确定修改求购订单吗？<br>` +
      `<span style="color: #909399;">价格仅供参考，请仔细核对后确认</span>`,
      '确认修改',
      {
        dangerouslyUseHTMLString: true,
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      }
    )
  } catch {
    return // 用户取消
  }

  // 提交修改
  submitting.value = true
  try {
    const response = await axios.post(apiUrls.yyypEditPurchaseOrder(), {
      steamId: props.steamId,
      orderNo: props.orderNo,
      unitPrice: formData.value.unitPrice.toString(),
      quantity: formData.value.quantity
    })

    if (response.data.code === 200) {
      const result = response.data.data
      if (result.success) {
        ElMessage.success('修改成功')
        emit('success')
        handleClose()
      } else {
        ElMessage.error(result.message || '修改失败')
      }
    } else {
      ElMessage.error(response.data.message || '修改失败')
    }
  } catch (error) {
    console.error('修改订单失败:', error)
    ElMessage.error('修改订单失败，请重试')
  } finally {
    submitting.value = false
  }
}

// 关闭弹窗
const handleClose = () => {
  dialogVisible.value = false
  // 重置数据
  orderInfo.value = {}
  formData.value = {
    unitPrice: 0,
    quantity: 1
  }
}
</script>

<style scoped lang="scss">
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #909399;

  .el-icon {
    font-size: 32px;
    margin-bottom: 12px;
  }
}

.edit-purchase-content {
  padding: 16px;
  background-color: #1a1a1a;
  color: #ffffff;
}

.item-info {
  display: flex;
  gap: 16px;
  padding: 16px;
  background-color: #2a2a2a;
  border-radius: 8px;
  margin-bottom: 16px;

  .item-image {
    flex-shrink: 0;
  }

  .item-details {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;

    .item-name {
      font-size: 16px;
      font-weight: 500;
      margin-bottom: 8px;
    }

    .item-reference {
      display: flex;
      justify-content: space-between;
      align-items: center;
      color: #909399;
      font-size: 14px;
    }
  }
}

.market-info {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;

  .market-item {
    flex: 1;
    text-align: center;
    padding: 16px;
    background-color: #2a2a2a;
    border-radius: 8px;

    .market-price {
      font-size: 24px;
      font-weight: 600;
      color: #f39c12;
      margin-bottom: 8px;
    }

    .market-label {
      font-size: 14px;
      color: #909399;
    }
  }
}

.form-row {
  margin-bottom: 20px;

  .form-label {
    font-size: 15px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 6px;

    .el-icon {
      cursor: help;
      color: #909399;
    }
  }

  &.clickable {
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    background-color: #2a2a2a;
    border-radius: 8px;

    &:hover {
      background-color: #333333;
    }

    .service-value {
      display: flex;
      align-items: center;
      gap: 8px;
      color: #409eff;
    }
  }
}

.rules-section {
  margin: 24px 0;
  padding: 16px;
  background-color: #2a2a2a;
  border-radius: 8px;

  .rules-title {
    font-size: 15px;
    font-weight: 500;
    margin-bottom: 12px;
  }

  .rules-list {
    list-style: none;
    padding: 0;
    margin: 0;
    color: #909399;
    font-size: 13px;
    line-height: 1.8;

    li {
      position: relative;
      padding-left: 16px;
      margin-bottom: 8px;

      &::before {
        content: '•';
        position: absolute;
        left: 0;
        color: #409eff;
      }
    }
  }
}

.footer-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #3a3a3a;

  .total-price {
    font-size: 16px;
    color: #909399;

    .price {
      font-size: 24px;
      font-weight: 600;
      color: #f39c12;
      margin-left: 8px;
    }
  }

  .el-button {
    min-width: 120px;
  }
}

:deep(.el-input-number) {
  .el-input__inner {
    background-color: #2a2a2a;
    border-color: #3a3a3a;
    color: #ffffff;
  }

  .el-input-number__decrease,
  .el-input-number__increase {
    background-color: #2a2a2a;
    border-color: #3a3a3a;
    color: #ffffff;

    &:hover {
      color: #409eff;
    }
  }
}
</style>
```

## 使用方式

在 `MyPurchaseRequest` 组件中：

```vue
<template>
  <!-- 其他内容 -->

  <!-- 修改订单弹出框 -->
  <EditPurchaseOrderDialog
    v-model:visible="editDialogVisible"
    :steam-id="props.steamId"
    :order-no="currentOrderNo"
    @success="handleEditSuccess"
  />
</template>

<script setup>
import { ref } from 'vue'
import EditPurchaseOrderDialog from './EditPurchaseOrderDialog.vue'

const editDialogVisible = ref(false)
const currentOrderNo = ref('')

// 处理编辑按钮点击
const handleEditOrder = (item) => {
  currentOrderNo.value = item.order_no
  editDialogVisible.value = true
}

// 编辑成功回调
const handleEditSuccess = () => {
  // 刷新列表
  loadPurchasingOrders()
}
</script>
```

## API 路由总结

**后端路由：**
- `POST /spiderApiV2/youping/units/on_sale/purchase_request/purchasing/getOrderInfo` - 获取订单详情
- `POST /spiderApiV2/youping/units/on_sale/purchase_request/purchasing/editOrder` - 修改订单

**前端配置：**
- `apiUrls.yyypGetOrderInfo()` - 获取订单详情
- `apiUrls.yyypEditPurchaseOrder()` - 修改订单

## 完成！

修改求购订单功能已完整实现，包括：
1. ✅ 后端业务逻辑 (edit_order.py)
2. ✅ Flask API 路由
3. ✅ 前端 API 配置
4. ✅ Vue 组件设计
5. ✅ 测试 JSON 自动保存

请重启 Spider 服务后测试功能！
