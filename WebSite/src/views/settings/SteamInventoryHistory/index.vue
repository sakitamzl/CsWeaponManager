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
import { useSteamInventoryHistory } from './useSteamInventoryHistory.js'

const {
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
} = useSteamInventoryHistory()
</script>

<style scoped src="./styles-scoped.css"></style>
<style src="./styles-global.css"></style>
