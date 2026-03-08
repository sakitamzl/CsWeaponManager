<template>
  <div class="card chart-card csqaq-compact-card">
    <div class="chart-header">
      <h3>CSQAQ 市场指数</h3>
    </div>

    <!-- 加载中 -->
    <div v-if="dataLoading" class="compact-loading">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <!-- 数据展示 - 折线图有数据即显示（不等指数），布局：指数左、折线图右 -->
    <div v-else-if="chartData?.values?.length || marketIndexData" class="compact-content">
      <div class="main-item-with-chart">
        <!-- 指数 - 左边（有指数数据时显示，否则占位） -->
        <div class="main-item-left">
          <template v-if="marketIndexData">
            <div class="list-content">
              <div class="list-value">
                <span class="main-value">{{ marketIndexData.now }}</span>
                <span class="change-value" :class="marketIndexData.rate >= 0 ? 'positive' : 'negative'">
                  {{ marketIndexData.rate >= 0 ? '+' : '' }}{{ marketIndexData.rate }}%
                  ({{ marketIndexData.rate >= 0 ? '+' : '' }}{{ marketIndexData.amplitude }})
                </span>
              </div>
              <div class="list-update">更新时间: {{ formatUpdateTime }}</div>
            </div>
          </template>
          <template v-else>
            <span class="loading-sub">加载指数中...</span>
          </template>
        </div>
        <!-- 折线图 - 右边（有数据即显示，不等待指数） -->
        <div v-if="chartData?.values?.length" class="main-item-right">
          <div ref="chartContainer" class="mini-chart-container"></div>
        </div>
      </div>
    </div>

    <!-- 无数据 -->
    <div v-else class="compact-empty">
      <span>暂无数据</span>
    </div>

    <!-- 所有指数列表 -->
    <div v-if="indexListData && indexListData.length > 0" class="index-list-section">
      <div class="index-list-scrollable">
        <div
          v-for="index in indexListData"
          :key="index.id"
          class="index-item-row"
        >
          <div class="index-item-left">
            <img v-if="index.img" :src="index.img" :alt="index.name" class="index-icon" />
            <span class="index-name">{{ index.name }}</span>
          </div>
          <div class="index-item-right">
            <span class="index-current-value">{{ index.market_index }}</span>
            <span
              class="index-change-value"
              :class="index.chg_rate >= 0 ? 'positive' : 'negative'"
            >
              {{ index.chg_rate >= 0 ? '+' : '' }}{{ index.chg_rate }}%
            </span>
            <span
              class="index-change-num"
              :class="index.chg_num >= 0 ? 'positive' : 'negative'"
            >
              {{ index.chg_num >= 0 ? '+' : '' }}{{ index.chg_num }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import { useCSQAQMarketIndex } from './useCSQAQMarketIndex.js'

const {
  dataLoading,
  marketIndexData,
  chartData,
  chartContainer,
  lastUpdate,
  indexListData
} = useCSQAQMarketIndex()

// 格式化更新时间
const formatUpdateTime = computed(() => {
  if (!lastUpdate.value) return ''
  const date = lastUpdate.value
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}:${String(date.getSeconds()).padStart(2, '0')}`
})
</script>

<style scoped src="./styles.css"></style>
