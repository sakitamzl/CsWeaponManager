<template>
  <div>
    <div class="stats-summary">
      <div class="card">
        <div class="search-section">
          <div class="flex flex-wrap gap-4 items-center">
            <el-input
              v-model="searchText"
              placeholder="搜索消息标题、内容、订单号..."
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
        
        <div class="search-stats-divider"></div>
        
        <div class="stats-container">
          <div class="stats-section">
            <h3>消息统计</h3>
            <div class="stats-grid">
              <div class="stat-item">
                <span class="stat-label">总消息数:</span>
                <span class="stat-value">{{ totalStats.totalCount }} 条</span>
              </div>
            </div>
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
        <el-table-column prop="message_id" label="消息ID" width="150" show-overflow-tooltip align="left" />
        <el-table-column prop="title" label="标题" width="250" show-overflow-tooltip align="left" />
        <el-table-column prop="sentName" label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getMessageTypeColor(row.sentName)" size="small">
              {{ row.sentName || '-' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message_text" label="消息内容" min-width="300" show-overflow-tooltip align="left" />
        <el-table-column prop="orderNo" label="订单号" width="180" show-overflow-tooltip align="left" />
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
  name: 'MessageBox',
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
    const totalStats = ref({
      totalCount: 0,
      readCount: 0,
      unreadCount: 0
    })

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

    const fetchMessageStats = async () => {
      try {
        const response = await axios.get(apiUrls.messageStats())
        if (response.data.success) {
          const stats = response.data.data
          totalStats.value = {
            totalCount: stats.totalCount || 0,
            readCount: stats.readCount || 0,
            unreadCount: stats.unreadCount || 0
          }
        }
      } catch (error) {
        console.error('获取消息统计失败:', error)
      }
    }

    const fetchMessages = async () => {
      loading.value = true
      try {
        const response = await axios.get(apiUrls.messageData(currentPage.value, pageSize.value))
        if (response.data.success) {
          messageData.value = response.data.data
          await fetchMessageStats()
          totalItems.value = totalStats.value.totalCount
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
          totalItems.value = response.data.data.length
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
          totalItems.value = response.data.data.length
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
          totalItems.value = response.data.data.length
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
      totalStats,
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
.stats-summary {
  margin-bottom: 20px;
}

.card {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.search-section {
  margin-bottom: 20px;
}

.flex {
  display: flex;
}

.flex-wrap {
  flex-wrap: wrap;
}

.gap-4 {
  gap: 1rem;
}

.items-center {
  align-items: center;
}

.search-input {
  width: 300px;
}

.type-select {
  width: 250px;
}

.date-picker {
  width: 280px;
}

.search-stats-divider {
  height: 1px;
  background: var(--border-color);
  margin: 20px 0;
}

.stats-container {
  display: flex;
  gap: 30px;
}

.stats-section {
  flex: 1;
}

.stats-section h3 {
  margin-bottom: 15px;
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 600;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 15px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.stat-label {
  color: var(--text-secondary);
  font-size: 14px;
}

.stat-value {
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 600;
}

.table-container {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.pagination {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.pagination-top {
  border-bottom: 1px solid var(--border-color);
}

.pagination-bottom {
  border-top: 1px solid var(--border-color);
}
</style>
