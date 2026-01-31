import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { apiUrls } from '@/config/api'


export function useYyypMessageBox() {
  const loading = ref(false)
  const searchText = ref('')
  const messageTypeFilter = ref([])
  const dateRange = ref(null)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const totalItems = ref(0)
  const messageData = ref([])
  const messageTypes = ref([])

  const fetchMessageTypes = async () => {
    try {
      const response = await axios.get(apiUrls.messageTypes())
      if (response.data.success) {
        messageTypes.value = response.data.data
      }
    } catch (error) {
      console.error('获取消息类型失败:', error)
    }
  }

  const fetchMessages = async () => {
    loading.value = true
    try {
      const response = await axios.get(apiUrls.messageData(currentPage.value, pageSize.value))
      if (response.data.success) {
        messageData.value = response.data.data
        totalItems.value = response.data.total || 0
      } else {
        ElMessage.error(response.data.message || '获取消息列表失败')
      }
    } catch (error) {
      console.error('获取消息列表失败:', error)
      ElMessage.error('获取消息列表失败')
    } finally {
      loading.value = false
    }
  }

  const handleSearch = async () => {
    if (!searchText.value.trim()) {
      ElMessage.warning('请输入搜索关键词')
      return
    }

    loading.value = true
    try {
      const response = await axios.post(apiUrls.searchMessageByKeyword(), {
        keyword: searchText.value,
        page: currentPage.value,
        page_size: pageSize.value
      })
      if (response.data.success) {
        messageData.value = response.data.data
        totalItems.value = response.data.total || 0
      } else {
        ElMessage.error(response.data.message || '搜索失败')
      }
    } catch (error) {
      console.error('搜索失败:', error)
      ElMessage.error('搜索失败')
    } finally {
      loading.value = false
    }
  }

  const handleClearSearch = () => {
    searchText.value = ''
    messageTypeFilter.value = []
    dateRange.value = null
    currentPage.value = 1
    fetchMessages()
  }

  const handleTypeChange = async () => {
    if (messageTypeFilter.value.length === 0) {
      fetchMessages()
      return
    }

    loading.value = true
    try {
      const response = await axios.post(apiUrls.searchMessageByType(), {
        message_types: messageTypeFilter.value,
        page: currentPage.value,
        page_size: pageSize.value
      })
      if (response.data.success) {
        messageData.value = response.data.data
        totalItems.value = response.data.total || 0
      } else {
        ElMessage.error(response.data.message || '搜索失败')
      }
    } catch (error) {
      console.error('按类型搜索失败:', error)
      ElMessage.error('按类型搜索失败')
    } finally {
      loading.value = false
    }
  }

  const handleTimeSearch = async () => {
    if (!dateRange.value || dateRange.value.length !== 2) {
      ElMessage.warning('请选择时间范围')
      return
    }

    loading.value = true
    try {
      const response = await axios.post(apiUrls.searchMessageByTime(), {
        start_date: dateRange.value[0],
        end_date: dateRange.value[1],
        page: currentPage.value,
        page_size: pageSize.value
      })
      if (response.data.success) {
        messageData.value = response.data.data
        totalItems.value = response.data.total || 0
      } else {
        ElMessage.error(response.data.message || '搜索失败')
      }
    } catch (error) {
      console.error('按时间搜索失败:', error)
      ElMessage.error('按时间搜索失败')
    } finally {
      loading.value = false
    }
  }

  const handleDateRangeChange = (value) => {
    dateRange.value = value
  }

  const handleCurrentChange = (page) => {
    currentPage.value = page
    fetchMessages()
  }

  const handleSizeChange = (size) => {
    pageSize.value = size
    currentPage.value = 1
    fetchMessages()
  }

  const getMessageTypeColor = (type) => {
    const colorMap = {
      '购买': 'success',
      '出售': 'warning',
      '租赁': 'primary',
      '提取': 'info',
      '诚信卖家': 'danger'
    }
    return colorMap[type] || ''
  }

  const filteredMessageData = computed(() => {
    return messageData.value
  })

  onMounted(() => {
    fetchMessages()
    fetchMessageTypes()
  })

  return {
    loading,
    searchText,
    messageTypeFilter,
    dateRange,
    currentPage,
    pageSize,
    totalItems,
    messageData,
    messageTypes,
    filteredMessageData,
    handleSearch,
    handleClearSearch,
    handleTypeChange,
    handleTimeSearch,
    handleDateRangeChange,
    handleCurrentChange,
    handleSizeChange,
    getMessageTypeColor
  }
  }
}
}
