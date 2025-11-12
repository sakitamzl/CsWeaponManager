<template>
  <div>
    <div class="stats-summary">
      <div class="card">
        <div class="search-section">
          <div class="flex flex-wrap gap-4 items-center">
            <el-input
              v-model="searchText"
              placeholder="搜索消息标题、内容、订单号...（仅本页支持类型筛选与分页展示）"
              prefix-icon="Search"
              class="search-input"
              @keyup.enter="handleSearch"
              @clear="handleClearSearch"
              clearable
            />
            <el-button type="primary" @click="handleSearch" :loading="loading">搜索</el-button>
            <el-button @click="handleClearSearch" :disabled="loading">重置</el-button>
            <el-select 
              v-model="messageTypeFilter" 
              placeholder="选择消息类型（可多选）" 
              class="type-select" 
              @change="handleTypeChange" 
              multiple
              collapse-tags
              collapse-tags-tooltip
              clearable
            >
              <el-option v-for="type in messageTypes" :key="type" :label="type" :value="type" />
            </el-select>
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              class="date-picker"
              @change="handleDateRangeChange"
              clearable
            />
            <el-button type="success" @click="handleTimeSearch" :loading="loading">按时间搜索</el-button>
          </div>
        </div>
      </div>
    </div>

    <div class="table-container">
      <div class="pagination pagination-top">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalItems"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
      
      <el-table
        :data="filteredMessageData"
        v-loading="loading"
        element-loading-text="加载中..."
        style="width: 100%"
        :row-style="{ backgroundColor: 'transparent' }"
        :header-row-style="{ backgroundColor: 'var(--bg-tertiary)' }"
      >
        <el-table-column prop="message_id" label="消息ID" width="220" show-overflow-tooltip align="left" />
        <el-table-column prop="title" label="标题" width="250" show-overflow-tooltip align="left" />
        <el-table-column prop="message_text" label="消息内容" min-width="300" show-overflow-tooltip align="left" />
        <el-table-column prop="createTime" label="创建时间" width="180" align="center" />
      </el-table>

      <div class="pagination pagination-bottom">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalItems"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { apiUrls } from '@/config/api'

export default {
  name: 'BuffMessageBox',
  setup() {
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
}
</script>

<style scoped>
.stats-summary { margin-bottom: 20px; }
.card { background: var(--bg-secondary); border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.search-section { margin-bottom: 20px; }
.flex { display: flex; }
.flex-wrap { flex-wrap: wrap; }
.gap-4 { gap: 1rem; }
.items-center { align-items: center; }
.search-input { width: 300px; }
.type-select { width: 250px; }
.date-picker { width: 280px; }
.table-container { background: var(--bg-secondary); border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.pagination { display: flex; justify-content: center; padding: 20px 0; }
.pagination-top { border-bottom: 1px solid var(--border-color); }
.pagination-bottom { border-top: 1px solid var(--border-color); }
</style>
