import { ref, computed, watch, nextTick, inject, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import axios from 'axios'
import { API_CONFIG, apiUrls } from '@/config/api.js'

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

  // ========== 收藏 ==========
  const isFavorited = ref(false)
  const favoriteLoading = ref(false)
  /** 本列表加载周期内已请求过模板详情的 key（templateId_steamId），避免重复请求导致 429 */
  const templateDetailRequestedKey = ref('')
  const favoriteStatusLoading = ref(false)

  // 根据服务端 template/info 的 IsFavorite 同步收藏状态（同一 templateId+steamId 仅请求一次）
  const fetchFavoriteStatus = async () => {
    const weapon = props.yyypCurrentWeapon
    const steamId = props.selectedSteamId
    if (!weapon?.yyyp_id || !steamId) {
      isFavorited.value = false
      return
    }
    const key = `${weapon.yyyp_id}_${steamId}`
    if (templateDetailRequestedKey.value === key) return
    if (favoriteStatusLoading.value) return
    templateDetailRequestedKey.value = key
    favoriteStatusLoading.value = true
    try {
      const url = `${API_CONFIG.SPIDER_BASE_URL}/spiderApiV2/src/web_site/youping/units/item_search/on_sale/getTemplateInfo`
      const response = await axios.post(url, {
        steamId,
        templateId: Number(weapon.yyyp_id)
      })
      const res = response.data
      if (res && res.success && res.data) {
        isFavorited.value = !!res.data.isFavorite
      } else {
        isFavorited.value = false
      }
    } catch {
      isFavorited.value = false
      templateDetailRequestedKey.value = '' // 失败则允许下次再请求
    } finally {
      favoriteStatusLoading.value = false
    }
  }

  // 武器/Steam 清空时重置收藏状态
  watch(
    () => [props.yyypCurrentWeapon?.yyyp_id, props.selectedSteamId],
    ([templateId, steamId]) => {
      if (!templateId || !steamId) {
        isFavorited.value = false
      }
    },
    { immediate: true }
  )

  // 列表开始加载时重置“已请求”标记，便于本次加载完成后只请求一次模板详情
  watch(
    () => props.isSearching,
    (isSearching) => {
      if (isSearching) templateDetailRequestedKey.value = ''
    }
  )

  // 在售列表加载完成后，间隔 1.5s 再请求模板详情一次（避免与列表同时请求导致 429）
  let detailDelayTimer = null
  watch(
    () => [props.isSearching, props.showYYYPList, props.yyypCurrentWeapon?.yyyp_id, props.selectedSteamId],
    (newVals, oldVals) => {
      const [isSearching, showList, templateId, steamId] = newVals
      if (!templateId || !steamId || !showList) return
      const wasSearching = oldVals ? oldVals[0] : false
      if (wasSearching === true && isSearching === false) {
        if (detailDelayTimer) clearTimeout(detailDelayTimer)
        detailDelayTimer = setTimeout(() => {
          detailDelayTimer = null
          fetchFavoriteStatus()
        }, 1500)
      }
    }
  )
  onBeforeUnmount(() => {
    if (detailDelayTimer) clearTimeout(detailDelayTimer)
  })

  const toggleFavorite = async () => {
    if (!props.yyypCurrentWeapon) {
      ElMessage.warning('请先选择武器')
      return
    }
    const templateId = props.yyypCurrentWeapon.yyyp_id
    if (templateId == null || templateId === '') {
      ElMessage.warning('当前武器无悠悠有品模板ID')
      return
    }
    if (favoriteLoading.value) return
    favoriteLoading.value = true
    try {
      const url = `${API_CONFIG.SPIDER_BASE_URL}/spiderApiV2/src/web_site/youping/units/item_search/on_sale/favoriteTemplate`
      const response = await axios.post(url, {
        steamId: props.selectedSteamId || '',
        templateId: Number(templateId)
      })
      const res = response.data
      if (res && res.success) {
        isFavorited.value = !isFavorited.value
        ElMessage.success(res.message || '关注状态变更成功')
      } else {
        ElMessage.error(res?.message || '操作失败')
      }
    } catch (error) {
      const msg = error.response?.data?.message || error.message || '请求失败'
      ElMessage.error(msg)
    } finally {
      favoriteLoading.value = false
    }
  }

  // ========== 发布求购 ==========
  const wantedDialogVisible = ref(false)
  const submittingWanted = ref(false)
  const wantedTemplateInfo = ref(null)
  const wantedBalance = ref(null)
  const wantedBalanceLoading = ref(false)
  const transferInDialogVisible = ref(false)
  const transferInAvailableYuan = ref(0)
  const transferInLoading = ref(false)

  /** 打开发布求购弹窗：先拉发布详情，再在弹窗内单独拉求购余额（仅点击发布求购后再获取余额） */
  const handleOpenWantedDialog = async () => {
    if (!props.yyypCurrentWeapon) {
      ElMessage.warning('请先选择武器')
      return
    }
    wantedTemplateInfo.value = null
    wantedBalance.value = null
    const templateId = props.yyypCurrentWeapon.yyyp_id
    const steamId = props.selectedSteamId || ''
    wantedDialogVisible.value = true
    if (!steamId) return
    try {
      if (templateId != null) {
        const templateRes = await axios.post(apiUrls.yyypItemSearchPublishWantedGetTemplateInfo(), {
          steamId,
          templateId: Number(templateId)
        })
        if (templateRes.data?.code === 200 && templateRes.data?.data) {
          wantedTemplateInfo.value = templateRes.data.data
        }
      }
      // 求购余额：仅在点击发布求购并打开弹窗后再获取
      wantedBalanceLoading.value = true
      try {
        const balanceRes = await axios.post(apiUrls.yyypItemSearchPublishWantedGetBalance(), { steamId })
        if (balanceRes.data?.code === 200 && balanceRes.data?.data) {
          wantedBalance.value = balanceRes.data.data
        }
      } finally {
        wantedBalanceLoading.value = false
      }
    } catch (e) {
      console.error('获取发布求购数据失败:', e)
    }
  }

  /** 发布求购弹窗提交（由 PublishWantedDialog 的 submit 事件触发，与 on_sale 流程一致） */
  const handlePublishWantedSubmit = async (submitData) => {
    const { unitPrice, quantity, autoReceived, templateData } = submitData
    const ti = templateData?.template_info
    if (!ti) {
      ElMessage.error('发布详情缺失，请关闭后重试')
      return
    }
    const purchasePrice = parseFloat(unitPrice)
    const purchaseNum = parseInt(quantity)
    const totalAmount = purchasePrice * purchaseNum
    const incrementServiceCode = autoReceived ? [1001] : []

    submittingWanted.value = true
    try {
      const preCheckRes = await axios.post(apiUrls.yyypItemSearchPublishWantedPreCheck(), {
        steamId: props.selectedSteamId || '',
        orderData: {
          specialStyleObj: {},
          isCheckMaxPrice: false,
          templateHashName: ti.template_hash_name || '',
          totalAmount,
          referencePrice: ti.reference_price || '0',
          purchasePrice,
          purchaseNum,
          discountAmount: 0,
          minSellPrice: parseFloat(ti.min_sell_price || 0),
          maxPurchasePrice: parseFloat(ti.max_purchase_price || 9999999.99),
          templateId: String(ti.template_id),
          incrementServiceCode
        }
      })
      if (!preCheckRes.data || preCheckRes.data.code !== 200) {
        ElMessage.error(preCheckRes.data?.message || '预检查失败')
        return
      }
      const preCheckResult = preCheckRes.data.data
      const needAmount = parseFloat(preCheckResult.needPaymentAmount || 0)
      await ElMessageBox.confirm(
        `确定发布求购吗？<br>` +
        `单价：<span style="color:#F56C6C;font-weight:bold;">¥${purchasePrice}</span>，` +
        `数量：<span style="font-weight:bold;">${purchaseNum}</span><br>` +
        `需支付：<span style="color:#F56C6C;font-weight:bold;">¥${needAmount.toFixed(2)}</span>`,
        '确认发布求购',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
          dangerouslyUseHTMLString: true
        }
      )
      const saveRes = await axios.post(apiUrls.yyypItemSearchPublishWantedSaveOrder(), {
        steamId: props.selectedSteamId || '',
        orderData: {
          templateId: ti.template_id,
          templateHashName: ti.template_hash_name || '',
          commodityName: ti.commodity_name || '',
          referencePrice: ti.reference_price || '0',
          minSellPrice: ti.min_sell_price || '0',
          maxPurchasePrice: ti.max_purchase_price || '9999999.99',
          purchasePrice,
          purchaseNum,
          needPaymentAmount: preCheckResult.needPaymentAmount,
          incrementServiceCode,
          totalAmount: preCheckResult.totalAmount,
          templateName: preCheckResult.templateName,
          priceDifference: preCheckResult.priceDifference,
          discountAmount: 0,
          payConfirmFlag: false,
          repeatOrderCancelFlag: false
        }
      })
      if (saveRes.data && saveRes.data.code === 200) {
        const saveResult = saveRes.data.data
        ElMessage.success(`发布求购成功！订单号：${saveResult?.orderNo || ''}`)
        wantedDialogVisible.value = false
        emit('refresh-yyyp')
      } else {
        ElMessage.error(saveRes.data?.message || '提交求购失败')
      }
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error('发布求购失败: ' + (error.message || '未知错误'))
      }
    } finally {
      submittingWanted.value = false
    }
  }

  /** 打开从钱包转入对话框：先查可用余额再显示 */
  const openTransferIn = async () => {
    const steamId = props.selectedSteamId || ''
    if (!steamId) {
      ElMessage.warning('请先选择 Steam 账号')
      return
    }
    transferInLoading.value = true
    try {
      const res = await axios.post(apiUrls.yyypItemSearchPublishWantedQueryTransferInBalance(), { steamId })
      if (res.data?.code === 200 && res.data?.data) {
        transferInAvailableYuan.value = res.data.data.available_yuan ?? 0
        transferInDialogVisible.value = true
      } else {
        ElMessage.error(res.data?.message || '查询钱包可用余额失败')
      }
    } catch (e) {
      ElMessage.error('查询钱包可用余额失败: ' + (e.message || '未知错误'))
    } finally {
      transferInLoading.value = false
    }
  }

  /** 确认转入：调用接口后刷新求购余额 */
  const handleTransferInConfirm = async (transferMoney) => {
    transferInDialogVisible.value = false
    const steamId = props.selectedSteamId || ''
    try {
      const res = await axios.post(apiUrls.yyypItemSearchPublishWantedConfirmTransferIn(), {
        steamId,
        transferMoney
      })
      if (res.data?.code === 200) {
        ElMessage.success(`成功转入 ¥${parseFloat(transferMoney).toFixed(2)} 到求购余额`)
        wantedBalanceLoading.value = true
        try {
          const balanceRes = await axios.post(apiUrls.yyypItemSearchPublishWantedGetBalance(), { steamId })
          if (balanceRes.data?.code === 200 && balanceRes.data?.data) {
            wantedBalance.value = balanceRes.data.data
          }
        } finally {
          wantedBalanceLoading.value = false
        }
      } else {
        ElMessage.error(res.data?.message || '转入失败')
      }
    } catch (e) {
      ElMessage.error('转入失败: ' + (e.message || '未知错误'))
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
    confirmOnSalePayment,

    // 收藏
    isFavorited,
    favoriteLoading,
    toggleFavorite,

    // 发布求购
    wantedDialogVisible,
    wantedTemplateInfo,
    wantedBalance,
    wantedBalanceLoading,
    submittingWanted,
    handleOpenWantedDialog,
    handlePublishWantedSubmit,
    transferInDialogVisible,
    transferInAvailableYuan,
    transferInLoading,
    openTransferIn,
    handleTransferInConfirm
  }
}
