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

    <!-- 数据展示 - 市场指数和折线图 -->
    <div v-else-if="marketIndexData" class="compact-content">
      <!-- 市场指数 - 左边数据,右边小折线图 -->
      <div class="main-item-with-chart">
        <div class="main-item-left">
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
        </div>
        <div class="main-item-right">
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
      <div class="index-list-header">
        <h4>市场指数列表</h4>
      </div>
      <div class="index-list-grid">
        <div
          v-for="index in indexListData"
          :key="index.id"
          class="index-item-card"
        >
          <div class="index-item-header">
            <img v-if="index.img" :src="index.img" :alt="index.name" class="index-icon" />
            <span class="index-name">{{ index.name }}</span>
          </div>
          <div class="index-item-content">
            <div class="index-value-row">
              <span class="index-current-value">{{ index.market_index }}</span>
              <span
                class="index-change-value"
                :class="index.chg_rate >= 0 ? 'positive' : 'negative'"
              >
                {{ index.chg_rate >= 0 ? '+' : '' }}{{ index.chg_rate }}%
              </span>
            </div>
            <div class="index-detail-row">
              <span class="index-detail-label">涨跌:</span>
              <span
                class="index-detail-value"
                :class="index.chg_num >= 0 ? 'positive' : 'negative'"
              >
                {{ index.chg_num >= 0 ? '+' : '' }}{{ index.chg_num }}
              </span>
            </div>
            <div class="index-detail-row">
              <span class="index-detail-label">开盘:</span>
              <span class="index-detail-value">{{ index.open }}</span>
              <span class="index-detail-label">收盘:</span>
              <span class="index-detail-value">{{ index.close }}</span>
            </div>
            <div class="index-detail-row">
              <span class="index-detail-label">最高:</span>
              <span class="index-detail-value">{{ index.high }}</span>
              <span class="index-detail-label">最低:</span>
              <span class="index-detail-value">{{ index.low }}</span>
            </div>
            <div class="index-update-time">
              更新: {{ index.updated_at ? new Date(index.updated_at).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }) : 'N/A' }}
            </div>
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
