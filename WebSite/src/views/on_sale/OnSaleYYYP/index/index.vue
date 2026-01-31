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
    <div class="component-container">
      <Suspense>
        <template #default>
          <component :is="currentComponent" :key="selectedTradeType" />
        </template>
        <template #fallback>
          <div class="component-loading">
            <p>正在加载 {{ currentComponent }} 组件...</p>
          </div>
        </template>
      </Suspense>
    </div>
  </div>
</template>

<script>
import { defineAsyncComponent } from 'vue'
import { useOnSaleYYYPIndex } from './useOnSaleYYYPIndex.js'

export default {
  name: 'OnSaleYYYPIndex',
  components: {
    OnSaleSale: defineAsyncComponent(() => import('../OnSaleSale/index.vue')),
    OnSaleLease: defineAsyncComponent(() => import('../OnSaleLease/index.vue')),
    OnSaleSublease: defineAsyncComponent(() => import('../OnSaleSublease/index.vue')),
    OnSalePresale: defineAsyncComponent(() => import('../OnSalePresale/index.vue')),
    OnSaleTransfer: defineAsyncComponent(() => import('../OnSaleTransfer/index.vue')),
    OnSaleRentedOut: defineAsyncComponent(() => import('../OnSaleRentedOut/index.vue')),
    OnSaleInstant: defineAsyncComponent(() => import('../OnSaleInstant/index.vue'))
  },
  setup() {
    const result = useOnSaleYYYPIndex()
    return result
  },
  mounted() {
    // 调试信息：检查组件是否正确注册
    console.log('OnSaleYYYP mounted - 已注册的组件:', Object.keys(this.$options.components || {}))
    console.log('当前选中的交易类型:', this.selectedTradeType)
    console.log('当前组件名称:', this.currentComponent)

    // 验证组件是否存在
    if (this.$options.components && this.$options.components[this.currentComponent]) {
      console.log('组件已注册并可用:', this.currentComponent)
    } else {
      console.error('组件未找到:', this.currentComponent)
    }
  },
  errorCaptured(err, instance, info) {
    console.error('组件加载错误:', err, info)
    return false
  }
}
</script>

<style scoped src="./styles.css"></style>
