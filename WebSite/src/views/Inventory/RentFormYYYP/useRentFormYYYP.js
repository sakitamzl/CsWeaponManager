import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { apiUrls } from '@/config/api'

export function useRentFormYYYP(props, { emit }) {
  const autoPricingLoading = ref(false)

  // 赔付文本（富文本HTML）
  const compensationRichText = ref('')

  // 全局表单数据（交易方式/租期/增值服务）
  const formData = reactive({
    tradeMode: 1, // 默认租赁
    rentDays: 8, // 默认天数
    customDays: null,
    services: {
      zeroCooldown: false, // 0CD出租
      rentActivity: false  // 租送活动
    }
  })

  // 每个饰品独立的价格表单：短租/长租/押金
  const itemFormMap = reactive({})

  // 从 initData 解析交易方式
  const tradeMethods = computed(() => {
    if (!props.initData?.tradingMethodDTOList) {
      return [
        { id: '2', name: '租赁', type: 1 },
        { id: '3', name: '可租可售', type: 2 }
      ]
    }
    // 过滤掉"出售"选项,只保留租赁相关
    return props.initData.tradingMethodDTOList
      .filter(item => item.tradingMethodType !== 0)
      .map(item => ({
        id: item.tradingMethodId,
        name: item.tradingMethodName,
        type: item.tradingMethodType
      }))
  })

  // 从 initData 解析出租天数选项
  const rentDaysOptions = computed(() => {
    return props.initData?.leaseDayList || [8, 15, 30]
  })

  // 获取第一个饰品的配置信息
  const firstItemConfig = computed(() => {
    if (!props.items || props.items.length === 0 || !props.initData) {
      return null
    }
    const firstItem = props.items[0]
    const hashName = firstItem.steam_hash_name || firstItem.name

    return {
      coefficient: props.initData.coefficientMap?.[hashName],
      zeroRent: props.initData.zeroRentMap?.[hashName],
      depositProtect: props.initData.depositProtectFeeConfigMap?.[hashName],
      enableZeroCD: props.initData.zeroCDRentSupportTempateMap?.[hashName]
    }
  })

  // 最小/最大租赁天数
  const minRentDays = computed(() => {
    return firstItemConfig.value?.coefficient?.minRentDays || 8
  })

  const maxRentDays = computed(() => {
    return firstItemConfig.value?.coefficient?.maxRentDays || 100
  })

  // 租金提示
  const rentPriceTip = computed(() => {
    return firstItemConfig.value?.zeroRent?.activityRentDesc || '租金<=0.89更快出租'
  })

  // 押金提示
  const depositTip = computed(() => {
    return firstItemConfig.value?.zeroRent?.activityDepositDesc || '押金<=1299，优先展示'
  })

  // 服务费率
  const serviceFeeRate = computed(() => {
    const rate = firstItemConfig.value?.depositProtect?.rate
    return rate ? (rate * 100).toFixed(0) : '25'
  })

  const vipServiceFeeRate = computed(() => {
    const vipRate = firstItemConfig.value?.depositProtect?.vipRate
    return vipRate ? (vipRate * 100).toFixed(0) : null
  })

  // 检测赔付文本中是否有删除线（表示有折扣活动）
  const hasStrikethrough = computed(() => {
    if (!compensationRichText.value) {
      return false
    }
    // 检查HTML中是否包含 text-decoration: line-through
    return compensationRichText.value.includes('text-decoration: line-through')
  })

  // 是否可以启用0CD出租（需要同时满足：后端支持 + 有折扣活动）
  const canEnableZeroCD = computed(() => {
    return hasStrikethrough.value && firstItemConfig.value?.enableZeroCD === true
  })

  // 是否显示长租价格输入框（租期>21天时显示）
  const showLongRentPrice = computed(() => {
    const currentDays = formData.rentDays === 'custom' ? formData.customDays : formData.rentDays
    return currentDays && currentDays > 21
  })

  // 租送活动
  const rentActivities = computed(() => {
    if (!props.initData?.activityCustomConfigDTOList) {
      return []
    }
    return props.initData.activityCustomConfigDTOList.filter(
      activity => activity.activityType === 0 && activity.activityStatus === 0
    )
  })

  const rentActivityDesc = computed(() => {
    if (rentActivities.value.length === 0) {
      return ''
    }
    const activity = rentActivities.value[0]
    if (activity.activityItemList && activity.activityItemList.length > 0) {
      return activity.activityItemList.map(item => item.itemDesc).join('、')
    }
    return activity.activityDesc || ''
  })

  // 初始化表单数据（全局 + 每个饰品）
  const initForms = () => {
    // 全局租期默认值：优先使用当前租期，否则使用第一个选项
    if (props.items && props.items.length > 0 && props.items[0].currentRentDays) {
      formData.rentDays = props.items[0].currentRentDays
    } else if (rentDaysOptions.value.length > 0) {
      formData.rentDays = rentDaysOptions.value[0]
    }

    // 初始化每个饰品的价格表单，自动填充原有数据
    if (props.items && props.items.length > 0) {
      props.items.forEach((item) => {
        if (!itemFormMap[item.assetid]) {
          // 自动填充当前的租赁价格数据
          itemFormMap[item.assetid] = {
            shortRentPrice: item.currentShortRentPrice || '',
            longRentPrice: item.currentLongRentPrice || '',
            depositPrice: item.currentDepositPrice || item.weapon_classID?.yyyp_Price || ''
          }
        }
      })
    }
  }

  // 获取赔付文本
  const fetchCompensationText = async () => {
    console.log('[DEBUG] fetchCompensationText called')
    console.log('[DEBUG] props.items:', props.items)
    console.log('[DEBUG] props.steamId:', props.steamId)

    if (!props.items || props.items.length === 0) {
      console.log('[DEBUG] No items, returning early')
      return
    }

    try {
      // 使用第一个饰品的数据
      const firstItem = props.items[0]
      console.log('[DEBUG] firstItem:', firstItem)

      // 构建itemInfo
      const itemInfo = {
        abrade: String(firstItem.weapon_float || firstItem.float || '0'),
        leaseType: formData.tradeMode === 1 ? 0 : 1,  // 0=租赁, 1=可租可售
        marketHashName: firstItem.steam_hash_name || firstItem.name,
        marketPrice: String(firstItem.yyyp_Price || firstItem.weapon_classID?.yyyp_Price || '0'),
        pageSourceType: 10,
        paintSeed: parseInt(firstItem.paintseed || 0),
        steamAssetId: parseInt(firstItem.assetid || 0),
        supportEasyCompensation: false,
        templateId: parseInt(firstItem.weapon_classID?.yyyp_id || 0)
      }
      console.log('[DEBUG] itemInfo:', itemInfo)

      const requestBody = {
        steamId: props.steamId || '',
        itemInfo: itemInfo
      }
      console.log('[DEBUG] Request body:', requestBody)

      const apiUrl = `${window.location.origin.replace('9003', '9005')}/youping898SpiderV1/getCompensationText`
      console.log('[DEBUG] API URL:', apiUrl)

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      })

      console.log('[DEBUG] Response status:', response.status)
      const result = await response.json()
      console.log('[DEBUG] Response result:', result)

      if (result.success && result.data) {
        // 使用富文本HTML
        const richContent = result.data.compensationRichContent
        console.log('[DEBUG] Rich content:', richContent)
        if (richContent) {
          compensationRichText.value = richContent
          console.log('[DEBUG] Compensation text set successfully')
        }
      } else {
        console.log('[DEBUG] Response not successful or no data')
      }
    } catch (error) {
      console.error('[DEBUG] Error in fetchCompensationText:', error)
      // 失败时保留默认值
    }
  }

  watch(
    () => [props.initData, props.items],
    (newVal, oldVal) => {
      console.log('[DEBUG] Watch triggered')
      console.log('[DEBUG] New initData:', newVal[0])
      console.log('[DEBUG] New items:', newVal[1])
      console.log('[DEBUG] Old initData:', oldVal?.[0])
      console.log('[DEBUG] Old items:', oldVal?.[1])

      initForms()

      // 直接从 initData 中获取赔付文本（已在 handleRentPlatformSelect 中预加载）
      if (props.initData?.compensationRichContent) {
        compensationRichText.value = props.initData.compensationRichContent
        console.log('[DEBUG] 从 initData 加载赔付文本:', props.initData.compensationRichContent)

        // 检测是否有删除线，如果有则自动开启0CD
        if (hasStrikethrough.value && firstItemConfig.value?.enableZeroCD === true) {
          formData.services.zeroCooldown = true
          console.log('[DEBUG] 检测到折扣活动，自动开启0CD')
        } else {
          formData.services.zeroCooldown = false
          console.log('[DEBUG] 无折扣活动或不支持0CD，禁用0CD')
        }
      } else {
        // 如果 initData 中没有，则尝试请求API（降级方案）
        console.log('[DEBUG] initData 中没有赔付文本，尝试请求API')
        fetchCompensationText()
      }
    },
    { immediate: true, deep: true }
  )

  // 切换服务选项
  const toggleService = (serviceName) => {
    formData.services[serviceName] = !formData.services[serviceName]
  }

  // 处理图片加载错误
  const handleImageError = (e) => {
    e.target.style.display = 'none'
  }

  // 处理取消
  const handleCancel = () => {
    emit('cancel')
  }

  // 处理提交
  const handleSubmit = () => {
    // 验证表单
    if (!validateForm()) {
      return
    }

    // 准备提交数据（全局配置 + 每个饰品的独立价格）
    const submitData = {
      tradeMode: formData.tradeMode,
      rentDays: formData.rentDays === 'custom' ? formData.customDays : formData.rentDays,
      services: formData.services,
      items: props.items.map((item) => ({
        assetid: item.assetid,
        steam_hash_name: item.steam_hash_name,
        shortRentPrice: parseFloat(itemFormMap[item.assetid].shortRentPrice),
        longRentPrice: itemFormMap[item.assetid].longRentPrice
          ? parseFloat(itemFormMap[item.assetid].longRentPrice)
          : null,
        depositPrice: parseFloat(itemFormMap[item.assetid].depositPrice)
      }))
    }

    emit('submit', submitData)
  }

  // 表单验证
  const validateForm = () => {
    // 验证租赁天数
    if (formData.rentDays === 'custom') {
      if (!formData.customDays || formData.customDays <= 0) {
        ElMessage.warning('请输入有效的租赁天数')
        return false
      }
      if (formData.customDays < minRentDays.value || formData.customDays > maxRentDays.value) {
        ElMessage.warning(`租赁天数必须在 ${minRentDays.value}-${maxRentDays.value} 之间`)
        return false
      }
    }

    // 验证每个饰品的价格配置
    const minRent = firstItemConfig.value?.coefficient?.minRent
    const maxRent = firstItemConfig.value?.coefficient?.maxRent
    const minDeposit = firstItemConfig.value?.coefficient?.minDeposit
    const maxDeposit = firstItemConfig.value?.coefficient?.maxDeposit

    for (const item of props.items || []) {
      const itemForm = itemFormMap[item.assetid]
      if (!itemForm) continue

      // 短租租金必填
      if (!itemForm.shortRentPrice || itemForm.shortRentPrice === '') {
        ElMessage.warning(`【${item.name}】请输入短租租金`)
        return false
      }
      const shortRent = parseFloat(itemForm.shortRentPrice)
      if (isNaN(shortRent) || shortRent <= 0) {
        ElMessage.warning(`【${item.name}】请输入有效的短租租金`)
        return false
      }
      if (minRent && shortRent < parseFloat(minRent)) {
        ElMessage.warning(`【${item.name}】租金不能低于 ¥${minRent}/天`)
        return false
      }
      if (maxRent && shortRent > parseFloat(maxRent)) {
        ElMessage.warning(`【${item.name}】租金不能高于 ¥${maxRent}/天`)
        return false
      }

      // 押金必填
      if (!itemForm.depositPrice || itemForm.depositPrice === '') {
        ElMessage.warning(`【${item.name}】请输入商品押金`)
        return false
      }
      const deposit = parseFloat(itemForm.depositPrice)
      if (isNaN(deposit) || deposit <= 0) {
        ElMessage.warning(`【${item.name}】请输入有效的押金`)
        return false
      }
      if (minDeposit && deposit < parseFloat(minDeposit)) {
        ElMessage.warning(`【${item.name}】押金不能低于 ¥${minDeposit}`)
        return false
      }
      if (maxDeposit && deposit > parseFloat(maxDeposit)) {
        ElMessage.warning(`【${item.name}】押金不能高于 ¥${maxDeposit}`)
        return false
      }
    }

    return true
  }

  // 本地回退的一键定价逻辑（按购入价简单估算）
  const localAutoPricingFallback = () => {
    if (!props.items || props.items.length === 0) {
      ElMessage.warning('没有可定价的饰品')
      return 0
    }

    let successCount = 0

    props.items.forEach((item) => {
      const itemForm = itemFormMap[item.assetid]
      if (!itemForm) return

      const buyPrice = parseFloat(item.buyPrice || item.buy_price || 0)
      if (buyPrice > 0) {
        const shortRent = (buyPrice * 0.015).toFixed(2)
        itemForm.shortRentPrice = shortRent

        const longRent = (parseFloat(shortRent) * 0.8).toFixed(2)
        itemForm.longRentPrice = longRent

        const deposit = (buyPrice * 1.05).toFixed(2)
        itemForm.depositPrice = deposit

        successCount++
      }
    })

    return successCount
  }

  // 一键定价功能：优先调用后端自动定价接口，失败时回退到本地估算
  const handleAutoPricing = async () => {
    if (!props.items || props.items.length === 0) {
      ElMessage.warning('没有可定价的饰品')
      return
    }

    // 收集 steam_hash_name -> assetid 列表
    const hashNameSet = new Set()
    const hashToAssetIds = {}
    props.items.forEach(item => {
      const hashName = item.steam_hash_name || item.name
      if (!hashName) return
      hashNameSet.add(hashName)
      if (!hashToAssetIds[hashName]) {
        hashToAssetIds[hashName] = []
      }
      hashToAssetIds[hashName].push(item.assetid)
    })

    const steamHashNames = Array.from(hashNameSet)
    if (!steamHashNames.length) {
      ElMessage.warning('选中的饰品缺少 steam_hash_name，无法调用自动定价，将使用本地估算')
      const localCount = localAutoPricingFallback()
      if (localCount > 0) {
        ElMessage.success(`已为 ${localCount} 件饰品按购入价估算定价`)
      }
      return
    }

    autoPricingLoading.value = true
    try {
      const resp = await fetch(apiUrls.yyypRentAutoPricing(), {
        method: 'POST',
        mode: 'cors',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          steamId: props.steamId || '',
          steam_hash_name: steamHashNames
        })
      })

      if (!resp.ok) {
        throw new Error(`HTTP ${resp.status}`)
      }

      const result = await resp.json()
      if (!result.success) {
        ElMessage.error(result.message || '自动定价失败，将使用本地估算')
        const localCount = localAutoPricingFallback()
        if (localCount > 0) {
          ElMessage.success(`已为 ${localCount} 件饰品按购入价估算定价`)
        }
        return
      }

      const data = result.data || {}
      const pricingList = data.pricingInfoVos || []
      if (!pricingList.length) {
        ElMessage.warning('自动定价成功，但未返回任何定价数据，将使用本地估算')
        const localCount = localAutoPricingFallback()
        if (localCount > 0) {
          ElMessage.success(`已为 ${localCount} 件饰品按购入价估算定价`)
        }
        return
      }

      // 构建 commodityHashName -> 定价信息 映射
      const priceMap = {}
      pricingList.forEach(p => {
        if (!p.commodityHashName) return
        priceMap[p.commodityHashName] = {
          price: p.price,
          shortLeaseUnitPrice: p.shortLeaseUnitPrice,
          longLeaseUnitPrice: p.longLeaseUnitPrice,
          leaseDeposit: p.leaseDeposit,
          leaseMaxDays: p.leaseMaxDays
        }
      })

      let successCount = 0
      // 将定价结果写入每个饰品对应的表单
      Object.entries(hashToAssetIds).forEach(([hashName, assetIds]) => {
        const pricing = priceMap[hashName]
        if (!pricing) return

        assetIds.forEach(assetid => {
          const itemForm = itemFormMap[assetid]
          if (!itemForm) return

          const shortRent = parseFloat(pricing.shortLeaseUnitPrice || pricing.price || 0)
          const longRent = parseFloat(pricing.longLeaseUnitPrice || 0)
          const deposit = parseFloat(pricing.leaseDeposit || 0)

          if (shortRent > 0) {
            itemForm.shortRentPrice = shortRent.toFixed(2)
          }
          if (longRent > 0) {
            itemForm.longRentPrice = longRent.toFixed(2)
          }
          if (deposit > 0) {
            itemForm.depositPrice = deposit.toFixed(2)
          }

          successCount++
        })
      })

      if (successCount > 0) {
        ElMessage.success(`已为 ${successCount} 件饰品完成悠悠有品自动定价`)
      } else {
        ElMessage.warning('未能为当前饰品匹配到定价数据，将使用本地估算')
        const localCount = localAutoPricingFallback()
        if (localCount > 0) {
          ElMessage.success(`已为 ${localCount} 件饰品按购入价估算定价`)
        }
      }
    } catch (e) {
      console.error('悠悠有品自动定价接口异常:', e)
      ElMessage.error(`自动定价失败: ${e.message}，将使用本地估算`)
      const localCount = localAutoPricingFallback()
      if (localCount > 0) {
        ElMessage.success(`已为 ${localCount} 件饰品按购入价估算定价`)
      }
    } finally {
      autoPricingLoading.value = false
    }
  }

  return {
    formData,
    itemFormMap,
    tradeMethods,
    rentDaysOptions,
    minRentDays,
    maxRentDays,
    rentPriceTip,
    depositTip,
    serviceFeeRate,
    vipServiceFeeRate,
    compensationRichText,
    hasStrikethrough,
    canEnableZeroCD,
    showLongRentPrice,
    rentActivities,
    rentActivityDesc,
    toggleService,
    handleImageError,
    handleCancel,
    handleSubmit,
    handleAutoPricing,
    autoPricingLoading
  }
}
