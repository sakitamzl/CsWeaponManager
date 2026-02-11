import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { apiUrls } from '@/config/api.js'

export function useCSQAQMarketIndex() {
  const dataLoading = ref(false)
  const marketIndexData = ref(null)
  const chartContainer = ref(null)
  let chart = null
  let refreshTimer = null

  // 获取市场指数数据
  const fetchMarketIndexData = async () => {
    dataLoading.value = true
    try {
      const response = await fetch(apiUrls.csqaqMarketIndex())
      const result = await response.json()

      if (result.code === 200 && result.data) {
        const data = result.data

        // 更新市场指数数据
        marketIndexData.value = {
          now: data.count?.now || 0,
          amplitude: data.count?.amplitude || 0,
          rate: data.count?.rate || 0,
          max_value: data.count?.max_value || 0,
          min_value: data.count?.min_value || 0,
          consecutive_days: data.count?.consecutive_days || 0
        }

        // 绘制折线图
        if (data.hourly_list && data.hourly_list.length > 0) {
          renderMiniChart(data.hourly_list)
        }
      }
    } catch (error) {
      console.error('获取CSQAQ市场指数失败:', error)
    } finally {
      dataLoading.value = false
    }
  }

  // 绘制小型折线图
  const renderMiniChart = (hourlyData) => {
    if (!chartContainer.value) return

    if (!chart) {
      chart = echarts.init(chartContainer.value)
    }

    // 生成时间标签（最近N小时）
    const timeLabels = hourlyData.map((_, index) => `${index}h`)

    const option = {
      grid: {
        left: 0,
        right: 0,
        top: 5,
        bottom: 5,
        containLabel: false
      },
      xAxis: {
        type: 'category',
        data: timeLabels,
        show: false,
        boundaryGap: false
      },
      yAxis: {
        type: 'value',
        show: false,
        scale: true
      },
      series: [
        {
          type: 'line',
          data: hourlyData,
          smooth: true,
          showSymbol: false,
          lineStyle: {
            width: 2,
            color: marketIndexData.value.rate >= 0 ? '#67c23a' : '#f56c6c'
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                {
                  offset: 0,
                  color: marketIndexData.value.rate >= 0
                    ? 'rgba(103, 194, 58, 0.3)'
                    : 'rgba(245, 108, 108, 0.3)'
                },
                {
                  offset: 1,
                  color: marketIndexData.value.rate >= 0
                    ? 'rgba(103, 194, 58, 0)'
                    : 'rgba(245, 108, 108, 0)'
                }
              ]
            }
          }
        }
      ]
    }

    chart.setOption(option)
  }

  // 自动刷新数据（每5分钟）
  const startAutoRefresh = () => {
    refreshTimer = setInterval(() => {
      fetchMarketIndexData()
    }, 5 * 60 * 1000) // 5分钟
  }

  // 处理窗口大小变化
  const handleResize = () => {
    if (chart) {
      chart.resize()
    }
  }

  onMounted(() => {
    fetchMarketIndexData()
    startAutoRefresh()
    window.addEventListener('resize', handleResize)
  })

  onUnmounted(() => {
    if (refreshTimer) {
      clearInterval(refreshTimer)
    }
    if (chart) {
      chart.dispose()
      chart = null
    }
    window.removeEventListener('resize', handleResize)
  })

  return {
    dataLoading,
    marketIndexData,
    chartContainer
  }
}
