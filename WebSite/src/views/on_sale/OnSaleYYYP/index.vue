<template>
  <div class="on-sale-yyyp-container">
    <!-- 交易类型选择栏 -->
    <div class="trade-type-bar card">
      <div class="trade-type-tabs">
        <div
          v-for="type in tradeTypes"
          :key="type.value"
          class="trade-type-tab"
          :class="{ active: selectedTradeType === type.value }"
          @click="handleTradeTypeChange(type.value)"
        >
          <span class="trade-type-icon">{{ type.icon }}</span>
          <span class="trade-type-label">{{ type.label }}</span>
        </div>
      </div>
    </div>

    <!-- 动态组件切换 -->
    <component :is="currentComponent" />
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import OnSaleSale from './OnSaleSale.vue'
import OnSaleLease from './OnSaleLease.vue'
import OnSaleSublease from './OnSaleSublease.vue'
import OnSalePresale from './OnSalePresale.vue'
import OnSaleTransfer from './OnSaleTransfer.vue'
import OnSaleRentedOut from './OnSaleRentedOut.vue'
import OnSaleInstant from './OnSaleInstant.vue'

export default {
  name: 'OnSaleYYYPIndex',
  components: {
    OnSaleSale,
    OnSaleLease,
    OnSaleSublease,
    OnSalePresale,
    OnSaleTransfer,
    OnSaleRentedOut,
    OnSaleInstant
  },
  setup() {
    // 交易类型
    const selectedTradeType = ref('sale') // 默认选择"出售"
    const tradeTypes = ref([
      { value: 'sale', label: '出售', icon: '💰' },
      { value: 'lease', label: '租赁', icon: '🔄' },
      { value: 'sublease', label: '转租', icon: '🔁' },
      { value: 'presale', label: '预售', icon: '⏰' },
      { value: 'transfer', label: '过户', icon: '📝' },
      { value: 'rented-out', label: '已租出', icon: '📦' },
      { value: 'instant', label: '秒到账', icon: '⚡' }
    ])

    // 组件映射
    const componentMap = {
      'sale': 'OnSaleSale',
      'lease': 'OnSaleLease',
      'sublease': 'OnSaleSublease',
      'presale': 'OnSalePresale',
      'transfer': 'OnSaleTransfer',
      'rented-out': 'OnSaleRentedOut',
      'instant': 'OnSaleInstant'
    }

    // 当前组件
    const currentComponent = computed(() => {
      return componentMap[selectedTradeType.value] || 'OnSaleSale'
    })

    // 处理交易类型切换
    const handleTradeTypeChange = (tradeType) => {
      selectedTradeType.value = tradeType
    }

    return {
      selectedTradeType,
      tradeTypes,
      currentComponent,
      handleTradeTypeChange
    }
  }
}
</script>

<style scoped>
.on-sale-yyyp-container {
  padding: 1rem;
}

/* 交易类型选择栏样式 */
.trade-type-bar {
  margin-bottom: 1rem;
  padding: 0.75rem 1rem;
  background: var(--bg-secondary);
  border-radius: 8px;
  overflow-x: auto;
}

.trade-type-tabs {
  display: flex;
  gap: 0.5rem;
  min-width: max-content;
}

.trade-type-tab {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: var(--bg-tertiary);
  border: 2px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  position: relative;
  user-select: none;
}

.trade-type-tab:hover {
  background: rgba(64, 158, 255, 0.1);
  border-color: rgba(64, 158, 255, 0.3);
  transform: translateY(-2px);
}

.trade-type-tab.active {
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.2) 0%, rgba(64, 158, 255, 0.1) 100%);
  border-color: var(--el-color-primary);
  box-shadow: 0 0 12px rgba(64, 158, 255, 0.3);
}

.trade-type-icon {
  font-size: 1.2rem;
  line-height: 1;
}

.trade-type-label {
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--text-primary);
}

.trade-type-tab.active .trade-type-label {
  color: var(--el-color-primary);
  font-weight: 600;
}

.card {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 1rem;
}
</style>
