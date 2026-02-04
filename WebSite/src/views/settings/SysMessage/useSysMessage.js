import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

export function useSysMessage() {
  const messageData = ref([])
  const loading = ref(false)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const totalItems = ref(0)
  const searchText = ref('')
  const dateRange = ref([])
  const selectedIds = ref([])

  // 筛选条件
  const filterType = ref(null)
  const filterLevel = ref(null)
  const filterSource = ref(null)
  const filterReadStatus = ref(null)

  // 统计数据
  const stats = ref({
    totalCount: 0,
    unreadCount: 0,
    readCount: 0
  })

  // 通知类型和来源列表
  const messageTypes = ref([])
  const messageSources = ref([])

  // 搜索模式
  const searchMode = ref('default') // default, keyword, time, filter

  // 获取通知数据
  const fetchSysMessages = async () => {
    try {
      loading.value = true
      const response = await axios.get(
        `/api/getSysMessageData/${currentPage.value}/${pageSize.value}`
      )

      if (response.data.success) {
        messageData.value = response.data.data
        totalItems.value = response.data.total
      } else {
        ElMessage.error('获取通知数据失败')
      }
    } catch (error) {
      console.error('获取通知数据失败:', error)
      ElMessage.error('获取通知数据失败')
    } finally {
      loading.value = false
    }
  }

  // 获取统计数据
  const fetchStats = async () => {
    try {
      const response = await axios.get('/api/getSysMessageStats')
      if (response.data.success) {
        stats.value = response.data.data
      }
    } catch (error) {
      console.error('获取统计数据失败:', error)
    }
  }

  // 获取通知类型
  const fetchSysMessageTypes = async () => {
    try {
      const response = await axios.get('/api/getSysMessageTypes')
      if (response.data.success) {
        messageTypes.value = response.data.data
      }
    } catch (error) {
      console.error('获取通知类型失败:', error)
    }
  }

  // 获取通知来源
  const fetchSysMessageSources = async () => {
    try {
      const response = await axios.get('/api/getSysMessageSources')
      if (response.data.success) {
        messageSources.value = response.data.data
      }
    } catch (error) {
      console.error('获取通知来源失败:', error)
    }
  }

  // 关键词搜索
  const searchByKeyword = async () => {
    if (!searchText.value.trim()) {
      ElMessage.warning('请输入搜索关键词')
      return
    }

    try {
      loading.value = true
      const response = await axios.post('/api/searchSysMessageByKeyword', {
        keyword: searchText.value,
        page: currentPage.value,
        page_size: pageSize.value
      })

      if (response.data.success) {
        messageData.value = response.data.data
        totalItems.value = response.data.total
        searchMode.value = 'keyword'
      } else {
        ElMessage.error('搜索失败')
      }
    } catch (error) {
      console.error('搜索失败:', error)
      ElMessage.error('搜索失败')
    } finally {
      loading.value = false
    }
  }

  // 时间范围搜索
  const searchByTime = async () => {
    if (!dateRange.value || dateRange.value.length !== 2) {
      ElMessage.warning('请选择时间范围')
      return
    }

    try {
      loading.value = true
      const response = await axios.post('/api/searchSysMessageByTime', {
        start_date: dateRange.value[0],
        end_date: dateRange.value[1],
        page: currentPage.value,
        page_size: pageSize.value
      })

      if (response.data.success) {
        messageData.value = response.data.data
        totalItems.value = response.data.total
        searchMode.value = 'time'
      } else {
        ElMessage.error('搜索失败')
      }
    } catch (error) {
      console.error('搜索失败:', error)
      ElMessage.error('搜索失败')
    } finally {
      loading.value = false
    }
  }

  // 多条件筛选
  const searchByFilter = async () => {
    try {
      loading.value = true

      const types = filterType.value ? [filterType.value] : []
      const levels = filterLevel.value ? [filterLevel.value] : []
      const sources = filterSource.value ? [filterSource.value] : []

      const response = await axios.post('/api/searchSysMessageByFilter', {
        types: types,
        levels: levels,
        sources: sources,
        is_read: filterReadStatus.value,
        page: currentPage.value,
        page_size: pageSize.value
      })

      if (response.data.success) {
        messageData.value = response.data.data
        totalItems.value = response.data.total
        searchMode.value = 'filter'
      } else {
        ElMessage.error('筛选失败')
      }
    } catch (error) {
      console.error('筛选失败:', error)
      ElMessage.error('筛选失败')
    } finally {
      loading.value = false
    }
  }

  // 标记为已读
  const markAsRead = async (messageIds) => {
    try {
      const response = await axios.post('/api/markAsRead', {
        message_ids: messageIds
      })

      if (response.data.success) {
        ElMessage.success(response.data.message)
        await fetchStats()
        refreshCurrentView()
      } else {
        ElMessage.error('标记失败')
      }
    } catch (error) {
      console.error('标记失败:', error)
      ElMessage.error('标记失败')
    }
  }

  // 标记所有为已读
  const markAllAsRead = async () => {
    try {
      await ElMessageBox.confirm('确定要将所有未读通知标记为已读吗？', '确认操作', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })

      const response = await axios.post('/api/markAllAsRead')

      if (response.data.success) {
        ElMessage.success(response.data.message)
        await fetchStats()
        refreshCurrentView()
      } else {
        ElMessage.error('标记失败')
      }
    } catch (error) {
      if (error !== 'cancel') {
        console.error('标记失败:', error)
        ElMessage.error('标记失败')
      }
    }
  }

  // 删除通知
  const deleteSysMessages = async (messageIds) => {
    try {
      await ElMessageBox.confirm('确定要删除选中的通知吗？', '确认删除', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })

      const response = await axios.post('/api/deleteSysMessage', {
        message_ids: messageIds
      })

      if (response.data.success) {
        ElMessage.success(response.data.message)
        await fetchStats()
        refreshCurrentView()
      } else {
        ElMessage.error('删除失败')
      }
    } catch (error) {
      if (error !== 'cancel') {
        console.error('删除失败:', error)
        ElMessage.error('删除失败')
      }
    }
  }

  // 刷新当前视图
  const refreshCurrentView = () => {
    if (searchMode.value === 'keyword') {
      searchByKeyword()
    } else if (searchMode.value === 'time') {
      searchByTime()
    } else if (searchMode.value === 'filter') {
      searchByFilter()
    } else {
      fetchSysMessages()
    }
  }

  // 处理搜索
  const handleSearch = () => {
    currentPage.value = 1
    searchByKeyword()
  }

  // 处理清空搜索
  const handleClearSearch = () => {
    searchText.value = ''
    dateRange.value = []
    filterType.value = null
    filterLevel.value = null
    filterSource.value = null
    filterReadStatus.value = null
    currentPage.value = 1
    searchMode.value = 'default'
    fetchSysMessages()
  }

  // 处理时间搜索
  const handleTimeSearch = () => {
    currentPage.value = 1
    searchByTime()
  }

  // 处理筛选变化
  const handleFilterChange = () => {
    currentPage.value = 1
    searchByFilter()
  }

  // 处理日期范围变化
  const handleDateRangeChange = () => {
    if (!dateRange.value || dateRange.value.length === 0) {
      handleClearSearch()
    }
  }

  // 处理分页大小变化
  const handleSizeChange = (newSize) => {
    pageSize.value = newSize
    currentPage.value = 1
    refreshCurrentView()
  }

  // 处理当前页变化
  const handleCurrentChange = (newPage) => {
    currentPage.value = newPage
    refreshCurrentView()
  }

  // 处理选择变化
  const handleSelectionChange = (selection) => {
    selectedIds.value = selection.map((item) => item.message_id)
  }

  // 处理标记已读
  const handleMarkAsRead = (ids) => {
    markAsRead(ids)
  }

  // 处理标记选中为已读
  const handleMarkSelectedAsRead = () => {
    if (selectedIds.value.length === 0) {
      ElMessage.warning('请选择要标记的通知')
      return
    }
    markAsRead(selectedIds.value)
  }

  // 处理标记所有为已读
  const handleMarkAllAsRead = () => {
    markAllAsRead()
  }

  // 处理删除
  const handleDelete = (ids) => {
    deleteSysMessages(ids)
  }

  // 处理删除选中
  const handleDeleteSelected = () => {
    if (selectedIds.value.length === 0) {
      ElMessage.warning('请选择要删除的通知')
      return
    }
    deleteSysMessages(selectedIds.value)
  }

  // 获取行样式
  const getRowStyle = ({ row }) => {
    if (!row.is_read) {
      return { backgroundColor: 'rgba(64, 158, 255, 0.05)' }
    }
    return { backgroundColor: 'transparent' }
  }

  // 获取类型标签颜色
  const getTypeTagColor = (type) => {
    const colorMap = {
      system: '',
      transaction: 'success',
      warning: 'warning',
      error: 'danger',
      info: 'info'
    }
    return colorMap[type] || ''
  }

  // 获取级别标签颜色
  const getLevelTagColor = (level) => {
    const colorMap = {
      info: 'info',
      success: 'success',
      warning: 'warning',
      error: 'danger'
    }
    return colorMap[level] || 'info'
  }

  // 获取类型标签
  const getTypeLabel = (type) => {
    const labelMap = {
      system: '系统通知',
      transaction: '交易通知',
      warning: '警告',
      error: '错误',
      info: '信息'
    }
    return labelMap[type] || type
  }

  // 获取级别标签
  const getLevelLabel = (level) => {
    const labelMap = {
      info: '信息',
      success: '成功',
      warning: '警告',
      error: '错误'
    }
    return labelMap[level] || level
  }

  // 获取来源标签
  const getSourceLabel = (source) => {
    const labelMap = {
      system: '系统',
      buff: 'BUFF',
      yyyp: '悠悠有品',
      steam: 'Steam',
      igxe: 'IGXE',
      csfloat: 'CSFloat'
    }
    return labelMap[source] || source
  }

  onMounted(() => {
    fetchSysMessages()
    fetchStats()
    fetchSysMessageTypes()
    fetchSysMessageSources()
  })

  return {
    messageData,
    loading,
    currentPage,
    pageSize,
    totalItems,
    searchText,
    dateRange,
    selectedIds,
    filterType,
    filterLevel,
    filterSource,
    filterReadStatus,
    stats,
    messageTypes,
    messageSources,
    handleSearch,
    handleClearSearch,
    handleTimeSearch,
    handleFilterChange,
    handleDateRangeChange,
    handleSizeChange,
    handleCurrentChange,
    handleSelectionChange,
    handleMarkAsRead,
    handleMarkSelectedAsRead,
    handleMarkAllAsRead,
    handleDelete,
    handleDeleteSelected,
    getRowStyle,
    getTypeTagColor,
    getLevelTagColor,
    getTypeLabel,
    getLevelLabel,
    getSourceLabel
  }
}
