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

    <!-- 数据展示 - 大盘指数、折线图、饰品成交额 -->
    <div v-else-if="marketIndexData" class="compact-content">
      <!-- 大盘 - 左边数据,右边小折线图 -->
      <div class="main-item-with-chart">
        <div class="main-item-left">
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
        <div class="main-item-right">
          <div ref="chartContainer" class="mini-chart-container"></div>
        </div>
      </div>

      <!-- 饰品成交数据信息 - 第一行：成交额和成交量 -->
      <div v-if="homepageData" class="homepage-data-section">
        <!-- 左列：成交额 -->
        <div class="data-column">
          <div class="data-column-header">
            <span class="column-title">饰品成交额</span>
            <span v-if="homepageData.ratio" class="column-ratio" :class="homepageData.ratio.includes('↓') ? 'negative' : 'positive'">
              环比 {{ homepageData.ratio }}
            </span>
          </div>
          <div class="data-column-main">
            <span class="main-number orange">{{ homepageData.turnover }}</span>
            <span class="main-unit">万</span>
          </div>
          <div class="data-column-footer">
            昨日 {{ homepageData.yesterday }}
          </div>
        </div>

        <!-- 右列：成交量 -->
        <div class="data-column">
          <div class="data-column-header">
            <span class="column-title">饰品成交量</span>
            <span v-if="homepageData.volume_ratio" class="column-ratio" :class="homepageData.volume_ratio.includes('↓') ? 'negative' : 'positive'">
              环比 {{ homepageData.volume_ratio }}
            </span>
          </div>
          <div class="data-column-main">
            <span class="main-number blue">{{ homepageData.volume }}</span>
            <span class="main-unit">万</span>
          </div>
          <div class="data-column-footer">
            昨日 {{ homepageData.yesterday_volume }}
          </div>
        </div>
      </div>

      <!-- 饰品新增数据信息 - 第二行：新增额和新增量 -->
      <div v-if="homepageData" class="homepage-data-section">
        <!-- 左列：新增额 -->
        <div class="data-column">
          <div class="data-column-header">
            <span class="column-title">饰品新增额</span>
            <span v-if="homepageData.add_valuation_ratio" class="column-ratio" :class="homepageData.add_valuation_ratio.includes('↓') ? 'negative' : 'positive'">
              环比 {{ homepageData.add_valuation_ratio }}
            </span>
          </div>
          <div class="data-column-main">
            <span class="main-number orange">{{ homepageData.add_valuation }}</span>
            <span class="main-unit">万</span>
          </div>
          <div class="data-column-footer">
            昨日 {{ homepageData.yesterday_add_valuation }}
          </div>
        </div>

        <!-- 右列：新增量 -->
        <div class="data-column">
          <div class="data-column-header">
            <span class="column-title">饰品新增量</span>
            <span v-if="homepageData.add_num_ratio" class="column-ratio" :class="homepageData.add_num_ratio.includes('↓') ? 'negative' : 'positive'">
              环比 {{ homepageData.add_num_ratio }}
            </span>
          </div>
          <div class="data-column-main">
            <span class="main-number blue">{{ homepageData.add_num }}</span>
            <span class="main-unit">万</span>
          </div>
          <div class="data-column-footer">
            昨日 {{ homepageData.yesterday_add_num }}
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
  homepageData,
  lastUpdate,
  chartContainer
} = useSteamDT()

// 格式化更新时间
const formatUpdateTime = computed(() => {
  if (!lastUpdate.value) return ''
  const date = lastUpdate.value
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}:${String(date.getSeconds()).padStart(2, '0')}`
})
</script>

<style scoped src="./styles.css"></style>
