import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, WarningFilled } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import axios from 'axios'
import { apiUrls } from '@/config/api'

export function useMarketOverview() {
  const loading = ref(false)
  const loadingSteamDT = ref(false)
  const loadingCSQAQ = ref(false)
  const chartRefSteamDT = ref(null)
  const chartRefCSQAQ = ref(null)
  const lastUpdateTime = ref('')
  const statsDataSteamDT = ref(null)
  const statsDataCSQAQ = ref(null)
  let chartInstanceSteamDT = null
  let chartInstanceCSQAQ = null
  
  const queryForm = reactive({
    period: '1h'
  })
  
  // 初始化图表
  const initChart = (chartRef, chartInstance) => {
    if (!chartRef) return null
    
    const instance = echarts.init(chartRef, 'dark', {
      renderer: 'canvas',
      useDirtyRect: true
    })
    
    const option = {
      backgroundColor: 'transparent',
      animation: true,
      animationDuration: 300,  // 减少动画时间
      animationEasing: 'cubicOut',
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
          link: [{ xAxisIndex: 'all' }]
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
        },
        top: '0%'
      },
      axisPointer: {
        link: [{ xAxisIndex: 'all' }]
      },
      grid: [
        {
          left: '3%',
          right: '3%',
          top: '10%',
          height: '60%',
          containLabel: true
        },
        {
          left: '3%',
          right: '3%',
          top: '75%',
          height: '18%',
          containLabel: true
        }
      ],
      xAxis: [
        {
          type: 'category',
          data: [],
          boundaryGap: true,
          axisLine: {
            lineStyle: {
              color: '#3a3a3a'
            }
          },
          axisLabel: {
            show: false
          },
          gridIndex: 0
        },
        {
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
          },
          gridIndex: 1
        }
      ],
      yAxis: [
        {
          scale: true,
          splitLine: {
            lineStyle: {
              color: '#3a3a3a'
            }
          },
          axisLabel: {
            color: '#b0b0b0'
          },
          gridIndex: 0
        },
        {
          scale: true,
          splitLine: {
            show: false
          },
          axisLabel: {
            color: '#b0b0b0',
            fontSize: 10
          },
          gridIndex: 1,
          splitNumber: 3
        }
      ],
      dataZoom: [
        {
          type: 'inside',
          start: 0,
          end: 100,
          zoomOnMouseWheel: true,  // 启用鼠标滚轮缩放
          moveOnMouseMove: true,   // 启用鼠标拖拽平移
          moveOnMouseWheel: false  // 禁用滚轮平移（只用于缩放）
        }
      ],
      series: [
        {
          name: 'K线',
          type: 'candlestick',
          data: [],
          itemStyle: {
            color: '#ef5350',      // 上涨红色
            color0: '#00c853',     // 下跌绿色
            borderColor: '#ef5350', // 上涨边框红色
            borderColor0: '#00c853' // 下跌边框绿色
          },
          xAxisIndex: 0,
          yAxisIndex: 0
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
          showSymbol: false,
          xAxisIndex: 0,
          yAxisIndex: 0
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
          showSymbol: false,
          xAxisIndex: 0,
          yAxisIndex: 0
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
          showSymbol: false,
          xAxisIndex: 0,
          yAxisIndex: 0
        },
        {
          name: '成交量',
          type: 'bar',
          data: [],
          itemStyle: {
            color: function(params) {
              // 根据涨跌设置颜色
              return params.data.isUp ? '#ef5350' : '#00c853'
            }
          },
          xAxisIndex: 1,
          yAxisIndex: 1
        }
      ]
    }
    
    instance.setOption(option)
    return instance
  }
  
  // 初始化所有图表
  const initAllCharts = () => {
    if (chartRefSteamDT.value) {
      chartInstanceSteamDT = initChart(chartRefSteamDT.value, chartInstanceSteamDT)
    }
    if (chartRefCSQAQ.value) {
      chartInstanceCSQAQ = initChart(chartRefCSQAQ.value, chartInstanceCSQAQ)
    }
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
  
  // 获取 SteamDT 数据
  const fetchSteamDTData = async () => {
    // SteamDT 不支持 4小时线
    if (queryForm.period === '4h') {
      return
    }
    
    loadingSteamDT.value = true
    try {
      const response = await axios.get(apiUrls.steamdtKline(), {
        params: {
          period: queryForm.period
        }
      })
      
      if (response.data && response.data.code === 200) {
        const data = response.data.data
        updateChart(data, chartInstanceSteamDT, 'SteamDT')
        updateStats(data, 'SteamDT')
      } else {
        throw new Error(response.data.message || 'SteamDT数据加载失败')
      }
    } catch (error) {
      console.error('获取SteamDT数据失败:', error)
      ElMessage.error('获取SteamDT数据失败: ' + (error.message || '请检查网络连接'))
    } finally {
      loadingSteamDT.value = false
    }
  }
  
  // 获取 CSQAQ 数据
  const fetchCSQAQData = async () => {
    loadingCSQAQ.value = true
    try {
      const response = await axios.get(apiUrls.csqaqKline(), {
        params: {
          period: queryForm.period
        }
      })
      
      if (response.data && response.data.code === 200) {
        const data = response.data.data
        updateChart(data, chartInstanceCSQAQ, 'CSQAQ')
        updateStats(data, 'CSQAQ')
      } else {
        throw new Error(response.data.message || 'CSQAQ数据加载失败')
      }
    } catch (error) {
      console.error('获取CSQAQ数据失败:', error)
      ElMessage.error('获取CSQAQ数据失败: ' + (error.message || '请检查网络连接'))
    } finally {
      loadingCSQAQ.value = false
    }
  }
  
  // 获取所有数据
  const fetchAllData = async () => {
    loading.value = true
    await Promise.all([
      fetchSteamDTData(),
      fetchCSQAQData()
    ])
    lastUpdateTime.value = new Date().toLocaleString('zh-CN')
    loading.value = false
    ElMessage.success('数据加载成功')
  }
  
  // 更新图表
  const updateChart = (data, chartInstance, dataSource) => {
    if (!chartInstance || !data || data.length === 0) return
    
    const times = data.map(item => item.time)
    const klineData = data.map(item => [
      parseFloat(item.open),
      parseFloat(item.close),
      parseFloat(item.low),
      parseFloat(item.high)
    ])
    
    // 计算成交量数据（根据涨跌设置颜色）
    // 如果API返回的成交量都是0，则使用价格波动幅度作为成交量的视觉表示
    const volumeData = data.map((item, index) => {
      const open = parseFloat(item.open)
      const close = parseFloat(item.close)
      const high = parseFloat(item.high)
      const low = parseFloat(item.low)
      let volume = parseFloat(item.volume || 0)
      
      // 如果成交量为0，使用价格波动幅度 (high - low) 作为替代
      if (volume === 0) {
        volume = Math.abs(high - low) * 100  // 放大100倍以便显示
      }
      
      return {
        value: volume,
        isUp: close >= open
      }
    })
    
    const ma5 = calculateMA(klineData, 5)
    const ma10 = calculateMA(klineData, 10)
    const ma20 = calculateMA(klineData, 20)
    
    // 找出当前可见范围内K线的最高点和最低点
    const findVisibleExtremes = (startPercent, endPercent) => {
      const totalCount = klineData.length
      const startIndex = Math.floor(totalCount * startPercent / 100)
      const endIndex = Math.ceil(totalCount * endPercent / 100)
      
      let maxValue = -Infinity
      let minValue = Infinity
      let maxIndex = 0
      let minIndex = 0
      
      for (let i = startIndex; i < endIndex && i < klineData.length; i++) {
        const high = klineData[i][3]  // high价格
        const low = klineData[i][2]   // low价格
        
        if (high > maxValue) {
          maxValue = high
          maxIndex = i
        }
        if (low < minValue) {
          minValue = low
          minIndex = i
        }
      }
      
      return { maxValue, minValue, maxIndex, minIndex }
    }
    
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
    
    // 计算初始可见范围的K线极值
    const extremes = findVisibleExtremes(startPercent, endPercent)
    
    // 创建K线标记点数据 - 使用简单的箭头符号
    const markPointData = [
      {
        name: '最高',
        coord: [extremes.maxIndex, extremes.maxValue],
        value: extremes.maxValue.toFixed(2),
        symbol: 'arrow',
        symbolSize: 20,
        symbolRotate: 180,  // 向下
        itemStyle: {
          color: '#ef5350'
        },
        label: {
          show: true,
          position: 'top',
          formatter: '{c}',
          color: '#ef5350',
          fontSize: 12,
          fontWeight: 'bold',
          distance: 15
        }
      },
      {
        name: '最低',
        coord: [extremes.minIndex, extremes.minValue],
        value: extremes.minValue.toFixed(2),
        symbol: 'arrow',
        symbolSize: 20,
        symbolRotate: 0,  // 向上
        itemStyle: {
          color: '#00c853'
        },
        label: {
          show: true,
          position: 'bottom',
          formatter: '{c}',
          color: '#00c853',
          fontSize: 12,
          fontWeight: 'bold',
          distance: 15
        }
      }
    ]
    
    chartInstance.setOption({
      xAxis: [
        {
          data: times
        },
        {
          data: times
        }
      ],
      dataZoom: [
        {
          type: 'inside',
          xAxisIndex: [0, 1],
          start: startPercent,
          end: endPercent,
          zoomOnMouseWheel: true,
          moveOnMouseMove: true,
          moveOnMouseWheel: false,
          throttle: 50  // 节流，减少更新频率
        }
      ],
      series: [
        {
          data: klineData,
          markPoint: {
            data: markPointData,
            animation: false  // 标记点不需要动画
          }
        },
        {
          data: ma5
        },
        {
          data: ma10
        },
        {
          data: ma20
        },
        {
          data: volumeData
        }
      ]
    }, false, true)  // notMerge: false, lazyUpdate: true
    
    // 监听dataZoom事件，当缩放或平移时更新K线标记点
    chartInstance.off('dataZoom')
    chartInstance.on('dataZoom', (params) => {
      const option = chartInstance.getOption()
      const dataZoom = option.dataZoom[0]
      const newExtremes = findVisibleExtremes(dataZoom.start, dataZoom.end)
      
      const newMarkPointData = [
        {
          name: '最高',
          coord: [newExtremes.maxIndex, newExtremes.maxValue],
          value: newExtremes.maxValue.toFixed(2),
          symbol: 'arrow',
          symbolSize: 20,
          symbolRotate: 180,
          itemStyle: {
            color: '#ef5350'
          },
          label: {
            show: true,
            position: 'top',
            formatter: '{c}',
            color: '#ef5350',
            fontSize: 12,
            fontWeight: 'bold',
            distance: 15
          }
        },
        {
          name: '最低',
          coord: [newExtremes.minIndex, newExtremes.minValue],
          value: newExtremes.minValue.toFixed(2),
          symbol: 'arrow',
          symbolSize: 20,
          symbolRotate: 0,
          itemStyle: {
            color: '#00c853'
          },
          label: {
            show: true,
            position: 'bottom',
            formatter: '{c}',
            color: '#00c853',
            fontSize: 12,
            fontWeight: 'bold',
            distance: 15
          }
        }
      ]
      
      chartInstance.setOption({
        series: [
          {
            markPoint: {
              data: newMarkPointData,
              animation: false
            }
          }
        ]
      }, { notMerge: false, lazyUpdate: true })
    })
  }
  
  // 更新统计信息
  const updateStats = (data, dataSource) => {
    if (!data || data.length === 0) return
    
    const latest = parseFloat(data[data.length - 1].close)
    const previous = parseFloat(data[data.length - 2]?.close || data[0].close)
    const change = ((latest - previous) / previous * 100).toFixed(2)
    
    const prices = data.map(item => parseFloat(item.high))
    const high = Math.max(...prices).toFixed(2)
    const low = Math.min(...data.map(item => parseFloat(item.low))).toFixed(2)
    
    const stats = {
      latest: latest.toFixed(2),
      change: parseFloat(change),
      high,
      low
    }
    
    if (dataSource === 'SteamDT') {
      statsDataSteamDT.value = stats
    } else if (dataSource === 'CSQAQ') {
      statsDataCSQAQ.value = stats
    }
  }
  
  // 周期变化处理
  const changePeriod = (period) => {
    queryForm.period = period
    fetchAllData()
  }
  
  // 窗口大小变化处理
  const handleResize = () => {
    if (chartInstanceSteamDT) {
      chartInstanceSteamDT.resize()
    }
    if (chartInstanceCSQAQ) {
      chartInstanceCSQAQ.resize()
    }
  }
  
  onMounted(async () => {
    await nextTick()
    initAllCharts()
    fetchAllData()
    window.addEventListener('resize', handleResize)
  })
  
  onUnmounted(() => {
    if (chartInstanceSteamDT) {
      chartInstanceSteamDT.dispose()
    }
    if (chartInstanceCSQAQ) {
      chartInstanceCSQAQ.dispose()
    }
    window.removeEventListener('resize', handleResize)
  })

  return {
    loading,
    loadingSteamDT,
    loadingCSQAQ,
    chartRefSteamDT,
    chartRefCSQAQ,
    lastUpdateTime,
    statsDataSteamDT,
    statsDataCSQAQ,
    queryForm,
    changePeriod,
    fetchAllData,
    Refresh,
    WarningFilled
  }
}
