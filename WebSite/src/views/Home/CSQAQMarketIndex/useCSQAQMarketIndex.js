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
   * 获取市场指数数据
   */
  const fetchMarketIndexData = async () => {
    dataLoading.value = true
    // console.log('[CSQAQ] 开始获取市场指数...')

    try {
      const response = await fetch(apiUrls.csqaqMarketIndex())
      const result = await response.json()

      // console.log('[CSQAQ] API 响应:', result)

      if (result.code === 200 && result.data) {
        // 新的数据结构包含两个API的响应
        // result.data.market_index - 历史数据
        // result.data.current_data - 当前所有指数数据

        // 处理market_index数据（历史折线图）
        if (result.data.market_index && result.data.market_index.data) {
          const data = result.data.market_index.data

          // 更新市场指数数据
          marketIndexData.value = {
            now: data.count?.now || 0,
            amplitude: data.count?.amplitude || 0,
            rate: data.count?.rate || 0,
            max_value: data.count?.max_value || 0,
            min_value: data.count?.min_value || 0,
            consecutive_days: data.count?.consecutive_days || 0
          }

          // 解析折线图数据 - 使用 hourly_list（小时数据）
          // 取最新的72小时数据（3天）
          const hourlyList = data.hourly_list || []
          const dataCount = 72 // 3天 = 72小时
          const values = hourlyList.slice(-dataCount)

          // 生成时间戳（假设最新数据是当前时间，往前推算）
          const now = Date.now()
          const timestamps = values.map((_, index) => {
            const hoursAgo = values.length - 1 - index
            return now - hoursAgo * 3600000 // 每小时 3600000 毫秒
          })

          chartData.value = {
            timestamps: timestamps,
            values: values
          }

          // console.log('[CSQAQ] 市场指数获取成功:', marketIndexData.value)
          // console.log('[CSQAQ] 折线图数据获取成功,数据点数量:', chartData.value.values.length)
        }

        // 处理current_data数据（所有指数列表）
        if (result.data.current_data && result.data.current_data.data) {
          const currentData = result.data.current_data.data
          if (currentData.sub_index_data && Array.isArray(currentData.sub_index_data)) {
            indexListData.value = currentData.sub_index_data
            // console.log('[CSQAQ] 指数列表获取成功,数量:', indexListData.value.length)
          }
        }

        // 更新最后更新时间
        lastUpdate.value = new Date()

        // 手动更新图表（使用 nextTick 确保 DOM 已更新）
        // 注意：不在这里初始化图表，由 watch(marketIndexData) 负责初始化
        // 这里只负责在图表已存在的情况下更新数据
        nextTick(() => {
          if (chartInstance && chartData.value && chartData.value.values.length > 0) {
            // console.log('[CSQAQ] 手动触发图表更新')
            updateChart()
          } else {
            // console.log('[CSQAQ] 等待 watch 监听器初始化图表')
          }
        })

        ElMessage.success('CSQAQ市场指数数据已更新')
      } else {
        console.error('[CSQAQ] 获取失败:', result.message)
        ElMessage.error('获取市场指数失败: ' + (result.message || '未知错误'))
      }
    } catch (error) {
      console.error('[CSQAQ] 请求失败:', error)
      ElMessage.error('网络请求失败: ' + error.message)
    } finally {
      dataLoading.value = false
    }
  }


  // 监听 marketIndexData 变化,确保容器渲染后初始化图表
  watch(marketIndexData, (newData) => {
    if (newData) {
      // console.log('[CSQAQ] marketIndexData 已加载,准备初始化图表')
      nextTick(() => {
        // console.log('[CSQAQ] DOM 更新后,chartContainer.value:', !!chartContainer.value)
        if (chartContainer.value && !chartInstance) {
          // console.log('[CSQAQ] 容器已就绪,初始化图表')
          const initSuccess = initChart()
          // 如果初始化成功且数据已存在,立即更新图表
          if (initSuccess && chartData.value && chartData.value.values && chartData.value.values.length > 0) {
            // console.log('[CSQAQ] 数据已存在,立即更新图表')
            updateChart()
          }
        } else if (!chartContainer.value) {
          // console.warn('[CSQAQ] 容器尚未渲染到 DOM')
        } else if (chartInstance) {
          // console.log('[CSQAQ] 图表实例已存在，跳过初始化')
        }
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
    chartContainer,
    lastUpdate,
    indexListData,

    // 方法
    fetchMarketIndexData
  }
}
