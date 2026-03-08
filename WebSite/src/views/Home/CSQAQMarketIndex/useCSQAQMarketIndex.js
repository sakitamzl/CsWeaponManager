import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { apiUrls } from '@/config/api.js'

export function useCSQAQMarketIndex() {
  // 状态
  const dataLoading = ref(false)

  // 数据
  const marketIndexData = ref(null)
  const chartData = ref(null)  // 折线图数据 { timestamps, values }
  const lastUpdate = ref(null)  // 最后更新时间
  const indexListData = ref([])  // 所有指数列表数据

  // 图表相关
  const chartContainer = ref(null)
  let chartInstance = null

  /**
   * 初始化图表(小型迷你图表)
   */
  const initChart = () => {
    if (!chartContainer.value) {
      // console.log('[CSQAQ] chartContainer 未找到')
      return false
    }

    // console.log('[CSQAQ] 初始化图表...')

    // 销毁旧实例
    if (chartInstance) {
      // console.log('[CSQAQ] 销毁旧图表实例')
      chartInstance.dispose()
    }

    // 创建新实例
    chartInstance = echarts.init(chartContainer.value)
    // console.log('[CSQAQ] 图表实例已创建')

    // 设置初始配置 - 迷你图表样式
    const option = {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(50, 50, 50, 0.9)',
        borderColor: '#409eff',
        borderWidth: 1,
        textStyle: {
          color: '#fff',
          fontSize: 12
        },
        axisPointer: {
          type: 'line',
          lineStyle: {
            color: '#409eff',
            width: 1,
            type: 'solid'
          }
        },
        formatter: function(params) {
          const point = params[0]
          return `${point.name}<br/>${point.seriesName}: ${point.value}`
        }
      },
      grid: {
        left: '0',
        right: '0',
        bottom: '0',
        top: '0',
        containLabel: false
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        show: false, // 隐藏X轴
        data: []
      },
      yAxis: {
        type: 'value',
        show: false, // 隐藏Y轴
        scale: true
      },
      series: [
        {
          name: '市场指数',
          type: 'line',
          smooth: true,
          symbol: 'none',
          sampling: 'lttb',
          lineStyle: {
            color: '#409eff',
            width: 1.5
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              {
                offset: 0,
                color: 'rgba(64, 158, 255, 0.3)'
              },
              {
                offset: 1,
                color: 'rgba(64, 158, 255, 0.05)'
              }
            ])
          },
          data: []
        }
      ]
    }

    chartInstance.setOption(option)
    // console.log('[CSQAQ] 图表配置已设置')

    // 监听窗口大小变化
    window.addEventListener('resize', handleResize)

    return true
  }

  /**
   * 更新图表数据
   */
  const updateChart = () => {
    // console.log('[CSQAQ] updateChart 调用 - chartInstance:', !!chartInstance, 'chartData:', !!chartData.value)

    if (!chartInstance) {
      // console.log('[CSQAQ] 图表实例不存在,无法更新')
      return
    }

    if (!chartData.value) {
      // console.log('[CSQAQ] 图表数据为空,无法更新')
      return
    }

    // chartData 结构: { timestamps: [...], values: [...] }
    const { timestamps, values } = chartData.value

    if (!timestamps || !values || timestamps.length !== values.length) {
      // console.log('[CSQAQ] 数据格式错误')
      return
    }

    const dataLength = values.length
    const dates = []
    const markLineData = [] // 日期分界线数据
    let lastDate = null

    // 遍历时间戳，生成索引和分界线
    for (let i = 0; i < dataLength; i++) {
      const date = new Date(timestamps[i])
      const dateStr = `${date.getMonth() + 1}/${date.getDate()}`

      // X轴使用索引，不显示时间
      dates.push(i.toString())

      // 检测日期变化，添加分界线
      if (lastDate && lastDate !== dateStr) {
        markLineData.push({
          xAxis: i,
          label: {
            show: true,
            position: 'end',
            formatter: dateStr,
            fontSize: 10,
            color: '#909399'
          },
          lineStyle: {
            type: 'dashed',
            color: 'rgba(144, 147, 153, 0.3)',
            width: 1
          }
        })
      }

      lastDate = dateStr
    }

    // console.log('[CSQAQ] 准备设置数据 - dates:', dates.length, 'values:', values.length)
    // console.log('[CSQAQ] 数值范围:', { min: Math.min(...values), max: Math.max(...values) })
    // console.log('[CSQAQ] 日期分界线数量:', markLineData.length)

    // 更新图表
    chartInstance.setOption({
      xAxis: {
        data: dates
      },
      series: [
        {
          data: values,
          markLine: {
            symbol: 'none', // 不显示箭头
            silent: true, // 不响应鼠标事件
            data: markLineData
          }
        }
      ]
    })
    chartInstance.resize()

    // console.log('[CSQAQ] 图表已更新,数据点数量:', values.length)
  }

  /**
   * 处理窗口大小变化
   */
  const handleResize = () => {
    if (chartInstance) {
      chartInstance.resize()
    }
  }

  /**
   * 获取市场指数数据：指数 API + 折线 API 分别请求，返回一个就显示一个
   */
  const fetchMarketIndexData = async () => {
    dataLoading.value = true
    let indexOk = false
    let chartOk = false

    const applyIndex = (result) => {
      if (result.code !== 200 || !result.data) return
      const currentData = result.data.current_data?.data ?? result.data
      const subIndexList = currentData.sub_index_data && Array.isArray(currentData.sub_index_data)
        ? currentData.sub_index_data
        : []
      indexListData.value = subIndexList
      const initIndex = subIndexList.find(item => item.name_key === 'init') || subIndexList[0]
      if (initIndex) {
        marketIndexData.value = {
          now: initIndex.market_index ?? 0,
          amplitude: initIndex.chg_num ?? 0,
          rate: initIndex.chg_rate ?? 0,
          max_value: initIndex.high ?? 0,
          min_value: initIndex.low ?? 0,
          consecutive_days: 0
        }
      }
      lastUpdate.value = new Date()
      indexOk = true
    }

    const applyChart = (result) => {
      if (result.code !== 200 || !result.data?.market_index?.data) return
      const data = result.data.market_index.data
      const hourlyList = data.hourly_list || []
      const dataCount = 24
      const values = hourlyList.slice(-dataCount)
      const timestamps = data.timestamp && data.timestamp.length >= values.length
        ? data.timestamp.slice(-dataCount)
        : values.map((_, i) => Date.now() - (values.length - 1 - i) * 3600000)
      chartData.value = { timestamps, values }
      lastUpdate.value = new Date()
      chartOk = true
      nextTick(() => {
        if (chartInstance && chartData.value?.values?.length) {
          updateChart()
          if (chartInstance) chartInstance.resize()
        }
      })
    }

    // 先请求折线图，返回后立即结束 loading、先显示折线图，再请求指数
    try {
      const chartRes = await fetch(apiUrls.csqaqChartData()).then(r => r.json())
      applyChart(chartRes)
      dataLoading.value = false
    } catch (err) {
      console.error('[CSQAQ] 折线图 API 失败:', err)
      ElMessage.error('折线图数据请求失败: ' + (err.message || '未知错误'))
      dataLoading.value = false
    }
    try {
      const indexRes = await fetch(apiUrls.csqaqIndexData()).then(r => r.json())
      applyIndex(indexRes)
    } catch (err) {
      console.error('[CSQAQ] 指数 API 失败:', err)
      ElMessage.error('指数数据请求失败: ' + (err.message || '未知错误'))
    }
    if (indexOk || chartOk) ElMessage.success('CSQAQ市场指数数据已更新')

    // 数据加载完成后再次确保折线图渲染：DOM 已显示（marketIndexData 已设），此时补初始化/更新
    await nextTick()
    if (chartContainer.value && chartData.value?.values?.length) {
      if (!chartInstance) {
        initChart()
      }
      if (chartInstance) {
        updateChart()
        chartInstance.resize()
      }
    }
  }


  // 监听 marketIndexData 变化,确保容器渲染后初始化图表
  watch(marketIndexData, (newData) => {
    if (newData) {
      nextTick(() => {
        nextTick(() => {
          if (chartContainer.value && !chartInstance) {
            const initSuccess = initChart()
            if (initSuccess && chartData.value?.values?.length) {
              updateChart()
              if (chartInstance) chartInstance.resize()
            }
          } else if (chartInstance && chartData.value?.values?.length) {
            updateChart()
            chartInstance.resize()
          }
        })
      })
    }
  })

  // 监听 chartData 变化,更新图表数据
  watch(chartData, (newData) => {
    // console.log('[CSQAQ] chartData 变化,数据点:', newData?.values?.length)
    if (!newData || !newData.values || newData.values.length === 0) {
      // console.log('[CSQAQ] 数据为空,跳过更新')
      return
    }

    nextTick(() => {
      // 如果图表还没初始化,先检查容器并初始化
      if (!chartInstance) {
        // console.log('[CSQAQ] 图表未初始化,先检查容器')
        if (chartContainer.value) {
          // console.log('[CSQAQ] 容器存在,尝试初始化图表')
          const initSuccess = initChart()
          if (!initSuccess) {
            // console.warn('[CSQAQ] 图表初始化失败，无法更新数据')
            return
          }
        } else {
          // console.log('[CSQAQ] 容器不存在,等待 marketIndexData 加载触发容器渲染')
          return
        }
      }
      // 更新图表数据
      // console.log('[CSQAQ] 准备更新图表数据')
      updateChart()
    })
  })

  // 组件挂载时
  onMounted(() => {
    // console.log('[CSQAQ] 组件已挂载')
    // 自动获取数据(不在这里初始化图表,等待数据加载后再初始化)
    fetchMarketIndexData()
  })

  // 组件卸载时
  onUnmounted(() => {
    // 移除窗口大小监听
    window.removeEventListener('resize', handleResize)

    // 销毁图表实例
    if (chartInstance) {
      chartInstance.dispose()
      chartInstance = null
    }
  })

  return {
    // 状态
    dataLoading,
    marketIndexData,
    chartData,
    chartContainer,
    lastUpdate,
    indexListData,

    // 方法
    fetchMarketIndexData
  }
}
