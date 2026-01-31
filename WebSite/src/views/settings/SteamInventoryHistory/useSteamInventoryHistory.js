import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { API_CONFIG } from '@/config/api'


export function useSteamInventoryHistory() {
  // 配置
  const API_BASE_URL = API_CONFIG.BASE_URL
  const API_PREFIX = '/webSteamInventoryHistoryV1' // 使用变量统一管理API前缀
  
  // 数据
  const tableData = ref([])
  const loading = ref(false)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const totalCount = ref(0)
  const searchText = ref('')
  const tradeTypeFilter = ref('all')
  const dateRange = ref([])
  
  // 统计数据
  const gainCount = ref(0)
  const lossCount = ref(0)
  
  // 排序参数
  const sortField = ref('order_time')
  const sortOrder = ref('desc')
  
  // 缓存标记 - 用于判断是否需要重新查询统计
  const lastSearchParams = ref('')
  const statsLoaded = ref(false)
  
  // 计算属性
  const hasAdvancedFilters = computed(() => {
    return (searchText.value && searchText.value.trim()) || 
           (tradeTypeFilter.value && tradeTypeFilter.value !== 'all') ||
           (dateRange.value && dateRange.value.length === 2)
  })
  
  const gainPercentage = computed(() => {
    if (totalCount.value === 0) return 0
    return ((gainCount.value / totalCount.value) * 100).toFixed(1)
  })
  
  const lossPercentage = computed(() => {
    if (totalCount.value === 0) return 0
    return ((lossCount.value / totalCount.value) * 100).toFixed(1)
  })
  
  // 格式化日期时间
  const formatDateTime = (dateTimeStr) => {
    if (!dateTimeStr) return '-'
    return dateTimeStr.replace('T', ' ').substring(0, 19)
  }
  
  // 加载数据 - 优化版
  const loadData = async (forceReloadStats = false) => {
    loading.value = true
    try {
      // 构建查询参数
      const params = {
        page: currentPage.value,
        page_size: pageSize.value,
        trade_type: tradeTypeFilter.value !== 'all' ? tradeTypeFilter.value : null,
        search: searchText.value || null,
        start_date: dateRange.value?.[0] || null,
        end_date: dateRange.value?.[1] || null,
        sort_field: sortField.value,
        sort_order: sortOrder.value
      }
  
      // 生成搜索参数标识
      const searchParamsKey = JSON.stringify({
        trade_type: params.trade_type,
        search: params.search,
        start_date: params.start_date,
        end_date: params.end_date
      })
  
      // 判断是否需要重新加载统计数据
      const needStats = forceReloadStats || searchParamsKey !== lastSearchParams.value || !statsLoaded.value
      
      // 只在切换页或改变排序时不查询统计，其他情况都查询
      params.need_stats = needStats ? 'true' : 'false'
  
      // 移除null值
      Object.keys(params).forEach(key => {
        if (params[key] === null) {
          delete params[key]
        }
      })
  
      // 调用后端API
      const response = await axios.get(`${API_BASE_URL}${API_PREFIX}/list`, { params })
      
      if (response.data.success) {
        tableData.value = response.data.data.records
        totalCount.value = response.data.data.total
        
        // 如果返回了统计数据，更新缓存
        if (needStats) {
          gainCount.value = response.data.data.gain_count
          lossCount.value = response.data.data.loss_count
          lastSearchParams.value = searchParamsKey
          statsLoaded.value = true
        }
      } else {
        ElMessage.error('加载数据失败: ' + (response.data.error || '未知错误'))
        tableData.value = []
        totalCount.value = 0
        if (needStats) {
          gainCount.value = 0
          lossCount.value = 0
        }
      }
      
    } catch (error) {
      console.error('加载数据失败:', error)
      ElMessage.error('加载数据失败: ' + (error.message || '未知错误'))
      tableData.value = []
      totalCount.value = 0
      gainCount.value = 0
      lossCount.value = 0
    } finally {
      loading.value = false
    }
  }
  
  // 搜索
  const handleSearch = () => {
    currentPage.value = 1
    loadData(true) // 强制重新加载统计
  }
  
  // 清空搜索
  const handleClearSearch = () => {
    searchText.value = ''
    tradeTypeFilter.value = 'all'
    dateRange.value = []
    currentPage.value = 1
    statsLoaded.value = false
    loadData(true) // 强制重新加载统计
  }
  
  // 交易类型变化
  const handleTradeTypeChange = () => {
    currentPage.value = 1
    loadData(true) // 强制重新加载统计
  }
  
  // 日期范围变化
  const handleDateRangeChange = () => {
    // 不自动搜索，等待用户点击按钮
  }
  
  // 按时间搜索
  const handleTimeSearch = () => {
    if (!dateRange.value || dateRange.value.length !== 2) {
      ElMessage.warning('请选择时间范围')
      return
    }
    currentPage.value = 1
    loadData(true) // 强制重新加载统计
  }
  
  // 分页变化 - 优化：不重新查询统计
  const handleSizeChange = (val) => {
    pageSize.value = val
    currentPage.value = 1
    loadData(false) // 不重新加载统计
  }
  
  const handleCurrentChange = (val) => {
    currentPage.value = val
    loadData(false) // 不重新加载统计，切换页速度更快
  }
  
  // 排序变化 - 优化：不重新查询统计
  const handleSortChange = ({ prop, order }) => {
    if (prop) {
      sortField.value = prop
      sortOrder.value = order === 'ascending' ? 'asc' : 'desc'
      loadData(false) // 不重新加载统计
    }
  }
  
  // 初始化
  onMounted(() => {
    loadData(true) // 首次加载需要统计数据
  })
}
