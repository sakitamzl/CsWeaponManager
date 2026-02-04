<template>
  <div>
    <div class="stats-summary">
      <div class="card">
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-label">总通知数</div>
            <div class="stat-value">{{ stats.totalCount || 0 }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">未读通知</div>
            <div class="stat-value unread">{{ stats.unreadCount || 0 }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">已读通知</div>
            <div class="stat-value read">{{ stats.readCount || 0 }}</div>
          </div>
        </div>

        <div class="search-section">
          <div class="flex flex-wrap gap-4 items-center">
            <el-input
              v-model="searchText"
              placeholder="搜索通知标题、内容、关联ID..."
              prefix-icon="Search"
              class="search-input"
              @keyup.enter="handleSearch"
              @clear="handleClearSearch"
              clearable
            />
            <el-button type="primary" @click="handleSearch" :loading="loading">搜索</el-button>
            <el-button @click="handleClearSearch" :disabled="loading">重置</el-button>

            <el-select
              v-model="filterType"
              placeholder="选择通知类型"
              class="filter-select"
              @change="handleFilterChange"
              clearable
            >
              <el-option
                v-for="type in notificationTypes"
                :key="type"
                :label="getTypeLabel(type)"
                :value="type"
              />
            </el-select>

            <el-select
              v-model="filterLevel"
              placeholder="选择级别"
              class="filter-select"
              @change="handleFilterChange"
              clearable
            >
              <el-option label="信息" value="info" />
              <el-option label="成功" value="success" />
              <el-option label="警告" value="warning" />
              <el-option label="错误" value="error" />
            </el-select>

            <el-select
              v-model="filterSource"
              placeholder="选择来源"
              class="filter-select"
              @change="handleFilterChange"
              clearable
            >
              <el-option
                v-for="source in notificationSources"
                :key="source"
                :label="getSourceLabel(source)"
                :value="source"
              />
            </el-select>

            <el-select
              v-model="filterReadStatus"
              placeholder="阅读状态"
              class="filter-select"
              @change="handleFilterChange"
              clearable
            >
              <el-option label="未读" :value="0" />
              <el-option label="已读" :value="1" />
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
            <el-button type="warning" @click="handleMarkAllAsRead" :loading="loading">全部标记已读</el-button>
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
        :data="notificationData"
        v-loading="loading"
        element-loading-text="加载中..."
        style="width: 100%"
        :row-style="getRowStyle"
        :header-row-style="{ backgroundColor: 'var(--bg-tertiary)' }"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="notification_id" label="ID" width="80" align="center" />
        <el-table-column prop="title" label="标题" width="200" show-overflow-tooltip align="left" />
        <el-table-column prop="content" label="内容" min-width="300" show-overflow-tooltip align="left" />
        <el-table-column prop="type" label="类型" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getTypeTagColor(row.type)" size="small">
              {{ getTypeLabel(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="level" label="级别" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getLevelTagColor(row.level)" size="small">
              {{ getLevelLabel(row.level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="来源" width="120" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ getSourceLabel(row.source) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_read" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_read ? 'info' : 'warning'" size="small">
              {{ row.is_read ? '已读' : '未读' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="180" align="center" />
        <el-table-column label="操作" width="180" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="!row.is_read"
              type="primary"
              size="small"
              @click="handleMarkAsRead([row.notification_id])"
            >
              标记已读
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete([row.notification_id])">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination pagination-bottom">
        <div class="batch-actions">
          <el-button
            type="primary"
            size="small"
            @click="handleMarkSelectedAsRead"
            :disabled="selectedIds.length === 0"
          >
            标记选中为已读
          </el-button>
          <el-button
            type="danger"
            size="small"
            @click="handleDeleteSelected"
            :disabled="selectedIds.length === 0"
          >
            删除选中
          </el-button>
        </div>
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
import { useSysMessage } from './useSysMessage.js'

export default {
  name: 'SystemMessage',
  setup() {
    return useSysMessage()
  }
}
</script>

<style scoped src="./styles.css"></style>
