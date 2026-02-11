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

    <!-- 数据展示 -->
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
            <div class="list-update">连涨天数: {{ marketIndexData.consecutive_days }} 天</div>
          </div>
        </div>
        <div class="main-item-right">
          <div ref="chartContainer" class="mini-chart-container"></div>
        </div>
      </div>

      <!-- 统计信息 -->
      <div class="stats-section">
        <div class="stat-item">
          <span class="stat-label">最高:</span>
          <span class="stat-value">{{ marketIndexData.max_value }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">最低:</span>
          <span class="stat-value">{{ marketIndexData.min_value }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">振幅:</span>
          <span class="stat-value">{{ marketIndexData.amplitude }}</span>
        </div>
      </div>
    </div>

    <!-- 无数据 -->
    <div v-else class="compact-empty">
      <span>暂无数据</span>
    </div>
  </div>
</template>

<script setup>
import { Loading } from '@element-plus/icons-vue'
import { useCSQAQMarketIndex } from './useCSQAQMarketIndex.js'

const {
  dataLoading,
  marketIndexData,
  chartContainer
} = useCSQAQMarketIndex()
</script>

<style scoped src="./styles.css"></style>
