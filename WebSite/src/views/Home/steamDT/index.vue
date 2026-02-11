<template>
  <div class="card chart-card steamdt-compact-card">
    <div class="chart-header">
      <h3>SteamDT 市场指数</h3>
    </div>

    <!-- 加载中 -->
    <div v-if="dataLoading" class="compact-loading">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载中...</span>
    </div>

    <!-- 数据展示 - 列表样式 -->
    <div v-else-if="marketIndexData" class="compact-content">
      <!-- 大盘 -->
      <div class="list-item main-item">
        <div class="list-label">大盘</div>
        <div class="list-content">
          <div class="list-value">
            <span class="main-value">{{ marketIndexData.index }}</span>
            <span class="change-value" :class="marketIndexData.riseFallRate >= 0 ? 'positive' : 'negative'">
              {{ marketIndexData.riseFallRate >= 0 ? '+' : '' }}{{ marketIndexData.riseFallRate }}%
              ({{ marketIndexData.riseFallRate >= 0 ? '+' : '' }}{{ marketIndexData.riseFallDiff }})
            </span>
          </div>
          <div class="list-update">更新时间: {{ formatUpdateTime }}</div>
        </div>
      </div>

      <!-- 品类列表 - 可滚动区域 -->
      <div class="compact-scrollable">
        <div v-for="category in categoryData" :key="category.typeVal" class="list-item">
          <div class="list-label">{{ category.nameZh }}</div>
          <div class="list-content">
            <div class="list-value">
              <span class="main-value">{{ category.index }}</span>
              <span class="change-value" :class="category.riseFallRate >= 0 ? 'positive' : 'negative'">
                {{ category.riseFallRate >= 0 ? '+' : '' }}{{ category.riseFallRate }}%
                ({{ category.riseFallRate >= 0 ? '+' : '' }}{{ category.riseFallDiff }})
              </span>
            </div>
          </div>
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
import { computed } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import { useSteamDT } from './useSteamDT.js'

const {
  dataLoading,
  marketIndexData,
  categoryData,
  lastUpdate
} = useSteamDT()

// 格式化更新时间
const formatUpdateTime = computed(() => {
  if (!lastUpdate.value) return ''
  const date = lastUpdate.value
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}:${String(date.getSeconds()).padStart(2, '0')}`
})
</script>

<style scoped src="./styles.css"></style>
