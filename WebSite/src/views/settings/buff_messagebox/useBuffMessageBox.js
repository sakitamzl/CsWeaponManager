import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { apiUrls } from '@/config/api'


export function useBuffMessageBox() {
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
      const response = await axios.get(apiUrls.buffMessageTypes())
      if (response.data.success) {
        messageTypes.value = response.data.data
      }
    } catch (error) {
      console.error('获取BUFF消息类型失败:', error)
    }
  }

  const fetchMessages = async () => {
    loading.value = true
    try {
      const response = await axios.get(apiUrls.buffMessageData(currentPage.value, pageSize.value))
      if (response.data.success) {
        messageData.value = response.data.data
        totalItems.value = response.data.total || 0
      } else {
        ElMessage.error(response.data.error || response.data.message || '获取消息列表失败')
      }
    } catch (error) {
      console.error('获取BUFF消息列表失败:', error)
      ElMessage.error('获取消息列表失败')
    } finally {
      loading.value = false
    }
  }

  const handleSearch = async () => {
    // 仅做前端过滤显示（后端未提供搜索接口）
    currentPage.value = 1
  }

  const handleClearSearch = () => {
    searchText.value = ''
    messageTypeFilter.value = []
    dateRange.value = null
    currentPage.value = 1
    fetchMessages()
  }

  const handleTypeChange = async () => {
    // 仅前端过滤
    currentPage.value = 1
  }

  const handleTimeSearch = async () => {
    // 仅前端过滤（如需后端时间搜索，可新增接口）
    currentPage.value = 1
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
    let data = messageData.value
    if (messageTypeFilter.value && messageTypeFilter.value.length) {
      data = data.filter(d => messageTypeFilter.value.includes(d.sentName))
    }
    if (searchText.value && searchText.value.trim()) {
      const kw = searchText.value.trim()
      data = data.filter(d =>
        String(d.title || '').includes(kw) ||
        String(d.message_text || '').includes(kw) ||
        String(d.orderNo || '').includes(kw)
      )
    }
    if (dateRange.value && dateRange.value.length === 2) {
      const [start, end] = dateRange.value
      data = data.filter(d => d.createTime >= start && d.createTime <= end)
    }
    return data
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
