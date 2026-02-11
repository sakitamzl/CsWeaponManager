import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import axios from 'axios'
import { API_CONFIG, apiUrls } from '@/config/api.js'
import * as echarts from 'echarts'


export function useHome() {
  const buyStats = ref({
    totalAmount: '0.00',
    totalCount: 0
  })
  const sellStats = ref({
    totalAmount: '0.00',
    totalCount: 0
  })
  const inventoryStats = ref({
    totalCount: 0,
    total_price: '0.00',
    yyyp_price: '0.00',
    yyyp_diff: '0.00',
    buff_price: '0.00',
    buff_diff: '0.00',
    steam_price: '0.00',
    steam_diff: '0.00'
  })
  const componentStats = ref({
    totalCount: 0,
    yyyp_price: '0.00',
    buff_price: '0.00',
    steam_price: '0.00'
  })
  
  // 计算总库存数量（库存 + 组件）
  const totalInventoryCount = computed(() => {
    return (inventoryStats.value?.totalCount || 0) + (componentStats.value?.totalCount || 0)
  })

  // 计算总悠悠有品价格（库存 + 组件）
  const totalYyypPrice = computed(() => {
    const inventoryPrice = parseFloat(inventoryStats.value?.yyyp_price || 0)
    const componentPrice = parseFloat(componentStats.value?.yyyp_price || 0)
    return (inventoryPrice + componentPrice).toFixed(2)
  })

  // 计算总悠悠有品价差（库存）
  const totalYyypDiff = computed(() => {
    return inventoryStats.value?.yyyp_diff || '0.00'
  })

  // 计算总BUFF价格（库存 + 组件）
  const totalBuffPrice = computed(() => {
    const inventoryPrice = parseFloat(inventoryStats.value?.buff_price || 0)
    const componentPrice = parseFloat(componentStats.value?.buff_price || 0)
    return (inventoryPrice + componentPrice).toFixed(2)
  })

  // 计算总BUFF价差（库存）
  const totalBuffDiff = computed(() => {
    return inventoryStats.value?.buff_diff || '0.00'
  })
  const steamIdList = ref([])
  const selectedSteamId = ref('')
  const selectedInventorySteamId = ref('all') // 库存图表的Steam ID选择
  const selectedComponentSteamId = ref('all') // 组件图表的Steam ID选择
  const selectedBuySteamId = ref('all') // 购入图表的Steam ID选择
  const selectedSellSteamId = ref('all') // 出售图表的Steam ID选择
  const inventoryChartRef = ref(null)
  const componentChartRef = ref(null)
  const buyChartRef = ref(null)
  const sellChartRef = ref(null)
  const csqaqChartRef = ref(null)
  let inventoryChart = null
  let componentChart = null
  let buyChart = null
  let sellChart = null
  let csqaqChart = null

  // 图表模式切换
  const inventoryChartMode = ref('value') // 'value' 或 'count'
  const componentChartMode = ref('value') // 'value' 或 'count'
  const buyChartMode = ref('value') // 'value' 或 'count'
  const sellChartMode = ref('value') // 'value' 或 'count'


  // CSQAQ K线图相关
  const csqaqPeriod = ref('1h')
  const loadingCSQAQ = ref(false)
  
  // 数据源选择
  const dataSource = ref('inventory') // 'inventory' 或 'components'
  
  // 饰品列表相关
  const itemListVisible = ref(false)
  const selectedRange = ref('')
  const filteredItems = ref([])
  const displayedItems = ref([])
  const allInventoryData = ref([])
  const allComponentsData = ref([])
  const allBuyData = ref([])
  const allSellData = ref([])
  const dialogScrollRef = ref(null)
  const loadingMore = ref(false)
  const pageSize = 50
  const currentDisplayPage = ref(1)

  // 图表统计数据
  const inventoryChartStats = ref({
    totalCount: 0,
    totalValue: '0.00'
  })
  const componentChartStats = ref({
    totalCount: 0,
    totalValue: '0.00'
  })
  const buyChartStats = ref({
    totalCount: 0,
    totalValue: '0.00'
  })
  const sellChartStats = ref({
    totalCount: 0,
    totalValue: '0.00'
  })

  // 加载购买统计数据
  const loadBuyStats = async () => {
    try {
      const response = await axios.get(`${API_CONFIG.BASE_URL}/webBuyV1/getBuyStats`)
      if (response.data) {
        buyStats.value = {
          totalAmount: response.data.total_amount?.toFixed(2) || '0.00',
          totalCount: response.data.total_count || 0
        }
      }
    } catch (error) {
      console.error('加载购买统计失败:', error)
      // 保持默认值
      buyStats.value = {
        totalAmount: '0.00',
        totalCount: 0
      }
    }
  }

  // 加载出售统计数据
  const loadSellStats = async () => {
    try {
      const response = await axios.get(`${API_CONFIG.BASE_URL}/webSellV1/getSellStats`)
      if (response.data) {
        sellStats.value = {
          totalAmount: response.data.total_amount?.toFixed(2) || '0.00',
          totalCount: response.data.total_count || 0
        }
      }
    } catch (error) {
      console.error('加载出售统计失败:', error)
      // 保持默认值
      sellStats.value = {
        totalAmount: '0.00',
        totalCount: 0
      }
    }
  }

  // 加载Steam ID列表
  const loadSteamIdList = async () => {
    try {
      const response = await axios.get(`${API_CONFIG.BASE_URL}/webInventoryV1/steam_ids`)
      if (response.data.success && response.data.data.length > 0) {
        steamIdList.value = response.data.data
        selectedSteamId.value = steamIdList.value[0].steamID
      }
    } catch (error) {
      console.error('加载Steam ID列表失败:', error)
    }
  }

  // 加载库存统计数据
  const loadInventoryStats = async (steamId = null) => {
    try {
      let inventoryData = []
      
      if (!steamId || steamId === 'all') {
        // 使用新的API获取所有数据
        const response = await axios.get(apiUrls.homeInventoryAll())
        if (response.data.success) {
          inventoryData = response.data.data
        }
      } else {
        // 获取指定Steam ID的数据
        const response = await axios.get(
          `${API_CONFIG.BASE_URL}/webInventoryV1/inventory/${steamId}`,
          {
            params: {
              limit: 999999,
              offset: 0
            }
          }
        )
        if (response.data.success) {
          inventoryData = response.data.data
        }
      }
      
      // 根据选择的Steam ID过滤数据
      if (steamId && steamId !== 'all') {
        inventoryData = inventoryData.filter(item => item.data_user === steamId)
      }
      
      allInventoryData.value = inventoryData // 保存完整数据用于后续筛选
      
      // 计算统计数据（仅在加载全部数据时更新顶部统计卡片）
      if (!steamId || steamId === 'all') {
        let totalCount = inventoryData.length
        let buy_total = 0
        let yyyp_total = 0
        let buff_total = 0
        let buff_total_after_fee = 0
        let steam_total = 0
        
        inventoryData.forEach(item => {
          if (item.buy_price) {
            const price = parseFloat(item.buy_price)
            if (!isNaN(price)) {
              buy_total += price
            }
          }
          if (item.yyyp_price) {
            const price = parseFloat(item.yyyp_price)
            if (!isNaN(price)) {
              yyyp_total += price
            }
          }
          if (item.buff_price) {
            const price = parseFloat(item.buff_price)
            if (!isNaN(price)) {
              buff_total += price
              buff_total_after_fee += price * 0.975
            }
          }
          if (item.steam_price) {
            const price = parseFloat(item.steam_price)
            if (!isNaN(price)) {
              steam_total += price
            }
          }
        })
        
        inventoryStats.value = {
          totalCount: totalCount,
          total_price: buy_total.toFixed(2),
          yyyp_price: yyyp_total.toFixed(2),
          yyyp_diff: (yyyp_total - buy_total).toFixed(2),
          buff_price: buff_total_after_fee.toFixed(2),
          buff_diff: (buff_total_after_fee - buy_total).toFixed(2),
          steam_price: steam_total.toFixed(2),
          steam_diff: (steam_total - buy_total).toFixed(2)
        }
      }

      // 加载价格区间分析图表
      await loadInventoryChart(inventoryData)
      
      // 计算图表统计数据
      let totalCount = inventoryData.length
      let totalValue = 0
      inventoryData.forEach(item => {
        if (item.buy_price) {
          const price = parseFloat(item.buy_price)
          if (!isNaN(price)) {
            totalValue += price
          }
        }
      })
      inventoryChartStats.value = {
        totalCount: totalCount,
        totalValue: totalValue.toFixed(2)
      }
    } catch (error) {
      console.error('加载库存统计失败:', error)
      // 保持默认值
      if (!steamId || steamId === 'all') {
        inventoryStats.value = {
          totalCount: 0,
          total_price: '0.00',
          yyyp_price: '0.00',
          yyyp_diff: '0.00',
          buff_price: '0.00',
          buff_diff: '0.00',
          steam_price: '0.00',
          steam_diff: '0.00'
        }
      }
      inventoryChartStats.value = {
        totalCount: 0,
        totalValue: '0.00'
      }
    }
  }

  // 加载库存组件统计数据
  const loadComponentsStats = async (steamId = null) => {
    try {
      let componentsData = []

      if (!steamId || steamId === 'all') {
        // 使用新的API获取所有数据
        const response = await axios.get(apiUrls.homeComponentsAll())
        if (response.data.success) {
          componentsData = response.data.data
        }
      } else {
        // 获取指定Steam ID的数据
        const response = await axios.get(
          `${API_CONFIG.BASE_URL}/webStockComponentsV1/components/${steamId}`,
          {
            params: {
              search: '',
              page: 1,
              page_size: 999999
            }
          }
        )
        if (response.data.success) {
          componentsData = response.data.data
        }
      }

      // 根据选择的Steam ID过滤数据
      if (steamId && steamId !== 'all') {
        componentsData = componentsData.filter(item => item.data_user === steamId)
      }

      allComponentsData.value = componentsData // 保存完整数据用于后续筛选

      // 加载库存组件价格区间分析图表
      await loadComponentChart(componentsData)

      // 计算图表统计数据
      let totalCount = componentsData.length
      let totalValue = 0
      componentsData.forEach(item => {
        if (item.buy_price) {
          const price = parseFloat(item.buy_price)
          if (!isNaN(price)) {
            totalValue += price
          }
        }
      })
      componentChartStats.value = {
        totalCount: totalCount,
        totalValue: totalValue.toFixed(2)
      }

      // 更新顶部统计卡片的组件数量和价格（仅在加载全部数据时）
      if (!steamId || steamId === 'all') {
        let yyyp_total = 0
        let buff_total = 0
        let steam_total = 0

        componentsData.forEach(item => {
          if (item.yyyp_price) {
            const price = parseFloat(item.yyyp_price)
            if (!isNaN(price)) {
              yyyp_total += price
            }
          }
          if (item.buff_price) {
            const price = parseFloat(item.buff_price)
            if (!isNaN(price)) {
              buff_total += price * 0.975 // BUFF 手续费
            }
          }
          if (item.steam_price) {
            const price = parseFloat(item.steam_price)
            if (!isNaN(price)) {
              steam_total += price
            }
          }
        })

        componentStats.value = {
          totalCount: totalCount,
          yyyp_price: yyyp_total.toFixed(2),
          buff_price: buff_total.toFixed(2),
          steam_price: steam_total.toFixed(2)
        }
      }
    } catch (error) {
      console.error('加载库存组件统计失败:', error)
      // 保持默认值
      if (!steamId || steamId === 'all') {
        componentStats.value = {
          totalCount: 0,
          yyyp_price: '0.00',
          buff_price: '0.00',
          steam_price: '0.00'
        }
      }
      componentChartStats.value = {
        totalCount: 0,
        totalValue: '0.00'
      }
    }
  }

  // 加载购入列表图表数据
  const loadBuyChartData = async (steamId = null) => {
    try {
      let buyData = []
      
      if (!steamId || steamId === 'all') {
        // 使用新的API获取所有数据
        const response = await axios.get(apiUrls.homeBuyAll())
        if (response.data.success) {
          buyData = response.data.data
        }
      } else {
        // 获取指定Steam ID的数据 - 需要从全部数据中过滤
        const response = await axios.get(apiUrls.homeBuyAll())
        if (response.data.success) {
          buyData = response.data.data.filter(item => item.data_user === steamId)
        }
      }
      
      allBuyData.value = buyData // 保存完整数据用于后续筛选
      
      // 加载购入价格区间分析图表
      await loadBuyChart(buyData)
      
      // 计算图表统计数据
      let totalCount = buyData.length
      let totalValue = 0
      buyData.forEach(item => {
        if (item.buy_price) {
          const price = parseFloat(item.buy_price)
          if (!isNaN(price)) {
            totalValue += price
          }
        }
      })
      buyChartStats.value = {
        totalCount: totalCount,
        totalValue: totalValue.toFixed(2)
      }
    } catch (error) {
      console.error('加载购入数据失败:', error)
    }
  }

  // 加载出售列表图表数据
  const loadSellChartData = async (steamId = null) => {
    try {
      let sellData = []
      
      if (!steamId || steamId === 'all') {
        // 使用新的API获取所有数据
        const response = await axios.get(apiUrls.homeSellAll())
        if (response.data.success) {
          sellData = response.data.data
        }
      } else {
        // 获取指定Steam ID的数据 - 需要从全部数据中过滤
        const response = await axios.get(apiUrls.homeSellAll())
        if (response.data.success) {
          sellData = response.data.data.filter(item => item.data_user === steamId)
        }
      }
      
      allSellData.value = sellData // 保存完整数据用于后续筛选
      
      // 加载出售价格区间分析图表
      await loadSellChart(sellData)
      
      // 计算图表统计数据
      let totalCount = sellData.length
      let totalValue = 0
      sellData.forEach(item => {
        if (item.sell_price) {
          const price = parseFloat(item.sell_price)
          if (!isNaN(price)) {
            totalValue += price
          }
        }
      })
      sellChartStats.value = {
        totalCount: totalCount,
        totalValue: totalValue.toFixed(2)
      }
    } catch (error) {
      console.error('加载出售数据失败:', error)
    }
  }

  // 根据价格区间筛选饰品（组合相同的饰品）
  const filterItemsByRange = (rangeName) => {
    const priceRanges = {
      '¥0-100': { min: 0, max: 100 },
      '¥101-500': { min: 101, max: 500 },
      '¥501-1000': { min: 501, max: 1000 },
      '¥1001-2000': { min: 1001, max: 2000 },
      '¥2001-5000': { min: 2001, max: 5000 },
      '¥5001-10000': { min: 5001, max: 10000 },
      '¥10001-20000': { min: 10001, max: 20000 },
      '¥20001+': { min: 20001, max: Infinity }
    }

    const range = priceRanges[rangeName]
    if (!range) return []

    const filtered = allInventoryData.value.filter(item => {
      if (item.buy_price) {
        const price = parseFloat(item.buy_price)
        return !isNaN(price) && price >= range.min && price <= range.max
      }
      return false
    })

    // 组合相同的饰品
    return groupItems(filtered)
  }

  // 根据价格区间筛选库存组件（组合相同的组件）
  const filterComponentsByRange = (rangeName) => {
    const priceRanges = {
      '¥0-100': { min: 0, max: 100 },
      '¥101-500': { min: 101, max: 500 },
      '¥501-1000': { min: 501, max: 1000 },
      '¥1001-2000': { min: 1001, max: 2000 },
      '¥2001-5000': { min: 2001, max: 5000 },
      '¥5001-10000': { min: 5001, max: 10000 },
      '¥10001-20000': { min: 10001, max: 20000 },
      '¥20001+': { min: 20001, max: Infinity }
    }

    const range = priceRanges[rangeName]
    if (!range) return []

    const filtered = allComponentsData.value.filter(item => {
      if (item.buy_price) {
        const price = parseFloat(item.buy_price)
        return !isNaN(price) && price >= range.min && price <= range.max
      }
      return false
    })

    // 组合相同的组件
    return groupItems(filtered)
  }

  // 根据价格区间筛选购入饰品（组合相同的饰品）
  const filterBuyItemsByRange = (rangeName) => {
    const priceRanges = {
      '¥0-100': { min: 0, max: 100 },
      '¥101-500': { min: 101, max: 500 },
      '¥501-1000': { min: 501, max: 1000 },
      '¥1001-2000': { min: 1001, max: 2000 },
      '¥2001-5000': { min: 2001, max: 5000 },
      '¥5001-10000': { min: 5001, max: 10000 },
      '¥10001-20000': { min: 10001, max: 20000 },
      '¥20001+': { min: 20001, max: Infinity }
    }

    const range = priceRanges[rangeName]
    if (!range) return []

    const filtered = allBuyData.value.filter(item => {
      if (item.buy_price) {
        const price = parseFloat(item.buy_price)
        return !isNaN(price) && price >= range.min && price <= range.max
      }
      return false
    })

    // 组合相同的饰品
    return groupItems(filtered)
  }

  // 根据价格区间筛选出售饰品（组合相同的饰品）
  const filterSellItemsByRange = (rangeName) => {
    const priceRanges = {
      '¥0-100': { min: 0, max: 100 },
      '¥101-500': { min: 101, max: 500 },
      '¥501-1000': { min: 501, max: 1000 },
      '¥1001-2000': { min: 1001, max: 2000 },
      '¥2001-5000': { min: 2001, max: 5000 },
      '¥5001-10000': { min: 5001, max: 10000 },
      '¥10001-20000': { min: 10001, max: 20000 },
      '¥20001+': { min: 20001, max: Infinity }
    }

    const range = priceRanges[rangeName]
    if (!range) return []

    const filtered = allSellData.value.filter(item => {
      if (item.sell_price) {
        const price = parseFloat(item.sell_price)
        return !isNaN(price) && price >= range.min && price <= range.max
      }
      return false
    })

    // 组合相同的饰品
    return groupItems(filtered)
  }

  // 组合相同的饰品/组件
  const groupItems = (items) => {
    const grouped = {}
    
    items.forEach(item => {
      // 使用 steam_hash_name 作为分组键
      const key = item.steam_hash_name || item.item_name
      
      if (!grouped[key]) {
        grouped[key] = {
          ...item,
          count: 1,
          items: [item]
        }
      } else {
        grouped[key].count++
        grouped[key].items.push(item)
        
        // 累加价格
        if (item.buy_price) {
          grouped[key].buy_price = (parseFloat(grouped[key].buy_price || 0) + parseFloat(item.buy_price)).toFixed(2)
        }
        if (item.yyyp_price) {
          grouped[key].yyyp_price = (parseFloat(grouped[key].yyyp_price || 0) + parseFloat(item.yyyp_price)).toFixed(2)
        }
        if (item.buff_price) {
          grouped[key].buff_price = (parseFloat(grouped[key].buff_price || 0) + parseFloat(item.buff_price)).toFixed(2)
        }
        if (item.steam_price) {
          grouped[key].steam_price = (parseFloat(grouped[key].steam_price || 0) + parseFloat(item.steam_price)).toFixed(2)
        }
      }
    })
    
    return Object.values(grouped)
  }

  // 获取组合后的商品标题
  const getItemTitle = (item) => {
    const weaponName = (item.weapon_name || '').trim()
    const itemName = (item.item_name || '').trim()
    const parts = []

    if (weaponName && itemName) {
      if (weaponName === itemName) {
        parts.push(itemName)
      } else {
        parts.push(weaponName)
        parts.push(itemName)
      }
    } else if (weaponName) {
      parts.push(weaponName)
    } else if (itemName) {
      parts.push(itemName)
    }

    let title = parts.join(' | ')
    if (item.float_range) {
      title += ` （${item.float_range}）`
    }
    return title
  }

  // 加载库存图表
  const loadInventoryChart = async (inventoryData) => {
    await nextTick()
    
    if (!inventoryChartRef.value) return

    // 定义价格区间
    const priceRanges = [
      { name: '0-100', min: 0, max: 100, count: 0, totalValue: 0 },
      { name: '101-500', min: 101, max: 500, count: 0, totalValue: 0 },
      { name: '501-1000', min: 501, max: 1000, count: 0, totalValue: 0 },
      { name: '1001-2000', min: 1001, max: 2000, count: 0, totalValue: 0 },
      { name: '2001-5000', min: 2001, max: 5000, count: 0, totalValue: 0 },
      { name: '5001-10000', min: 5001, max: 10000, count: 0, totalValue: 0 },
      { name: '10001-20000', min: 10001, max: 20000, count: 0, totalValue: 0 },
      { name: '20001+', min: 20001, max: Infinity, count: 0, totalValue: 0 }
    ]

    // 统计每个价格区间的数量和总价值
    inventoryData.forEach(item => {
      if (item.buy_price) {
        const price = parseFloat(item.buy_price)
        if (!isNaN(price)) {
          for (let range of priceRanges) {
            if (price >= range.min && price <= range.max) {
              range.count++
              range.totalValue += price
              break
            }
          }
        }
      }
    })

    // 根据模式选择数据
    const isValueMode = inventoryChartMode.value === 'value'
    const chartData = priceRanges
      .filter(range => range.count > 0)
      .map(range => ({
        name: `¥${range.name}`,
        value: isValueMode ? range.totalValue : range.count,
        count: range.count,
        totalValue: range.totalValue,
        avgPrice: range.totalValue / range.count
      }))

    // 初始化或更新图表
    if (!inventoryChart) {
      inventoryChart = echarts.init(inventoryChartRef.value)
      
      // 添加点击事件
      inventoryChart.on('click', (params) => {
        if (params.componentType === 'series') {
          selectedRange.value = params.name
          filteredItems.value = filterItemsByRange(params.name)
          initDisplayedItems()
          itemListVisible.value = true
        }
      })
    }

    const option = {
      tooltip: {
        trigger: 'item',
        formatter: (params) => {
          const data = params.data
          return `${params.seriesName}<br/>
                  ${params.name}<br/>
                  件数: ${data.count} 件<br/>
                  总价值: ¥${data.totalValue.toFixed(2)}<br/>
                  平均价格: ¥${data.avgPrice.toFixed(2)}<br/>
                  占比: ${params.percent}%`
        },
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        borderColor: '#333',
        textStyle: {
          color: '#fff'
        }
      },
      legend: {
        show: window.innerWidth > 1366,
        orient: 'vertical',
        right: '5%',
        top: 'center',
        textStyle: {
          color: '#fff',
          fontSize: 12
        },
        itemWidth: 25,
        itemHeight: 14,
        itemGap: 10,
        formatter: (name) => {
          const item = chartData.find(d => d.name === name)
          if (item) {
            return isValueMode
              ? `${name}\n${item.count}件 ¥${item.totalValue.toFixed(0)}`
              : `${name}\n${item.count}件`
          }
          return name
        }
      },
      series: [
        {
          name: isValueMode ? '价格区间分布' : '数量区间分布',
          type: 'pie',
          radius: window.innerWidth > 1366 ? ['40%', '70%'] : ['35%', '65%'],
          center: window.innerWidth > 1366 ? ['40%', '50%'] : ['50%', '50%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#1a1a1a',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: (params) => {
              return isValueMode
                ? `${params.name}\n${params.data.count}件\n¥${params.data.totalValue.toFixed(0)}`
                : `${params.name}\n${params.data.count}件`
            },
            color: '#fff',
            fontSize: 11
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 14,
              fontWeight: 'bold'
            },
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          labelLine: {
            show: true,
            lineStyle: {
              color: '#888'
            }
          },
          data: chartData,
          color: [
            '#5470c6',
            '#91cc75',
            '#fac858',
            '#ee6666',
            '#73c0de',
            '#3ba272',
            '#fc8452',
            '#9a60b4'
          ]
        }
      ]
    }

    inventoryChart.setOption(option)
  }

  // 加载库存组件图表
  const loadComponentChart = async (componentsData) => {
    await nextTick()
    
    if (!componentChartRef.value) return

    // 定义价格区间
    const priceRanges = [
      { name: '0-100', min: 0, max: 100, count: 0, totalValue: 0 },
      { name: '101-500', min: 101, max: 500, count: 0, totalValue: 0 },
      { name: '501-1000', min: 501, max: 1000, count: 0, totalValue: 0 },
      { name: '1001-2000', min: 1001, max: 2000, count: 0, totalValue: 0 },
      { name: '2001-5000', min: 2001, max: 5000, count: 0, totalValue: 0 },
      { name: '5001-10000', min: 5001, max: 10000, count: 0, totalValue: 0 },
      { name: '10001-20000', min: 10001, max: 20000, count: 0, totalValue: 0 },
      { name: '20001+', min: 20001, max: Infinity, count: 0, totalValue: 0 }
    ]

    // 统计每个价格区间的数量和总价值
    componentsData.forEach(item => {
      if (item.buy_price) {
        const price = parseFloat(item.buy_price)
        if (!isNaN(price)) {
          for (let range of priceRanges) {
            if (price >= range.min && price <= range.max) {
              range.count++
              range.totalValue += price
              break
            }
          }
        }
      }
    })

    // 根据模式选择数据
    const isValueMode = componentChartMode.value === 'value'
    const chartData = priceRanges
      .filter(range => range.count > 0)
      .map(range => ({
        name: `¥${range.name}`,
        value: isValueMode ? range.totalValue : range.count,
        count: range.count,
        totalValue: range.totalValue,
        avgPrice: range.totalValue / range.count
      }))

    // 初始化或更新图表
    if (!componentChart) {
      componentChart = echarts.init(componentChartRef.value)
      
      // 添加点击事件
      componentChart.on('click', (params) => {
        if (params.componentType === 'series') {
          selectedRange.value = params.name
          filteredItems.value = filterComponentsByRange(params.name)
          initDisplayedItems()
          itemListVisible.value = true
        }
      })
    }

    const option = {
      tooltip: {
        trigger: 'item',
        formatter: (params) => {
          const data = params.data
          return `${params.seriesName}<br/>
                  ${params.name}<br/>
                  件数: ${data.count} 件<br/>
                  总价值: ¥${data.totalValue.toFixed(2)}<br/>
                  平均价格: ¥${data.avgPrice.toFixed(2)}<br/>
                  占比: ${params.percent}%`
        },
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        borderColor: '#333',
        textStyle: {
          color: '#fff'
        }
      },
      legend: {
        show: window.innerWidth > 1366,
        orient: 'vertical',
        right: '5%',
        top: 'center',
        textStyle: {
          color: '#fff',
          fontSize: 12
        },
        itemWidth: 25,
        itemHeight: 14,
        itemGap: 10,
        formatter: (name) => {
          const item = chartData.find(d => d.name === name)
          if (item) {
            return isValueMode
              ? `${name}\n${item.count}件 ¥${item.totalValue.toFixed(0)}`
              : `${name}\n${item.count}件`
          }
          return name
        }
      },
      series: [
        {
          name: isValueMode ? '价格区间分布' : '数量区间分布',
          type: 'pie',
          radius: window.innerWidth > 1366 ? ['40%', '70%'] : ['35%', '65%'],
          center: window.innerWidth > 1366 ? ['40%', '50%'] : ['50%', '50%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#1a1a1a',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: (params) => {
              return isValueMode
                ? `${params.name}\n${params.data.count}件\n¥${params.data.totalValue.toFixed(0)}`
                : `${params.name}\n${params.data.count}件`
            },
            color: '#fff',
            fontSize: 11
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 14,
              fontWeight: 'bold'
            },
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          labelLine: {
            show: true,
            lineStyle: {
              color: '#888'
            }
          },
          data: chartData,
          color: [
            '#5470c6',
            '#91cc75',
            '#fac858',
            '#ee6666',
            '#73c0de',
            '#3ba272',
            '#fc8452',
            '#9a60b4'
          ]
        }
      ]
    }

    componentChart.setOption(option)
  }

  // 加载购入图表
  const loadBuyChart = async (buyData) => {
    await nextTick()
    
    if (!buyChartRef.value) return

    // 定义价格区间
    const priceRanges = [
      { name: '0-100', min: 0, max: 100, count: 0, totalValue: 0 },
      { name: '101-500', min: 101, max: 500, count: 0, totalValue: 0 },
      { name: '501-1000', min: 501, max: 1000, count: 0, totalValue: 0 },
      { name: '1001-2000', min: 1001, max: 2000, count: 0, totalValue: 0 },
      { name: '2001-5000', min: 2001, max: 5000, count: 0, totalValue: 0 },
      { name: '5001-10000', min: 5001, max: 10000, count: 0, totalValue: 0 },
      { name: '10001-20000', min: 10001, max: 20000, count: 0, totalValue: 0 },
      { name: '20001+', min: 20001, max: Infinity, count: 0, totalValue: 0 }
    ]

    // 统计每个价格区间的数量和总价值
    buyData.forEach(item => {
      if (item.buy_price) {
        const price = parseFloat(item.buy_price)
        if (!isNaN(price)) {
          for (let range of priceRanges) {
            if (price >= range.min && price <= range.max) {
              range.count++
              range.totalValue += price
              break
            }
          }
        }
      }
    })

    // 根据模式选择数据
    const isValueMode = buyChartMode.value === 'value'
    const chartData = priceRanges
      .filter(range => range.count > 0)
      .map(range => ({
        name: `¥${range.name}`,
        value: isValueMode ? range.totalValue : range.count,
        count: range.count,
        totalValue: range.totalValue,
        avgPrice: range.totalValue / range.count
      }))

    // 初始化或更新图表
    if (!buyChart) {
      buyChart = echarts.init(buyChartRef.value)
      
      // 添加点击事件
      buyChart.on('click', (params) => {
        if (params.componentType === 'series') {
          selectedRange.value = params.name
          filteredItems.value = filterBuyItemsByRange(params.name)
          initDisplayedItems()
          itemListVisible.value = true
        }
      })
    }

    const option = {
      tooltip: {
        trigger: 'item',
        formatter: (params) => {
          const data = params.data
          return `${params.seriesName}<br/>
                  ${params.name}<br/>
                  件数: ${data.count} 件<br/>
                  总价值: ¥${data.totalValue.toFixed(2)}<br/>
                  平均价格: ¥${data.avgPrice.toFixed(2)}<br/>
                  占比: ${params.percent}%`
        },
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        borderColor: '#333',
        textStyle: {
          color: '#fff'
        }
      },
      legend: {
        show: window.innerWidth > 1366,
        orient: 'vertical',
        right: '5%',
        top: 'center',
        textStyle: {
          color: '#fff',
          fontSize: 12
        },
        itemWidth: 25,
        itemHeight: 14,
        itemGap: 10,
        formatter: (name) => {
          const item = chartData.find(d => d.name === name)
          if (item) {
            return isValueMode
              ? `${name}\n${item.count}件 ¥${item.totalValue.toFixed(0)}`
              : `${name}\n${item.count}件`
          }
          return name
        }
      },
      series: [
        {
          name: isValueMode ? '价格区间分布' : '数量区间分布',
          type: 'pie',
          radius: window.innerWidth > 1366 ? ['40%', '70%'] : ['35%', '65%'],
          center: window.innerWidth > 1366 ? ['40%', '50%'] : ['50%', '50%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#1a1a1a',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: (params) => {
              return isValueMode
                ? `${params.name}\n${params.data.count}件\n¥${params.data.totalValue.toFixed(0)}`
                : `${params.name}\n${params.data.count}件`
            },
            color: '#fff',
            fontSize: 11
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 14,
              fontWeight: 'bold'
            },
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          labelLine: {
            show: true,
            lineStyle: {
              color: '#888'
            }
          },
          data: chartData,
          color: [
            '#5470c6',
            '#91cc75',
            '#fac858',
            '#ee6666',
            '#73c0de',
            '#3ba272',
            '#fc8452',
            '#9a60b4'
          ]
        }
      ]
    }

    buyChart.setOption(option)
  }

  // 加载出售图表
  const loadSellChart = async (sellData) => {
    await nextTick()
    
    if (!sellChartRef.value) return

    // 定义价格区间
    const priceRanges = [
      { name: '0-100', min: 0, max: 100, count: 0, totalValue: 0 },
      { name: '101-500', min: 101, max: 500, count: 0, totalValue: 0 },
      { name: '501-1000', min: 501, max: 1000, count: 0, totalValue: 0 },
      { name: '1001-2000', min: 1001, max: 2000, count: 0, totalValue: 0 },
      { name: '2001-5000', min: 2001, max: 5000, count: 0, totalValue: 0 },
      { name: '5001-10000', min: 5001, max: 10000, count: 0, totalValue: 0 },
      { name: '10001-20000', min: 10001, max: 20000, count: 0, totalValue: 0 },
      { name: '20001+', min: 20001, max: Infinity, count: 0, totalValue: 0 }
    ]

    // 统计每个价格区间的数量和总价值
    sellData.forEach(item => {
      if (item.sell_price) {
        const price = parseFloat(item.sell_price)
        if (!isNaN(price)) {
          for (let range of priceRanges) {
            if (price >= range.min && price <= range.max) {
              range.count++
              range.totalValue += price
              break
            }
          }
        }
      }
    })

    // 根据模式选择数据
    const isValueMode = sellChartMode.value === 'value'
    const chartData = priceRanges
      .filter(range => range.count > 0)
      .map(range => ({
        name: `¥${range.name}`,
        value: isValueMode ? range.totalValue : range.count,
        count: range.count,
        totalValue: range.totalValue,
        avgPrice: range.totalValue / range.count
      }))

    // 初始化或更新图表
    if (!sellChart) {
      sellChart = echarts.init(sellChartRef.value)
      
      // 添加点击事件
      sellChart.on('click', (params) => {
        if (params.componentType === 'series') {
          selectedRange.value = params.name
          filteredItems.value = filterSellItemsByRange(params.name)
          initDisplayedItems()
          itemListVisible.value = true
        }
      })
    }

    const option = {
      tooltip: {
        trigger: 'item',
        formatter: (params) => {
          const data = params.data
          return `${params.seriesName}<br/>
                  ${params.name}<br/>
                  件数: ${data.count} 件<br/>
                  总价值: ¥${data.totalValue.toFixed(2)}<br/>
                  平均价格: ¥${data.avgPrice.toFixed(2)}<br/>
                  占比: ${params.percent}%`
        },
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        borderColor: '#333',
        textStyle: {
          color: '#fff'
        }
      },
      legend: {
        show: window.innerWidth > 1366,
        orient: 'vertical',
        right: '5%',
        top: 'center',
        textStyle: {
          color: '#fff',
          fontSize: 12
        },
        itemWidth: 25,
        itemHeight: 14,
        itemGap: 10,
        formatter: (name) => {
          const item = chartData.find(d => d.name === name)
          if (item) {
            return isValueMode
              ? `${name}\n${item.count}件 ¥${item.totalValue.toFixed(0)}`
              : `${name}\n${item.count}件`
          }
          return name
        }
      },
      series: [
        {
          name: isValueMode ? '价格区间分布' : '数量区间分布',
          type: 'pie',
          radius: window.innerWidth > 1366 ? ['40%', '70%'] : ['35%', '65%'],
          center: window.innerWidth > 1366 ? ['40%', '50%'] : ['50%', '50%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#1a1a1a',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: (params) => {
              return isValueMode
                ? `${params.name}\n${params.data.count}件\n¥${params.data.totalValue.toFixed(0)}`
                : `${params.name}\n${params.data.count}件`
            },
            color: '#fff',
            fontSize: 11
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 14,
              fontWeight: 'bold'
            },
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          labelLine: {
            show: true,
            lineStyle: {
              color: '#888'
            }
          },
          data: chartData,
          color: [
            '#5470c6',
            '#91cc75',
            '#fac858',
            '#ee6666',
            '#73c0de',
            '#3ba272',
            '#fc8452',
            '#9a60b4'
          ]
        }
      ]
    }

    sellChart.setOption(option)
  }


  // 计算移动平均线（用于 CSQAQ K 线图）
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

  // 初始化CSQAQ K线图
  const initCSQAQChart = async () => {
    await nextTick()
    
    if (!csqaqChartRef.value) return

    csqaqChart = echarts.init(csqaqChartRef.value)
    
    const option = {
      backgroundColor: 'transparent',
      animation: true,
      animationDuration: 300,
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
          link: [{ xAxisIndex: 'all' }]
        },
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        borderColor: '#333',
        textStyle: {
          color: '#fff'
        }
      },
      legend: {
        data: ['K线', 'MA5', 'MA10', 'MA20'],
        textStyle: {
          color: '#fff'
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
          top: '12%',
          height: '60%',
          containLabel: true
        },
        {
          left: '3%',
          right: '3%',
          top: '77%',
          height: '16%',
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
            color: '#fff',
            fontSize: 10
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
            color: '#fff'
          },
          gridIndex: 0
        },
        {
          scale: true,
          splitLine: {
            show: false
          },
          axisLabel: {
            color: '#fff',
            fontSize: 10
          },
          gridIndex: 1,
          splitNumber: 2
        }
      ],
      dataZoom: [
        {
          type: 'inside',
          xAxisIndex: [0, 1],
          start: 0,
          end: 100,
          zoomOnMouseWheel: true,
          moveOnMouseMove: true,
          moveOnMouseWheel: false
        }
      ],
      series: [
        {
          name: 'K线',
          type: 'candlestick',
          data: [],
          itemStyle: {
            color: '#ef5350',
            color0: '#00c853',
            borderColor: '#ef5350',
            borderColor0: '#00c853'
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
              return params.data.isUp ? '#ef5350' : '#00c853'
            }
          },
          xAxisIndex: 1,
          yAxisIndex: 1
        }
      ]
    }
    
    csqaqChart.setOption(option)
  }

  // 加载CSQAQ K线图数据
  const loadCSQAQData = async () => {
    loadingCSQAQ.value = true
    try {
      const response = await axios.get('/spider/csqaqSpiderV1/getKline', {
        params: {
          period: csqaqPeriod.value
        }
      })
      
      if (response.data && response.data.code === 200) {
        const data = response.data.data
        updateCSQAQChart(data)
      }
    } catch (error) {
      console.error('获取CSQAQ K线数据失败:', error)
    } finally {
      loadingCSQAQ.value = false
    }
  }

  // 更新CSQAQ K线图
  const updateCSQAQChart = (data) => {
    if (!csqaqChart || !data || data.length === 0) return
    
    const times = data.map(item => item.time)
    const klineData = data.map(item => [
      parseFloat(item.open),
      parseFloat(item.close),
      parseFloat(item.low),
      parseFloat(item.high)
    ])
    
    // 计算成交量数据（根据涨跌设置颜色）
    const volumeData = data.map((item, index) => {
      const open = parseFloat(item.open)
      const close = parseFloat(item.close)
      const high = parseFloat(item.high)
      const low = parseFloat(item.low)
      let volume = parseFloat(item.volume || 0)
      
      // 如果成交量为0，使用价格波动幅度作为替代
      if (volume === 0) {
        volume = Math.abs(high - low) * 100
      }
      
      return {
        value: volume,
        isUp: close >= open
      }
    })
    
    const ma5 = calculateMA(klineData, 5)
    const ma10 = calculateMA(klineData, 10)
    const ma20 = calculateMA(klineData, 20)
    
    // 默认显示最后36条数据
    const defaultDisplayCount = 36
    
    const totalCount = data.length
    const startPercent = Math.max(0, ((totalCount - defaultDisplayCount) / totalCount) * 100)
    const endPercent = 100
    
    csqaqChart.setOption({
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
          moveOnMouseWheel: false
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
        },
        {
          data: volumeData
        }
      ]
    })
  }

  // 切换CSQAQ K线周期
  const changeCSQAQPeriod = (period) => {
    csqaqPeriod.value = period
    loadCSQAQData()
  }

  // 处理窗口大小变化
  const handleResize = () => {
    if (inventoryChart) {
      inventoryChart.resize()
    }
    if (componentChart) {
      componentChart.resize()
    }
    if (buyChart) {
      buyChart.resize()
    }
    if (sellChart) {
      sellChart.resize()
    }
    if (csqaqChart) {
      csqaqChart.resize()
    }
  }

  // ResizeObserver 用于监听容器大小变化
  let resizeObserver = null

  // 初始化 ResizeObserver
  const initResizeObserver = () => {
    if (typeof ResizeObserver !== 'undefined') {
      resizeObserver = new ResizeObserver(() => {
        handleResize()
      })

      // 监听所有图表容器
      if (inventoryChartRef.value) {
        resizeObserver.observe(inventoryChartRef.value)
      }
      if (componentChartRef.value) {
        resizeObserver.observe(componentChartRef.value)
      }
      if (buyChartRef.value) {
        resizeObserver.observe(buyChartRef.value)
      }
      if (sellChartRef.value) {
        resizeObserver.observe(sellChartRef.value)
      }
      if (csqaqChartRef.value) {
        resizeObserver.observe(csqaqChartRef.value)
      }
    }
  }

  // 加载所有统计数据
  const loadAllStats = async () => {
    await loadSteamIdList()

    // 并行加载所有数据
    await Promise.all([
      loadBuyStats(),
      loadSellStats(),
      loadInventoryStats(),
      loadComponentsStats(),
      loadBuyChartData(),
      loadSellChartData()
    ])

    // 初始化并加载CSQAQ K线图
    await initCSQAQChart()
    await loadCSQAQData()

    // 初始化 ResizeObserver
    await nextTick()
    initResizeObserver()
  }

  // 处理数据源切换
  const handleDataSourceChange = async () => {
    console.log('数据源切换为:', dataSource.value)
    // 数据源切换时不需要重新加载，因为数据已经加载过了
  }

  // 处理库存图表Steam ID切换
  const handleInventorySteamIdChange = async () => {
    console.log('库存图表Steam ID切换为:', selectedInventorySteamId.value)
    await loadInventoryStats(selectedInventorySteamId.value)
  }

  // 处理组件图表Steam ID切换
  const handleComponentSteamIdChange = async () => {
    console.log('组件图表Steam ID切换为:', selectedComponentSteamId.value)
    await loadComponentsStats(selectedComponentSteamId.value)
  }

  // 处理购入图表Steam ID切换
  const handleBuySteamIdChange = async () => {
    console.log('购入图表Steam ID切换为:', selectedBuySteamId.value)
    await loadBuyChartData(selectedBuySteamId.value)
  }

  // 处理出售图表Steam ID切换
  const handleSellSteamIdChange = async () => {
    console.log('出售图表Steam ID切换为:', selectedSellSteamId.value)
    await loadSellChartData(selectedSellSteamId.value)
  }

  // 计算是否还有更多数据
  const hasMoreItems = computed(() => {
    return displayedItems.value.length < filteredItems.value.length
  })

  // 加载更多数据
  const loadMoreItems = () => {
    if (loadingMore.value || !hasMoreItems.value) {
      return
    }

    loadingMore.value = true
    
    setTimeout(() => {
      const start = currentDisplayPage.value * pageSize
      const end = start + pageSize
      const moreItems = filteredItems.value.slice(start, end)
      
      displayedItems.value = [...displayedItems.value, ...moreItems]
      currentDisplayPage.value++
      loadingMore.value = false
    }, 300) // 模拟加载延迟
  }

  // 处理弹窗滚动事件
  const handleDialogScroll = (event) => {
    const target = event.target
    const scrollTop = target.scrollTop
    const scrollHeight = target.scrollHeight
    const clientHeight = target.clientHeight
    
    // 当滚动到距离底部100px时触发加载
    if (scrollHeight - scrollTop - clientHeight < 100) {
      loadMoreItems()
    }
  }

  // 初始化显示的数据
  const initDisplayedItems = () => {
    currentDisplayPage.value = 1
    displayedItems.value = filteredItems.value.slice(0, pageSize)
    
    // 重置滚动位置
    if (dialogScrollRef.value) {
      dialogScrollRef.value.scrollTop = 0
    }
  }

  onMounted(() => {
    loadAllStats()
    // 监听窗口大小变化
    window.addEventListener('resize', handleResize)
  })

  // 监听图表模式切换
  watch(inventoryChartMode, () => {
    if (allInventoryData.value.length > 0) {
      loadInventoryChart(allInventoryData.value)
    }
  })

  watch(componentChartMode, () => {
    if (allComponentsData.value.length > 0) {
      loadComponentChart(allComponentsData.value)
    }
  })

  watch(buyChartMode, () => {
    if (allBuyData.value.length > 0) {
      loadBuyChart(allBuyData.value)
    }
  })

  watch(sellChartMode, () => {
    if (allSellData.value.length > 0) {
      loadSellChart(allSellData.value)
    }
  })

  onUnmounted(() => {
    // 移除 window resize 监听
    window.removeEventListener('resize', handleResize)

    // 断开 ResizeObserver
    if (resizeObserver) {
      resizeObserver.disconnect()
      resizeObserver = null
    }

    // 销毁图表实例
    if (inventoryChart) {
      inventoryChart.dispose()
      inventoryChart = null
    }
    if (componentChart) {
      componentChart.dispose()
      componentChart = null
    }
    if (buyChart) {
      buyChart.dispose()
      buyChart = null
    }
    if (sellChart) {
      sellChart.dispose()
      sellChart = null
    }
    if (csqaqChart) {
      csqaqChart.dispose()
      csqaqChart = null
    }
  })

  // 图片404缓存
  const image404Cache = ref(new Set())

  // 获取武器图片路径
  const getWeaponImage = (steamHashName) => {
    if (!steamHashName) {
      return null
    }
    // 检查是否已经在404缓存中
    if (image404Cache.value.has(steamHashName)) {
      return null
    }
    // 将空格和竖线分别替换为下划线，并添加.png扩展名
    const imageName = steamHashName
      .replace(/\s*\|\s*/g, '___')
      .replace(/\s/g, '_')
      + '.png'

    return apiUrls.weaponImage(imageName)
  }

  // 处理图片加载错误
  const handleImageError = (event, steamHashName) => {
    // 将失败的steam_hash_name添加到404缓存中
    if (steamHashName) {
      image404Cache.value.add(steamHashName)
    }
    
    // 移除错误监听器，防止重复触发
    event.target.onerror = null
    
    // 隐藏图片
    event.target.style.display = 'none'
  }

  return {
    buyStats,
    sellStats,
    inventoryStats,
    componentStats,
    totalInventoryCount,
    totalYyypPrice,
    totalYyypDiff,
    totalBuffPrice,
    totalBuffDiff,
    steamIdList,
    selectedSteamId,
    selectedInventorySteamId,
    selectedComponentSteamId,
    selectedBuySteamId,
    selectedSellSteamId,
    inventoryChartRef,
    componentChartRef,
    buyChartRef,
    sellChartRef,
    csqaqChartRef,
    inventoryChartMode,
    componentChartMode,
    buyChartMode,
    sellChartMode,
    csqaqPeriod,
    loadingCSQAQ,
    itemListVisible,
    selectedRange,
    filteredItems,
    displayedItems,
    dialogScrollRef,
    loadingMore,
    hasMoreItems,
    dataSource,
    inventoryChartStats,
    componentChartStats,
    buyChartStats,
    sellChartStats,
    handleDataSourceChange,
    handleInventorySteamIdChange,
    handleComponentSteamIdChange,
    handleBuySteamIdChange,
    handleSellSteamIdChange,
    handleDialogScroll,
    getItemTitle,
    getWeaponImage,
    handleImageError,
    changeCSQAQPeriod
  }
}
