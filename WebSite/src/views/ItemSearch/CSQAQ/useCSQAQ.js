import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { apiUrls } from '@/config/api.js'

/**
 * CSQAQ 单件饰品图表与详情逻辑
 * @param {import('vue').ComputedRef|import('vue').Ref} chartWeapon - 当前选中的武器（来自 yyypCurrentWeapon 或 buffCurrentWeapon）
 * @param {import('vue').Ref} showYYYPList
 * @param {import('vue').Ref} showBuffList
 * @param {{ onStatisticLoaded?: (value: number) => void }} [options] - 存世量加载完成后回调（用于表头展示）
 */
export function useCSQAQ(chartWeapon, showYYYPList, showBuffList, options = {}) {
  const { onStatisticLoaded } = options
  const chartGoodId = ref(null)
  const chartData = ref(null)
  const chartLoading = ref(false)
  const goodDetail = ref(null)
  const goodDetailLoading = ref(false)
  const chartKey = ref('sell_price')
  const chartPlatform = ref(2)
  const chartPeriod = ref(30)
  const chartStyle = ref('all_style')
  const chartViewMode = ref('line') // line | kline | chips
  const csqaqChartRef = ref(null)
  let csqaqChartInstance = null
  const klineData = ref(null)
  const klineLoading = ref(false)
  // K 线图专用：周期默认日线，平台默认 BUFF
  const klinePeriod = ref('1d')   // 1h | 4h | 1d | 1w
  const klinePlatform = ref(1)   // 1 BUFF, 2 悠悠有品
  const chipData = ref(null)    // 获利筹码 chipData：{ low, high, avg, volume, date }
  const chipLoading = ref(false)
  const chipSummary = ref(null) // 获利筹码汇总 { profitRatio, avgCost, p90Low, p90High, concentration }，供控制栏同一行展示
  const statisticData = ref(null)
  const statisticLoading = ref(false)
  const statisticChartRef = ref(null)
  let statisticChartInstance = null
  const statisticDialogVisible = ref(false)

  const CHART_KEY_OPTIONS_ALL = [
    { value: 'sell_price', label: '出售价' },
    { value: 'buy_price', label: '求购价' },
    { value: 'sell_num', label: '在售数量' },
    { value: 'buy_num', label: '求购数量' },
    { value: 'short_lease_price', label: '短租租金' },
    { value: 'long_lease_price', label: '长租租金' },
    { value: 'lease_annual', label: '短租收益率' },
    { value: 'long_lease_annual', label: '长租收益率' },
    { value: 'lease_num', label: '在租数量' },
    { value: 'turnover_number', label: '日成交量' },
    { value: 'transfer_price', label: '租赁过户价' }
  ]
  const KEY_BY_PLATFORM = {
    1: ['sell_price', 'buy_price', 'sell_num', 'buy_num'],
    2: ['sell_price', 'buy_price', 'sell_num', 'buy_num', 'short_lease_price', 'long_lease_price', 'lease_annual', 'long_lease_annual', 'lease_num', 'transfer_price'],
    3: ['sell_price', 'buy_price', 'sell_num', 'buy_num', 'turnover_number']
  }
  const CHART_KEY_OPTIONS = computed(() => {
    const allowed = KEY_BY_PLATFORM[chartPlatform.value] || KEY_BY_PLATFORM[1]
    return CHART_KEY_OPTIONS_ALL.filter(opt => allowed.includes(opt.value))
  })
  const CHART_PLATFORM_OPTIONS = [
    { value: 1, label: 'BUFF' },
    { value: 2, label: '悠悠有品' },
    { value: 3, label: 'Steam' }
  ]
  const CHART_PERIOD_OPTIONS = [
    { value: 7, label: '近7天' },
    { value: 15, label: '近15天' },
    { value: 30, label: '近1月' },
    { value: 90, label: '近3月' },
    { value: 180, label: '近6月' },
    { value: 365, label: '近1年' },
    { value: 1095, label: '近3年' }
  ]
  const CHART_STYLE_OPTIONS = [
    { value: 'all_style', label: '全部' },
    { value: 'Phase1', label: 'P1' },
    { value: 'Phase2', label: 'P2' },
    { value: 'Phase3', label: 'P3' },
    { value: 'Phase4', label: 'P4' },
    { value: 'Sapphire', label: '蓝宝石' },
    { value: 'Ruby', label: '红宝石' },
    { value: 'Black Pearl', label: '黑珍珠' },
    { value: 'Emerald', label: '绿宝石' }
  ]

  const showChartStyleSelect = computed(() =>
    (chartWeapon.value?.market_listing_item_name || '').includes('多普勒')
  )

  const CHART_VIEW_MODES = [
    { value: 'line', label: '走势图' },
    { value: 'kline', label: 'K 线图' },
    { value: 'chips', label: '获利筹码' }
  ]
  const KLINE_PERIOD_OPTIONS = [
    { value: '1h', label: '1小时' },
    { value: '4h', label: '4小时' },
    { value: '1d', label: '日线' },
    { value: '1w', label: '周线' }
  ]
  const KLINE_PLATFORM_OPTIONS = [
    { value: 1, label: 'BUFF' },
    { value: 2, label: '悠悠有品' }
  ]

  watch(chartPlatform, (platform) => {
    const allowed = KEY_BY_PLATFORM[platform] || KEY_BY_PLATFORM[1]
    if (!allowed.includes(chartKey.value)) chartKey.value = 'sell_price'
  })

  const getGoodIdForChart = async (marketListingItemName) => {
    if (!marketListingItemName) return null
    try {
      const response = await fetch(apiUrls.weaponCsqaqId(), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ market_listing_item_name: marketListingItemName })
      })
      if (!response.ok) return null
      const result = await response.json()
      return result.success && result.csqaq_id ? result.csqaq_id : null
    } catch (e) {
      console.error('getGoodIdForChart:', e)
      return null
    }
  }

  const fetchGoodDetail = async (goodId) => {
    if (goodId == null) {
      goodDetail.value = null
      return
    }
    goodDetailLoading.value = true
    goodDetail.value = null
    try {
      const url = apiUrls.csqaqWeaponInfoGood(goodId)
      const response = await fetch(url, { method: 'GET', headers: { 'Accept': 'application/json' } })
      if (!response.ok) {
        goodDetail.value = null
        return
      }
      const res = await response.json()
      if (res.code === 200 && res.data) goodDetail.value = res
      else goodDetail.value = null
    } catch (e) {
      console.error('fetchGoodDetail:', e)
      goodDetail.value = null
    } finally {
      goodDetailLoading.value = false
    }
  }

  const fetchChartData = async () => {
    const weapon = chartWeapon.value
    const weaponName = weapon?.market_listing_item_name || weapon?.item_name || weapon?.steam_hash_name
    if (!weaponName) {
      chartData.value = null
      clearChartInstance()
      return
    }
    chartLoading.value = true
    chartData.value = null
    try {
      let goodId = chartGoodId.value
      if (goodId == null) {
        goodId = await getGoodIdForChart(weaponName)
        chartGoodId.value = goodId
      }
      if (goodId == null) {
        ElMessage.warning('未找到该饰品的 CSQAQ ID，无法加载图表')
        clearChartInstance()
        goodDetail.value = null
        statisticData.value = null
        return
      }
      // 加载顺序：1) 左侧详情 2) 右侧图表 3) 存世量；每步完成即展示
      if (!goodDetail.value) await fetchGoodDetail(goodId)
      chartLoading.value = true
      chartData.value = null
      const response = await fetch(apiUrls.csqaqWeaponInfoChart(), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          good_id: goodId,
          key: chartKey.value,
          platform: chartPlatform.value,
          period: chartPeriod.value,
          style: chartStyle.value
        })
      })
      if (response.status === 404) {
        chartData.value = null
        clearChartInstance()
        ElMessage.warning('该数据类型在当前平台不可用，请切换平台或数据类型')
        return
      }
      if (!response.ok) throw new Error('请求失败')
      const res = await response.json()
      if (res.code === 200 && res.data) {
        const data = res.data
        const hasData = data.timestamp?.length > 0 && (data.main_data?.length ?? 0) > 0
        if (hasData) {
          chartData.value = data
          await nextTick()
          renderActiveChart()
        } else {
          chartData.value = null
          clearChartInstance()
        }
      } else {
        chartData.value = null
        clearChartInstance()
        ElMessage.warning(res.msg || '获取图表数据失败')
      }
      if (!statisticData.value?.length) {
        await fetchStatisticData()
        if (statisticData.value?.length && onStatisticLoaded) {
          const last = statisticData.value[statisticData.value.length - 1]
          onStatisticLoaded(last.statistic)
        }
      }
    } catch (e) {
      console.error('fetchChartData:', e)
      chartData.value = null
      clearChartInstance()
      ElMessage.error('加载图表失败')
    } finally {
      chartLoading.value = false
    }
  }

  const clearChartInstance = () => {
    if (csqaqChartInstance) {
      csqaqChartInstance.dispose()
      csqaqChartInstance = null
    }
  }

  const clearStatisticChartInstance = () => {
    if (statisticChartInstance) {
      statisticChartInstance.dispose()
      statisticChartInstance = null
    }
  }

  let chartFetchTimer = null
  const scheduleChartFetch = () => {
    if (chartFetchTimer) clearTimeout(chartFetchTimer)
    chartFetchTimer = setTimeout(() => {
      chartFetchTimer = null
      fetchChartData()
    }, 150)
  }

  const getScaleMinMax = (arr, paddingRatio = 0.08) => {
    const valid = arr.filter(v => v != null && v !== '' && !Number.isNaN(Number(v))).map(Number)
    if (valid.length === 0) return { min: 0, max: 100 }
    const min = Math.min(...valid)
    const max = Math.max(...valid)
    const range = max - min || 1
    const pad = range * paddingRatio
    return { min: min - pad, max: max + pad }
  }

  const renderLineChart = () => {
    if (!csqaqChartRef.value || !chartData.value?.timestamp?.length) return
    const el = csqaqChartRef.value
    const { clientWidth, clientHeight } = el
    if (!clientWidth || !clientHeight) {
      // 容器尚未完成布局，稍后重试
      setTimeout(() => {
        renderActiveChart()
      }, 100)
      return
    }
    clearChartInstance()
    csqaqChartInstance = echarts.init(el)
    const timestamps = chartData.value.timestamp
    const mainData = chartData.value.main_data || []
    const numData = chartData.value.num_data
    const hasNumData = Array.isArray(numData) && numData.length > 0
    const dates = timestamps.map(ts => {
      const d = new Date(ts)
      return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
    })
    const mainMinMax = getScaleMinMax(mainData)
    const series = [{ name: '数值', type: 'line', data: mainData, smooth: true, lineStyle: { width: 2, color: '#409eff' }, itemStyle: { color: '#409eff' }, areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(64, 158, 255, 0.3)' }, { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }] } }, yAxisIndex: 0 }]
    let yAxisOption
    if (hasNumData) {
      series.push({ name: '在售数量', type: 'line', data: numData, smooth: true, lineStyle: { width: 2, color: '#67c23a' }, itemStyle: { color: '#67c23a' }, yAxisIndex: 1 })
      const numMinMax = getScaleMinMax(numData)
      yAxisOption = [
        { type: 'value', min: mainMinMax.min, max: mainMinMax.max, nameTextStyle: { color: '#999' }, axisLine: { lineStyle: { color: '#555' } }, axisLabel: { color: '#999' }, splitLine: { show: false } },
        { type: 'value', min: numMinMax.min, max: numMinMax.max, name: '在售数量', nameTextStyle: { color: '#67c23a' }, axisLine: { lineStyle: { color: '#67c23a' } }, axisLabel: { color: '#999' }, splitLine: { lineStyle: { color: '#333' } } }
      ]
    } else {
      yAxisOption = { type: 'value', min: mainMinMax.min, max: mainMinMax.max, nameTextStyle: { color: '#999' }, axisLine: { lineStyle: { color: '#555' } }, axisLabel: { color: '#999' }, splitLine: { lineStyle: { color: '#333' } } }
    }
    const option = {
      tooltip: { trigger: 'axis', backgroundColor: 'rgba(50,50,50,0.95)', borderColor: '#555', textStyle: { color: '#e0e0e0' } },
      grid: { left: '1%', right: hasNumData ? '6%' : '2%', bottom: '15%', top: '10%', containLabel: true },
      xAxis: { type: 'category', data: dates, boundaryGap: false, axisLine: { lineStyle: { color: '#555' } }, axisLabel: { color: '#999', rotate: 45, interval: 'auto' } },
      yAxis: yAxisOption,
      series
    }
    csqaqChartInstance.setOption(option)
    nextTick(() => { csqaqChartInstance?.resize() })
  }

  const calculateMA = (data, period) => {
    const result = []
    for (let i = 0; i < data.length; i++) {
      if (i < period - 1) {
        result.push('-')
        continue
      }
      let sum = 0
      for (let j = 0; j < period; j++) {
        sum += data[i - j][1]
      }
      result.push((sum / period).toFixed(2))
    }
    return result
  }

  const fetchKlineData = async () => {
    const goodId = chartGoodId.value
    if (goodId == null) {
      klineData.value = []
      return
    }
    klineLoading.value = true
    klineData.value = null
    try {
      const response = await fetch(apiUrls.csqaqWeaponInfoKline(goodId, klinePeriod.value, klinePlatform.value), { method: 'GET', headers: { Accept: 'application/json' } })
      if (!response.ok) throw new Error('请求失败')
      const res = await response.json()
      if (res.code === 200 && Array.isArray(res.data)) {
        klineData.value = res.data.length ? res.data : []
      } else {
        klineData.value = []
      }
    } catch (e) {
      console.error('fetchKlineData:', e)
      klineData.value = []
      ElMessage.error('K线数据加载失败')
    } finally {
      klineLoading.value = false
    }
    await nextTick()
    renderKlineChart()
  }

  const renderKlineChart = () => {
    if (!csqaqChartRef.value) return
    if (!klineData.value?.length && chartGoodId.value != null) {
      fetchKlineData()
      return
    }
    if (!klineData.value?.length) {
      clearChartInstance()
      return
    }
    const el = csqaqChartRef.value
    const { clientWidth, clientHeight } = el
    if (!clientWidth || !clientHeight) {
      setTimeout(renderKlineChart, 100)
      return
    }
    clearChartInstance()
    csqaqChartInstance = echarts.init(el)
    const data = klineData.value
    const times = data.map(item => item.time)
    const klineArr = data.map(item => [
      parseFloat(item.open),
      parseFloat(item.close),
      parseFloat(item.low),
      parseFloat(item.high)
    ])
    const volumeData = data.map((item) => {
      const open = parseFloat(item.open)
      const close = parseFloat(item.close)
      let volume = parseFloat(item.volume || 0)
      if (volume === 0) volume = Math.abs(parseFloat(item.high) - parseFloat(item.low)) * 100
      return { value: volume, isUp: close >= open }
    })
    const ma5 = calculateMA(klineArr, 5)
    const ma10 = calculateMA(klineArr, 10)
    const ma20 = calculateMA(klineArr, 20)
    const option = {
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis', axisPointer: { type: 'cross' }, backgroundColor: 'rgba(50,50,50,0.95)', borderColor: '#555', textStyle: { color: '#e0e0e0' } },
      legend: { data: ['K线', 'MA5', 'MA10', 'MA20'], textStyle: { color: '#999' }, top: 0 },
      grid: [
        { left: '2%', right: '2%', top: '12%', height: '58%', containLabel: true },
        { left: '2%', right: '2%', top: '76%', height: '16%', containLabel: true }
      ],
      xAxis: [
        { type: 'category', data: times, boundaryGap: true, axisLine: { lineStyle: { color: '#555' } }, axisLabel: { color: '#999', show: false }, gridIndex: 0 },
        { type: 'category', data: times, boundaryGap: true, axisLine: { lineStyle: { color: '#555' } }, axisLabel: { color: '#999', rotate: 45 }, gridIndex: 1 }
      ],
      yAxis: [
        { scale: true, splitLine: { lineStyle: { color: '#333' } }, axisLabel: { color: '#999' }, gridIndex: 0 },
        { scale: true, splitLine: { show: false }, axisLabel: { color: '#999', fontSize: 10 }, gridIndex: 1 }
      ],
      dataZoom: [{ type: 'inside', xAxisIndex: [0, 1], start: Math.max(0, (1 - 60 / data.length) * 100), end: 100 }],
      series: [
        { name: 'K线', type: 'candlestick', data: klineArr, itemStyle: { color: '#ef5350', color0: '#00c853', borderColor: '#ef5350', borderColor0: '#00c853' }, xAxisIndex: 0, yAxisIndex: 0 },
        { name: 'MA5', type: 'line', data: ma5, smooth: true, lineStyle: { width: 1, color: '#409eff' }, showSymbol: false, xAxisIndex: 0, yAxisIndex: 0 },
        { name: 'MA10', type: 'line', data: ma10, smooth: true, lineStyle: { width: 1, color: '#e6a23c' }, showSymbol: false, xAxisIndex: 0, yAxisIndex: 0 },
        { name: 'MA20', type: 'line', data: ma20, smooth: true, lineStyle: { width: 1, color: '#909399' }, showSymbol: false, xAxisIndex: 0, yAxisIndex: 0 },
        { name: '成交量', type: 'bar', data: volumeData, itemStyle: { color: (params) => (params.data.isUp ? '#ef5350' : '#00c853') }, xAxisIndex: 1, yAxisIndex: 1 }
      ]
    }
    csqaqChartInstance.setOption(option)
    nextTick(() => { csqaqChartInstance?.resize() })
  }

  const fetchChipData = async () => {
    const goodId = chartGoodId.value
    if (goodId == null) {
      chipData.value = null
      return
    }
    chipLoading.value = true
    chipData.value = null
    try {
      const response = await fetch(apiUrls.csqaqWeaponInfoChipData(goodId), { method: 'GET', headers: { Accept: 'application/json' } })
      if (!response.ok) throw new Error('请求失败')
      const res = await response.json()
      if (res.code === 200 && res.data && (res.data.low?.length || res.data.avg?.length)) {
        chipData.value = res.data
      } else {
        chipData.value = null
      }
    } catch (e) {
      console.error('fetchChipData:', e)
      chipData.value = null
      ElMessage.error('筹码数据加载失败')
    } finally {
      chipLoading.value = false
    }
    await nextTick()
    renderChipsChart()
  }

  const renderChipsChart = () => {
    if (!csqaqChartRef.value) return
    if (!chipData.value && chartGoodId.value != null) {
      fetchChipData()
      return
    }
    if (!chipData.value || !chipData.value.date?.length) {
      chipSummary.value = null
      clearChartInstance()
      return
    }
    const el = csqaqChartRef.value
    const { clientWidth, clientHeight } = el
    if (!clientWidth || !clientHeight) {
      setTimeout(renderChipsChart, 100)
      return
    }
    const raw = chipData.value
    const dates = raw.date || []
    const low = raw.low || []
    const high = raw.high || []
    const avg = raw.avg || []
    const volume = raw.volume || []
    const len = dates.length
    if (!len) {
      clearChartInstance()
      return
    }
    const currentPrice = avg[len - 1] != null ? Number(avg[len - 1]) : (Number(high[len - 1]) + Number(low[len - 1])) / 2
    const priceMin = Math.min(...low.map(Number).filter((n) => !Number.isNaN(n)), currentPrice)
    const priceMax = Math.max(...high.map(Number).filter((n) => !Number.isNaN(n)), currentPrice)
    const range = priceMax - priceMin || 1
    const bucketStep = 1
    const bucketCount = Math.ceil(range / bucketStep) + 1
    const buckets = Array.from({ length: bucketCount }, (_, i) => ({ price: priceMin + i * bucketStep, trapped: 0, profit: 0 }))
    let totalVol = 0
    for (let i = 0; i < len; i++) {
      const lo = Number(low[i])
      const hi = Number(high[i])
      const v = Number(volume[i]) || 0
      const a = Number(avg[i])
      if (Number.isNaN(lo) || Number.isNaN(hi)) continue
      totalVol += v
      const idx = Math.min(bucketCount - 1, Math.floor((a - priceMin) / bucketStep))
      if (idx >= 0 && idx < bucketCount) {
        if (a < currentPrice) buckets[idx].profit += v
        else buckets[idx].trapped += v
      }
    }
    const profitVol = buckets.reduce((s, b) => s + b.profit, 0)
    const profitRatio = totalVol > 0 ? ((profitVol / totalVol) * 100).toFixed(2) : '0'
    const avgCost = totalVol > 0 ? buckets.reduce((s, b) => s + (b.price + bucketStep / 2) * (b.profit + b.trapped), 0) / totalVol : currentPrice
    const sorted = buckets.slice().sort((a, b) => a.price - b.price)
    let acc = 0
    let p90Low = priceMin
    let p90High = priceMax
    for (const b of sorted) {
      const v = b.profit + b.trapped
      acc += v
      if (acc >= totalVol * 0.05) { p90Low = b.price; break }
    }
    acc = 0
    for (let i = sorted.length - 1; i >= 0; i--) {
      acc += sorted[i].profit + sorted[i].trapped
      if (acc >= totalVol * 0.05) { p90High = sorted[i].price + bucketStep; break }
    }
    const concentration = avgCost > 0 ? (((p90High - p90Low) / avgCost) * 100).toFixed(2) : '0'
    chipSummary.value = { profitRatio, avgCost, p90Low, p90High, concentration }

    clearChartInstance()
    csqaqChartInstance = echarts.init(el)
    const priceCenter = (p) => p + bucketStep / 2
    const maxVol = Math.max(1, ...buckets.map((b) => Math.max(b.trapped, b.profit)))
    const trappedBarData = buckets.map((b) => [-b.trapped, priceCenter(b.price)])
    const profitBarData = buckets.map((b) => [b.profit, priceCenter(b.price)])
    const option = {
      backgroundColor: 'transparent',
      title: [
        {
          text: '套牢筹码',
          right: '2%',
          top: 4,
          textStyle: { color: '#67c23a', fontSize: 11 }
        },
        {
          text: '获利筹码',
          right: '2%',
          top: 20,
          textStyle: { color: '#ef5350', fontSize: 11 }
        }
      ],
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, backgroundColor: 'rgba(50,50,50,0.95)', borderColor: '#555', textStyle: { color: '#e0e0e0' } },
      grid: [
        { left: '2%', right: '50%', top: '18%', height: '72%', containLabel: true },
        { left: '50%', right: '4%', top: '18%', height: '72%', containLabel: true }
      ],
      xAxis: [
        { type: 'category', data: dates, boundaryGap: true, axisLine: { lineStyle: { color: '#555' } }, axisLabel: { color: '#999', rotate: 45 }, gridIndex: 0 },
        {
          type: 'value',
          name: '成交量',
          position: 'bottom',
          min: -maxVol,
          max: maxVol,
          axisLine: { lineStyle: { color: '#555' }, onZero: true },
          axisLabel: { color: '#999', formatter: (v) => Math.abs(v) },
          splitLine: { lineStyle: { color: '#333', type: 'dashed' } },
          gridIndex: 1
        }
      ],
      yAxis: [
        {
          type: 'value',
          scale: true,
          name: '价格',
          min: priceMin,
          max: priceMax,
          position: 'right',
          splitLine: { lineStyle: { color: '#333' } },
          axisLine: { lineStyle: { color: '#555' } },
          axisLabel: { color: '#999' },
          gridIndex: 0
        },
        {
          type: 'value',
          scale: true,
          min: priceMin,
          max: priceMax,
          position: 'left',
          gridIndex: 1,
          axisLine: { show: false },
          axisLabel: { show: false },
          splitLine: { show: false }
        }
      ],
      series: [
        { name: '价格', type: 'line', data: avg.map(Number), symbol: 'none', lineStyle: { color: '#6b9fff', width: 2 }, xAxisIndex: 0, yAxisIndex: 0 },
        { name: '套牢筹码', type: 'bar', data: trappedBarData, itemStyle: { color: '#67c23a' }, barGap: '-100%', barCategoryGap: '0%', barMaxWidth: 3, xAxisIndex: 1, yAxisIndex: 1 },
        { name: '获利筹码', type: 'bar', data: profitBarData, itemStyle: { color: '#ef5350' }, barGap: '-100%', barCategoryGap: '0%', barMaxWidth: 3, xAxisIndex: 1, yAxisIndex: 1 }
      ]
    }
    csqaqChartInstance.setOption(option)
    nextTick(() => { csqaqChartInstance?.resize() })
  }

  const renderActiveChart = () => {
    if (chartViewMode.value === 'kline') {
      renderKlineChart()
      return
    }
    if (chartViewMode.value === 'chips') {
      renderChipsChart()
      return
    }
    if (!chartData.value?.timestamp?.length) {
      clearChartInstance()
      return
    }
    renderLineChart()
  }

  const fetchStatisticData = async () => {
    const goodId = chartGoodId.value
    if (goodId == null) {
      statisticData.value = null
      clearStatisticChartInstance()
      return
    }
    statisticLoading.value = true
    statisticData.value = null
    try {
      const response = await fetch(apiUrls.csqaqWeaponInfoStatistic(goodId), { method: 'GET', headers: { Accept: 'application/json' } })
      if (!response.ok) {
        statisticData.value = null
        return
      }
      const res = await response.json()
      if (res.code === 200 && Array.isArray(res.data)) {
        statisticData.value = res.data
      } else {
        statisticData.value = null
      }
    } catch (e) {
      console.error('fetchStatisticData:', e)
      statisticData.value = null
    } finally {
      statisticLoading.value = false
    }
  }

  const renderStatisticChart = () => {
    if (!statisticChartRef.value || !statisticData.value?.length) return
    const el = statisticChartRef.value
    const { clientWidth, clientHeight } = el
    if (!clientWidth || !clientHeight) {
      setTimeout(() => {
        renderStatisticChart()
      }, 100)
      return
    }
    clearStatisticChartInstance()
    statisticChartInstance = echarts.init(el)
    const dates = statisticData.value.map(item => {
      const d = new Date(item.created_at)
      return `${d.getMonth() + 1}/${d.getDate()}`
    })
    const values = statisticData.value.map(item => item.statistic)
    const minMax = getScaleMinMax(values)
    const option = {
      title: { text: '存世量走势（近180天）', left: 'center', top: 4, textStyle: { fontSize: 12, color: '#999' } },
      tooltip: { trigger: 'axis', backgroundColor: 'rgba(50,50,50,0.95)', borderColor: '#555', textStyle: { color: '#e0e0e0' } },
      grid: { left: '2%', right: '2%', bottom: '12%', top: '14%', containLabel: true },
      xAxis: { type: 'category', data: dates, boundaryGap: false, axisLine: { lineStyle: { color: '#555' } }, axisLabel: { color: '#999', rotate: 45, interval: 'auto' } },
      yAxis: { type: 'value', min: minMax.min, max: minMax.max, name: '存世量', nameTextStyle: { color: '#999' }, axisLine: { lineStyle: { color: '#555' } }, axisLabel: { color: '#999' }, splitLine: { lineStyle: { color: '#333' } } },
      series: [{ name: '存世量', type: 'line', data: values, smooth: true, lineStyle: { width: 2, color: '#e6a23c' }, itemStyle: { color: '#e6a23c' }, areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(230, 162, 60, 0.3)' }, { offset: 1, color: 'rgba(230, 162, 60, 0.05)' }] } } }]
    }
    statisticChartInstance.setOption(option)
    nextTick(() => { statisticChartInstance?.resize() })
  }

  const openStatisticDialog = async () => {
    if (!chartGoodId.value) return
    if (!statisticData.value || !statisticData.value.length) {
      await fetchStatisticData()
    }
    statisticDialogVisible.value = true
    await nextTick()
    if (statisticData.value && statisticData.value.length) {
      renderStatisticChart()
    }
  }

  // 只要有 chartWeapon 就加载对应饰品；flush: 'post' 确保 DOM 已渲染后再请求
  const shouldLoadChart = computed(() => !!chartWeapon.value)
  watch(shouldLoadChart, (yes) => {
    if (yes) {
      chartGoodId.value = null
      chartData.value = null
      klineData.value = null
      chipData.value = null
      chipSummary.value = null
      goodDetail.value = null
      statisticData.value = null
      clearChartInstance()
      clearStatisticChartInstance()
      scheduleChartFetch()
    }
  }, { immediate: true, flush: 'post' })

  watch(chartWeapon, (weapon) => {
    chartGoodId.value = null
    chartData.value = null
    klineData.value = null
    chipData.value = null
    chipSummary.value = null
    goodDetail.value = null
    statisticData.value = null
    clearChartInstance()
    clearStatisticChartInstance()
    if (weapon) {
      scheduleChartFetch()
      if (chartViewMode.value === 'kline') scheduleKlineFetch()
      if (chartViewMode.value === 'chips') scheduleChipFetch()
    }
  }, { immediate: true })

  watch([chartKey, chartPlatform, chartPeriod, chartStyle], () => {
    if (chartWeapon.value && chartGoodId.value != null) scheduleChartFetch()
  })

  watch([klinePeriod, klinePlatform], () => {
    if (chartViewMode.value === 'kline' && chartWeapon.value && chartGoodId.value != null) scheduleKlineFetch()
  })

  watch(chartViewMode, () => {
    if (chartViewMode.value === 'chips' && chartWeapon.value && chartGoodId.value != null) scheduleChipFetch()
  })

  let klineFetchTimer = null
  const scheduleKlineFetch = () => {
    if (klineFetchTimer) clearTimeout(klineFetchTimer)
    klineFetchTimer = setTimeout(() => {
      klineFetchTimer = null
      fetchKlineData()
    }, 150)
  }

  let chipFetchTimer = null
  const scheduleChipFetch = () => {
    if (chipFetchTimer) clearTimeout(chipFetchTimer)
    chipFetchTimer = setTimeout(() => {
      chipFetchTimer = null
      fetchChipData()
    }, 150)
  }

  const selectGoodDetailButton = (btn) => {
    if (!btn || btn.current) return
    chartGoodId.value = btn.id
    fetchGoodDetail(btn.id)
    scheduleChartFetch()
  }

  const formatPrice = (v) => {
    if (v == null || v === '') return '-'
    const n = Number(v)
    return Number.isNaN(n) ? String(v) : n.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 2 })
  }
  const formatRate = (v) => {
    if (v == null || v === '') return '-'
    const n = Number(v)
    return Number.isNaN(n) ? String(v) : n.toFixed(2)
  }
  const getRateClass = (v) => {
    if (v == null) return ''
    const n = Number(v)
    if (Number.isNaN(n)) return ''
    return n > 0 ? 'rate-up' : n < 0 ? 'rate-down' : ''
  }
  const formatUpdatedAt = (s) => {
    if (!s) return '-'
    try {
      const d = new Date(s)
      return Number.isNaN(d.getTime()) ? s : `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
    } catch {
      return s
    }
  }
  const formatDecimal = (v) => (v == null || v === '') ? '-' : (Number.isNaN(Number(v)) ? String(v) : Number(v).toFixed(2))

  const hasTodayStat = (g) => g && (g.sell_price_rate_1 != null || g.sell_price_1 != null)
  const hasWeekStat = (g) => g && (g.sell_price_rate_7 != null || g.sell_price_7 != null)
  const getTodayDir = (g) => (g?.sell_price_rate_1 != null && Number(g.sell_price_rate_1) >= 0) ? '↑' : '↓'
  const getWeekDir = (g) => (g?.sell_price_rate_7 != null && Number(g.sell_price_rate_7) >= 0) ? '↑' : '↓'
  const formatTodayOverviewValue = (g) => {
    const amount = g.sell_price_1
    const rate = g.sell_price_rate_1
    const amountStr = amount != null ? `¥${Number(amount).toFixed(1)}` : ''
    const rateStr = rate != null ? ` (${formatRate(rate)}%)` : ''
    return `${amountStr}${rateStr}`.trim() || '-'
  }
  const formatWeekOverviewValue = (g) => {
    const amount = g.sell_price_7
    const rate = g.sell_price_rate_7
    const amountStr = amount != null ? `¥${Number(amount).toFixed(0)}` : ''
    const rateStr = rate != null ? ` (${formatRate(rate)}%)` : ''
    return `${amountStr}${rateStr}`.trim() || '-'
  }

  const hasBuffData = (g) => g && (g.buff_sell_price != null || g.buff_buy_price != null)
  const hasYyypData = (g) => g && (g.yyyp_sell_price != null || g.yyyp_buy_price != null)
  const hasSteamData = (g) => g && (g.steam_sell_price != null || g.steam_buy_price != null)
  const hasR8Data = (g) => g && (g.r8_sell_price != null || g.r8_sell_num != null)
  const isYyypPriceLow = (g) => {
    if (!g || g.yyyp_sell_price == null) return false
    const yyyp = Number(g.yyyp_sell_price)
    const buff = g.buff_sell_price != null ? Number(g.buff_sell_price) : null
    const steam = g.steam_sell_price != null && g.steam_sell_price > 0 ? Number(g.steam_sell_price) : null
    return (buff != null && yyyp < buff) || (steam != null && yyyp < steam)
  }
  const hasYyypLeaseData = (g) => g && (g.yyyp_lease_price != null || g.yyyp_long_lease_price != null || g.yyyp_lease_num != null)
  const hasSteamConversionData = (g) => g && (g.steam_buff_buy_conversion != null || g.turnover_number != null || g.turnover_avg_price != null)

  const handleChartResize = () => {
    csqaqChartInstance?.resize()
    statisticChartInstance?.resize()
  }

  watch(chartViewMode, () => {
    if (chartData.value?.timestamp?.length) {
      nextTick().then(() => {
        renderActiveChart()
      })
    }
  })

  onMounted(() => {
    window.addEventListener('resize', handleChartResize)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', handleChartResize)
    clearChartInstance()
    clearStatisticChartInstance()
  })

  return {
    chartGoodId,
    chartData,
    chartLoading,
    klineData,
    klineLoading,
    chipData,
    chipLoading,
    chipSummary,
    goodDetail,
    goodDetailLoading,
    chartKey,
    chartPlatform,
    chartPeriod,
    chartStyle,
    chartViewMode,
    csqaqChartRef,
    showChartStyleSelect,
    klinePeriod,
    klinePlatform,
    KLINE_PERIOD_OPTIONS,
    KLINE_PLATFORM_OPTIONS,
    CHART_KEY_OPTIONS,
    CHART_PLATFORM_OPTIONS,
    CHART_PERIOD_OPTIONS,
    CHART_STYLE_OPTIONS,
    CHART_VIEW_MODES,
    fetchChartData,
    fetchKlineData,
    fetchChipData,
    selectGoodDetailButton,
    formatPrice,
    formatRate,
    formatDecimal,
    getRateClass,
    formatUpdatedAt,
    hasTodayStat,
    hasWeekStat,
    getTodayDir,
    getWeekDir,
    formatTodayOverviewValue,
    formatWeekOverviewValue,
    hasBuffData,
    hasYyypData,
    hasSteamData,
    hasR8Data,
    isYyypPriceLow,
    hasYyypLeaseData,
    hasSteamConversionData,
    statisticData,
    statisticLoading,
    statisticChartRef,
    statisticDialogVisible,
    openStatisticDialog
  }
}
