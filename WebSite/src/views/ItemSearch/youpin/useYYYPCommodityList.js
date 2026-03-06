import { ref, computed, nextTick, inject } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import axios from 'axios'
import { API_CONFIG } from '@/config/api.js'

export function useYYYPCommodityList(props, emit) {
  // ========== 排序和磨损区间 ==========
  const sortType = ref('default')
  const wearRange = ref('')

  const wearRangeOptions = computed(() => {
    if (!props.yyypCurrentWeapon?.market_listing_item_name) return []

    const name = props.yyypCurrentWeapon.market_listing_item_name

    if (name.includes('崭新出厂') || name.includes('Factory New')) {
      return [
        { label: '0.00 - 0.01', value: '0.00-0.01' },
        { label: '0.01 - 0.02', value: '0.01-0.02' },
        { label: '0.02 - 0.03', value: '0.02-0.03' },
        { label: '0.03 - 0.04', value: '0.03-0.04' },
        { label: '0.04 - 0.07', value: '0.04-0.07' }
      ]
    }

    if (name.includes('略有磨损') || name.includes('Minimal Wear')) {
      return [
        { label: '0.07 - 0.08', value: '0.07-0.08' },
        { label: '0.08 - 0.09', value: '0.08-0.09' },
        { label: '0.09 - 0.10', value: '0.09-0.10' },
        { label: '0.10 - 0.11', value: '0.10-0.11' },
        { label: '0.11 - 0.15', value: '0.11-0.15' }
      ]
    }

    if (name.includes('久经沙场') || name.includes('Field-Tested')) {
      return [
        { label: '0.15 - 0.18', value: '0.15-0.18' },
        { label: '0.18 - 0.21', value: '0.18-0.21' },
        { label: '0.21 - 0.24', value: '0.21-0.24' },
        { label: '0.24 - 0.27', value: '0.24-0.27' },
        { label: '0.27 - 0.38', value: '0.27-0.38' }
      ]
    }

    if (name.includes('破损不堪') || name.includes('Well-Worn')) {
      return [
        { label: '0.38 - 0.39', value: '0.38-0.39' },
        { label: '0.39 - 0.40', value: '0.39-0.40' },
        { label: '0.40 - 0.41', value: '0.40-0.41' },
        { label: '0.41 - 0.42', value: '0.41-0.42' },
        { label: '0.42 - 0.45', value: '0.42-0.45' }
      ]
    }

    if (name.includes('战痕累累') || name.includes('Battle-Scarred')) {
      return [
        { label: '全部', value: '' },
        { label: '0.45 - 0.50', value: '0.45-0.50' },
        { label: '0.50 - 0.63', value: '0.50-0.63' },
        { label: '0.63 - 0.76', value: '0.63-0.76' },
        { label: '0.76 - 0.90', value: '0.76-0.90' },
        { label: '0.90 - 1.00', value: '0.90-1.00' }
      ]
    }

    return []
  })

  const handleSortChange = (value) => {
    console.log('排序变更:', value)
    emit('sort-change', value)
  }

  const handleWearRangeChange = (value) => {
    console.log('磨损区间变更:', value)
    emit('wear-range-change', value)
  }

  // ========== 高级筛选 ==========
  const filterDialogVisible = ref(false)

  const filterForm = ref({
    templateId: '',
    wearMin: '',
    wearMax: '',
    hasNameTag: null,
    nameTagText: '',
    hasStickerFilter: null,
    stickerName: '',
    hasPendant: null,
    pendantName: '',
    fastDelivery: false,
    priceMin: '',
    priceMax: ''
  })

  const handleFilterChange = (filterType) => {
    emit('filter-change', filterType)
  }

  const handleAdvancedFilter = () => {
    filterDialogVisible.value = true
  }

  const handleResetFilter = () => {
    filterForm.value = {
      templateId: '',
      wearMin: '',
      wearMax: '',
      hasNameTag: null,
      nameTagText: '',
      hasStickerFilter: null,
      stickerName: '',
      hasPendant: null,
      pendantName: '',
      fastDelivery: false,
      priceMin: '',
      priceMax: ''
    }
  }

  const handleApplyFilter = () => {
    console.log('应用筛选:', filterForm.value)
    emit('advanced-filter', filterForm.value)
    filterDialogVisible.value = false
  }

  // ========== 价格走势 ==========
  const priceTrendDialogVisible = ref(false)
  const selectedDays = ref(30)
  const priceTrendData = ref(null)
  const priceTrendLoading = ref(false)
  const priceTrendChart = ref(null)
  let chartInstance = null

  const priceStats = computed(() => {
    if (!priceTrendData.value?.tradeDataList?.length) {
      return { maxPrice: '0.00', minPrice: '0.00', avgPrice: '0.00', count: 0 }
    }

    const prices = priceTrendData.value.tradeDataList.map(item => parseFloat(item.price))
    return {
      maxPrice: Math.max(...prices).toFixed(2),
      minPrice: Math.min(...prices).toFixed(2),
      avgPrice: (prices.reduce((a, b) => a + b, 0) / prices.length).toFixed(2),
      count: prices.length
    }
  })

  const handleOpenPriceTrend = () => {
    if (!props.yyypCurrentWeapon) {
      ElMessage.warning('请先选择武器')
      return
    }
    priceTrendDialogVisible.value = true
    selectedDays.value = 30
    loadPriceTrend()
  }

  const loadPriceTrend = async () => {
    if (!props.yyypCurrentWeapon?.yyyp_id) {
      ElMessage.error('缺少武器ID信息')
      return
    }

    priceTrendLoading.value = true

    try {
      const url = `${API_CONFIG.SPIDER_BASE_URL}/spiderApiV2/src/web_site/youping/units/item_search/price_trend/getPriceTrend`
      const response = await axios.post(url, {
        yyypId: props.yyypCurrentWeapon.yyyp_id,
        day: selectedDays.value
      })

      if (response.data.success) {
        priceTrendData.value = response.data.data
        await nextTick()
        initPriceTrendChart()
      } else {
        ElMessage.error(response.data.message || '获取价格走势失败')
      }
    } catch (error) {
      console.error('加载价格走势失败:', error)
      ElMessage.error('加载价格走势失败: ' + (error.message || '未知错误'))
    } finally {
      priceTrendLoading.value = false
    }
  }

  const initPriceTrendChart = () => {
    if (!priceTrendChart.value || !priceTrendData.value?.tradeDataList) return

    if (chartInstance) {
      chartInstance.dispose()
    }

    chartInstance = echarts.init(priceTrendChart.value)

    const tradeDataList = priceTrendData.value.tradeDataList
    const dates = tradeDataList.map(item => {
      const date = new Date(item.time)
      const month = date.getMonth() + 1
      const day = date.getDate()
      const hours = date.getHours().toString().padStart(2, '0')
      const minutes = date.getMinutes().toString().padStart(2, '0')
      return `${month}/${day} ${hours}:${minutes}`
    })
    const prices = tradeDataList.map(item => parseFloat(item.price))

    const minPrice = Math.min(...prices)
    const maxPrice = Math.max(...prices)
    const priceRange = maxPrice - minPrice
    const padding = priceRange * 0.1
    const yAxisMin = Math.max(0, minPrice - padding)
    const yAxisMax = maxPrice + padding

    const option = {
      title: {
        text: '价格走势',
        left: 'center',
        textStyle: { color: '#e0e0e0', fontSize: 16 }
      },
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(50, 50, 50, 0.95)',
        borderColor: '#555',
        textStyle: { color: '#e0e0e0' },
        formatter: (params) => {
          const param = params[0]
          return `${param.name}<br/>价格: ¥${param.value}`
        }
      },
      grid: {
        left: '3%', right: '4%', bottom: '15%', top: '15%', containLabel: true
      },
      xAxis: {
        type: 'category',
        data: dates,
        boundaryGap: false,
        axisLine: { lineStyle: { color: '#555' } },
        axisLabel: { color: '#999', rotate: 45, interval: 'auto' }
      },
      yAxis: {
        type: 'value',
        name: '价格 (¥)',
        min: yAxisMin,
        max: yAxisMax,
        nameTextStyle: { color: '#999' },
        axisLine: { lineStyle: { color: '#555' } },
        axisLabel: { color: '#999', formatter: '¥{value}' },
        splitLine: { lineStyle: { color: '#333' } }
      },
      series: [
        {
          name: '价格',
          type: 'line',
          data: prices,
          smooth: true,
          lineStyle: { width: 2, color: '#409eff' },
          itemStyle: { color: '#409eff' },
          areaStyle: {
            color: {
              type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
                { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
              ]
            }
          }
        }
      ]
    }

    chartInstance.setOption(option)
  }

  // ========== 通用方法 ==========
  const toggleYYYPList = () => emit('toggle-yyyp-list')
  const handleRefreshYYYP = () => emit('refresh-yyyp')
  const toggleMultiSelectMode = () => emit('toggle-multi-select')
  const selectAllCommodities = (type) => emit('select-all', type)
  const handleCommodityCardClick = (item, type, event) => emit('commodity-click', { item, type, event })
  const handleYYYPScroll = (event) => emit('yyyp-scroll', event)
  const fetchSingleNameTag = (item) => emit('fetch-single-nametag', item)
  const handleImageError = (e) => { e.target.style.display = 'none' }

  const getButtonText = (item) => {
    if (item.isPurchaseOrder) return '供应'
    if (item.isLeaseItem) return '租用'
    return '购买'
  }

  const getButtonType = (item) => {
    if (item.isPurchaseOrder) return 'primary'
    if (item.isLeaseItem) return 'primary'
    return 'success'
  }

  // ========== 注入 ==========
  const isCommoditySelected = inject('isCommoditySelected', () => false)
  const getWeaponImage = inject('getWeaponImage', (hashName) => {
    if (!hashName) return ''
    return `/weapon_imgs/${encodeURIComponent(hashName)}.png`
  })

  // ========== 预售购买 ==========
  const presaleBuyDialogVisible = ref(false)
  const presaleDetail = ref(null)
  const presaleDetailLoading = ref(false)
  const buyingPresale = ref(false)
  const currentPresaleItem = ref(null)

  const presaleBuyForm = ref({
    autoConfirmPayment: true,
    pollPayment: true,
    paymentChannel: 'balance'
  })

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '-'
    const date = new Date(timestamp)
    return date.toLocaleString('zh-CN', {
      year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit'
    })
  }

  const filteredPayList = computed(() => {
    if (!presaleDetail.value?.payList) return []
    return presaleDetail.value.payList.filter(pay => pay.channelId === 100)
  })

  const isPresaleBalanceSufficient = computed(() => {
    if (!presaleDetail.value?.commodity) return false
    if (filteredPayList.value.length === 0) return false

    const balance = filteredPayList.value[0].balance || 0
    const depositAmount = presaleDetail.value.commodity.commodityPreSaleDTO?.depositAmount || 0

    return balance >= depositAmount
  })

  const openPresaleBuyDialog = async (item) => {
    if (!item?.id) {
      ElMessage.warning('商品信息不完整')
      return
    }

    currentPresaleItem.value = item
    presaleBuyDialogVisible.value = true
    presaleDetailLoading.value = true
    presaleDetail.value = null

    try {
      const url = `${API_CONFIG.SPIDER_BASE_URL}/spiderApiV2/src/web_site/youping/units/item_search/presale/getPresaleDetail`
      const response = await axios.post(url, {
        steamId: props.selectedSteamId || '',
        commodityId: item.id.toString()
      })

      if (response.data.success) {
        presaleDetail.value = response.data.data
        console.log('预售详情:', presaleDetail.value)
      } else {
        throw new Error(response.data.message || '获取预售详情失败')
      }
    } catch (error) {
      console.error('获取预售详情失败:', error)
      ElMessage.error(error.message || '获取预售详情失败')
      presaleBuyDialogVisible.value = false
    } finally {
      presaleDetailLoading.value = false
    }
  }

  const confirmPresaleBuy = async () => {
    if (!currentPresaleItem.value || !presaleDetail.value) {
      ElMessage.error('商品信息不完整')
      return
    }

    const commodity = presaleDetail.value.commodity
    if (!commodity) {
      ElMessage.error('商品详情缺失')
      return
    }

    const depositAmount = commodity.commodityPreSaleDTO?.depositAmount
    if (!depositAmount) {
      ElMessage.error('定金金额缺失')
      return
    }

    try {
      await ElMessageBox.confirm(
        `确认购买 ${commodity.commodityName}？\n定金: ¥${depositAmount}`,
        '确认购买',
        { confirmButtonText: '确认', cancelButtonText: '取消', type: 'warning' }
      )
    } catch {
      return
    }

    buyingPresale.value = true

    try {
      const url = `${API_CONFIG.SPIDER_BASE_URL}/spiderApiV2/src/web_site/youping/units/item_search/presale/buyPresaleCommodity`
      const response = await axios.post(url, {
        steamId: props.selectedSteamId || '',
        commodityId: currentPresaleItem.value.id.toString(),
        price: depositAmount.toString(),
        autoConfirmPayment: presaleBuyForm.value.autoConfirmPayment,
        pollPayment: presaleBuyForm.value.pollPayment,
        paymentChannel: presaleBuyForm.value.paymentChannel
      })

      if (response.data.success) {
        ElMessage.success('购买成功！')

        const orderData = response.data.data?.order
        if (orderData?.orderNo) {
          ElMessage.info(`订单号: ${orderData.orderNo}`)
        }

        presaleBuyDialogVisible.value = false
        emit('refresh-yyyp')
      } else {
        throw new Error(response.data.message || '购买失败')
      }
    } catch (error) {
      console.error('购买预售商品失败:', error)
      const errorMsg = error.response?.data?.message || error.message || '购买失败，请稍后重试'
      ElMessage.error(errorMsg)
    } finally {
      buyingPresale.value = false
    }
  }

  // ========== 在售购买 ==========
  const onSaleBuyDialogVisible = ref(false)
  const onSaleDetail = ref(null)
  const onSaleDetailLoading = ref(false)
  const buyingOnSale = ref(false)
  const currentOnSaleItem = ref(null)

  const onSaleOrderNo = ref(null)
  const onSaleWaitPaymentDataNo = ref(null)
  const onSalePayList = ref([])
  const onSaleOrderLoading = ref(false)
  const onSaleOrderError = ref(null)

  const onSaleBalanceChannel = computed(() =>
    onSalePayList.value.find(p => p.channelId === 100) || null
  )
  const onSaleBalance = computed(() =>
    onSaleBalanceChannel.value ? parseFloat(onSaleBalanceChannel.value.balance || 0) : null
  )
  const onSalePrice = computed(() => {
    const commodity = onSaleDetail.value?.commodity
    if (!commodity) return 0
    return parseFloat(
      commodity.commodityConversionPrice ||
      (commodity.commodityPrice ? commodity.commodityPrice / 100 : 0)
    )
  })
  const onSaleBalanceAfter = computed(() =>
    onSaleBalance.value !== null ? (onSaleBalance.value - onSalePrice.value) : null
  )
  const onSaleBalanceInsufficient = computed(() =>
    onSaleBalance.value !== null && onSaleBalance.value < onSalePrice.value
  )

  const handleBuyCommodityWithPresale = async (item) => {
    if (item.isPreSale === 1 || props.yyypFilterType === 'presale') {
      await openPresaleBuyDialog(item)
    } else if (props.yyypFilterType === 'on_sale') {
      await openOnSaleBuyDialog(item)
    } else {
      emit('buy-commodity', item)
    }
  }

  const openOnSaleBuyDialog = async (item) => {
    if (!item?.id) {
      ElMessage.warning('商品信息不完整')
      return
    }

    currentOnSaleItem.value = item
    onSaleDetail.value = null
    onSaleOrderNo.value = null
    onSaleWaitPaymentDataNo.value = null
    onSalePayList.value = []
    onSaleOrderError.value = null
    onSaleDetailLoading.value = true
    onSaleOrderLoading.value = true
    onSaleBuyDialogVisible.value = true

    const detailUrl = `${API_CONFIG.SPIDER_BASE_URL}/spiderApiV2/src/web_site/youping/units/item_search/on_sale/getWeaponDetail`
    const createOrderUrl = `${API_CONFIG.SPIDER_BASE_URL}/spiderApiV2/src/web_site/youping/units/item_search/on_sale/createOrder`

    try {
      const detailRes = await axios.post(detailUrl, {
        steamId: props.selectedSteamId || '',
        commodityId: item.id.toString()
      })
      if (!detailRes.data.success) {
        throw new Error(detailRes.data.message || '获取商品详情失败')
      }
      onSaleDetail.value = detailRes.data.data
    } catch (error) {
      ElMessage.error(error.message || '获取商品详情失败')
      onSaleBuyDialogVisible.value = false
      onSaleDetailLoading.value = false
      onSaleOrderLoading.value = false
      return
    } finally {
      onSaleDetailLoading.value = false
    }

    const commodity = onSaleDetail.value?.commodity
    const price = commodity
      ? (commodity.commodityConversionPrice || (commodity.commodityPrice ? commodity.commodityPrice / 100 : 0))
      : 0

    if (!price) {
      onSaleOrderError.value = '商品价格缺失，无法创建订单'
      onSaleOrderLoading.value = false
      return
    }

    try {
      const orderRes = await axios.post(createOrderUrl, {
        steamId: props.selectedSteamId || '',
        commodityId: item.id.toString(),
        price: price.toString()
      })
      if (!orderRes.data.success) {
        throw new Error(orderRes.data.message || '创建订单失败')
      }
      const orderData = orderRes.data.data
      onSaleOrderNo.value = orderData.orderNo
      onSaleWaitPaymentDataNo.value = orderData.waitPaymentDataNo
      onSalePayList.value = orderData.payList || []
    } catch (error) {
      onSaleOrderError.value = error.response?.data?.message || error.message || '创建订单失败'
    } finally {
      onSaleOrderLoading.value = false
    }
  }

  let _cancellingOrder = false
  const cancelOnSaleOrder = async () => {
    if (_cancellingOrder) return
    _cancellingOrder = true

    onSaleBuyDialogVisible.value = false

    if (onSaleOrderNo.value) {
      const orderNoToCancel = onSaleOrderNo.value
      onSaleOrderNo.value = null
      try {
        await axios.post(
          `${API_CONFIG.SPIDER_BASE_URL}/spiderApiV2/src/web_site/youping/units/item_search/on_sale/cancelOrder`,
          { steamId: props.selectedSteamId || '', orderNo: orderNoToCancel }
        )
      } catch {
        // 撤单失败静默处理
      }
    }

    _cancellingOrder = false
  }

  const confirmOnSalePayment = async () => {
    if (!onSaleOrderNo.value || !onSaleWaitPaymentDataNo.value) {
      ElMessage.error('订单信息不完整，请重新打开购买窗口')
      return
    }

    buyingOnSale.value = true

    try {
      const url = `${API_CONFIG.SPIDER_BASE_URL}/spiderApiV2/src/web_site/youping/units/item_search/on_sale/submitPayment`
      const response = await axios.post(url, {
        steamId: props.selectedSteamId || '',
        orderNo: onSaleOrderNo.value,
        waitPaymentDataNo: onSaleWaitPaymentDataNo.value,
        price: onSalePrice.value.toString()
      })

      if (response.data.success) {
        const orderNo = response.data.data?.orderNo || onSaleOrderNo.value
        ElMessage.success(`购买成功！订单号: ${orderNo}`)
        onSaleOrderNo.value = null
        onSaleBuyDialogVisible.value = false
        emit('refresh-yyyp')
      } else {
        throw new Error(response.data.message || '支付失败')
      }
    } catch (error) {
      const errorMsg = error.response?.data?.message || error.message || '支付失败，请稍后重试'
      ElMessage.error(errorMsg)
    } finally {
      buyingOnSale.value = false
    }
  }

  return {
    // 排序和磨损区间
    sortType,
    wearRange,
    wearRangeOptions,
    handleSortChange,
    handleWearRangeChange,

    // 高级筛选
    filterDialogVisible,
    filterForm,
    handleFilterChange,
    handleAdvancedFilter,
    handleResetFilter,
    handleApplyFilter,

    // 价格走势
    priceTrendDialogVisible,
    selectedDays,
    priceTrendData,
    priceTrendLoading,
    priceTrendChart,
    priceStats,
    handleOpenPriceTrend,
    loadPriceTrend,

    // 通用方法
    toggleYYYPList,
    handleRefreshYYYP,
    toggleMultiSelectMode,
    selectAllCommodities,
    handleCommodityCardClick,
    handleYYYPScroll,
    fetchSingleNameTag,
    handleImageError,
    getButtonText,
    getButtonType,

    // 注入
    isCommoditySelected,
    getWeaponImage,

    // 预售购买
    presaleBuyDialogVisible,
    presaleDetail,
    presaleDetailLoading,
    buyingPresale,
    presaleBuyForm,
    filteredPayList,
    isPresaleBalanceSufficient,
    formatTimestamp,
    confirmPresaleBuy,

    // 在售购买
    onSaleBuyDialogVisible,
    onSaleDetail,
    onSaleDetailLoading,
    buyingOnSale,
    onSaleOrderNo,
    onSaleOrderLoading,
    onSaleOrderError,
    onSaleBalance,
    onSalePrice,
    onSaleBalanceAfter,
    onSaleBalanceInsufficient,
    handleBuyCommodityWithPresale,
    cancelOnSaleOrder,
    confirmOnSalePayment
  }
}
