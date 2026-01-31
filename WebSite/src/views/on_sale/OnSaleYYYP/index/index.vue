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
import { useOnSaleYYYPIndex } from './useOnSaleYYYPIndex.js'

export default {
  name: 'OnSaleYYYPIndex',
  components: {
    OnSaleSale: () => import('../OnSaleSale/index.vue'),
    OnSaleLease: () => import('../OnSaleLease/index.vue'),
    OnSaleSublease: () => import('../OnSaleSublease/index.vue'),
    OnSalePresale: () => import('../OnSalePresale/index.vue'),
    OnSaleTransfer: () => import('../OnSaleTransfer/index.vue'),
    OnSaleRentedOut: () => import('../OnSaleRentedOut/index.vue'),
    OnSaleInstant: () => import('../OnSaleInstant/index.vue')
  },
  setup() {
    return useOnSaleYYYPIndex()
  }
}
</script>

<style scoped src="./styles.css"></style>
