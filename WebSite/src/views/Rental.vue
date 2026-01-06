<template>
  <div class="rental-page-container">
    <!-- 搜索与统计数据 -->
    <div class="stats-summary">
      <div class="card">
        <!-- 搜索栏 -->
        <div class="search-section">
          <div class="flex flex-wrap gap-4 items-center">
            <el-input
              v-model="searchText"
              prefix-icon="Search"
              placeholder="搜索商品名称"
              class="search-input"
              clearable
            />
            <el-select
              v-model="statusFilter"
              placeholder="选择状态"
              class="status-select"
              clearable
            >
              <el-option label="进行中" value="进行中" />
              <el-option label="已完成" value="已完成" />
              <el-option label="已取消" value="已取消" />
            </el-select>
            <el-select
              v-model="sourceFilter"
              placeholder="选择平台"
              class="status-select"
              clearable
            >
              <el-option v-for="src in sourceList" :key="src" :label="sourceLabel(src)" :value="src" />
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
              clearable
            />
            <el-button type="primary" @click="handleSearch">
              搜索
            </el-button>
            <el-button @click="handleClearSearch">
              重置
            </el-button>
          </div>
        </div>
        
        <!-- 分隔线 -->
        <div class="search-stats-divider"></div>
        
        <!-- 统计数据 -->
        <div class="stats-container">
          <div class="stats-section">
            <h3>统计数据</h3>
            <div class="stats-grid-3x2">
              <div class="stat-item">
                <span class="stat-label">总借贷数量:</span>
                <span class="stat-value">{{ totalStats.totalCount }} 件</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">总借贷金额:</span>
                <span class="stat-value">¥{{ totalStats.totalAmount }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">平均借贷价格:</span>
                <span class="stat-value">¥{{ totalStats.avgPrice }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">已完成数量:</span>
                <span class="stat-value">{{ totalStats.completedCount }} 件</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">已取消数量:</span>
                <span class="stat-value">{{ totalStats.cancelledCount }} 件</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">进行中数量:</span>
                <span class="stat-value">{{ totalStats.pendingCount }} 件</span>
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
        :data="rentalData"
        v-loading="loading"
        element-loading-text="加载中..."
        style="width: 100%"
      >
        <el-table-column label="图片" width="144" align="center">
          <template #default>
            <div class="weapon-image-cell">
              <span class="no-image">无图</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="商品名称" min-width="250">
          <template #default>
            <div class="item-name-cell">
              <div class="item-title">示例商品</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="磨损值" width="200">
          <template #default>
            <span style="color: #888;">N/A</span>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="120">
          <template #default>
            <span>-</span>
          </template>
        </el-table-column>
        <el-table-column label="借贷价格" min-width="100">
          <template #default>
            <span>¥0.00</span>
          </template>
        </el-table-column>
        <el-table-column label="来源" min-width="80">
          <template #default>
            <span>-</span>
          </template>
        </el-table-column>
        <el-table-column label="借贷时间" min-width="160">
          <template #default>
            <span>-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" min-width="80">
          <template #default>
            <el-tag type="info" size="small">待开发</el-tag>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination">
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
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'Rental',
  setup() {
    const loading = ref(false)
    const rentalData = ref([])
    const searchText = ref('')
    const statusFilter = ref('')
    const sourceFilter = ref('')
    const sourceList = ref(['yyyp', 'buff', 'csfloat', 'SMK', 'ING'])
    const currentPage = ref(1)
    const pageSize = ref(10)
    const totalItems = ref(0)
    const dateRange = ref(null)
    
    const totalStats = ref({
      totalCount: 0,
      totalAmount: '0.00',
      avgPrice: '0.00',
      completedCount: 0,
      cancelledCount: 0,
      pendingCount: 0
    })

    const sourceLabel = (val) => {
      const map = {
        yyyp: '悠悠有品',
        buff: 'BUFF',
        csfloat: 'CsFloat',
        SMK: 'steam市场',
        ING: '游戏内购'
      }
      return map[val] || val
    }

    const handleSizeChange = (val) => {
      pageSize.value = val
      currentPage.value = 1
      ElMessage.info('分页功能需要后端 API 支持')
    }

    const handleCurrentChange = (val) => {
      currentPage.value = val
      ElMessage.info('分页功能需要后端 API 支持')
    }

    const handleSearch = () => {
      ElMessage.info('搜索功能需要后端 API 支持')
    }

    const handleClearSearch = () => {
      searchText.value = ''
      statusFilter.value = ''
      sourceFilter.value = ''
      dateRange.value = null
      currentPage.value = 1
      ElMessage.success('已重置筛选条件')
    }

    return {
      loading,
      rentalData,
      searchText,
      statusFilter,
      sourceFilter,
      sourceList,
      currentPage,
      pageSize,
      totalItems,
      dateRange,
      totalStats,
      sourceLabel,
      handleSizeChange,
      handleCurrentChange,
      handleSearch,
      handleClearSearch
    }
  }
}
</script>


<style scoped>
.rental-page-container {
  padding: 1.5rem;
}

.weapon-image-cell {
  width: 100%;
  height: 100%;
  min-height: 90px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  padding: 4px;
  box-sizing: border-box;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

.no-image {
  color: #666;
  font-size: 0.75rem;
}

.search-input {
  width: 200px;
  min-width: 200px;
  max-width: 200px;
}

.status-select {
  width: 120px;
  min-width: 120px;
  max-width: 120px;
}

.date-picker {
  flex: 1 1 320px;
  min-width: 320px;
  max-width: 100%;
  width: 100%;
}

.pagination {
  margin-top: 1.25rem;
  display: flex;
  justify-content: center;
}

.pagination-top {
  margin-top: 0;
  margin-bottom: 1.25rem;
}

.stats-summary {
  margin-bottom: 1.25rem;
}

.search-section {
  margin-bottom: 1.5rem;
}

.search-stats-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border-default) 20%, var(--border-default) 80%, transparent);
  margin: 1.5rem 0;
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
  font-size: 1.125rem;
  font-weight: 600;
}

.stats-grid-3x2 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: 1rem;
  align-items: stretch;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background-color: #2a2a2a;
  border-radius: 0.375rem;
}

.stat-label {
  color: #ccc;
  font-size: 0.875rem;
}

.stat-value {
  font-weight: bold;
  color: #fff;
  font-size: 1rem;
}

.item-name-cell {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.item-title {
  line-height: 1.4;
}

@media (max-width: 768px) {
  .search-input {
    min-width: unset;
    width: 100%;
    max-width: none;
  }

  .stats-grid-3x2 {
    grid-template-columns: 1fr;
    grid-template-rows: repeat(6, 1fr);
  }

  .stat-item {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }
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

:deep(.el-table) {
  background-color: transparent;
  color: #fff;
  font-size: 0.875rem;
}

:deep(.el-table .el-table__row) {
  min-height: 90px;
}

:deep(.el-table td:first-child) {
  height: auto;
  min-height: 90px;
  vertical-align: middle;
}

:deep(.el-table th) {
  background-color: var(--bg-tertiary) !important;
  color: #fff;
  border-bottom: 1px solid var(--border-default);
  padding: 0.375rem 2px;
}

:deep(.el-table td) {
  background-color: transparent !important;
  border-bottom: 1px solid var(--border-default);
  color: #fff;
  padding: 0.375rem 2px;
}

:deep(.el-table tr:hover > td) {
  background-color: transparent !important;
}

:deep(.el-input__inner) {
  background-color: #1a1a1a;
  border-color: #333;
  color: #fff;
}

:deep(.el-select .el-input__inner) {
  background-color: #1a1a1a;
  border-color: #333;
  color: #fff;
}

:deep(.el-date-editor .el-input__inner) {
  background-color: #1a1a1a !important;
  border-color: #333 !important;
  color: #fff !important;
}
</style>
