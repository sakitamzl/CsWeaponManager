/**
 * SearchPendant组件的业务逻辑
 * 处理挂件搜索功能
 */
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import { API_CONFIG, apiUrls } from '@/config/api.js'

export function useSearchPendant() {
  const router = useRouter()
  const crawlFormRef = ref(null)
  const platformAccountLists = ref({})
  const accountLoadingStates = ref({})
  const isProgrammaticPlatformChange = ref(false)
  const isCrawling = ref(false)
  const crawlResult = ref(null)

  const pollingTimer = ref(null)
  const POLL_INTERVAL = 1000
  const noDataCount = ref(0)
  const MAX_NO_DATA_COUNT = 60
  const lastPollingTime = ref(0)

  const getItemIconUrl = (item) => {
    if (!item) return ''
    const raw = item.iconUrl ?? item.icon_url
    if (!raw) return ''
    const url = typeof raw === 'string' ? raw.trim() : ''
    if (!url) return ''
    if (url.startsWith('http://') || url.startsWith('https://')) {
      return url
    }
    if (url.startsWith('//')) {
      return `https:${url}`
    }
    return url
  }

  const parsePendants = (rawPendants) => {
    if (!rawPendants) {
      return []
    }
    if (Array.isArray(rawPendants)) {
      return rawPendants
    }
    if (typeof rawPendants === 'string') {
      try {
        const parsed = JSON.parse(rawPendants)
        return Array.isArray(parsed) ? parsed : []
      } catch (error) {
        console.warn('[挂件] 无法解析 pendants 字段:', rawPendants, error)
        return []
      }
    }
    return []
  }

  const normalizeApiItems = (items = []) => {
    return items.map(item => ({
    id: item.commodityId,
    commodityNo: item.commodityNo,
    price: parseFloat(item.price) || 0,
    lowest_price: parseFloat(item.lowestPrice) || 0,
    spread: parseFloat(item.spread) || 0,
    abrade: item.abrade,
    paintSeed: item.paintSeed,
    nameTag: item.nameTag,
    userNickName: item.sellerName,
    assetId: item.assetId,
    iconUrl: item.iconUrl || item.icon_url,
    weapon_name: item.weaponName,
    weaponName: item.weaponName,
    weaponId: item.weaponId,
    commissionFee: parseFloat(item.commissionFee) || 0,
    priceDiff: parseFloat(item.priceDiff) || 0,
    pendants: parsePendants(item.pendants),
    pendantTotalPrice: parseFloat(item.pendantTotalPrice) || 0,
    priceDiffPercentage: parseFloat(item.priceDiffPercentage) || 0
  }))
  }

  const rebuildCrawlResult = (items = []) => {
    const weaponGroups = {}
    items.forEach(item => {
      const weaponDisplayName = item.weapon_name || item.weaponName || '未知饰品'
      if (!weaponGroups[weaponDisplayName]) {
        weaponGroups[weaponDisplayName] = []
      }
      weaponGroups[weaponDisplayName].push(item)
    })

    const weapons = Object.keys(weaponGroups).map(name => ({
      weapon_name: name,
      items: weaponGroups[name]
    }))

    crawlResult.value = { weapons }
  }

  const loadRecentSearchResults = async () => {
  try {
    console.log('[挂件] 尝试加载历史结果...')
    // 获取搜索结果，根据选中的配置ID过滤
    const params = new URLSearchParams({
      dataType: 'pendant'
    })
    // 如果选中了配置，则只查询该配置的数据
    if (selectedConfigId.value) {
      params.append('configId', selectedConfigId.value.toString())
    }
    const response = await fetch(`${API_CONFIG.BASE_URL}/searchRename/items/list?${params.toString()}`)
    if (!response.ok) {
      console.warn('[挂件] 历史数据请求失败')
      return
    }
    const result = await response.json()
    if (result.success && Array.isArray(result.items) && result.items.length > 0) {
      const mappedItems = normalizeApiItems(result.items)
      rebuildCrawlResult(mappedItems)
      console.log(`[挂件] 已加载 ${mappedItems.length} 条历史结果`)
    } else {
      console.log('[挂件] 没有找到历史结果')
    }
  } catch (error) {
    console.error('[挂件] 加载历史数据失败:', error)
  }
  }

  const updateCrawlResultWithItems = (newItems) => {
    const currentItems = crawlResult.value?.weapons?.flatMap(weapon => weapon.items) || []
    const itemMap = new Map()
    currentItems.forEach(item => itemMap.set(item.id, item))
    newItems.forEach(item => itemMap.set(item.id, item))
    const mergedItems = Array.from(itemMap.values())
    mergedItems.sort((a, b) => {
      const diffA = a.priceDiff !== undefined ? a.priceDiff : -Infinity
      const diffB = b.priceDiff !== undefined ? b.priceDiff : -Infinity
      return diffB - diffA
    })
    rebuildCrawlResult(mergedItems)
  }

  const pollSearchResults = async () => {
  try {
    lastPollingTime.value = Date.now()
    // 获取所有数据，根据选中的配置ID过滤
    const params = new URLSearchParams({
      dataType: 'pendant'
    })
    // 如果选中了配置，则只查询该配置的数据
    if (selectedConfigId.value) {
      params.append('configId', selectedConfigId.value.toString())
    }
    const response = await fetch(`${API_CONFIG.BASE_URL}/searchRename/items/list?${params.toString()}`)
    if (!response.ok) {
      console.error('[挂件] 轮询失败: HTTP', response.status)
      return
    }
    const result = await response.json()
    
    // 如果没有查询到数据，直接返回，不进行其他操作
    if (!result.success || !Array.isArray(result.items) || result.items.length === 0) {
      return
    }
    
    if (result.items.length > 0) {
      const mappedItems = normalizeApiItems(result.items)
      updateCrawlResultWithItems(mappedItems)
      if (isCrawling.value) {
        noDataCount.value = 0
      }
    }
  } catch (error) {
    console.error('[挂件] 轮询出错:', error)
  }
  }

  const startPolling = () => {
  if (pollingTimer.value) {
    return
  }
  console.log(`[挂件] 启动轮询，间隔 ${POLL_INTERVAL}ms`)
  pollingTimer.value = setInterval(pollSearchResults, POLL_INTERVAL)
  pollSearchResults()
  }

  const stopPolling = () => {
  if (pollingTimer.value) {
    clearInterval(pollingTimer.value)
    pollingTimer.value = null
    console.log('[挂件] 已停止轮询')
  }
  }

  const clearCrawlHistory = async (skipConfirm = false) => {
  try {
    // 如果有选中的配置，只清空该配置的数据；否则清空所有数据
    const clearMessage = selectedConfigId.value
      ? '确定要清空当前配置的挂件搜索结果吗？此操作将删除该配置的所有挂件数据，不可恢复。'
      : '确定要清空所有挂件搜索结果吗？此操作不可恢复。'
    
    if (!skipConfirm) {
      await ElMessageBox.confirm(
        clearMessage,
        '确认清空',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
    }

    // 构建请求体
    const requestBody = {
      dataType: 'pendant'
    }
    
    // 如果有选中的配置，只清空该配置的数据
    if (selectedConfigId.value) {
      requestBody.configId = selectedConfigId.value
    }

    const response = await fetch(`${API_CONFIG.BASE_URL}/searchRename/clear`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody)
    })

    if (!response.ok) {
      throw new Error('清空失败')
    }

    const result = await response.json()
    if (result.success) {
      crawlResult.value = null
      purchasedItems.value.clear()
      if (!skipConfirm) {
        ElMessage.success(result.message || '已清空挂件数据')
      }
    } else {
      throw new Error(result.message || '清空失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清空挂件数据失败:', error)
      if (!skipConfirm) {
        ElMessage.error(error.message || '清空失败')
      }
    }
  }
  }

  // 合并所有武器的items到一个统一列表，并按差价从高到低排序
  const allCrawlItems = computed(() => {
    if (!crawlResult.value || !crawlResult.value.weapons) {
      return []
    }
    
    const items = []
    crawlResult.value.weapons.forEach(weapon => {
      if (weapon.items && weapon.items.length > 0) {
        weapon.items.forEach(item => {
          items.push({
            ...item,
            weapon_name: weapon.weapon_name,  // 添加武器名称
            weapon_id: weapon.weapon_id
          })
        })
      }
    })
    
    // 按差价从高到低排序
    items.sort((a, b) => {
      const diffA = a.priceDiff !== undefined ? a.priceDiff : -Infinity
      const diffB = b.priceDiff !== undefined ? b.priceDiff : -Infinity
      return diffB - diffA  // 从高到低
    })
    
    return items
  })

  // 配置管理相关
  const savedConfigs = ref([])
  const selectedConfigId = ref(null)

  // 饰品搜索相关
  const weaponSearchKeyword = ref('')
  const weaponSearchResults = ref([])
  const isSearchingWeapon = ref(false)
  const isLoadingMore = ref(false)  // 加载更多数据中
  const currentPage = ref(1)  // 当前页码
  const pageSize = ref(50)  // 每页数量
  const hasMore = ref(true)  // 是否还有更多数据
  const weaponSearchFilters = ref({
    weaponType: '',  // 武器类型筛选
    weaponName: '',  // 武器名称筛选
    rarity: '',      // 稀有度筛选
    priceMin: null,  // 最低价格
    priceMax: null,  // 最高价格
    minOnSaleCount: null  // 最小在售数量
  })
  const weaponNameList = ref([])  // 武器名称列表
  const isLoadingWeaponNames = ref(false)  // 加载武器名称中

  // 购买相关
  const buyingItems = ref({})  // 正在购买的商品 {itemId: true/false}
  const purchasedItems = ref(new Set())  // 已成功购买的商品ID集合

  // 工具与配置区域联动折叠状态
  const isConfigSectionsCollapsed = ref(false)
  const isSearchResultsCollapsed = ref(false)  // 搜索结果列表折叠状态
  const isWeaponListCollapsed = ref(true)  // 饰品列表折叠状态（默认折叠）

  const createDefaultCustomConfig = () => ({
  '饰品自动查询间隔': 3,
  '是否自动购买': false,
  '最大差价百分比': 80,
  '最大溢价': 200,
  '印花板': false,
  '收益不少于': 3
})

const booleanOptions = [
  { label: '是', value: true },
  { label: '否', value: false }
]

const customConfigForm = ref(createDefaultCustomConfig())
const isProgrammaticCustomConfigChange = ref(false)

const crawlForm = ref({
  configName: '',      // 对应 dataName
  steamId: '',         // 购买账号
  crawlAccountId: '',  // 爬取账号
  platformType: '',    // 平台类型：youpin 或 buff
  weaponId: []         // 改为数组，存储 {id, name} 对象
})

// 计算属性：获取饰品列表
const weaponIdList = computed(() => {
  return crawlForm.value.weaponId || []
})

// 计算是否可以开始爬取
const canStartCrawl = computed(() => {
  if (!crawlForm.value.configName) return false
  if (!crawlForm.value.platformType) return false
  if (!crawlForm.value.crawlAccountId) return false
  if (!crawlForm.value.steamId) return false
  if (!crawlForm.value.weaponId || crawlForm.value.weaponId.length === 0) return false
  return true
})

const normalizePlatformKey = (value) => {
  if (!value && value !== 0) return ''
  const normalized = value.toString().trim().toLowerCase()
  if (['youpin', 'yyyp', 'you_pin', 'you-pin', '悠悠有品'].some(k => normalized === k.toLowerCase())) {
    return 'youpin'
  }
  if (['buff', 'buff平台'].some(k => normalized === k.toLowerCase())) {
    return 'buff'
  }
  return normalized
}

const PLATFORM_ACCOUNT_SOURCE_MAP = {
  youpin: { key1: 'youpin', key2: 'config', label: '悠悠有品' },
  buff: { key1: 'buff', key2: 'config', label: 'BUFF' }
}

const filteredSteamIdList = computed(() => {
  const platformKey = normalizePlatformKey(crawlForm.value.platformType || '')
  if (!platformKey) {
    console.log('[账号列表] 未选择平台，返回空账号列表')
    return []
  }
  const accounts = platformAccountLists.value[platformKey] || []
  console.log(`[账号列表] 平台: ${platformKey}, 账号数量: ${accounts.length}`, accounts)
  return accounts
})

const loadAccountsForPlatform = async (platformType) => {
  const platformKey = normalizePlatformKey(platformType)
  if (!platformKey) {
    return
  }

  const sourceConfig = PLATFORM_ACCOUNT_SOURCE_MAP[platformKey]
  if (!sourceConfig) {
    console.warn(`[平台账号] 未配置平台 ${platformKey} 的数据源`)
    return
  }

  if (accountLoadingStates.value[platformKey]) {
    return
  }

  const cachedList = platformAccountLists.value[platformKey]
  if (cachedList && cachedList.length > 0) {
    return
  }

  accountLoadingStates.value = {
    ...accountLoadingStates.value,
    [platformKey]: true
  }

  try {
    const response = await axios.get(`${API_CONFIG.BASE_URL}/configV1/list`, {
      params: {
        key1: sourceConfig.key1,
        key2: sourceConfig.key2
      }
    })
    console.log(`[平台账号] ${platformKey} 配置API响应:`, response.data)
    if (response.data.success && Array.isArray(response.data.data)) {
      const mappedList = response.data.data.map(item => {
        let parsedValue = {}
        if (item.value) {
          try {
            parsedValue = typeof item.value === 'string'
              ? JSON.parse(item.value)
              : (item.value || {})
          } catch (parseError) {
            console.error(`[平台账号] 解析配置 value 失败 (${platformKey}):`, parseError)
          }
        }
        const steamId = parsedValue.steam_id || parsedValue.steamId || item.steamId || item.steamID || ''
        const displayName = item.dataName || parsedValue.accountName || parsedValue.name || `配置账号 #${item.id}`
        return {
          ...item,
          steamID: steamId,
          steam_id: steamId,
          dataName: displayName,
          platformKey,
          platformLabel: sourceConfig.label,
          rawConfig: parsedValue
        }
      })

      platformAccountLists.value = {
        ...platformAccountLists.value,
        [platformKey]: mappedList
      }
    }
  } catch (error) {
    console.error(`[平台账号] 加载 ${platformKey} 账号配置失败:`, error)
  } finally {
    accountLoadingStates.value = {
      ...accountLoadingStates.value,
      [platformKey]: false
    }
  }
}

const resetCustomConfigForm = () => {
  isProgrammaticCustomConfigChange.value = true
  customConfigForm.value = createDefaultCustomConfig()
  nextTick(() => {
    isProgrammaticCustomConfigChange.value = false
  })
}

const normalizeBooleanValue = (value, defaultValue) => {
  if (value === true || value === false) return value
  if (typeof value === 'string') {
    const normalized = value.trim().toLowerCase()
    if (['true', '1', '是', 'yes', 'y'].includes(normalized)) return true
    if (['false', '0', '否', 'no', 'n'].includes(normalized)) return false
  }
  return defaultValue
}

const normalizeNumberValue = (value, defaultValue) => {
  const num = Number(value)
  return Number.isFinite(num) ? num : defaultValue
}

const buildCustomConfig = () => ({
  '饰品自动查询间隔': normalizeNumberValue(
    customConfigForm.value['饰品自动查询间隔'],
    3
  ),
  '是否自动购买': normalizeBooleanValue(
    customConfigForm.value['是否自动购买'],
    false
  ),
  '最大差价百分比': normalizeNumberValue(
    customConfigForm.value['最大差价百分比'],
    80
  ),
  '最大溢价': normalizeNumberValue(
    customConfigForm.value['最大溢价'],
    200
  ),
  '印花板': normalizeBooleanValue(
    customConfigForm.value['印花板'],
    false
  ),
  '收益不少于': normalizeNumberValue(
    customConfigForm.value['收益不少于'],
    0
  ),
  '是否授权': true
})

const validateCustomConfig = () => {
  const config = buildCustomConfig()

  if (config['饰品自动查询间隔'] <= 0) {
    return { valid: false, message: '查询间隔必须大于 0 秒' }
  }
  if (config['最大差价百分比'] < 0) {
    return { valid: false, message: '最大差价百分比不能为负数' }
  }
  if (config['最大溢价'] < 0) {
    return { valid: false, message: '最大溢价不能为负数' }
  }

  return { valid: true, config }
}

const applyCustomConfig = (config = {}) => {
  const defaults = createDefaultCustomConfig()
  isProgrammaticCustomConfigChange.value = true
  customConfigForm.value = {
    '饰品自动查询间隔': normalizeNumberValue(
      config['饰品自动查询间隔'],
      defaults['饰品自动查询间隔']
    ),
    '是否自动购买': normalizeBooleanValue(
      config['是否自动购买'],
      defaults['是否自动购买']
    ),
    '最大差价百分比': normalizeNumberValue(
      config['最大差价百分比'],
      defaults['最大差价百分比']
    ),
    '最大溢价': normalizeNumberValue(
      config['最大溢价'],
      defaults['最大溢价']
    ),
    '印花板': normalizeBooleanValue(
      config['印花板'],
      defaults['印花板']
    ),
    '收益不少于': normalizeNumberValue(
      config['收益不少于'],
      defaults['收益不少于']
    )
  }
  nextTick(() => {
    isProgrammaticCustomConfigChange.value = false
  })
}

// 联动切换配置管理与爬取配置
const toggleConfigSections = () => {
  isConfigSectionsCollapsed.value = !isConfigSectionsCollapsed.value
}

// 切换搜索结果列表显示/隐藏
const toggleSearchResults = () => {
  isSearchResultsCollapsed.value = !isSearchResultsCollapsed.value
}

// 切换饰品列表显示/隐藏
const toggleWeaponList = () => {
  isWeaponListCollapsed.value = !isWeaponListCollapsed.value
}

const handleSidebarAreaClick = (event) => {
  const target = event.target
  if (!target) return

  if (target.closest && target.closest('.config-item')) {
    return
  }

  toggleConfigSections()
}

// 开始爬取（流式接收）
const startCrawl = async () => {
  // 开始搜索时自动折叠工具与配置区域
  isConfigSectionsCollapsed.value = true
  // 清空已购买记录
  purchasedItems.value.clear()
  // 验证基本配置
  if (!crawlForm.value.configName) {
    ElMessage.warning('请输入配置名称')
    return
  }

  if (!crawlForm.value.platformType) {
    ElMessage.warning('请选择平台类型')
    return
  }
  
  if (!crawlForm.value.crawlAccountId) {
    ElMessage.warning('请选择爬取账号')
    return
  }
  
  if (!crawlForm.value.steamId) {
    ElMessage.warning('请选择购买账号')
    return
  }
  
  if (!crawlForm.value.weaponId || crawlForm.value.weaponId.length === 0) {
    ElMessage.warning('请至少添加一个饰品ID')
    return
  }

  // 验证自定义配置
  const customConfigResult = validateCustomConfig()
  if (!customConfigResult.valid) {
    ElMessage.error(customConfigResult.message)
    return
  }
  const customConfig = customConfigResult.config

  // 确认对话框
  try {
    let confirmMessage = `确定要开始查询带挂件饰品吗？\n\n`
    confirmMessage += `配置名称: ${crawlForm.value.configName}\n`
    confirmMessage += `爬取账号: ${crawlForm.value.crawlAccountId}\n`
    confirmMessage += `购买账号: ${crawlForm.value.steamId}\n`
    confirmMessage += `平台类型: ${getSourceLabel(crawlForm.value.platformType)}\n`
    confirmMessage += `监控饰品数量: ${crawlForm.value.weaponId.length} 个`
    
    confirmMessage += `\n查询间隔: ${customConfig['饰品自动查询间隔']} 秒`
    confirmMessage += `\n自动购买: ${customConfig['是否自动购买'] ? '是' : '否'}`
    confirmMessage += `\n最大差价百分比: ${customConfig['最大差价百分比']}%`
    confirmMessage += `\n最大溢价: ${customConfig['最大溢价']} 元`
    confirmMessage += `\n印花板: ${customConfig['印花板'] ? '是' : '否'}`
    confirmMessage += `\n收益不少于: ${customConfig['收益不少于']} 元`

    await ElMessageBox.confirm(
      confirmMessage,
      '确认执行',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
  } catch {
    return
  }

  await clearCrawlHistory(true)
  isCrawling.value = true
  crawlResult.value = { weapons: [] }
  noDataCount.value = 0
  ElMessage.info('正在启动查询任务...')
  startPolling()
  pollSearchResults()

  try {
    const spiderConfig = {
      weapon_id: crawlForm.value.weaponId,
      steam_id: crawlForm.value.crawlAccountId,
      最大差价: 5,
      饰品自动查询间隔: 3,
      ...customConfig
    }
    
    // 如果有选中的配置ID，传递给后端
    if (selectedConfigId.value) {
      spiderConfig.config_id = selectedConfigId.value
    }

    const requestData = {
      steamId: crawlForm.value.crawlAccountId,
      spider_config: spiderConfig
    }

    fetch(
      `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/auto_buy_pendant_weapon`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
      }
    ).then(async response => {
      let result = null
      try {
        result = await response.json()
      } catch (parseError) {
        console.warn('[挂件] 响应解析失败:', parseError)
      }

      if (!response.ok || !result?.success) {
        const errMsg = result?.message || `HTTP ${response.status}`
        throw new Error(errMsg)
      }

      console.log('[挂件] 搜索任务响应:', result)
    }).catch(error => {
      console.error('[挂件] 搜索任务启动失败:', error)
      ElMessage.error(`启动搜索失败: ${error.message}`)
      isCrawling.value = false
    })

    setTimeout(() => {
      if (isCrawling.value) {
        console.log('[挂件] 搜索超时，结束搜索状态')
        isCrawling.value = false
        const totalItems = crawlResult.value?.weapons?.flatMap(w => w.items).length || 0
        ElMessage.warning(`搜索已超时结束，找到 ${totalItems} 个商品`)
      }
    }, 5 * 60 * 1000)

  } catch (error) {
    console.error('搜索失败:', error)
    ElMessage.error(error.message || '搜索失败')
    isCrawling.value = false
  }
}

// 停止搜索
const stopCrawl = async () => {
  if (!isCrawling.value) {
    ElMessage.warning('当前没有正在进行的搜索任务')
    return
  }

  if (!selectedConfigId.value) {
    ElMessage.error('无法停止：未找到配置ID')
    return
  }

  try {
    ElMessage.info('正在停止搜索...')

    const response = await fetch(
      `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/stop_pendant_search`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          config_id: selectedConfigId.value
        })
      }
    )

    const result = await response.json()

    if (!response.ok || !result?.success) {
      throw new Error(result?.message || `HTTP ${response.status}`)
    }

    ElMessage.success('停止信号已发送')
    // 延迟一下再设置状态，等待后端响应
    setTimeout(() => {
      isCrawling.value = false
    }, 500)

  } catch (error) {
    console.error('停止搜索失败:', error)
    ElMessage.error(`停止失败: ${error.message}`)
  }
}

// 重置表单
const resetForm = () => {
  isProgrammaticPlatformChange.value = true
  crawlForm.value = {
    configName: '',
    steamId: '',
    crawlAccountId: '',
    platformType: '',
    weaponId: []
  }
  crawlResult.value = null
  resetCustomConfigForm()
}

const getSourceLabel = (source) => {
  const labels = {
    youpin: '悠悠有品',
    buff: 'BUFF',
    steam: 'Steam库存'
  }
  if (!source) {
    return '未设置'
  }
  return labels[source] || source
}

// 加载配置列表
const loadConfigList = async () => {
  try {
    // 只加载 key1 = 'spider_pendant' 的配置
    const response = await axios.get(`${API_CONFIG.BASE_URL}/configV1/list`, {
      params: {
        key1: 'spider_pendant'
      }
    })
    
    console.log('配置列表响应:', response.data)
    
    // 保存平台类型
    savedConfigs.value = (response.data.data || []).map(config => ({
      ...config,
      platformType: config.key2 || ''
    }))
    
    // 按ID降序排序
    savedConfigs.value.sort((a, b) => b.id - a.id)
    
    console.log('加载的配置列表:', savedConfigs.value)
  } catch (error) {
    console.error('加载配置列表失败:', error)
  }
}

// 选择并加载配置
const selectConfig = async (configId) => {
  console.log('=== 开始加载配置 ===')
  console.log('配置ID:', configId)
  
  if (!configId) {
    console.warn('配置ID为空')
    return
  }

  selectedConfigId.value = configId
  console.log('已设置selectedConfigId:', selectedConfigId.value)
  
  // 切换配置时，先清空当前结果，避免显示混合数据
  crawlResult.value = { weapons: [] }

  try {
    const config = savedConfigs.value.find(c => c.id === configId)
    console.log('找到的配置对象:', config)
    
    if (config && config.value) {
      const platformType = config.platformType || ''
      if (platformType) {
        await loadAccountsForPlatform(platformType)
      }
      // 解析 value 字段（JSON字符串）
      let valueObj
      try {
        valueObj = typeof config.value === 'string' 
          ? JSON.parse(config.value) 
          : config.value
        console.log('解析后的配置值:', valueObj)
      } catch (parseError) {
        console.error('JSON解析失败:', parseError)
        ElMessage.error('配置数据格式错误')
        return
      }
      
      // 从 value 对象中提取饰品列表和Steam ID
      const weaponId = valueObj.weapon_id || []
      const steamId = valueObj.steam_id || ''
      
      console.log('提取的数据:')
      console.log('  - weaponId:', weaponId)
      console.log('  - steamId:', steamId)
      console.log('  - platformType:', config.platformType)
      
      // 移除 weapon_id 和 steam_id，剩余的作为自定义配置
      const { weapon_id, steam_id, crawl_account_id, ...restConfig } = valueObj
      
      // 构建新的表单数据
      const newFormData = {
        configName: config.dataName || '',
        steamId: steamId,
        crawlAccountId: crawl_account_id || steamId || '',
        platformType: platformType,
        weaponId: Array.isArray(weaponId) ? weaponId : []
      }
      
      console.log('准备填充的表单数据:', newFormData)
      
      // 加载配置数据到表单
      isProgrammaticPlatformChange.value = true
      crawlForm.value = newFormData
      applyCustomConfig(restConfig)
      
      // 等待下一个tick确保数据已更新
      await new Promise(resolve => setTimeout(resolve, 50))
      
      console.log('表单填充完成，当前表单值:')
      console.log('  - configName:', crawlForm.value.configName)
      console.log('  - steamId:', crawlForm.value.steamId)
      console.log('  - platformType:', crawlForm.value.platformType)
      console.log('  - weaponId:', crawlForm.value.weaponId)
      console.log('=== 配置加载完成 ===')
      
      // 选择配置后，启动轮询并立即刷新结果列表（显示该配置的数据）
      startPolling()
      await pollSearchResults()
      
      ElMessage.success(`已加载配置: ${config.dataName}`)
    } else {
      console.warn('配置缺少value字段:', config)
      ElMessage.warning('配置数据为空')
    }
  } catch (error) {
    console.error('加载配置失败:', error)
    console.error('错误堆栈:', error.stack)
    ElMessage.error(`加载配置失败: ${error.message}`)
  }
}

// 创建新配置（清空表单）
const createNewConfig = () => {
  selectedConfigId.value = null
  resetForm()
  ElMessage.info('已清空表单，可以创建新配置')
}

// 平台类型改变处理
const handlePlatformTypeChange = async () => {
  if (isProgrammaticPlatformChange.value) {
    isProgrammaticPlatformChange.value = false
  } else {
    crawlForm.value.crawlAccountId = ''
    crawlForm.value.steamId = ''
  }
  
  if (crawlForm.value.platformType) {
    await loadAccountsForPlatform(crawlForm.value.platformType)
  }
  
  if (selectedConfigId.value) {
    autoSaveConfig()
  }
}

// 自动保存配置
const autoSaveConfig = async () => {
  if (!selectedConfigId.value) {
    return
  }

  if (!crawlForm.value.configName || !crawlForm.value.platformType) {
    return
  }

  try {
    const customConfigResult = validateCustomConfig()
    if (!customConfigResult.valid) {
      console.log('自定义配置错误，跳过自动保存:', customConfigResult.message)
      return
    }

    const valueObj = {
      weapon_id: crawlForm.value.weaponId,
      steam_id: crawlForm.value.steamId,
      crawl_account_id: crawlForm.value.crawlAccountId,
      ...customConfigResult.config
    }

    const key2 = crawlForm.value.platformType

    const configData = {
      id: selectedConfigId.value,
      dataName: crawlForm.value.configName,
      key1: 'spider_pendant',
      key2: key2,
      value: JSON.stringify(valueObj)
    }

    const response = await axios.post(`${API_CONFIG.BASE_URL}/webConfigV1/updateConfig`, configData)
    
    if (response.data.success) {
      console.log('配置已自动保存')
    }
  } catch (error) {
    console.error('自动保存失败:', error)
  }
}

watch(
  customConfigForm,
  () => {
    if (isProgrammaticCustomConfigChange.value) {
      return
    }
    if (selectedConfigId.value) {
      autoSaveConfig()
    }
  },
  { deep: true }
)

// 保存配置（直接保存，不弹窗）
const saveConfig = async () => {
  if (!crawlForm.value.configName) {
    ElMessage.warning('请输入配置名称')
    return
  }

  if (!crawlForm.value.platformType) {
    ElMessage.warning('请选择平台类型')
    return
  }

  try {
    const customConfigResult = validateCustomConfig()
    if (!customConfigResult.valid) {
      ElMessage.error(customConfigResult.message)
      return
    }

    // 构建 value 对象
    let valueObj = { ...customConfigResult.config }
    
    // 将饰品列表添加到 value 对象中
    if (crawlForm.value.weaponId && crawlForm.value.weaponId.length > 0) {
      valueObj.weapon_id = crawlForm.value.weaponId
    }
    
    // 添加其他必要字段
    if (crawlForm.value.steamId) {
      valueObj.steam_id = crawlForm.value.steamId
    }
    if (crawlForm.value.crawlAccountId) {
      valueObj.crawl_account_id = crawlForm.value.crawlAccountId
    }

    // 根据平台类型设置 key2
    const key2 = crawlForm.value.platformType

    const configData = {
      dataName: crawlForm.value.configName,
      key1: 'spider_pendant',
      key2: key2,
      value: JSON.stringify(valueObj)
    }

    const isUpdating = !!selectedConfigId.value
    let response

    if (isUpdating) {
      configData.id = selectedConfigId.value
      response = await axios.post(`${API_CONFIG.BASE_URL}/configV1/update`, configData)
    } else {
      response = await axios.post(`${API_CONFIG.BASE_URL}/configV1/save`, configData)
    }
    
    if (response.data.success) {
      ElMessage.success(isUpdating ? '更新配置成功' : '保存配置成功')
      
      // 重新加载配置列表
      await loadConfigList()

      if (isUpdating && selectedConfigId.value) {
        await selectConfig(selectedConfigId.value)
      } else if (!isUpdating) {
        const newId = response.data.data?.id
        if (newId) {
          selectedConfigId.value = newId
          await selectConfig(newId)
        }
      }
    } else {
      throw new Error(response.data.message || '保存配置失败')
    }
  } catch (error) {
    console.error('保存配置失败:', error)
    const errorMessage = error.response?.data?.message || error.message || '保存配置失败'
    ElMessage.error(errorMessage)
  }
}

// 删除当前配置
const deleteCurrentConfig = async () => {
  if (!selectedConfigId.value) {
    ElMessage.warning('请先选择一个配置')
    return
  }
  await deleteConfig(selectedConfigId.value)
}

const deleteConfig = async (configId) => {
  if (!configId) {
    return
  }

  try {
    const config = savedConfigs.value.find(c => c.id === configId)
    
    await ElMessageBox.confirm(
      `确定要删除配置 "${config.dataName}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const response = await axios.delete(`${API_CONFIG.BASE_URL}/configV1/delete/${configId}`)
    
    if (response.data.success) {
      ElMessage.success('删除配置成功')
      
      // 如果删除的是当前选中的配置，清空选中状态
      if (selectedConfigId.value === configId) {
        selectedConfigId.value = null
      }
      
      // 重新加载配置列表
      await loadConfigList()
    } else {
      throw new Error(response.data.message || '删除配置失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除配置失败:', error)
      const errorMessage = error.response?.data?.message || error.message || '删除配置失败'
      ElMessage.error(errorMessage)
    }
  }
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 武器类型改变时，加载对应的武器名称列表
const handleWeaponTypeChange = async (weaponType) => {
  // 清空武器名称选择
  weaponSearchFilters.value.weaponName = ''
  weaponNameList.value = []
  
  // 无论是否选择武器类型，都加载武器名称列表
  await loadWeaponNames(weaponType)
}

// 加载武器名称列表
const loadWeaponNames = async (weaponType) => {
  isLoadingWeaponNames.value = true
  
  try {
    const params = {}
    
    // 如果指定了武器类型，添加到参数中；否则获取全部
    if (weaponType) {
      params.weaponType = weaponType
    }
    
    const response = await axios.get(`${API_CONFIG.BASE_URL}/webSelectWeaponV1/getWeaponNames`, {
      params: params
    })
    
    if (response.data.success) {
      weaponNameList.value = response.data.data || []
      console.log(`✅ 加载武器名称列表: ${weaponNameList.value.length} 个`, weaponType ? `(类型: ${weaponType})` : '(全部)')
    } else {
      ElMessage.error('获取武器名称失败')
    }
  } catch (error) {
    console.error('获取武器名称失败:', error)
    ElMessage.error('获取武器名称失败')
  } finally {
    isLoadingWeaponNames.value = false
  }
}

// 武器名称下拉框聚焦时，如果列表为空且没有选择武器类型，加载全部武器名称
const loadWeaponNamesIfNeeded = async () => {
  // 如果已经有数据，不重复加载
  if (weaponNameList.value.length > 0) {
    return
  }
  
  // 如果没有选择武器类型，加载全部武器名称
  if (!weaponSearchFilters.value.weaponType) {
    await loadWeaponNames(null)
  }
}

// 搜索饰品（重置并开始新搜索）
const handleSearchWeapon = async () => {
  // 验证价格区间
  if (weaponSearchFilters.value.priceMin !== null && 
      weaponSearchFilters.value.priceMax !== null &&
      weaponSearchFilters.value.priceMin > weaponSearchFilters.value.priceMax) {
    ElMessage.warning('最低价格不能大于最高价格')
    return
  }
  
  // 重置分页状态
  currentPage.value = 1
  weaponSearchResults.value = []
  hasMore.value = true
  
  // 执行搜索
  await loadWeaponData()
}

// 加载饰品数据
const loadWeaponData = async () => {
  if (!hasMore.value && currentPage.value > 1) {
    return
  }
  
  const loading = currentPage.value === 1
  if (loading) {
    isSearchingWeapon.value = true
  } else {
    isLoadingMore.value = true
  }
  
  try {
    const params = {
      page: currentPage.value,
      limit: pageSize.value
    }
    
    // 使用爬取配置中的平台类型
    params.platformType = crawlForm.value.platformType
    
    // 添加关键词（如果有）
    if (weaponSearchKeyword.value.trim()) {
      params.keyword = weaponSearchKeyword.value.trim()
    }
    
    // 如果选择了武器类型，添加到查询参数
    if (weaponSearchFilters.value.weaponType) {
      params.weaponType = weaponSearchFilters.value.weaponType
    }
    
    // 如果选择了武器名称，添加到查询参数
    if (weaponSearchFilters.value.weaponName) {
      params.weaponName = weaponSearchFilters.value.weaponName
    }
    
    // 如果选择了稀有度，添加到查询参数
    if (weaponSearchFilters.value.rarity) {
      params.rarity = weaponSearchFilters.value.rarity
    }
    
    // 如果设置了最低价格，添加到查询参数
    if (weaponSearchFilters.value.priceMin !== null && weaponSearchFilters.value.priceMin !== '') {
      params.priceMin = weaponSearchFilters.value.priceMin
    }
    
    // 如果设置了最高价格，添加到查询参数
    if (weaponSearchFilters.value.priceMax !== null && weaponSearchFilters.value.priceMax !== '') {
      params.priceMax = weaponSearchFilters.value.priceMax
    }
    
    // 如果设置了最小在售数量，添加到查询参数
    if (weaponSearchFilters.value.minOnSaleCount !== null && weaponSearchFilters.value.minOnSaleCount !== '') {
      params.minOnSaleCount = weaponSearchFilters.value.minOnSaleCount
    }
    
    const response = await axios.get(`${API_CONFIG.BASE_URL}/webSelectWeaponV1/searchWeaponDetail`, {
      params: params
    })
    
    if (response.data.success) {
      const newData = response.data.data || []
      const total = response.data.total || 0
      
      console.log('📦 加载数据响应', {
        page: currentPage.value,
        newDataLength: newData.length,
        total,
        pageSize: pageSize.value
      })
      
      if (currentPage.value === 1) {
        weaponSearchResults.value = newData
        if (newData.length === 0) {
          ElMessage.info('未找到匹配的饰品')
          hasMore.value = false
        } else {
          ElMessage.success(`找到 ${total} 件饰品，已加载 ${newData.length} 件`)
        }
      } else {
        weaponSearchResults.value.push(...newData)
        console.log(`📥 追加 ${newData.length} 条数据，总计 ${weaponSearchResults.value.length} 条`)
      }
      
      // 判断是否还有更多数据
      const hasMoreData = newData.length >= pageSize.value
      hasMore.value = hasMoreData
      
      console.log('📊 加载状态', {
        hasMore: hasMore.value,
        currentTotal: weaponSearchResults.value.length,
        newDataLength: newData.length,
        pageSize: pageSize.value
      })
      
    } else {
      ElMessage.error(response.data.message || '搜索失败')
    }
  } catch (error) {
    console.error('搜索饰品失败:', error)
    const errorMessage = error.response?.data?.message || error.message || '搜索饰品失败'
    ElMessage.error(errorMessage)
  } finally {
    isSearchingWeapon.value = false
    isLoadingMore.value = false
  }
}

// 加载更多数据
const loadMoreWeapons = async () => {
  if (isLoadingMore.value || !hasMore.value) {
    return
  }
  
  // 记录加载前的滚动位置和页面高度
  const oldScrollHeight = document.documentElement.scrollHeight
  const oldScrollTop = window.pageYOffset || document.documentElement.scrollTop
  
  console.log('🔄 开始加载更多', {
    currentPage: currentPage.value,
    oldScrollHeight,
    oldScrollTop
  })
  
  currentPage.value++
  await loadWeaponData()
  
  // 等待 DOM 更新后调整滚动位置
  await nextTick()
  
  // 加载完成后，将滚动位置向上调整，避免立即触发下一次加载
  const newScrollHeight = document.documentElement.scrollHeight
  const addedHeight = newScrollHeight - oldScrollHeight
  
  if (addedHeight > 0 && hasMore.value) {
    // 将滚动位置设置到距离底部 300px 的位置
    const clientHeight = window.innerHeight
    const targetScrollTop = newScrollHeight - clientHeight - 300
    
    // 确保新的滚动位置不会小于原来的位置
    if (targetScrollTop > oldScrollTop) {
      window.scrollTo({
        top: targetScrollTop,
        behavior: 'auto'  // 使用 auto 立即跳转，不使用平滑滚动
      })
      
      console.log('📍 调整滚动位置', {
        oldScrollHeight,
        newScrollHeight,
        addedHeight,
        oldScrollTop,
        targetScrollTop,
        distanceToBottom: newScrollHeight - targetScrollTop - clientHeight
      })
    }
  }
}

// 页面滚动事件处理
let scrollTimer = null
const handlePageScroll = () => {
  // 如果没有搜索结果，不处理滚动
  if (weaponSearchResults.value.length === 0) {
    console.log('❌ 跳过滚动检查：没有搜索结果')
    return
  }
  
  // 只有在爬取配置区域是展开状态时，才触发自动加载
  if (isConfigSectionsCollapsed.value) {
    console.log('❌ 跳过滚动检查：配置区域已收起')
    return
  }
  
  // 防抖处理，避免频繁触发
  if (scrollTimer) {
    clearTimeout(scrollTimer)
  }
  
  scrollTimer = setTimeout(() => {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop
    const scrollHeight = document.documentElement.scrollHeight
    const clientHeight = window.innerHeight
    const distanceToBottom = scrollHeight - scrollTop - clientHeight
    
    console.log('📏 滚动位置检查', {
      scrollTop: Math.round(scrollTop),
      scrollHeight,
      clientHeight,
      distanceToBottom: Math.round(distanceToBottom),
      hasMore: hasMore.value,
      isLoadingMore: isLoadingMore.value,
      isConfigSectionsCollapsed: isConfigSectionsCollapsed.value,
      currentPage: currentPage.value,
      resultsCount: weaponSearchResults.value.length
    })
    
    // 滚动到底部触发加载更多（距离底部200px时触发）
    if (distanceToBottom < 200 && hasMore.value && !isLoadingMore.value) {
      console.log('✅ 触发加载更多数据')
      loadMoreWeapons()
    } else {
      console.log('⏸️ 未触发加载', {
        '距离是否<200': distanceToBottom < 200,
        '有更多数据': hasMore.value,
        '未在加载中': !isLoadingMore.value
      })
    }
  }, 100) // 100ms 防抖延迟
}

// 清除搜索结果
const clearWeaponSearch = () => {
  weaponSearchResults.value = []
  weaponSearchKeyword.value = ''
  weaponSearchFilters.value.weaponType = ''
  weaponSearchFilters.value.weaponName = ''
  weaponSearchFilters.value.rarity = ''
  weaponSearchFilters.value.priceMin = null
  weaponSearchFilters.value.priceMax = null
  weaponNameList.value = []
  currentPage.value = 1
  hasMore.value = true
}

// 根据平台类型获取对应的饰品ID
const getWeaponIdByPlatform = (row) => {
  if (crawlForm.value.platformType === 'buff') {
    return row.buff_id || row.yyyp_id || row.id || ''
  }
  if (crawlForm.value.platformType === 'youpin') {
    return row.yyyp_id || row.buff_id || row.id || ''
  }
  return row.yyyp_id || row.buff_id || row.id || ''
}

// 添加饰品ID到表单
// 从搜索组件添加单个饰品
const handleAddWeaponFromSearch = ({ id, name }) => {
  if (!id || !name) {
    ElMessage.warning('无效的饰品数据')
    return
  }

  // 检查是否已存在
  if (crawlForm.value.weaponId.some(w => w.id === id.toString())) {
    ElMessage.warning('该饰品已存在')
    return
  }

  // 添加饰品对象
  crawlForm.value.weaponId.push({
    id: id.toString(),
    name: name
  })

  ElMessage.success('饰品已添加')

  // 自动保存配置
  if (selectedConfigId.value) {
    autoSaveConfig()
  }
}

// 从搜索组件一键添加全部饰品
const handleAddAllWeaponsFromSearch = (weaponsToAdd) => {
  if (!weaponsToAdd || weaponsToAdd.length === 0) {
    ElMessage.warning('没有可添加的饰品')
    return
  }

  let addedCount = 0
  weaponsToAdd.forEach(({ id, name }) => {
    if (id && name) {
      // 检查是否已存在
      const exists = crawlForm.value.weaponId.some(w => w.id === id.toString())
      if (!exists) {
        crawlForm.value.weaponId.push({ id: id.toString(), name })
        addedCount++
      }
    }
  })

  if (addedCount > 0) {
    ElMessage.success(`成功添加 ${addedCount} 个饰品ID`)

    // 自动保存配置
    if (selectedConfigId.value) {
      autoSaveConfig()
    }
  } else {
    ElMessage.info('所有饰品ID已存在')
  }
}

const addWeaponId = (row) => {
  if (!crawlForm.value.platformType) {
    ElMessage.warning('请先选择平台类型')
    return
  }

  const weaponId = getWeaponIdByPlatform(row)
  
  if (!weaponId) {
    const platformName = getSourceLabel(crawlForm.value.platformType) || '当前平台'
    ElMessage.warning(`该饰品没有${platformName}ID`)
    return
  }

  // 检查是否已存在
  if (crawlForm.value.weaponId.some(w => w.id === weaponId.toString())) {
    ElMessage.warning('该饰品已存在')
    return
  }
  
  // 添加饰品对象（包含ID和名称）
  crawlForm.value.weaponId.push({
    id: weaponId.toString(),
    name: row.market_listing_item_name || row.name || '未知饰品'
  })

  const platformName = getSourceLabel(crawlForm.value.platformType) || '当前平台'
  ElMessage.success(`已添加${platformName}饰品: ${row.market_listing_item_name || row.name}`)
}

// 一键添加全部饰品ID
const addAllWeaponIds = async () => {
  if (!crawlForm.value.platformType) {
    ElMessage.warning('请先选择平台类型')
    return
  }

  if (!weaponSearchResults.value || weaponSearchResults.value.length === 0) {
    ElMessage.warning('没有可添加的饰品')
    return
  }

  try {
    const platformName = getSourceLabel(crawlForm.value.platformType) || '当前平台'
    
    await ElMessageBox.confirm(
      `确定要添加全部 ${weaponSearchResults.value.length} 个饰品吗？`,
      '确认添加',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    )

    let addedCount = 0
    let skippedCount = 0
    let noIdCount = 0

    weaponSearchResults.value.forEach(row => {
      const weaponId = getWeaponIdByPlatform(row)
      
      // 没有ID的跳过
      if (!weaponId) {
        noIdCount++
        return
      }

      // 已存在的跳过
      if (crawlForm.value.weaponId.some(w => w.id === weaponId.toString())) {
        skippedCount++
        return
      }
      
      // 添加饰品对象
      crawlForm.value.weaponId.push({
        id: weaponId.toString(),
        name: row.market_listing_item_name || row.name || '未知饰品'
      })
      
      addedCount++
    })

    let message = `添加完成！成功添加 ${addedCount} 个饰品`
    if (skippedCount > 0) {
      message += `，跳过 ${skippedCount} 个已存在的饰品`
    }
    if (noIdCount > 0) {
      message += `，${noIdCount} 个饰品没有${platformName}ID`
    }
    
    ElMessage.success(message)
  } catch {
    // 用户取消操作
  }
}

// 删除饰品ID
const removeWeaponId = (idToRemove) => {
  crawlForm.value.weaponId = crawlForm.value.weaponId.filter(w => w.id !== idToRemove)
  ElMessage.success('已删除饰品')
}

// 一键清空饰品列表
const clearAllWeaponIds = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要清空所有饰品吗？此操作将清除 ${weaponIdList.value.length} 个饰品。`,
      '确认清空',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    crawlForm.value.weaponId = []
    ElMessage.success('已清空所有饰品')
  } catch {
    // 用户取消操作
  }
}

// 购买饰品
const handleBuyWeapon = async (item) => {
  console.log('购买商品:', item)
  
  // 确认购买
  try {
    const pendantNames = item.pendants ? item.pendants.map(p => p.name).join(', ') : '无'
    const priceDiffText = item.priceDiff >= 0 ? `+${item.priceDiff.toFixed(2)}` : `${item.priceDiff.toFixed(2)}`
    await ElMessageBox.confirm(
      `确认购买该商品吗？\n\n挂件：${pendantNames}\n价格：¥${item.price}\n磨损：${item.abrade || '-'}\n溢价：${item.spread.toFixed(2)}\n收益：${priceDiffText}`,
      '确认购买',
      {
        confirmButtonText: '确认购买',
        cancelButtonText: '取消',
        type: 'warning',
        distinguishCancelAndClose: true
      }
    )
  } catch (error) {
    // 用户取消
    ElMessage.info('已取消购买')
    return
  }
  
  // 设置购买中状态
  buyingItems.value[item.id] = true
  
  // 开始购买流程
  const loadingMessage = ElMessage({
    message: '正在创建订单...',
    type: 'info',
    duration: 0
  })
  
  try {
    const requestData = {
      steamId: crawlForm.value.steamId,  // ✅ 使用购买账号
      commodityId: item.id,
      buyQuantity: 1,
      price: item.price,
      autoConfirmPayment: true,  // 自动使用余额支付
      pollPayment: true  // 轮询支付状态
    }
    
    console.log('购买请求数据 (使用购买账号):', requestData)
    console.log('  - 购买账号:', crawlForm.value.steamId)
    console.log('  - 爬取账号:', crawlForm.value.crawlAccountId)
    
    // 调用完整购买接口（创建订单+自动支付）
    const response = await axios.post(
      `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/buyCommodity`,
      requestData
    )
    
    console.log('购买响应:', response.data)
    
    loadingMessage.close()
    
    if (response.data.success) {
      const orderData = response.data.data?.order || {}
      const paymentStatus = response.data.data?.payment_status || {}
      const orderNo = orderData.orderNo || '未知'
      const paymentAmount = item.price || '未知'
      
      // 检查支付状态
      const payStatus = paymentStatus.payStatus
      let message = ''
      
      if (payStatus === 2) {
        // 支付成功 - 标记为已购买
        purchasedItems.value.add(item.id)
        
        // 更新数据库中的状态为 buyed
        try {
          await axios.post(
            `${API_CONFIG.BASE_URL}/searchRename/item/update-status`,
            {
              commodityId: item.id,
              status: 'buyed'
            }
          )
          console.log('数据库状态已更新为 buyed')
        } catch (updateError) {
          console.error('更新数据库状态失败:', updateError)
          // 不影响购买成功的提示
        }
        
        message = `购买成功！\n\n商品：挂件饰品\n订单号：${orderNo}\n金额：¥${paymentAmount}\n状态：支付成功✅\n\n饰品将发送至您的库存。`
      } else if (payStatus === 1) {
        // 支付处理中
        message = `订单已创建！\n\n订单号：${orderNo}\n金额：¥${paymentAmount}\n状态：支付处理中⏳\n\n请稍后查看订单状态。`
      } else {
        // 订单创建成功但支付未完成
        message = `订单创建成功！\n\n订单号：${orderNo}\n金额：¥${paymentAmount}\n\n已自动使用余额支付，请稍后查看订单状态。`
      }
      
      // 显示购买成功信息
      ElMessageBox.alert(
        message,
        '购买完成',
        {
          confirmButtonText: '知道了',
          type: 'success',
          callback: () => {
            ElMessage.success(payStatus === 2 ? '购买成功！' : '订单已创建')
          }
        }
      )
    } else {
      ElMessageBox.alert(
        `购买失败：${response.data.message || '未知错误'}\n\n请检查配置或稍后重试。`,
        '购买失败',
        {
          confirmButtonText: '知道了',
          type: 'error'
        }
      )
    }
  } catch (error) {
    loadingMessage.close()
    console.error('购买商品失败:', error)
    
    const errorMessage = error.response?.data?.message || error.message || '网络错误，请稍后重试'
    
    ElMessageBox.alert(
      `购买失败：${errorMessage}`,
      '购买失败',
      {
        confirmButtonText: '知道了',
        type: 'error'
      }
    )
  } finally {
    // 移除购买中状态
    buyingItems.value[item.id] = false
  }
}

// 表格行样式
const getRowClassName = () => {
  return 'weapon-row'
}

// 判断挂件是否包含"高光时刻"
const hasHighlightMoment = (item) => {
  if (!item.pendants || item.pendants.length === 0) {
    return false
  }
  // 检查任意一个挂件名称是否包含"高光时刻"
  return item.pendants.some(pendant => 
    pendant.name && pendant.name.includes('高光时刻')
  )
}

// 获取购买按钮类型
const getBuyButtonType = (item) => {
  if (purchasedItems.value.has(item.id)) {
    return 'success'  // 已购买：绿色
  }
  if (hasHighlightMoment(item)) {
    return 'warning'  // 包含高光时刻：黄色
  }
  if (item.priceDiff < 0) {
    return 'danger'   // 亏损：红色
  }
  if (item.priceDiff < 3) {
    return 'warning'  // 低收益：黄色
  }
  return 'success'    // 高收益：绿色
}

// 获取稀有度颜色样式（与ItemSearch保持一致）
const getRarityColor = (rarity) => {
  if (!rarity) return ''
  const rarityColorMap = {
    '违禁': '#e4ae39',      // 金色
    '隐秘': '#eb4b4b',      // 红色
    '保密': '#d32ce6',      // 紫色/粉色
    '受限': '#8847ff',      // 紫色
    '军规级': '#4b69ff',    // 蓝色
    '工业级': '#5e98d9',    // 浅蓝色
    '消费级': '#b0c3d9',    // 灰蓝色
    '普通级': '#b0c3d9'     // 灰蓝色
  }
  return rarityColorMap[rarity] || '#fff'
}

  // 组件挂载时加载数据（不自动启动搜索和轮询）
  onMounted(() => {
    if (crawlForm.value.platformType) {
      loadAccountsForPlatform(crawlForm.value.platformType)
    }
    loadConfigList()
    // 不再自动加载搜索结果和启动轮询，需要点击配置卡片后才进行搜索
    // 添加页面滚动监听
    window.addEventListener('scroll', handlePageScroll)
  })

  onUnmounted(() => {
    // 移除页面滚动监听
    window.removeEventListener('scroll', handlePageScroll)
    stopPolling()
  })

  return {
    crawlFormRef,
    filteredSteamIdList,
    isCrawling,
    crawlForm,
    customConfigForm,
    booleanOptions,
    crawlResult,
    allCrawlItems,
    canStartCrawl,
    startCrawl,
    stopCrawl,
    resetForm,
    // 配置管理
    savedConfigs,
    selectedConfigId,
    loadConfigList,
    selectConfig,
    createNewConfig,
    saveConfig,
    autoSaveConfig,
    handlePlatformTypeChange,
    deleteConfig,
    deleteCurrentConfig,
    formatTime,
    // 饰品搜索
    weaponSearchKeyword,
    weaponSearchResults,
    isSearchingWeapon,
    isLoadingMore,
    hasMore,
    weaponSearchFilters,
    weaponNameList,
    isLoadingWeaponNames,
    handleWeaponTypeChange,
    loadWeaponNames,
    loadWeaponNamesIfNeeded,
    handleSearchWeapon,
    loadMoreWeapons,
    clearWeaponSearch,
    handleAddWeaponFromSearch,
    handleAddAllWeaponsFromSearch,
    getWeaponIdByPlatform,
    getSourceLabel,
    addWeaponId,
    addAllWeaponIds,
    removeWeaponId,
    clearAllWeaponIds,
    weaponIdList,
    getRowClassName,
    getRarityColor,
    // 购买相关
    buyingItems,
    purchasedItems,
    handleBuyWeapon,
    hasHighlightMoment,
    getBuyButtonType,
    getItemIconUrl,
    // 历史结果管理
    clearCrawlHistory,
    // 工具区域折叠
    isConfigSectionsCollapsed,
    toggleConfigSections,
    isSearchResultsCollapsed,
    toggleSearchResults,
    isWeaponListCollapsed,
    toggleWeaponList,
  }
}
