import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CaretRight, CaretBottom, Refresh, Check, Loading } from '@element-plus/icons-vue'
import { API_CONFIG, apiUrls } from '@/config/api.js'

export function useItemSearch() {
  const steamIdList = ref([])
  const selectedSteamId = ref('')
  const selectedExterior = ref('') // 选择的外观筛选
  const selectedStatTrak = ref('normal') // 选择的StatTrak筛选，默认非StatTrak™
  const showSearchResults = ref(false) // 是否展开搜索结果
  const displayMode = ref('card') // 显示模式：'list' 或 'card'，默认卡片模式
  const image404Cache = ref(new Set()) // 图片404缓存
  const activePopoverRow = ref(null) // 当前激活的 popover 行
  
  // 卡片模式弹出框
  const showCardPopover = ref(false)
  const cardPopoverPosition = ref({ x: 0, y: 0 })
  const selectedCardItem = ref(null)
  
  // 商品详情弹窗
  const commodityPreviewVisible = ref(false)
  const commodityPreviewItem = ref(null)
  const commodityPreviewType = ref('') // 'buff' 或 'yyyp'
  
  // 印花/挂件放大预览
  const stickerPreviewVisible = ref(false)
  const stickerPreviewData = ref({
    name: '',
    imageUrl: '',
    type: ''
  })
  
  // BUFF商品列表
  const buffCommodities = ref([])
  const buffCurrentWeapon = ref(null)
  const buffTotalCount = ref(0)  // 在售总数量
  const buffBuyNum = ref(0)  // 求购数量
  const buffRentNum = ref(0)  // 租赁数量
  const showBuffList = ref(false)
  const showBuffTable = ref(true)  // 控制BUFF表格的展开/折叠
  const buffCurrentPage = ref(1)  // BUFF分页当前页
  const buffPageSize = ref(5)  // BUFF每页显示5条
  const buffLoadingMore = ref(false)  // BUFF是否正在加载更多
  const buffHasMore = ref(true)  // BUFF是否还有更多数据
  const buffTotalPage = ref(1)  // BUFF总页数
  
  // 悠悠有品商品列表
  const yyypCommodities = ref([])
  const yyypCurrentWeapon = ref(null)
  const yyypTotalCount = ref(0)  // 在售总数量
  const showYYYPList = ref(false)
  const showYYYPTable = ref(true)  // 控制悠悠有品表格的展开/折叠
  const yyypCurrentPage = ref(1)  // 悠悠有品分页当前页
  const yyypPageSize = ref(50)  // 悠悠有品每页显示50条
  const yyypLoadingMore = ref(false)  // 是否正在加载更多
  const yyypHasMore = ref(true)  // 是否还有更多数据
  
  // 多选模式相关
  const isMultiSelectMode = ref(false)  // 是否开启多选模式
  const selectedCommodities = ref([])   // 选中的商品列表
  const selectedCommodityType = ref('') // 选中商品的类型 'buff' 或 'yyyp'
  
  // 图片缓存 - 存储已加载的图片URL
  const imageCache = new Set()
  
  // API 基础地址
  const API_BASE = `${API_CONFIG.BASE_URL}/webInventoryV1`

  // 搜索相关
  const searchKeyword = ref('')
  const searchResults = ref([])
  const isSearching = ref(false)
  const searchSource = ref('') // 'weapon' 或其他来源
  const currentPage = ref(1)
  const pageSize = ref(10)

  // 计算属性 - 筛选后的结果
  const filteredResults = computed(() => {
    let results = searchResults.value
    
    // 根据选择的外观筛选（从 market_listing_item_name 中提取磨损等级）
    if (selectedExterior.value) {
      results = results.filter(item => {
        const floatRange = extractFloatRangeFromName(item.market_listing_item_name)
        return floatRange === selectedExterior.value
      })
    }
    
    // 根据选择的StatTrak筛选
    if (selectedStatTrak.value === 'stattrak') {
      // 只显示StatTrak™饰品
      results = results.filter(item => {
        const itemName = item.market_listing_item_name || ''
        return itemName.includes('StatTrak™') || itemName.includes('（StatTrak™）')
      })
    } else if (selectedStatTrak.value === 'normal') {
      // 只显示非StatTrak™饰品
      results = results.filter(item => {
        const itemName = item.market_listing_item_name || ''
        return !itemName.includes('StatTrak™') && !itemName.includes('（StatTrak™）')
      })
    }
    // 如果是空值''，显示全部
    
    return results
  })

  // 计算属性 - 分页结果
  const paginatedResults = computed(() => {
    const start = (currentPage.value - 1) * pageSize.value
    const end = start + pageSize.value
    return filteredResults.value.slice(start, end)
  })

  // 计算属性 - BUFF商品分页结果
  const paginatedBuffCommodities = computed(() => {
    const start = (buffCurrentPage.value - 1) * buffPageSize.value
    const end = start + buffPageSize.value
    return buffCommodities.value.slice(start, end)
  })

  // 计算属性 - 悠悠有品商品分页结果
  const paginatedYYYPCommodities = computed(() => {
    const start = (yyypCurrentPage.value - 1) * yyypPageSize.value
    const end = start + yyypPageSize.value
    return yyypCommodities.value.slice(start, end)
  })

  // 预加载图片（相同URL只加载一次）
  const preloadImages = (commodityList) => {
    const uniqueUrls = new Set()
    
    // 收集所有唯一的图片URL
    commodityList.forEach(item => {
      if (item.iconUrl && !imageCache.has(item.iconUrl)) {
        uniqueUrls.add(item.iconUrl)
      }
    })
    
    // 预加载未缓存的图片
    uniqueUrls.forEach(url => {
      const img = new Image()
      img.onload = () => {
        imageCache.add(url)
        console.log(`图片已缓存: ${url}`)
      }
      img.onerror = () => {
        console.error(`图片加载失败: ${url}`)
      }
      img.src = url
    })
    
    console.log(`开始预加载 ${uniqueUrls.size} 张唯一图片，已缓存 ${imageCache.size} 张`)
  }

  // 实时搜索武器名称
  const querySearchAsync = async (queryString, cb) => {
    if (!queryString || queryString.trim().length === 0) {
      cb([])
      return
    }

    try {
      const response = await axios.get(apiUrls.searchWeapon(queryString.trim()))
      if (response.data.success && response.data.data) {
        const results = response.data.data.map(name => ({
          value: name
        }))
        cb(results)
      } else {
        cb([])
      }
    } catch (error) {
      console.error('搜索武器名称失败:', error)
      cb([])
    }
  }

  // 选择搜索建议
  const handleSelect = (item) => {
    searchKeyword.value = item.value
    console.log('已选择:', item.value)
  }

  // 搜索武器详情
  const handleSearchWeapon = async () => {
    if (!searchKeyword.value.trim()) {
      ElMessage.warning('请输入搜索关键词')
      return
    }

    isSearching.value = true
    searchSource.value = 'weapon'
    currentPage.value = 1
    
    try {
      console.log('搜索武器:', searchKeyword.value)
      
      const response = await axios.get(apiUrls.searchWeaponDetail(searchKeyword.value.trim()))
      
      if (response.data.success) {
        searchResults.value = response.data.data || []
        
        if (searchResults.value.length === 0) {
          ElMessage.info('未找到匹配的武器')
          showSearchResults.value = false
        } else {
          ElMessage.success(`找到 ${searchResults.value.length} 件武器`)
          showSearchResults.value = true  // 搜索成功后自动展开
        }
      } else {
        ElMessage.error('搜索失败: ' + (response.data.error || '未知错误'))
        searchResults.value = []
        showSearchResults.value = false
      }
      
    } catch (error) {
      console.error('搜索武器失败:', error)
      ElMessage.error('搜索失败: ' + (error.response?.data?.error || error.message))
      searchResults.value = []
      showSearchResults.value = false
    } finally {
      isSearching.value = false
    }
  }

  // 刷新搜索结果
  const handleRefreshSearch = async () => {
    if (!searchKeyword.value.trim()) {
      ElMessage.warning('请先输入搜索关键词')
      return
    }

    ElMessage.info('正在刷新数据...')
    await handleSearchWeapon()
  }

  // 加载Steam ID列表
  const loadSteamIdList = async () => {
    try {
      const response = await axios.get(`${API_BASE}/steam_ids`)
      console.log('Steam ID列表响应:', response.data)
      if (response.data.success) {
        steamIdList.value = response.data.data
        if (steamIdList.value.length > 0) {
          // 默认选择第一个 - 使用新格式 steamID（大写）
          selectedSteamId.value = steamIdList.value[0].steamID
          console.log('默认选择Steam ID:', selectedSteamId.value)
        } else {
          ElMessage.warning('没有找到库存数据，请先获取Steam库存')
        }
      }
    } catch (error) {
      console.error('加载Steam ID列表失败:', error)
      ElMessage.error('加载Steam ID列表失败: ' + (error.response?.data?.error || error.message))
    }
  }

  // Steam ID 改变处理
  const handleSteamIdChange = (value) => {
    console.log('Steam ID已改变:', value)
    selectedSteamId.value = value
  }

  // 外观筛选改变处理
  const handleExteriorChange = (value) => {
    console.log('外观筛选已改变:', value)
    selectedExterior.value = value
    currentPage.value = 1 // 重置到第一页
  }

  // StatTrak筛选改变处理
  const handleStatTrakChange = (value) => {
    console.log('StatTrak筛选已改变:', value)
    selectedStatTrak.value = value
    currentPage.value = 1 // 重置到第一页
  }

  // 处理从高级搜索组件选择单个武器
  const handleSelectWeaponFromSearch = (weapon) => {
    console.log('从高级搜索选择武器:', weapon)
    // 将选中的武器添加到搜索结果中
    const exists = searchResults.value.some(item => 
      item.market_listing_item_name === weapon.market_listing_item_name
    )
    
    if (!exists) {
      searchResults.value.push(weapon)
      ElMessage.success(`已添加: ${weapon.market_listing_item_name}`)
    } else {
      ElMessage.warning('该武器已在列表中')
    }
    
    showSearchResults.value = true
  }

  // 处理从高级搜索组件选择全部武器
  const handleSelectAllWeaponsFromSearch = (weapons) => {
    console.log('从高级搜索添加全部武器:', weapons.length)
    let addedCount = 0
    
    weapons.forEach(weapon => {
      const exists = searchResults.value.some(item => 
        item.market_listing_item_name === weapon.market_listing_item_name
      )
      
      if (!exists) {
        searchResults.value.push(weapon)
        addedCount++
      }
    })
    
    if (addedCount > 0) {
      ElMessage.success(`成功添加 ${addedCount} 件武器`)
      showSearchResults.value = true
    } else {
      ElMessage.info('所有武器已在列表中')
    }
  }

  // 刷新悠悠有品商品列表
  const handleRefreshYYYP = async () => {
    if (!yyypCurrentWeapon.value) {
      ElMessage.warning('无法刷新，请重新选择武器')
      return
    }

    yyypCurrentPage.value = 1  // 重置分页到第一页
    ElMessage.info('正在刷新悠悠有品商品数据...')
    await handleSearchYYYPByRow(yyypCurrentWeapon.value)
  }
  
  // 刷新BUFF商品列表
  const handleRefreshBuff = async () => {
    if (!buffCurrentWeapon.value) {
      ElMessage.warning('无法刷新，请重新选择武器')
      return
    }

    buffCurrentPage.value = 1  // 重置分页到第一页
    ElMessage.info('正在刷新BUFF商品数据...')
    await handleSearchBuffByRow(buffCurrentWeapon.value)
  }
  
  // 切换BUFF表格的展开/折叠
  const toggleBuffList = () => {
    showBuffTable.value = !showBuffTable.value
  }
  
  // 购买BUFF商品（暂未对接）
  const handleBuyBuffCommodity = (commodity) => {
    console.log('购买BUFF商品:', commodity)
    ElMessage.info(`购买功能开发中... 订单ID: ${commodity.id}`)
    // TODO: 对接BUFF购买接口
  }

  // 获取稀有度类型（根据CS:GO品质颜色）
  const getRarityType = (rarity) => {
    if (!rarity) return ''
    // 不使用Element Plus的type，使用自定义颜色
    return ''
  }
  
  // 获取稀有度颜色样式
  const getRarityColor = (rarity) => {
    if (!rarity) return ''
    
    // 移除"级"后缀进行匹配
    const normalizedRarity = rarity.replace(/级$/, '')
    
    const rarityColorMap = {
      '违禁': '#e4ae39',      // 金色
      '非凡': '#e4ae39',      // 金色
      '隐秘': '#eb4b4b',      // 红色
      '保密': '#d32ce6',      // 紫色/粉色
      '受限': '#8847ff',      // 紫色
      '军规': '#4b69ff',      // 蓝色
      '工业': '#5e98d9',      // 浅蓝色
      '消费': '#b0c3d9',      // 灰蓝色
      '普通': '#b0c3d9'       // 灰蓝色
    }
    return rarityColorMap[normalizedRarity] || '#fff'
  }

  // 获取武器类型颜色样式
  const getWeaponTypeColor = (weaponType) => {
    if (!weaponType) return '#909399'
    const typeColorMap = {
      '手枪': '#67c23a',        // 绿色
      '步枪': '#409eff',        // 蓝色
      '狙击步枪': '#e6a23c',    // 橙色
      '冲锋枪': '#909399',      // 灰色
      '霰弹枪': '#f56c6c',      // 红色
      '机枪': '#c45656',        // 深红色
      '挂件': '#d4a5ff',        // 浅紫色
      '挂件（纪念品）': '#ffd700', // 金色
      '匕首': '#ff4757',        // 亮红色
      '手套': '#ffa502',        // 橙黄色
      '探员': '#5f27cd',        // 紫色
      '印花': '#48dbfb',        // 青色
      '涂鸦': '#ff6348',        // 珊瑚红
      '音乐盒': '#1dd1a1',      // 青绿色
      '收藏品': '#ee5a6f',      // 粉红色
      '容器': '#c8d6e5'         // 浅灰蓝色
    }
    return typeColorMap[weaponType] || '#909399'
  }

  // 获取磨损等级的标签类型
  const getFloatRangeType = (floatRange) => {
    if (!floatRange) return ''
    const typeMap = {
      '崭新出厂': 'success',
      '略有磨损': 'success',
      '久经沙场': 'warning',
      '破损不堪': 'warning',
      '战痕累累': 'danger'
    }
    return typeMap[floatRange] || ''
  }

  // 从 market_listing_item_name 中提取磨损等级
  const extractFloatRangeFromName = (itemName) => {
    if (!itemName) return ''
    
    const wearLevels = ['崭新出厂', '略有磨损', '久经沙场', '破损不堪', '战痕累累']
    
    for (const wear of wearLevels) {
      if (itemName.includes(`(${wear})`) || itemName.includes(wear)) {
        return wear
      }
    }
    
    return ''
  }

  // 获取磨损等级的颜色
  const getFloatRangeColor = (floatRange) => {
    if (!floatRange) return '#fff'
    const colorMap = {
      '崭新出厂': '#4caf50',      // 绿色 - Factory New
      '略有磨损': '#8bc34a',      // 浅绿色 - Minimal Wear
      '久经沙场': '#ffc107',      // 黄色 - Field-Tested
      '破损不堪': '#ff9800',      // 橙色 - Well-Worn
      '战痕累累': '#f44336'       // 红色 - Battle-Scarred
    }
    return colorMap[floatRange] || '#fff'
  }

  // 根据磨损值返回颜色（用于进度条）
  const getWearColor = (abrade) => {
    if (!abrade) return '#4caf50'
    const wear = parseFloat(abrade)
    if (wear <= 0.07) return '#4caf50'      // 崭新出厂 - 绿色
    if (wear <= 0.15) return '#8bc34a'      // 略有磨损 - 浅绿色
    if (wear <= 0.38) return '#ffc107'      // 久经沙场 - 黄色
    if (wear <= 0.45) return '#ff9800'      // 破损不堪 - 橙色
    return '#f44336'                        // 战痕累累 - 红色
  }

  // 根据磨损值返回磨损等级名称
  const getWearRange = (abrade) => {
    if (!abrade) return ''
    const wear = parseFloat(abrade)
    if (wear <= 0.07) return '崭新出厂'
    if (wear <= 0.15) return '略有磨损'
    if (wear <= 0.38) return '久经沙场'
    if (wear <= 0.45) return '破损不堪'
    return '战痕累累'
  }

  // 获取外观（磨损）颜色样式
  const getExteriorColor = (itemName) => {
    if (!itemName) return '#fff'
    
    const exteriorColorMap = {
      '崭新出厂': '#4caf50',      // 绿色 - Factory New
      '略有磨损': '#8bc34a',      // 浅绿色 - Minimal Wear
      '久经沙场': '#ffc107',      // 黄色 - Field-Tested
      '破损不堪': '#ff9800',      // 橙色 - Well-Worn
      '战痕累累': '#f44336'       // 红色 - Battle-Scarred
    }
    
    // 检查饰品名称中是否包含外观关键词
    for (const [exterior, color] of Object.entries(exteriorColorMap)) {
      if (itemName.includes(exterior) || itemName.includes(`(${exterior})`)) {
        return color
      }
    }
    
    return '#fff' // 默认白色
  }

  // 通过行数据搜索悠悠有品
  const handleSearchYYYPByRow = async (row) => {
    console.log('=== 开始执行 handleSearchYYYPByRow ===')
    console.log('row数据:', row)
    console.log('row.yyyp_id:', row.yyyp_id)
    console.log('selectedSteamId.value:', selectedSteamId.value)
    
    if (!row.yyyp_id) {
      console.log('没有yyyp_id，退出')
      ElMessage.warning('该武器没有悠悠有品ID')
      return
    }

    if (!selectedSteamId.value) {
      console.log('没有选择Steam账号，退出')
      ElMessage.warning('请先选择Steam账号')
      return
    }

    console.log('通过验证，开始请求')
    isSearching.value = true
    searchSource.value = 'yyyp'
    
    try {
      console.log('搜索悠悠有品:', row.market_listing_item_name, 'ID:', row.yyyp_id, 'SteamID:', selectedSteamId.value)
      
      // 构建请求数据
      const requestData = {
        steamId: selectedSteamId.value || '',
        yyypId: row.yyyp_id,
        pageIndex: 1,
        pageSize: 50
      }
      
      const apiUrl = `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/getCommoditiesByTemplateId`
      
      console.log('请求URL:', apiUrl)
      console.log('请求数据:', requestData)
      
      // 调用悠悠有品商品列表API（使用Spider服务器地址）
      const response = await axios.post(apiUrl, requestData)
      
      console.log('API响应:', response.data)
      
      if (response.data.success) {
        const parsedData = response.data.data
        console.log('获取到悠悠有品已解析数据:', parsedData)
        
        // 直接使用Spider解析后的数据
        const commodityList = parsedData.commodityList || []
        const totalCount = parsedData.totalCount || 0
        console.log('商品列表:', commodityList)
        console.log('在售总数:', totalCount)
        
        // 更新状态，显示商品列表
        yyypCurrentWeapon.value = row
        yyypCommodities.value = commodityList
        yyypTotalCount.value = totalCount
        yyypCurrentPage.value = 1  // 重置分页到第一页
        yyypHasMore.value = commodityList.length < totalCount  // 判断是否还有更多
        showYYYPList.value = true
        showSearchResults.value = false  // 折叠搜索结果
        
        ElMessage.success(`成功获取 ${commodityList.length} 条商品数据，在售总数: ${totalCount}`)
        
        // 预加载图片（相同URL只加载一次）
        preloadImages(commodityList)
        
        // 批量获取印花/挂件价格
        fetchStickerPrices(commodityList)
        
        // 滚动到商品列表区域
        setTimeout(() => {
          const listElement = document.querySelector('.yyyp-commodity-list')
          if (listElement) {
            listElement.scrollIntoView({ behavior: 'smooth', block: 'start' })
          }
        }, 100)
        
        // 自动批量获取改名信息
        fetchAllNameTags(commodityList)
      } else {
        console.error('API返回失败:', response.data)
        ElMessage.error(response.data.message || '获取商品列表失败')
      }
      
    } catch (error) {
      console.error('搜索悠悠有品失败 - 完整错误:', error)
      console.error('错误响应:', error.response)
      console.error('错误数据:', error.response?.data)
      
      const errorMessage = error.response?.data?.message || error.message || '搜索失败，请检查网络连接'
      ElMessage.error(errorMessage)
    } finally {
      console.log('请求完成，重置加载状态')
      isSearching.value = false
      searchSource.value = ''
    }
  }

  // 悠悠有品加载更多
  const loadMoreYYYPCommodities = async () => {
    if (yyypLoadingMore.value || !yyypHasMore.value || !yyypCurrentWeapon.value) {
      return
    }
    
    yyypLoadingMore.value = true
    const nextPage = yyypCurrentPage.value + 1
    
    try {
      console.log(`加载悠悠有品第 ${nextPage} 页数据`)
      
      const requestData = {
        steamId: selectedSteamId.value || '',
        yyypId: yyypCurrentWeapon.value.yyyp_id,
        pageIndex: nextPage,
        pageSize: 50
      }
      
      const apiUrl = `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/getCommoditiesByTemplateId`
      const response = await axios.post(apiUrl, requestData)
      
      if (response.data.success) {
        const parsedData = response.data.data
        const newCommodities = parsedData.commodityList || []
        
        if (newCommodities.length > 0) {
          // 追加到现有列表
          yyypCommodities.value = [...yyypCommodities.value, ...newCommodities]
          yyypCurrentPage.value = nextPage
          
          // 判断是否还有更多
          yyypHasMore.value = yyypCommodities.value.length < yyypTotalCount.value
          
          console.log(`加载了 ${newCommodities.length} 条数据，当前共 ${yyypCommodities.value.length} 条`)
          
          // 预加载新图片
          preloadImages(newCommodities)
          
          // 批量获取新商品的印花/挂件价格
          fetchStickerPrices(newCommodities)
          
          // 获取新商品的改名信息
          fetchAllNameTags(newCommodities)
        } else {
          yyypHasMore.value = false
        }
      }
    } catch (error) {
      console.error('加载更多失败:', error)
      ElMessage.error('加载更多失败')
    } finally {
      yyypLoadingMore.value = false
    }
  }

  // 悠悠有品滚动事件处理
  const handleYYYPScroll = (event) => {
    const target = event.target
    const scrollTop = target.scrollTop
    const scrollHeight = target.scrollHeight
    const clientHeight = target.clientHeight
    
    // 当滚动到底部附近时（距离底部50px）加载更多
    if (scrollHeight - scrollTop - clientHeight < 50) {
      loadMoreYYYPCommodities()
    }
  }

  // BUFF加载更多
  const loadMoreBuffCommodities = async () => {
    if (buffLoadingMore.value || !buffHasMore.value || !buffCurrentWeapon.value) {
      return
    }
    
    buffLoadingMore.value = true
    const nextPage = buffCurrentPage.value + 1
    
    try {
      console.log(`加载BUFF第 ${nextPage} 页数据`)
      
      const requestData = {
        steamId: selectedSteamId.value || '',
        goodsId: buffCurrentWeapon.value.buff_id,
        pageIndex: nextPage
      }
      
      const apiUrl = `${API_CONFIG.SPIDER_BASE_URL}/buffSpiderV1/getCommoditiesByGoodsId`
      const response = await axios.post(apiUrl, requestData)
      
      if (response.data.success) {
        const parsedData = response.data.data
        const newCommodities = parsedData.commodityList || []
        
        if (newCommodities.length > 0) {
          // 追加到现有列表
          buffCommodities.value = [...buffCommodities.value, ...newCommodities]
          buffCurrentPage.value = nextPage
          
          // 判断是否还有更多
          buffHasMore.value = nextPage < buffTotalPage.value
          
          console.log(`加载了 ${newCommodities.length} 条数据，当前共 ${buffCommodities.value.length} 条`)
          
          // 预加载新图片
          preloadImages(newCommodities)
          
          // 批量获取新商品的印花/挂件价格
          fetchStickerPrices(newCommodities)
        } else {
          buffHasMore.value = false
        }
      }
    } catch (error) {
      console.error('BUFF加载更多失败:', error)
      ElMessage.error('加载更多失败')
    } finally {
      buffLoadingMore.value = false
    }
  }

  // BUFF滚动事件处理
  const handleBuffScroll = (event) => {
    const target = event.target
    const scrollTop = target.scrollTop
    const scrollHeight = target.scrollHeight
    const clientHeight = target.clientHeight
    
    // 当滚动到底部附近时（距离底部50px）加载更多
    if (scrollHeight - scrollTop - clientHeight < 50) {
      loadMoreBuffCommodities()
    }
  }

  // 查看商品详情（暂未对接）
  const handleViewDetail = (commodity) => {
    console.log('查看商品详情:', commodity)
    ElMessage.info(`查看详情功能开发中... 商品ID: ${commodity.id}`)
    // TODO: 对接查看详情接口
  }

  // 购买商品
  const handleBuyCommodity = async (commodity) => {
    console.log('购买商品:', commodity)
    
    // 确认购买
    try {
      await ElMessageBox.confirm(
        `确认购买该商品吗？\n\n商品：${commodity.commodityName}\n价格：¥${commodity.price}\n磨损：${commodity.abrade || '-'}`,
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
    
    // 开始购买流程
    const loadingMessage = ElMessage({
      message: '正在创建订单...',
      type: 'info',
      duration: 0,
      customClass: 'buy-loading-message'
    })
    
    try {
      const requestData = {
        steamId: selectedSteamId.value,
        commodityId: commodity.id,
        buyQuantity: 1,
        price: commodity.price,  // 添加商品价格
        autoConfirmPayment: true,  // 自动使用余额支付
        pollPayment: true  // 轮询支付状态
      }
      
      console.log('购买请求数据:', requestData)
      
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
        const paymentAmount = commodity.price || '未知'
        
        // 检查支付状态
        const payStatus = paymentStatus.payStatus
        let message = ''
        
        if (payStatus === 2) {
          // 支付成功
          message = `购买成功！\n\n订单号：${orderNo}\n金额：¥${paymentAmount}\n状态：支付成功✅\n\n饰品将发送至您的库存。`
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
        
        // 购买成功后自动刷新列表
        if (yyypCurrentWeapon.value) {
          console.log('购买成功，自动刷新悠悠有品列表...')
          setTimeout(async () => {
            await handleRefreshYYYP()
          }, 1000) // 延迟1秒刷新，确保后端数据已更新
        }
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
    }
  }

  // 批量获取改名信息（自动调用，只获取第一条）
  const fetchAllNameTags = async (commodityList) => {
    // 筛选出有改名标签的商品
    const commoditiesWithNameTag = commodityList.filter(item => item.haveNameTag === 1)
    
    if (commoditiesWithNameTag.length === 0) {
      console.log('没有需要获取改名信息的商品')
      return
    }

    // 只自动获取第一条
    console.log(`共有 ${commoditiesWithNameTag.length} 个商品有改名标签，自动获取第一个`)
    
    const commodity = commoditiesWithNameTag[0]
    
    try {
      console.log(`正在获取商品 ${commodity.id} 的改名信息`)
      
      // 调用接口获取详细信息
      const response = await axios.post(
        `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/getWeaponDetail`,
        {
          steamId: selectedSteamId.value,
          id: commodity.id
        }
      )

      if (response.data.success && response.data.data) {
        const detailData = response.data.data.Data
        const nameTags = detailData.NameTags || []
        
        // 缓存改名信息到商品对象中
        commodity.nameTags = nameTags
        commodity.nameTagText = nameTags.length > 0 ? nameTags[0].replace(/^名称标签：[""]?|[""]$/g, '') : ''
        
        console.log(`商品 ${commodity.id} 改名信息:`, nameTags)
      } else {
        console.error(`获取商品 ${commodity.id} 改名信息失败:`, response.data.message)
      }
    } catch (error) {
      console.error(`获取商品 ${commodity.id} 改名信息异常:`, error)
    }
    
    console.log(`自动获取改名信息完成`)
  }

  // 获取单个商品的改名信息（点击按钮时调用）
  const fetchSingleNameTag = async (commodity) => {
    try {
      // 设置加载状态
      commodity.nameTagLoading = true

      console.log('正在获取改名信息，商品ID:', commodity.id)

      // 调用接口获取详细信息
      const response = await axios.post(
        `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/getWeaponDetail`,
        {
          steamId: selectedSteamId.value,
          id: commodity.id
        }
      )

      console.log('改名信息响应:', response.data)

      if (response.data.success && response.data.data) {
        const detailData = response.data.data.Data
        const nameTags = detailData.NameTags || []
        
        // 缓存改名信息到商品对象中
        commodity.nameTags = nameTags
        commodity.nameTagText = nameTags.length > 0 ? nameTags[0].replace(/^名称标签：[""]?|[""]$/g, '') : ''

        if (nameTags.length === 0) {
          ElMessage.info('该商品没有改名信息')
        }
      } else {
        ElMessage.error('获取改名信息失败: ' + (response.data.message || '未知错误'))
      }
    } catch (error) {
      console.error('获取改名信息失败:', error)
      ElMessage.error('获取改名信息失败: ' + (error.response?.data?.message || error.message))
    } finally {
      commodity.nameTagLoading = false
    }
  }

  // 批量获取印花/挂件价格
  const fetchStickerPrices = async (commodityList) => {
    if (!commodityList || commodityList.length === 0) {
      return
    }

    console.log('开始批量获取印花/挂件价格')

    // 收集所有需要查询的 steam_hash_name
    const steamHashNames = new Set()
    
    commodityList.forEach(item => {
      // 设置加载状态
      item.priceLoading = true
      
      // 收集印花的 steam_hash_name
      if (item.stickers && item.stickers.length > 0) {
        item.stickers.forEach(sticker => {
          const hashName = sticker.TemplateHashName || sticker.steam_hash_name
          if (hashName) {
            steamHashNames.add(hashName)
          }
        })
      }
      
      // 收集挂件的 steam_hash_name
      if (item.pendants && item.pendants.length > 0) {
        item.pendants.forEach(pendant => {
          const hashName = pendant.steamHashName || pendant.steam_hash_name
          if (hashName) {
            steamHashNames.add(hashName)
          }
        })
      }
    })

    if (steamHashNames.size === 0) {
      console.log('没有需要查询价格的印花/挂件')
      commodityList.forEach(item => {
        item.priceLoading = false
      })
      return
    }

    console.log(`共需要查询 ${steamHashNames.size} 个印花/挂件的价格`)

    try {
      // 调用批量查询接口
      const apiUrl = '/api/itemSearchApiV1/batch-sticker-prices'
      console.log('准备调用API:', apiUrl)
      const response = await axios.post(
        apiUrl,
        {
          steam_hash_names: Array.from(steamHashNames)
        }
      )

      if (response.data.success) {
        const priceMap = response.data.data
        console.log('获取到价格数据:', priceMap)

        // 更新每个商品的印花/挂件价格信息
        commodityList.forEach(item => {
          let stickerTotalValue = 0
          let pendantTotalValue = 0

          // 处理印花价格
          if (item.stickers && item.stickers.length > 0) {
            item.stickers.forEach(sticker => {
              const hashName = sticker.TemplateHashName || sticker.steam_hash_name
              if (hashName && priceMap[hashName]) {
                const priceInfo = priceMap[hashName]
                sticker.priceInfo = priceInfo
                
                // 累加价格（优先使用悠悠有品价格）
                const price = parseFloat(priceInfo.yyyp_price || priceInfo.buff_price || 0)
                stickerTotalValue += price
              }
            })
          }

          // 处理挂件价格
          if (item.pendants && item.pendants.length > 0) {
            item.pendants.forEach(pendant => {
              const hashName = pendant.steamHashName || pendant.steam_hash_name
              if (hashName && priceMap[hashName]) {
                const priceInfo = priceMap[hashName]
                pendant.priceInfo = priceInfo
                
                // 累加价格（优先使用悠悠有品价格）
                const price = parseFloat(priceInfo.yyyp_price || priceInfo.buff_price || 0)
                pendantTotalValue += price
              }
            })
          }

          // 设置总价值
          item.stickerTotalValue = stickerTotalValue.toFixed(2)
          item.pendantTotalValue = pendantTotalValue.toFixed(2)
          item.priceLoading = false
        })

        console.log('印花/挂件价格更新完成')
      } else {
        console.error('批量查询价格失败:', response.data.message)
        commodityList.forEach(item => {
          item.priceLoading = false
        })
      }
    } catch (error) {
      console.error('批量查询价格异常:', error)
      commodityList.forEach(item => {
        item.priceLoading = false
      })
    }
  }

  // 显示印花信息对话框
  const showStickersDialog = (commodity) => {
    const stickers = commodity.stickers || []
    
    if (stickers.length === 0) {
      ElMessage.info('该商品没有印花')
      return
    }

    // 最多显示5个印花
    const displayStickers = stickers.slice(0, 5)

    // 构建印花信息HTML - 横向平铺展示（自适应宽度）
    let stickersHtml = `
      <div style="padding: 20px;">
        <div style="text-align: center; margin-bottom: 20px;">
          <h4 style="margin: 0 0 10px 0; color: #303133; font-size: 16px;">${commodity.commodityName}</h4>
          <p style="margin: 0; color: #909399; font-size: 14px;">印花数量：${stickers.length} 个${stickers.length > 5 ? '（显示前5个）' : ''}</p>
        </div>
        
        <div style="display: flex; justify-content: center; gap: 15px; flex-wrap: nowrap;">
    `
    
    displayStickers.forEach((sticker, index) => {
      stickersHtml += `
        <div style="text-align: center; min-width: 110px; flex-shrink: 0;">
          <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; padding: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
            <div style="background: white; border-radius: 8px; padding: 8px; margin-bottom: 8px;">
              <img src="${sticker.ImgUrl}" style="width: 70px; height: 52px; object-fit: contain; display: block; margin: 0 auto;" />
            </div>
            <div style="color: white; font-size: 11px; margin-bottom: 4px;">
              <strong>位置 ${sticker.RawIndex !== null ? sticker.RawIndex + 1 : '-'}</strong>
            </div>
            <div style="background: rgba(255,255,255,0.2); border-radius: 4px; padding: 3px 6px; font-size: 11px; color: white;">
              磨损: ${sticker.Abrade || '-'}
            </div>
            ${sticker.priceV1 ? `
              <div style="margin-top: 6px; background: rgba(255,255,255,0.9); border-radius: 4px; padding: 3px 6px; font-size: 12px; color: #f56c6c; font-weight: 600;">
                ${sticker.priceV1}
              </div>
            ` : ''}
          </div>
          <div style="margin-top: 6px; font-size: 11px; color: #606266; max-width: 110px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${sticker.Name || '-'}">
            ${sticker.Name || '-'}
          </div>
        </div>
      `
    })
    
    stickersHtml += `
        </div>
      </div>
    `
    
    // 根据印花数量计算对话框宽度（最多5个印花）
    // 每个卡片宽度110px，间距15px，加上对话框内边距和额外空间
    // 计算公式：卡片数量*110 + (卡片数量-1)*15 + 对话框边距和额外空间
    const dialogWidth = displayStickers.length * 110 + (displayStickers.length - 1) * 15 + 160
    
    ElMessageBox({
      title: '印花信息',
      message: stickersHtml,
      dangerouslyUseHTMLString: true,
      confirmButtonText: '关闭',
      customClass: 'stickers-dialog',
      width: `${dialogWidth}px`
    }).catch(() => {
      // 用户点击关闭或取消时，忽略错误
    })
  }

  // 关闭悠悠有品商品列表，返回搜索结果
  const closeYYYPList = () => {
    showYYYPList.value = false
    showSearchResults.value = true
    yyypCommodities.value = []
    yyypCurrentWeapon.value = null
  }

  // 切换搜索结果的展开/折叠
  const toggleSearchResults = () => {
    showSearchResults.value = !showSearchResults.value
  }

  // 切换悠悠有品表格的展开/折叠
  const toggleYYYPList = () => {
    showYYYPTable.value = !showYYYPTable.value
  }

  // 旧的对话框函数（已废弃，保留以防需要）
  const showYYYPCommoditiesDialog_OLD = (row, commodities, total) => {
    // 构建商品列表HTML
    let commoditiesHtml = `
      <div style="max-height: 500px; overflow-y: auto;">
        <p style="margin-bottom: 15px; color: #606266;">
          <strong>武器名称：</strong>${row.market_listing_item_name}<br/>
          <strong>悠悠有品ID：</strong>${row.yyyp_id}<br/>
          <strong>商品总数：</strong>${total} 条
        </p>
        <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
          <thead>
            <tr style="background-color: #f5f7fa; border-bottom: 2px solid #dcdfe6;">
              <th style="padding: 10px; text-align: left; border: 1px solid #dcdfe6;">商品名称</th>
              <th style="padding: 10px; text-align: center; border: 1px solid #dcdfe6; width: 100px;">价格</th>
              <th style="padding: 10px; text-align: center; border: 1px solid #dcdfe6; width: 80px;">磨损</th>
              <th style="padding: 10px; text-align: center; border: 1px solid #dcdfe6; width: 100px;">操作</th>
            </tr>
          </thead>
          <tbody>
    `
    
    if (commodities.length === 0) {
      commoditiesHtml += `
        <tr>
          <td colspan="4" style="padding: 20px; text-align: center; color: #909399;">暂无商品数据</td>
        </tr>
      `
    } else {
      commodities.forEach((item, index) => {
        const price = item.price ? (item.price / 100).toFixed(2) : '-'
        const abrade = item.abrade ? item.abrade.toFixed(4) : '-'
        const commodityUrl = `https://www.youpin898.com/goodInfo?id=${item.id}`
        
        commoditiesHtml += `
          <tr style="border-bottom: 1px solid #ebeef5; ${index % 2 === 0 ? 'background-color: #fafafa;' : ''}">
            <td style="padding: 10px; border: 1px solid #ebeef5;">
              <div style="display: flex; align-items: center;">
                ${item.iconUrl ? `<img src="${item.iconUrl}" style="width: 40px; height: 30px; margin-right: 10px; object-fit: contain;" />` : ''}
                <span style="flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${item.commodityName || '-'}</span>
              </div>
            </td>
            <td style="padding: 10px; text-align: center; border: 1px solid #ebeef5;">
              <span style="color: #f56c6c; font-weight: bold;">¥${price}</span>
            </td>
            <td style="padding: 10px; text-align: center; border: 1px solid #ebeef5;">${abrade}</td>
            <td style="padding: 10px; text-align: center; border: 1px solid #ebeef5;">
              <a href="${commodityUrl}" target="_blank" style="color: #409eff; text-decoration: none;">查看详情</a>
            </td>
          </tr>
        `
      })
    }
    
    commoditiesHtml += `
          </tbody>
        </table>
      </div>
    `
    
    ElMessageBox({
      title: '悠悠有品商品列表',
      message: commoditiesHtml,
      dangerouslyUseHTMLString: true,
      confirmButtonText: '关闭',
      customClass: 'yyyp-commodities-dialog',
      width: '900px'
    })
  }
  
  // 切换popover显示
  const togglePopover = (row) => {
    if (activePopoverRow.value === row) {
      activePopoverRow.value = null
    } else {
      activePopoverRow.value = row
    }
  }
  
  // 选择平台并搜索
  const selectPlatform = (row, platform) => {
    activePopoverRow.value = null // 关闭popover
    
    if (platform === 'yyyp') {
      handleSearchYYYPByRow(row)
    } else if (platform === 'buff') {
      handleSearchBuffByRow(row)
    } else if (platform === 'csfloat') {
      handleSearchCsFloatByRow(row)
    } else if (platform === 'all') {
      handleSearchAllPlatforms(row)
    }
  }

  // 同时搜索悠悠有品和BUFF
  const handleSearchAllPlatforms = async (row) => {
    console.log('=== 开始执行 handleSearchAllPlatforms ===')
    console.log('row数据:', row)
    
    if (!selectedSteamId.value) {
      console.log('没有选择Steam账号，退出')
      ElMessage.warning('请先选择Steam账号')
      return
    }

    // 检查是否有悠悠有品ID或BUFF ID
    const hasYYYPId = row.yyyp_id
    const hasBuffId = row.buff_id
    
    if (!hasYYYPId && !hasBuffId) {
      ElMessage.warning('该武器没有悠悠有品ID和BUFF ID')
      return
    }

    isSearching.value = true
    searchSource.value = 'all'
    
    try {
      ElMessage.info('正在同时搜索悠悠有品和BUFF...')
      
      // 并行请求悠悠有品和BUFF
      const promises = []
      
      if (hasYYYPId) {
        promises.push(handleSearchYYYPByRow(row))
      }
      
      if (hasBuffId) {
        promises.push(handleSearchBuffByRow(row))
      }
      
      await Promise.all(promises)
      
      ElMessage.success('全部平台搜索完成！')
      
    } catch (error) {
      console.error('搜索全部平台失败:', error)
      ElMessage.error('搜索失败，请重试')
    } finally {
      setTimeout(() => {
        isSearching.value = false
        searchSource.value = ''
      }, 300)
    }
  }

  // 通过行数据搜索BUFF
  const handleSearchBuffByRow = async (row) => {
    console.log('=== 开始执行 handleSearchBuffByRow ===')
    console.log('row数据:', row)
    console.log('row.buff_id:', row.buff_id)
    console.log('selectedSteamId.value:', selectedSteamId.value)
    
    if (!row.buff_id) {
      console.log('没有buff_id，退出')
      ElMessage.warning('该武器没有BUFF ID')
      return
    }

    if (!selectedSteamId.value) {
      console.log('没有选择Steam账号，退出')
      ElMessage.warning('请先选择Steam账号')
      return
    }

    console.log('通过验证，开始请求')
    isSearching.value = true
    searchSource.value = 'buff'
    
    try {
      console.log('搜索BUFF:', row.market_listing_item_name, 'ID:', row.buff_id, 'SteamID:', selectedSteamId.value)
      
      // 构建请求数据
      const requestData = {
        steamId: selectedSteamId.value || '',
        goodsId: row.buff_id
      }
      
      const apiUrl = `${API_CONFIG.SPIDER_BASE_URL}/buffSpiderV1/getCommoditiesByGoodsId`
      
      console.log('请求URL:', apiUrl)
      console.log('请求数据:', requestData)
      
      // 调用BUFF商品列表API
      const response = await axios.post(apiUrl, requestData)
      
      console.log('API响应:', response.data)
      
      if (response.data.success) {
        const parsedData = response.data.data
        console.log('获取到BUFF已解析数据:', parsedData)
        
        // 直接使用Spider解析后的数据
        const commodityList = parsedData.commodityList || []
        const totalCount = parsedData.totalCount || 0
        const buyNum = parsedData.buy_num || 0
        const sellNum = parsedData.sell_num || 0
        const rentNum = parsedData.rent_num || 0
        const totalPage = parsedData.totalPage || 1
        
        console.log('商品列表:', commodityList)
        console.log('在售总数:', totalCount)
        console.log('总页数:', totalPage)
        console.log('求购数:', buyNum, '在售数:', sellNum, '租赁数:', rentNum)
        
        // 更新BUFF状态，显示商品列表
        buffCurrentWeapon.value = row
        buffCommodities.value = commodityList
        buffTotalCount.value = totalCount
        buffBuyNum.value = buyNum
        buffRentNum.value = rentNum
        buffCurrentPage.value = 1  // 重置分页到第一页
        buffTotalPage.value = totalPage  // 设置总页数
        buffHasMore.value = totalPage > 1  // 判断是否还有更多
        showBuffList.value = true
        // showYYYPList.value = false  // 允许同时显示两个列表
        showSearchResults.value = false  // 折叠搜索结果
        
        ElMessage.success(`成功获取 ${commodityList.length} 条商品数据，在售总数: ${totalCount}（求购:${buyNum}, 租赁:${rentNum}）`)
        
        // 预加载图片（相同URL只加载一次）
        preloadImages(commodityList)
        
        // 批量获取印花/挂件价格
        fetchStickerPrices(commodityList)
        
        // 滚动到商品列表区域
        setTimeout(() => {
          const listElement = document.querySelector('.buff-commodity-list')
          if (listElement) {
            listElement.scrollIntoView({ behavior: 'smooth', block: 'start' })
          }
        }, 100)
        
      } else {
        console.error('API返回失败:', response.data)
        ElMessage.error(response.data.message || '获取商品列表失败')
      }
      
    } catch (error) {
      console.error('搜索BUFF失败 - 完整错误:', error)
      console.error('错误响应:', error.response)
      console.error('错误数据:', error.response?.data)
      
      const errorMessage = error.response?.data?.message || error.message || '搜索失败，请检查网络连接'
      ElMessage.error(errorMessage)
    } finally {
      console.log('请求完成，重置加载状态')
      isSearching.value = false
      searchSource.value = ''
    }
  }

  // 通过行数据搜索CsFloat
  const handleSearchCsFloatByRow = async (row) => {
    if (!row.steam_hash_name) {
      ElMessage.warning('该武器没有Steam Hash Name')
      return
    }

    isSearching.value = true
    searchSource.value = 'csfloat'
    
    try {
      console.log('搜索CsFloat:', row.market_listing_item_name, 'Hash Name:', row.steam_hash_name)
      
      // 对hash name进行URL编码
      const encodedName = encodeURIComponent(row.steam_hash_name)
      
      // 构建CsFloat搜索URL
      const csfloatUrl = `https://csfloat.com/search?name=${encodedName}`
      
      // 在新窗口中打开CsFloat搜索页面
      window.open(csfloatUrl, '_blank')
      
      ElMessage.success(`正在跳转到CsFloat: ${row.market_listing_item_name}`)
      
    } catch (error) {
      console.error('搜索CsFloat失败:', error)
      ElMessage.error('跳转失败,请检查浏览器设置是否允许弹出窗口')
    } finally {
      // 延迟关闭加载状态,给用户反馈
      setTimeout(() => {
        isSearching.value = false
      }, 300)
    }
  }

  const handleClearSearch = () => {
    searchKeyword.value = ''
    searchResults.value = []
    searchSource.value = ''
    selectedExterior.value = ''
    selectedStatTrak.value = 'normal' // 重置为默认值：非StatTrak™
    currentPage.value = 1
    ElMessage.info('已重置搜索')
  }

  const handleViewDetails = (item) => {
    ElMessage.info(`查看详情: ${item.name}`)
    // TODO: 实现详情查看功能
  }

  const handleSizeChange = (val) => {
    pageSize.value = val
    currentPage.value = 1
  }

  const handleCurrentChange = (val) => {
    currentPage.value = val
  }

  // BUFF分页切换
  const handleBuffPageChange = (val) => {
    buffCurrentPage.value = val
  }

  // 悠悠有品分页切换
  const handleYYYPPageChange = (val) => {
    yyypCurrentPage.value = val
  }

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
      .replace(/\s*\|\s*/g, '___')  // " | " -> "___"
      .replace(/\s/g, '_')          // 剩余所有空格 -> "_"
      + '.png'

    // 直接使用路径，不通过 getApiUrl（因为 WEAPON_IMAGE 已经包含 /api）
    return `/api/api/v1/images/weapon_image/${imageName}`
  }

  // 处理图片加载错误
  const handleImageError = (event, steamHashName) => {
    // 将失败的steam_hash_name添加到404缓存中
    if (steamHashName) {
      image404Cache.value.add(steamHashName)
    }
    // 设置默认图片或隐藏
    event.target.style.display = 'none'
  }

  // 处理卡片点击
  const handleCardClick = (item, event) => {
    // 获取鼠标点击位置
    const x = event.clientX
    const y = event.clientY
    
    // 设置弹出框位置和内容
    cardPopoverPosition.value = { x, y }
    selectedCardItem.value = item
    showCardPopover.value = true
  }

  // 处理商品卡片点击
  const handleCommodityCardClick = (item, type, event) => {
    if (isMultiSelectMode.value) {
      // 多选模式下切换选中状态
      toggleCommoditySelection(item, type)
    } else {
      // 非多选模式打开详情弹窗
      commodityPreviewItem.value = item
      commodityPreviewType.value = type
      commodityPreviewVisible.value = true
      
      // 如果商品有印花或挂件，且还没有价格信息，则获取价格
      const needsFetch = (item.stickers && item.stickers.length > 0 && !item.stickers[0].priceInfo) ||
                        (item.pendants && item.pendants.length > 0 && !item.pendants[0].priceInfo)
      
      if (needsFetch) {
        fetchStickerPrices([item])
      }
    }
  }

  // 切换多选模式
  const toggleMultiSelectMode = () => {
    isMultiSelectMode.value = !isMultiSelectMode.value
    if (!isMultiSelectMode.value) {
      // 退出多选模式时清空选择
      selectedCommodities.value = []
      selectedCommodityType.value = ''
    }
  }

  // 判断商品是否被选中
  const isCommoditySelected = (item) => {
    return selectedCommodities.value.some(c => c.id === item.id)
  }

  // 切换商品选中状态
  const toggleCommoditySelection = (item, type) => {
    // 如果切换了平台类型，清空之前的选择
    if (selectedCommodityType.value && selectedCommodityType.value !== type) {
      selectedCommodities.value = []
    }
    selectedCommodityType.value = type
    
    const index = selectedCommodities.value.findIndex(c => c.id === item.id)
    if (index > -1) {
      selectedCommodities.value.splice(index, 1)
    } else {
      selectedCommodities.value.push(item)
    }
  }

  // 清空选择
  const clearCommoditySelection = () => {
    selectedCommodities.value = []
    selectedCommodityType.value = ''
  }

  // 全选当前列表
  const selectAllCommodities = (type) => {
    selectedCommodityType.value = type
    if (type === 'buff') {
      selectedCommodities.value = [...buffCommodities.value]
    } else if (type === 'yyyp') {
      selectedCommodities.value = [...yyypCommodities.value]
    }
    ElMessage.success(`已选择 ${selectedCommodities.value.length} 件商品`)
  }

  // 批量购买
  const handleBatchBuy = async () => {
    if (selectedCommodities.value.length === 0) {
      ElMessage.warning('请先选择要购买的商品')
      return
    }
    
    const totalPrice = selectedCommodities.value.reduce((sum, item) => {
      return sum + parseFloat(item.price || 0)
    }, 0)
    
    try {
      await ElMessageBox.confirm(
        `确定要批量购买 ${selectedCommodities.value.length} 件商品吗？\n总价: ¥${totalPrice.toFixed(2)}\n\n购买将自动执行，无需再次确认。`,
        '批量购买确认',
        {
          confirmButtonText: '确定购买',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      
      // 显示批量购买进度
      const loadingMessage = ElMessage({
        message: `正在批量购买 0/${selectedCommodities.value.length} 件商品...`,
        type: 'info',
        duration: 0,
        customClass: 'batch-buy-loading-message'
      })
      
      let successCount = 0
      let failCount = 0
      const failedItems = []
      
      // 执行批量购买
      if (selectedCommodityType.value === 'buff') {
        for (let i = 0; i < selectedCommodities.value.length; i++) {
          const item = selectedCommodities.value[i]
          loadingMessage.message = `正在购买 ${i + 1}/${selectedCommodities.value.length} 件商品...\n${item.commodityName || item.name || '商品'}`
          
          try {
            // BUFF购买逻辑（暂未实现）
            console.log('购买BUFF商品:', item)
            // TODO: 实现BUFF购买
            successCount++
          } catch (error) {
            console.error('购买失败:', error)
            failCount++
            failedItems.push(item.commodityName || item.name || '未知商品')
          }
          
          // 添加延迟避免请求过快
          if (i < selectedCommodities.value.length - 1) {
            await new Promise(resolve => setTimeout(resolve, 500))
          }
        }
      } else if (selectedCommodityType.value === 'yyyp') {
        for (let i = 0; i < selectedCommodities.value.length; i++) {
          const item = selectedCommodities.value[i]
          loadingMessage.message = `正在购买 ${i + 1}/${selectedCommodities.value.length} 件商品...\n${item.commodityName || '商品'}`
          
          try {
            // 静默购买悠悠有品商品
            const requestData = {
              steamId: selectedSteamId.value,
              commodityId: item.id,
              buyQuantity: 1,
              price: item.price,
              autoConfirmPayment: true,
              pollPayment: true
            }
            
            const response = await axios.post(
              `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/buyCommodity`,
              requestData
            )
            
            if (response.data.success) {
              successCount++
              console.log(`购买成功 [${i + 1}/${selectedCommodities.value.length}]:`, item.commodityName)
            } else {
              failCount++
              failedItems.push(item.commodityName || '未知商品')
              console.error(`购买失败 [${i + 1}/${selectedCommodities.value.length}]:`, response.data.message)
            }
          } catch (error) {
            console.error('购买失败:', error)
            failCount++
            failedItems.push(item.commodityName || '未知商品')
          }
          
          // 添加延迟避免请求过快
          if (i < selectedCommodities.value.length - 1) {
            await new Promise(resolve => setTimeout(resolve, 500))
          }
        }
      }
      
      loadingMessage.close()
      
      // 显示批量购买结果
      let resultMessage = `批量购买完成！\n\n`
      resultMessage += `成功：${successCount} 件\n`
      resultMessage += `失败：${failCount} 件\n`
      resultMessage += `总价：¥${totalPrice.toFixed(2)}`
      
      if (failedItems.length > 0) {
        resultMessage += `\n\n失败商品：\n${failedItems.slice(0, 5).join('\n')}`
        if (failedItems.length > 5) {
          resultMessage += `\n... 还有 ${failedItems.length - 5} 件`
        }
      }
      
      ElMessageBox.alert(
        resultMessage,
        '批量购买结果',
        {
          confirmButtonText: '知道了',
          type: successCount > 0 ? 'success' : 'warning',
          callback: () => {
            if (successCount > 0) {
              ElMessage.success(`成功购买 ${successCount} 件商品`)
            }
          }
        }
      )
      
      clearCommoditySelection()
      
      // 如果有成功购买的商品，自动刷新列表
      if (successCount > 0) {
        console.log('批量购买成功，自动刷新列表...')
        setTimeout(async () => {
          if (selectedCommodityType.value === 'yyyp' && yyypCurrentWeapon.value) {
            await handleRefreshYYYP()
          } else if (selectedCommodityType.value === 'buff' && buffCurrentWeapon.value) {
            await handleRefreshBuff()
          }
        }, 1000) // 延迟1秒刷新，确保后端数据已更新
      }
      
    } catch (e) {
      if (e !== 'cancel') {
        console.error('批量购买失败:', e)
        ElMessage.error('批量购买失败: ' + (e.message || '未知错误'))
      }
    }
  }

  // 获取商品标题
  const getCommodityTitle = (item) => {
    if (!item) return ''
    return item.itemName || item.name || '商品详情'
  }

  // 显示印花放大预览
  const showStickerPreview = (sticker) => {
    let imageUrl = ''
    let name = ''
    
    if (sticker.TemplateHashName) {
      imageUrl = getWeaponImage(sticker.TemplateHashName)
      name = sticker.Name || '印花'
    } else if (sticker.ImgUrl || sticker.img_url) {
      imageUrl = sticker.ImgUrl || sticker.img_url
      name = sticker.Name || sticker.name || '印花'
    }
    
    if (imageUrl) {
      stickerPreviewData.value = {
        name: name,
        imageUrl: imageUrl,
        type: '印花'
      }
      stickerPreviewVisible.value = true
    }
  }

  // 显示挂件放大预览
  const showPendantPreview = (pendant) => {
    let imageUrl = ''
    let name = ''
    
    if (pendant.steamHashName) {
      imageUrl = getWeaponImage(pendant.steamHashName)
      name = pendant.name || '挂件'
    } else if (pendant.imgUrl) {
      imageUrl = pendant.imgUrl
      name = pendant.name || '挂件'
    }
    
    if (imageUrl) {
      stickerPreviewData.value = {
        name: pendant.pendantSourceName || name,
        imageUrl: imageUrl,
        type: '挂件'
      }
      stickerPreviewVisible.value = true
    }
  }

  // 从详情弹窗购买商品
  const handleBuyCommodityFromPreview = () => {
    commodityPreviewVisible.value = false
    if (commodityPreviewType.value === 'buff') {
      handleBuyBuffCommodity(commodityPreviewItem.value)
    } else if (commodityPreviewType.value === 'yyyp') {
      handleBuyCommodity(commodityPreviewItem.value)
    }
  }

  // 页面加载时获取Steam ID列表
  onMounted(async () => {
    await loadSteamIdList()
  })

  return {
    searchKeyword,
    searchResults,
    isSearching,
    searchSource,
    currentPage,
    pageSize,
    paginatedResults,
    filteredResults,
    steamIdList,
    selectedSteamId,
    selectedExterior,
    selectedStatTrak,
    showSearchResults,
    displayMode,
    toggleSearchResults,
    handleSearchWeapon,
    handleRefreshSearch,
    handleSteamIdChange,
    handleExteriorChange,
    handleStatTrakChange,
    querySearchAsync,
    handleSelect,
    getWeaponImage,
    handleImageError,
    handleCardClick,
    // 卡片弹出框
    showCardPopover,
    cardPopoverPosition,
    selectedCardItem,
    // 商品详情弹窗
    commodityPreviewVisible,
    commodityPreviewItem,
    commodityPreviewType,
    handleCommodityCardClick,
    getCommodityTitle,
    handleBuyCommodityFromPreview,
    // 印花/挂件预览
    stickerPreviewVisible,
    stickerPreviewData,
    showStickerPreview,
    showPendantPreview,
    // 多选模式
    isMultiSelectMode,
    selectedCommodities,
    selectedCommodityType,
    toggleMultiSelectMode,
    isCommoditySelected,
    toggleCommoditySelection,
    clearCommoditySelection,
    selectAllCommodities,
    handleBatchBuy,
    // BUFF商品列表
    buffCommodities,
    buffCurrentWeapon,
    buffTotalCount,
    buffBuyNum,
    buffRentNum,
    showBuffList,
    showBuffTable,
    buffCurrentPage,
    buffPageSize,
    buffLoadingMore,
    buffHasMore,
    buffTotalPage,
    paginatedBuffCommodities,
    toggleBuffList,
    handleRefreshBuff,
    handleBuyBuffCommodity,
    handleBuffPageChange,
    loadMoreBuffCommodities,
    handleBuffScroll,
    // 悠悠有品商品列表
    yyypCommodities,
    yyypCurrentWeapon,
    yyypTotalCount,
    showYYYPList,
    showYYYPTable,
    yyypCurrentPage,
    yyypPageSize,
    yyypLoadingMore,
    yyypHasMore,
    paginatedYYYPCommodities,
    toggleYYYPList,
    handleBuyCommodity,
    fetchSingleNameTag,
    fetchStickerPrices,
    showStickersDialog,
    closeYYYPList,
    handleYYYPPageChange,
    handleRefreshYYYP,
    handleSearchYYYPByRow,
    loadMoreYYYPCommodities,
    handleYYYPScroll,
    handleSearchBuffByRow,
    handleSearchCsFloatByRow,
    handleSearchAllPlatforms,
    activePopoverRow,
    togglePopover,
    selectPlatform,
    handleClearSearch,
    handleViewDetails,
    getRarityType,
    getRarityColor,
    getWeaponTypeColor,
    getFloatRangeType,
    getFloatRangeColor,
    extractFloatRangeFromName,
    getWearColor,
    getWearRange,
    getExteriorColor,
    handleSizeChange,
    handleCurrentChange
  }
}
