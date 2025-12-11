<template>
  <div class="market-overview-container">
    <div class="content-wrapper">
      <!-- K线图表 -->
      <el-card class="chart-card" v-loading="loading">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <span class="chart-title">市场指数K线图</span>
              <el-button-group class="period-buttons">
                <el-button 
                  size="small"
                  :type="queryForm.period === '1h' ? 'primary' : ''"
                  @click="changePeriod('1h')"
                >
                  1小时线
                </el-button>
                <el-button 
                  size="small"
                  :type="queryForm.period === '4h' ? 'primary' : ''"
                  @click="changePeriod('4h')"
                >
                  4小时线
                </el-button>
                <el-button 
                  size="small"
                  :type="queryForm.period === '1d' ? 'primary' : ''"
                  @click="changePeriod('1d')"
                >
                  日线
                </el-button>
                <el-button 
                  size="small"
                  :type="queryForm.period === '1w' ? 'primary' : ''"
                  @click="changePeriod('1w')"
                >
                  周线
                </el-button>
              </el-button-group>
            </div>
            <div class="header-right">
              <el-tag v-if="lastUpdateTime" type="info" size="small">
                更新时间: {{ lastUpdateTime }}
              </el-tag>
              <el-button size="small" @click="fetchData" :loading="loading">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </div>
        </template>
        
        <div ref="chartRef" class="chart-container"></div>
      </el-card>

      <!-- 统计信息 -->
      <el-card class="stats-card" v-if="statsData">
        <template #header>
          <div class="card-header">
            <span>市场统计</span>
          </div>
        </template>
        
        <el-row :gutter="20">
          <el-col :xs="12" :sm="6">
            <div class="stat-item">
              <div class="stat-label">最新价格</div>
              <div class="stat-value" :class="{ 'up': statsData.change > 0, 'down': statsData.change < 0 }">
                {{ statsData.latest }}
              </div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6">
            <div class="stat-item">
              <div class="stat-label">涨跌幅</div>
              <div class="stat-value" :class="{ 'up': statsData.change > 0, 'down': statsData.change < 0 }">
                {{ statsData.change > 0 ? '+' : '' }}{{ statsData.change }}%
              </div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6">
            <div class="stat-item">
              <div class="stat-label">最高价</div>
              <div class="stat-value">{{ statsData.high }}</div>
            </div>
          </el-col>
          <el-col :xs="12" :sm="6">
            <div class="stat-item">
              <div class="stat-label">最低价</div>
              <div class="stat-value">{{ statsData.low }}</div>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import axios from 'axios'

const loading = ref(false)
const chartRef = ref(null)
const lastUpdateTime = ref('')
const statsData = ref(null)
let chartInstance = null

const queryForm = reactive({
  period: '1h'
})

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return
  
  chartInstance = echarts.init(chartRef.value, 'dark')
  
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      backgroundColor: 'rgba(30, 30, 30, 0.95)',
      borderColor: '#333',
      textStyle: {
        color: '#fff'
      }
    },
    legend: {
      data: ['K线', 'MA5', 'MA10', 'MA20'],
      textStyle: {
        color: '#b0b0b0'
      }
    },
    grid: {
      left: '3%',
      right: '3%',
      bottom: '10%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: [],
      boundaryGap: true,
      axisLine: {
        lineStyle: {
          color: '#3a3a3a'
        }
      },
      axisLabel: {
        color: '#b0b0b0'
      }
    },
    yAxis: {
      scale: true,
      splitLine: {
        lineStyle: {
          color: '#3a3a3a'
        }
      },
      axisLabel: {
        color: '#b0b0b0'
      }
    },
    dataZoom: [
      {
        type: 'inside',
        start: 0,
        end: 100,
        zoomOnMouseWheel: true,  // 启用鼠标滚轮缩放
        moveOnMouseMove: true,   // 启用鼠标拖拽平移
        moveOnMouseWheel: false  // 禁用滚轮平移（只用于缩放）
      },
      {
        show: true,
        type: 'slider',
        bottom: '3%',
        start: 0,
        end: 100,
        backgroundColor: '#2a2a2a',
        fillerColor: 'rgba(239, 83, 80, 0.2)',
        borderColor: '#3a3a3a',
        textStyle: {
          color: '#b0b0b0'
        },
        handleStyle: {
          color: '#ef5350'
        }
      }
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: [],
        itemStyle: {
          color: '#ef5350',      // 上涨红色
          color0: '#00c853',     // 下跌绿色（更鲜艳的绿色）
          borderColor: '#ef5350', // 上涨边框红色
          borderColor0: '#00c853' // 下跌边框绿色
        }
      },
      {
        name: 'MA5',
        type: 'line',
        data: [],
        smooth: true,
        lineStyle: {
          width: 1,
          color: '#409eff'
        },
        showSymbol: false
      },
      {
        name: 'MA10',
        type: 'line',
        data: [],
        smooth: true,
        lineStyle: {
          width: 1,
          color: '#e6a23c'
        },
        showSymbol: false
      },
      {
        name: 'MA20',
        type: 'line',
        data: [],
        smooth: true,
        lineStyle: {
          width: 1,
          color: '#909399'
        },
        showSymbol: false
      }
    ]
  }
  
  chartInstance.setOption(option)
}

// 计算移动平均线
const calculateMA = (data, period) => {
  const result = []
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push('-')
      continue
    }
    let sum = 0
    for (let j = 0; j < period; j++) {
      sum += data[i - j][1] // 收盘价
    }
    result.push((sum / period).toFixed(2))
  }
  return result
}

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    // 通过后端Spider服务调用CSQAQ API获取指数K线图数据
    const response = await axios.get('/spider/csqaqSpiderV1/getKline', {
      params: {
        period: queryForm.period
      }
    })
    
    if (response.data && response.data.code === 200) {
      const data = response.data.data
      updateChart(data)
      updateStats(data)
      lastUpdateTime.value = new Date().toLocaleString('zh-CN')
      ElMessage.success('数据加载成功')
    } else {
      throw new Error(response.data.message || '数据加载失败')
    }
  } catch (error) {
    console.error('获取数据失败:', error)
    ElMessage.error('获取数据失败: ' + (error.message || '请检查网络连接'))
  } finally {
    loading.value = false
  }
}

// 更新图表
const updateChart = (data) => {
  if (!chartInstance || !data || data.length === 0) return
  
  const times = data.map(item => item.time)
  const klineData = data.map(item => [
    parseFloat(item.open),
    parseFloat(item.close),
    parseFloat(item.low),
    parseFloat(item.high)
  ])
  
  const ma5 = calculateMA(klineData, 5)
  const ma10 = calculateMA(klineData, 10)
  const ma20 = calculateMA(klineData, 20)
  
  // 根据周期计算默认显示的数据范围
  // 1小时线：显示最近3天（72小时）
  // 4小时线：显示最近12天（72个数据点）
  // 日线：显示最近3个月（90天）
  // 周线：显示最近1年（52周）
  let defaultDisplayCount = 72
  switch (queryForm.period) {
    case '1h':
      defaultDisplayCount = 72  // 3天 * 24小时
      break
    case '4h':
      defaultDisplayCount = 72  // 12天 * 6个点
      break
    case '1d':
      defaultDisplayCount = 90  // 3个月
      break
    case '1w':
      defaultDisplayCount = 52  // 1年
      break
  }
  
  // 计算显示范围的百分比
  const totalCount = data.length
  const startPercent = Math.max(0, ((totalCount - defaultDisplayCount) / totalCount) * 100)
  const endPercent = 100
  
  chartInstance.setOption({
    xAxis: {
      data: times
    },
    dataZoom: [
      {
        type: 'inside',
        start: startPercent,
        end: endPercent,
        zoomOnMouseWheel: true,
        moveOnMouseMove: true,
        moveOnMouseWheel: false
      },
      {
        type: 'slider',
        start: startPercent,
        end: endPercent
      }
    ],
    series: [
      {
        data: klineData
      },
      {
        data: ma5
      },
      {
        data: ma10
      },
      {
        data: ma20
      }
    ]
  })
}

// 更新统计信息
const updateStats = (data) => {
  if (!data || data.length === 0) return
  
  const latest = parseFloat(data[data.length - 1].close)
  const previous = parseFloat(data[data.length - 2]?.close || data[0].close)
  const change = ((latest - previous) / previous * 100).toFixed(2)
  
  const prices = data.map(item => parseFloat(item.high))
  const high = Math.max(...prices).toFixed(2)
  const low = Math.min(...data.map(item => parseFloat(item.low))).toFixed(2)
  
  statsData.value = {
    latest: latest.toFixed(2),
    change: parseFloat(change),
    high,
    low
  }
}

// 周期变化处理
const changePeriod = (period) => {
  queryForm.period = period
  fetchData()
}

// 窗口大小变化处理
const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

onMounted(async () => {
  await nextTick()
  initChart()
  fetchData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.market-overview-container {
  padding: 2rem;
  max-width: 1600px;
  margin: 0 auto;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.chart-card,
.stats-card {
  background: #1e1e1e;
  border: 1px solid #333;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.chart-title {
  font-weight: 600;
  color: #ffffff;
  font-size: 1rem;
}

.period-buttons {
  margin-left: 1rem;
}

.chart-container {
  width: 100%;
  height: 500px;
}

.stats-card {
  margin-top: 0;
}

.stat-item {
  text-align: center;
  padding: 1rem;
}

.stat-label {
  color: #909399;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.stat-value {
  color: #ffffff;
  font-size: 1.5rem;
  font-weight: 600;
}

.stat-value.up {
  color: #ef5350;  /* 上涨红色 */
}

.stat-value.down {
  color: #00c853;  /* 下跌绿色 */
}

:deep(.el-form-item__label) {
  color: #b0b0b0;
}

:deep(.el-input__wrapper) {
  background-color: #2a2a2a;
  box-shadow: 0 0 0 1px #3a3a3a inset;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #4a4a4a inset;
}

:deep(.el-input__inner) {
  color: #ffffff;
}

:deep(.el-select .el-input__wrapper) {
  background-color: #2a2a2a;
}

:deep(.el-card__header) {
  background-color: #252525;
  border-bottom: 1px solid #333;
  padding: 1rem 1.5rem;
}

:deep(.el-card__body) {
  padding: 1.5rem;
}

:deep(.el-input-number .el-input__wrapper) {
  background-color: #2a2a2a;
}

@media (max-width: 768px) {
  .market-overview-container {
    padding: 1rem;
  }

  .card-header {
    flex-direction: column;
    gap: 0.5rem;
    align-items: flex-start;
  }

  .header-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
    width: 100%;
  }

  .header-right {
    width: 100%;
    justify-content: space-between;
  }

  .period-buttons {
    margin-left: 0;
  }

  .chart-container {
    height: 350px;
  }

  .stat-value {
    font-size: 1.25rem;
  }
}
</style>
