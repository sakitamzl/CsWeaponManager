<template>
  <div>
    <!-- 搜索与统计数据 -->
    <div class="stats-summary">
      <div class="card">
        <!-- 搜索栏 -->
        <div class="search-section">
          <div class="flex flex-wrap gap-4 items-center">
            <el-input
              v-model="searchText"
              placeholder="搜索交易标题、物品名、武器名..."
              prefix-icon="Search"
              class="search-input"
              @keyup.enter="handleSearch"
              @clear="handleClearSearch"
              clearable
            />
            <el-button type="primary" @click="handleSearch" :loading="loading">
              搜索
            </el-button>
            <el-button @click="handleClearSearch" :disabled="loading">
              重置
            </el-button>
            <el-select 
              v-model="tradeTypeFilter" 
              placeholder="交易类型" 
              class="status-select" 
              @change="handleTradeTypeChange"
              clearable
            >
              <el-option label="全部类型" value="all" />
              <el-option label="获得 (+)" value="+" />
              <el-option label="失去 (-)" value="-" />
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
            <el-button type="success" @click="handleTimeSearch" :loading="loading">
              按时间搜索
            </el-button>
          </div>
        </div>
        
        <!-- 分隔线 -->
        <div class="search-stats-divider"></div>
        
        <!-- 当前筛选状态 -->
        <div class="filter-status" v-if="hasAdvancedFilters">
          <span class="filter-label">当前筛选：</span>
          <el-tag v-if="searchText && searchText.trim()" type="primary" size="small" closable @close="searchText = ''">
            关键词: {{ searchText }}
          </el-tag>
          <el-tag v-if="tradeTypeFilter && tradeTypeFilter !== 'all'" type="success" size="small" closable @close="tradeTypeFilter = 'all'">
            类型: {{ tradeTypeFilter === '+' ? '获得' : '失去' }}
          </el-tag>
          <el-tag v-if="dateRange && dateRange.length === 2" type="danger" size="small" closable @close="dateRange = null">
            时间: {{ dateRange[0] }} ~ {{ dateRange[1] }}
          </el-tag>
        </div>
        
        <!-- 统计数据 -->
        <div class="stats-container">
          <div class="stats-section">
            <h3>统计数据</h3>
            <div class="stats-grid-3x2">
              <div class="stat-item">
                <span class="stat-label">总记录数:</span>
                <span class="stat-value">{{ totalCount }} 条</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">获得记录:</span>
                <span class="stat-value gain">{{ gainCount }} 条</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">失去记录:</span>
                <span class="stat-value loss">{{ lossCount }} 条</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">当前页记录:</span>
                <span class="stat-value">{{ tableData.length }} 条</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">获得占比:</span>
                <span class="stat-value">{{ gainPercentage }}%</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">失去占比:</span>
                <span class="stat-value">{{ lossPercentage }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 表格 -->
    <div class="table-container">
      <div class="pagination pagination-top">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalCount"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>

      <el-table 
        :data="tableData" 
        v-loading="loading"
        element-loading-text="加载中..."
        style="width: 100%"
        :row-style="{ backgroundColor: 'transparent' }"
        :header-row-style="{ backgroundColor: 'var(--bg-tertiary)' }"
        :flexible="true"
        :scrollbar-always-on="true"
        @sort-change="handleSortChange"
      >
        <el-table-column 
          prop="order_time" 
          label="交易时间" 
          width="180"
          sortable="custom"
          align="left"
        >
          <template #default="scope">
            <span>{{ formatDateTime(scope.row.order_time) }}</span>
          </template>
        </el-table-column>

        <el-table-column 
          prop="trade_title" 
          label="交易标题" 
          min-width="250"
          show-overflow-tooltip
          align="left"
        >
          <template #default="scope">
            <span>{{ scope.row.trade_title || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column 
          prop="appid" 
          label="AppID" 
          width="100"
          align="center"
        >
          <template #default="scope">
            <span>{{ scope.row.appid || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column 
          prop="item_name" 
          label="物品名称" 
          min-width="200"
          show-overflow-tooltip
          align="left"
        >
          <template #default="scope">
            <span>{{ scope.row.item_name || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column 
          prop="weapon_name" 
          label="武器名称" 
          min-width="180"
          show-overflow-tooltip
          align="left"
        >
          <template #default="scope">
            <span>{{ scope.row.weapon_name || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column 
          prop="weapon_type" 
          label="武器类型" 
          width="120"
          show-overflow-tooltip
          align="left"
        >
          <template #default="scope">
            <span>{{ scope.row.weapon_type || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column 
          prop="float_range" 
          label="磨损等级" 
          width="120"
          align="center"
        >
          <template #default="scope">
            <span>{{ scope.row.float_range || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column 
          prop="trade_type" 
          label="类型" 
          width="100"
          align="center"
          fixed="right"
        >
          <template #default="scope">
            <el-tag 
              :type="scope.row.trade_type === '+' ? 'success' : 'danger'"
              effect="dark"
            >
              {{ scope.row.trade_type === '+' ? '获得' : '失去' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination pagination-bottom">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalCount"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// 配置
const API_BASE_URL = 'http://127.0.0.1:9001'
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
</script>

<style scoped>
/* 搜索输入框 */
.search-input {
  min-width: 200px;
  flex: 1;
  max-width: 300px;
}

.status-select {
  min-width: 120px;
  max-width: 150px;
}

.date-picker {
  min-width: 240px;
  max-width: 280px;
}

/* 分页 */
.pagination {
  margin-top: clamp(1rem, 3vw, 1.25rem);
  display: flex;
  justify-content: center;
}

.pagination-top {
  margin-top: 0;
  margin-bottom: clamp(1rem, 3vw, 1.25rem);
}

.pagination-bottom {
  margin-top: clamp(1rem, 3vw, 1.25rem);
}

:deep(.el-pagination) {
  background-color: transparent;
}

:deep(.el-pagination .el-pager li) {
  background-color: transparent;
  color: #fff;
  border: 1px solid #333;
}

:deep(.el-pagination .el-pager li:hover) {
  background-color: #333;
}

:deep(.el-pagination .el-pager li.is-active) {
  background-color: #4CAF50;
  color: #fff;
}

:deep(.el-pagination .btn-prev),
:deep(.el-pagination .btn-next) {
  background-color: transparent;
  color: #fff;
  border: 1px solid #333;
}

:deep(.el-pagination .btn-prev:hover),
:deep(.el-pagination .btn-next:hover) {
  background-color: #333;
}

:deep(.el-pagination .el-select .el-input__inner) {
  background-color: #484848 !important;
  color: #fff;
  border: 1px solid #333;
}

:deep(.el-pagination .el-input__inner) {
  background-color: #484848 !important;
  color: #fff;
  border: 1px solid #333;
}

/* 表格样式 */
:deep(.el-table) {
  background-color: transparent;
  color: #fff;
  font-size: clamp(0.75rem, 1.2vw, 0.875rem);
  min-width: 1000px;
}

:deep(.el-table th) {
  background-color: var(--bg-tertiary);
  color: #ccc;
  font-weight: 600;
}

:deep(.el-table tr) {
  background-color: transparent;
}

:deep(.el-table td) {
  border-bottom: 1px solid #333;
}

:deep(.el-table__body tr:hover > td) {
  background-color: #2a2a2a !important;
}

:deep(.el-table .el-table__cell) {
  word-break: break-word;
}

/* 统计数据区域 */
.stats-summary {
  margin-bottom: clamp(1rem, 3vw, 1.25rem);
}

.search-section {
  margin-bottom: 1.5rem;
}

.search-stats-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border-default) 20%, var(--border-default) 80%, transparent);
  margin: 1.5rem 0;
}

.filter-status {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: var(--bg-secondary);
  border-radius: 6px;
  border: 1px solid var(--border-default);
}

.filter-label {
  font-weight: 500;
  color: var(--text-primary);
  margin-right: 0.5rem;
}

.stats-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.stats-section {
  flex: 1;
}

.stats-section h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-size: clamp(1rem, 1.8vw, 1.125rem);
  font-weight: 600;
}

.stats-grid-3x2 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: clamp(0.75rem, 2vw, 1rem);
  align-items: stretch;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: clamp(0.5rem, 1.5vw, 0.75rem);
  background-color: #2a2a2a;
  border-radius: 0.375rem;
}

.stat-label {
  color: #ccc;
  font-size: clamp(0.75rem, 1.2vw, 0.875rem);
}

.stat-value {
  font-weight: bold;
  color: #fff;
  font-size: clamp(0.875rem, 1.4vw, 1rem);
}

.stat-value.gain {
  color: #67c23a;
}

.stat-value.loss {
  color: #f56c6c;
}

/* 表格特殊样式 */
.id-text {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #fff;
}

.user-id {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #fff;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .stats-grid-3x2 {
    grid-template-columns: 1fr;
    grid-template-rows: repeat(6, 1fr);
  }
  
  .stat-item {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }
  
  .search-input,
  .status-select,
  .date-picker {
    width: 100%;
    max-width: none;
  }

  :deep(.el-table) {
    font-size: 0.75rem;
    min-width: 800px;
  }
  
  :deep(.el-table th),
  :deep(.el-table td) {
    padding: 0.5rem 0.25rem;
  }
}

/* 加载遮罩样式 */
:deep(.el-loading-mask) {
  background-color: rgba(26, 26, 26, 0.8) !important;
}

:deep(.el-loading-spinner) {
  color: #409eff !important;
}

:deep(.el-loading-text) {
  color: #fff !important;
}
</style>

<style>
/* 全局日历面板样式 - 无scoped以确保最高优先级 */
.el-picker-panel,
.el-date-picker,
.el-date-range-picker,
.el-popper {
  background-color: #1a1a1a !important;
  border-color: #333 !important;
}

.el-picker-panel .el-picker-panel__content,
.el-picker-panel .el-picker-panel__body,
.el-date-picker .el-picker-panel__content {
  background-color: #1a1a1a !important;
}

.el-date-picker__header,
.el-date-picker__time-header {
  background-color: #1a1a1a !important;
  border-bottom-color: #333 !important;
}

.el-date-table th,
.el-date-table td,
.el-month-table td,
.el-year-table td {
  background-color: #1a1a1a !important;
  color: #fff !important;
}

.el-date-table th {
  color: #ccc !important;
}

.el-picker-panel__footer {
  background-color: #1a1a1a !important;
  border-top-color: #333 !important;
}

/* 下拉选择框样式 */
.el-select-dropdown {
  background-color: #484848 !important;
}

.el-select-dropdown .el-select-dropdown__item {
  background-color: #484848 !important;
  color: #fff !important;
}

.el-select-dropdown .el-select-dropdown__item:hover {
  background-color: #3b3b3b !important;
}
</style>
