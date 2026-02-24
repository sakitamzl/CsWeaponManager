import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { apiUrls } from '@/config/api'


export function useSteamInventoryHistory() {

  // 数据
  const tableData = ref([])
  const loading = ref(false)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const totalCount = ref(0)
  const searchText = ref('')
  const tradeTypeFilter = ref('all')
  const dateRange = ref([])

  // 排序参数
  const sortField = ref('order_time')
  const sortOrder = ref('desc')

  // 计算属性
  const hasAdvancedFilters = computed(() => {
    return (searchText.value && searchText.value.trim()) ||
           (tradeTypeFilter.value && tradeTypeFilter.value !== 'all') ||
           (dateRange.value && dateRange.value.length === 2)
  })

  // 格式化日期时间
  const formatDateTime = (dateTimeStr) => {
    if (!dateTimeStr) return '-'
    return dateTimeStr.replace('T', ' ').substring(0, 19)
  }

  // 加载数据
  const loadData = async () => {
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
        sort_order: sortOrder.value,
        need_stats: 'false'
      }

      // 移除null值
      Object.keys(params).forEach(key => {
        if (params[key] === null) {
          delete params[key]
        }
      })

      // 调用后端API
      const response = await axios.get(apiUrls.steamInventoryHistoryList(), { params })

      if (response.data.success) {
        tableData.value = response.data.data.records
        totalCount.value = response.data.data.total
      } else {
        ElMessage.error('加载数据失败: ' + (response.data.error || '未知错误'))
        tableData.value = []
        totalCount.value = 0
      }

    } catch (error) {
      console.error('加载数据失败:', error)
      ElMessage.error('加载数据失败: ' + (error.message || '未知错误'))
      tableData.value = []
      totalCount.value = 0
    } finally {
      loading.value = false
    }
  }

  // 搜索
  const handleSearch = () => {
    currentPage.value = 1
    loadData()
  }

  // 清空搜索
  const handleClearSearch = () => {
    searchText.value = ''
    tradeTypeFilter.value = 'all'
    dateRange.value = []
    currentPage.value = 1
    loadData()
  }

  // 交易类型变化
  const handleTradeTypeChange = () => {
    currentPage.value = 1
    loadData()
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
    loadData()
  }

  // 分页变化
  const handleSizeChange = (val) => {
    pageSize.value = val
    currentPage.value = 1
    loadData()
  }

  const handleCurrentChange = (val) => {
    currentPage.value = val
    loadData()
  }

  // 排序变化
  const handleSortChange = ({ prop, order }) => {
    if (prop) {
      sortField.value = prop
      sortOrder.value = order === 'ascending' ? 'asc' : 'desc'
      loadData()
    }
  }

  // 初始化
  onMounted(() => {
    loadData()
  })

  return {
    loading,
    tableData,
    currentPage,
    pageSize,
    totalCount,
    searchText,
    tradeTypeFilter,
    dateRange,
    hasAdvancedFilters,
    formatDateTime,
    handleSearch,
    handleClearSearch,
    handleTradeTypeChange,
    handleDateRangeChange,
    handleTimeSearch,
    handleSizeChange,
    handleCurrentChange,
    handleSortChange
  }
}
