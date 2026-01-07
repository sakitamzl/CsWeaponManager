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
                prefix-icon="Search"
                class="search-input"
                @keyup.enter="handleSearch"
                @clear="handleClearSearch"
                clearable
              />
              <el-select
                v-model="statusFilter"
                placeholder="选择状态"
                class="status-select"
                @change="handleStatusChange"
                clearable
              >
                <el-option v-for="status in statusList" :key="status" :label="status" :value="status" />
              </el-select>
              <el-select
                v-model="statusSubFilter"
                placeholder="选择子状态"
                class="status-select"
                @change="handleStatusSubChange"
                @visible-change="handleStatusSubVisibleChange"
                clearable
              >
                <el-option v-for="sub in statusSubList" :key="sub" :label="sub" :value="sub" />
              </el-select>
      <el-select
        v-model="platformFilter"
        placeholder="选择平台"
        class="status-select"
        @change="handlePlatformChange"
        clearable
      >
        <el-option v-for="platform in platformList" :key="platform" :label="mapSource(platform)" :value="platform" />
      </el-select>
      <el-select
        v-model="lessorFilter"
        placeholder="选择出租人"
        class="status-select"
        @change="handleLessorChange"
        clearable
      >
        <el-option v-for="user in lessorList" :key="user" :label="user" :value="user" />
      </el-select>
              <el-select 
                v-model="weaponTypeFilter" 
                placeholder="武器类型" 
                class="type-select" 
                @change="handleTypeChange" 
                multiple
                collapse-tags
                collapse-tags-tooltip
                clearable
              >
                <el-option v-for="type in weaponTypes" :key="type" :label="type" :value="type" />
              </el-select>
              <el-select 
                v-model="floatRangeFilter" 
                placeholder="磨损等级" 
                class="wear-select" 
                @change="handleWearChange" 
                multiple
                collapse-tags
                collapse-tags-tooltip
                clearable
              >
                <el-option v-for="range in floatRanges" :key="range" :label="range" :value="range" />
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
              <el-button type="primary" @click="handleSearch" :loading="loading">
                搜索
              </el-button>
              <el-button @click="handleClearSearch" :disabled="loading">
                重置
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
            <el-tag v-if="statusFilter && statusFilter !== 'all'" type="success" size="small" closable @close="statusFilter = 'all'">
              状态: {{ statusFilter }}
            </el-tag>
            <el-tag 
              v-for="type in weaponTypeFilter" 
              :key="type" 
              type="warning" 
              size="small" 
              closable 
              @close="removeWeaponType(type)"
            >
              类型: {{ type }}
            </el-tag>
            <el-tag v-if="statusSubFilter && statusSubFilter !== 'all'" type="success" size="small" closable @close="statusSubFilter = 'all'">
              子状态: {{ statusSubFilter }}
            </el-tag>
            <el-tag 
              v-for="range in floatRangeFilter" 
              :key="range" 
              type="info" 
              size="small" 
              closable 
              @close="removeFloatRange(range)"
            >
              磨损: {{ range }}
            </el-tag>
            <el-tag v-if="dateRange && dateRange.length === 2" type="danger" size="small" closable @close="dateRange = null">
              时间: {{ dateRange[0] }} ~ {{ dateRange[1] }}
            </el-tag>
          </div>
          
          <!-- 统计数据 -->
          <div class="stats-container">
            <div class="stats-section">
              <h3>全部借入统计</h3>
              <div class="stats-grid-3x2">
                <div class="stat-item">
                  <span class="stat-label">总借入数量:</span>
                  <span class="stat-value">{{ allDataStats.totalCount }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">总借入支出:</span>
                  <span class="stat-value">¥{{ allDataStats.totalAmount }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">平均租金:</span>
                  <span class="stat-value">¥{{ allDataStats.avgPrice }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">总租赁天数:</span>
                  <span class="stat-value">{{ allDataStats.totalLeaseDays }} 天</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">平均租期:</span>
                  <span class="stat-value">{{ allDataStats.avgLeaseDays }} 天</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">租赁中数量:</span>
                  <span class="stat-value">{{ allDataStats.rentingCount }}</span>
                </div>
              </div>
            </div>
            
            <div class="stats-divider"></div>
            
            <div class="stats-section">
              <h3>当前页面统计</h3>
              <div class="stats-grid-3x2">
                <div class="stat-item">
                  <span class="stat-label">当前数量:</span>
                  <span class="stat-value">{{ currentPageStats.totalCount }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">当前收入:</span>
                  <span class="stat-value">¥{{ currentPageStats.totalAmount }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">平均租金:</span>
                  <span class="stat-value">¥{{ currentPageStats.avgPrice }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">当前租赁天数:</span>
                  <span class="stat-value">{{ currentPageStats.totalLeaseDays }} 天</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">平均租期:</span>
                  <span class="stat-value">{{ currentPageStats.avgLeaseDays }} 天</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">租赁中数量:</span>
                  <span class="stat-value">{{ currentPageStats.rentingCount }}</span>
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
          :data="filteredRentalData"
          v-loading="loading"
          element-loading-text="加载中..."
          style="width: 100%"
          :row-style="{ backgroundColor: 'transparent' }"
          :header-row-style="{ backgroundColor: 'var(--bg-tertiary)' }"
          :flexible="true"
          :scrollbar-always-on="true"
          @sort-change="handleSortChange"
        >
          <!-- 图片列，与 /buy 一致的样式 -->
          <el-table-column label="图片" width="144" align="center">
            <template #default="scope">
              <div
                class="weapon-image-cell"
                @click="openPreview(scope.row)"
                style="cursor: pointer;"
              >
                <img
                  v-if="getWeaponImage(scope.row.steam_hash_name)"
                  :src="getWeaponImage(scope.row.steam_hash_name)"
                  :alt="getItemTitle(scope.row)"
                  class="weapon-img"
                  @error="(e) => e.target.style.display = 'none'"
                />
                <span v-else class="no-image">无图</span>
              </div>
            </template>
          </el-table-column>

          <!-- 名称列：组合武器名+饰品名+磨损，与 /buy 风格一致 -->
          <el-table-column label="商品名称" min-width="260" show-overflow-tooltip>
            <template #default="scope">
              <div class="item-name-cell">
                <div class="item-title">{{ getItemTitle(scope.row) }}</div>
                <div class="item-extras" v-if="hasExtras(scope.row)">
                  <!-- 印花图片 -->
                  <div class="sticker-list" v-if="scope.row.sticker">
                    <div
                      v-for="(sticker, idx) in parseStickers(scope.row.sticker)"
                      :key="idx"
                      class="sticker-item"
                      :title="sticker.name || '未知贴纸'"
                    >
                      <img
                        v-if="sticker.image"
                        :src="sticker.image"
                        :alt="sticker.name"
                        class="sticker-img"
                        @error="(e) => e.target.style.display = 'none'"
                      />
                      <div v-else class="sticker-placeholder">?</div>
                    </div>
                  </div>
                  <!-- 挂件图片 -->
                  <div class="pendant-list" v-if="scope.row.pendant">
                    <img
                      v-if="parsePendant(scope.row.pendant)?.image"
                      :src="parsePendant(scope.row.pendant).image"
                      :alt="parsePendant(scope.row.pendant)?.name"
                      class="pendant-img"
                      @error="(e) => e.target.style.display = 'none'"
                    />
                  </div>
                  <!-- 改名标签 -->
                  <div class="rename-tag" v-if="scope.row.rename">
                    <span class="rename-icon">📝</span>
                    <span class="rename-text">{{ scope.row.rename }}</span>
                  </div>
                </div>
              </div>
            </template>
          </el-table-column>

          <!-- 磨损值与进度条 -->
          <el-table-column prop="weapon_float" label="磨损值" width="200" align="left">
            <template #default="scope">
              <div v-if="scope.row.weapon_float">
                <div
                  style="font-family: monospace; font-size: 0.85rem; margin-bottom: 4px;"
                >
                  {{ scope.row.weapon_float }}
                </div>
                <div class="float-bar">
                  <div class="float-segment fn"></div>
                  <div class="float-segment mw"></div>
                  <div class="float-segment ft"></div>
                  <div class="float-segment ww"></div>
                  <div class="float-segment bs"></div>
                  <div
                    class="float-pointer"
                    :style="{ left: `${parseFloat(scope.row.weapon_float) * 100}%` }"
                  ></div>
                </div>
              </div>
              <span v-else style="color: #888;">N/A</span>
            </template>
          </el-table-column>

          <el-table-column prop="weapon_type" label="类型" width="120" />

          <!-- 借入相关信息 -->
          <el-table-column prop="price" label="租金/天" min-width="100">
            <template #default="scope">
              ¥{{ scope.row.price }}
            </template>
          </el-table-column>

          <!-- 租期 -->
          <el-table-column
            prop="total_Lease_Days"
            label="租期"
            min-width="80"
          >
            <template #default="scope">
              {{ scope.row.total_Lease_Days }} 天
            </template>
          </el-table-column>

          <!-- 租赁时间段 -->
          <el-table-column
            prop="lean_start_time"
            label="租赁时间段"
            min-width="220"
            sortable="custom"
          >
            <template #default="scope">
              <span class="rent-time-range">
                <span>{{ formatTime(scope.row.lean_start_time) || '—' }}</span>
                <span class="rent-time-separator">→</span>
                <span>{{ formatTime(scope.row.lean_end_time) || '—' }}</span>
              </span>
            </template>
          </el-table-column>

        <el-table-column prop="from" label="来源" min-width="100">
          <template #default="scope">
            {{ mapSource(scope.row.from) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" min-width="90">
          <template #default="scope">
            <el-tooltip
              :content="scope.row.status_sub || scope.row.status"
              placement="top"
              :disabled="!scope.row.status_sub"
            >
              <span>
                <el-tag
                  :type="getStatusType(scope.row.status)"
                  size="small"
                  :style="{
                    backgroundColor: getStatusColor(scope.row.status),
                    borderColor: getStatusColor(scope.row.status),
                    color: getStatusTextColor(scope.row.status)
                  }"
                >
                  {{ scope.row.status }}
                </el-tag>
              </span>
            </el-tooltip>
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

      <!-- 预览弹窗，样式与 /buy 一致，字段按借入场景简化 -->
      <el-dialog
        v-model="previewVisible"
        :title="previewItem ? getItemTitle(previewItem) : ''"
        width="800px"
        :close-on-click-modal="true"
        :close-on-press-escape="true"
        class="preview-dialog"
      >
        <div v-if="previewItem" class="preview-content">
          <div class="preview-main-layout">
            <!-- 左侧：图片 + 磨损 + 基本信息 -->
            <div class="preview-left-section">
              <div class="preview-image-section">
                <img
                  v-if="getWeaponImage(previewItem.steam_hash_name)"
                  :src="getWeaponImage(previewItem.steam_hash_name)"
                  :alt="getItemTitle(previewItem)"
                  class="preview-image"
                  loading="lazy"
                />
                <div v-else class="preview-image-placeholder">
                  <span>无图片</span>
                </div>
              </div>

              <div class="preview-info-section">
                <div
                  v-if="previewItem.weapon_float"
                  class="preview-float-section"
                >
                  <div class="preview-float-bar-container">
                    <div class="float-bar">
                      <div class="float-segment fn"></div>
                      <div class="float-segment mw"></div>
                      <div class="float-segment ft"></div>
                      <div class="float-segment ww"></div>
                      <div class="float-segment bs"></div>
                      <div
                        class="float-pointer"
                        :style="{
                          left: `${parseFloat(previewItem.weapon_float) * 100}%`
                        }"
                      ></div>
                    </div>
                  </div>
                  <div class="preview-float-value">
                    {{ previewItem.weapon_float }}
                  </div>
                  <div
                    class="preview-float-range"
                    v-if="previewItem.float_range"
                  >
                    {{ previewItem.float_range }}
                  </div>
                </div>

                <div class="preview-prices">
                  <div class="preview-price-row">
                    <div
                      class="preview-price-item"
                      v-if="previewItem.price"
                    >
                      <span class="preview-price-label">租金/天:</span>
                      <span class="preview-price-value buy-price">
                        ¥{{ parseFloat(previewItem.price).toFixed(2) }}
                      </span>
                    </div>
                    <div
                      class="preview-price-item"
                      v-if="previewItem.total_Lease_Days"
                    >
                      <span class="preview-price-label">租期:</span>
                      <span class="preview-price-value">
                        {{ previewItem.total_Lease_Days }} 天
                      </span>
                    </div>
                  </div>

                  <div class="preview-info-row">
                    <div
                      class="preview-info-item"
                      v-if="previewItem.lessor_name"
                    >
                      <span class="preview-info-label">出租人:</span>
                      <span class="preview-info-value">
                        {{ previewItem.lessor_name }}
                      </span>
                    </div>
                    <div
                      class="preview-info-item"
                      v-if="previewItem.status"
                    >
                      <span class="preview-info-label">状态:</span>
                      <el-tag
                        :type="getStatusType(previewItem.status)"
                        size="default"
                        :style="{
                          backgroundColor: getStatusColor(previewItem.status),
                          borderColor: getStatusColor(previewItem.status),
                          color: getStatusTextColor(previewItem.status)
                        }"
                      >
                        {{ previewItem.status }}
                      </el-tag>
                    </div>
                    <div
                      class="preview-info-item"
                      v-if="previewItem.status_sub"
                    >
                      <span class="preview-info-label">子状态:</span>
                      <span class="preview-info-value">
                        {{ previewItem.status_sub }}
                      </span>
                    </div>
                  </div>

                  <div
                    class="preview-info-row"
                    v-if="previewItem.lean_start_time || previewItem.lean_end_time"
                  >
                    <div
                      class="preview-info-item"
                      v-if="previewItem.lean_start_time"
                    >
                      <span class="preview-info-label">开始时间:</span>
                      <span class="preview-info-value">
                        {{ formatTime(previewItem.lean_start_time) }}
                      </span>
                    </div>
                    <div
                      class="preview-info-item"
                      v-if="previewItem.lean_end_time"
                    >
                      <span class="preview-info-label">结束时间:</span>
                      <span class="preview-info-value">
                        {{ formatTime(previewItem.lean_end_time) }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 右侧：印花、挂件和订单信息 -->
            <div class="preview-right-section">
              <!-- 订单ID - 放在最上方 -->
              <div class="preview-order-id" v-if="previewItem.ID">
                <span class="preview-order-icon">🧾</span>
                <span class="preview-order-text">订单 ID：{{ previewItem.ID }}</span>
              </div>

              <!-- 改名标签 -->
              <div class="preview-rename" v-if="previewItem.rename">
                <span class="preview-rename-icon">🏷️</span>
                <span class="preview-rename-text">{{ previewItem.rename }}</span>
              </div>

              <!-- 贴纸列表 -->
              <div v-if="previewItem.sticker && parseStickers(previewItem.sticker).length > 0" class="preview-sticker-list-section">
                <div class="preview-sticker-list">
                  <div
                    v-for="(sticker, index) in parseStickers(previewItem.sticker)"
                    :key="index"
                    class="preview-sticker-list-item"
                  >
                    <el-tooltip :content="sticker.name || '未知贴纸'" placement="left">
                      <div class="preview-sticker-list-img-wrapper">
                        <img
                          v-if="sticker.image"
                          :src="sticker.image"
                          :alt="sticker.name"
                          class="preview-sticker-list-img"
                          @error="(e) => e.target.style.display = 'none'"
                        />
                        <div v-else class="preview-sticker-list-placeholder">?</div>
                      </div>
                    </el-tooltip>
                    <div class="preview-sticker-list-name">{{ sticker.name || '未知贴纸' }}</div>
                  </div>
                </div>
              </div>

              <!-- 挂件信息 -->
              <div v-if="previewItem.pendant" class="preview-pendant-section">
                <div class="preview-pendant-list">
                  <div class="preview-pendant-list-item">
                    <el-tooltip :content="parsePendant(previewItem.pendant)?.name || '挂件'" placement="left">
                      <div class="preview-pendant-list-img-wrapper">
                        <img
                          v-if="parsePendant(previewItem.pendant)?.image"
                          :src="parsePendant(previewItem.pendant).image"
                          :alt="parsePendant(previewItem.pendant).name"
                          class="preview-pendant-list-img"
                          @error="(e) => e.target.style.display = 'none'"
                        />
                        <div v-else class="preview-pendant-list-placeholder">🎗️</div>
                      </div>
                    </el-tooltip>
                    <div class="preview-pendant-list-name">{{ parsePendant(previewItem.pendant)?.name || '挂件' }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { apiUrls } from '@/config/api'

export default {
  name: 'Rental',
  setup() {
    const loading = ref(false)
    const dataController = ref(null)
    const statsController = ref(null)
    const rentalData = ref([])
    const searchText = ref('')
    const statusFilter = ref('')
    const weaponTypeFilter = ref([])
    const floatRangeFilter = ref([])
    const weaponTypes = ref([])
    const floatRanges = ref([])
    const statusList = ref([])
    const statusSubList = ref([])
    const statusSubFilter = ref('')
    const platformList = ref([])
    const platformFilter = ref('')
    const lessorList = ref([])
    const lessorFilter = ref('')
    const lenterList = ref([]) // 添加 lenterList 变量
    const currentPage = ref(1)
    const pageSize = ref(10)
    const totalItems = ref(0)
    const dateRange = ref(null)
    const isTimeSearchMode = ref(false)
    const sortOrder = ref('descending')

    // API请求缓存（简单的内存缓存，5分钟过期）
    const apiCache = new Map()
    const CACHE_DURATION = 5 * 60 * 1000 // 5分钟

    const getCachedData = (key) => {
      const cached = apiCache.get(key)
      if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
        return cached.data
      }
      return null
    }

    const setCachedData = (key, data) => {
      apiCache.set(key, {
        data,
        timestamp: Date.now()
      })
    }
    
    // 高级搜索相关
    const hasAdvancedFilters = computed(() => {
      return (searchText.value && searchText.value.trim()) || 
             (statusFilter.value && statusFilter.value !== 'all') ||
             (statusSubFilter.value && statusSubFilter.value !== 'all') ||
             (weaponTypeFilter.value && weaponTypeFilter.value.length > 0) ||
             (floatRangeFilter.value && floatRangeFilter.value.length > 0) ||
             (dateRange.value && dateRange.value.length === 2)
    })
    // 全部数据统计（通过API获取）
    const allDataStats = ref({
      totalCount: 0,
      totalAmount: '0.00',
      avgPrice: '0.00',
      totalLeaseDays: 0,
      avgLeaseDays: '0.0',
      rentingCount: 0,
      completedCount: 0,
      cancelledCount: 0
    })

    // 当前页面统计（基于当前显示的数据计算）- 优化：减少重复遍历
    const currentPageStats = computed(() => {
      let totalCount = 0
      let totalAmount = 0
      let totalLeaseDays = 0
      let rentingCount = 0
      let completedCount = 0
      let cancelledCount = 0

      // 单次遍历计算所有统计
      for (const item of rentalData.value) {
        if (item.status === '已取消') {
          cancelledCount++
          continue
        }

        totalCount++
        const price = item.price || 0
        const days = item.total_Lease_Days || 0
        totalAmount += price * days
        totalLeaseDays += days

        if (item.status === '租赁中') rentingCount++
        else if (item.status === '已完成') completedCount++
      }

      return {
        totalCount,
        totalAmount: totalAmount.toFixed(2),
        avgPrice: totalCount > 0 ? (totalAmount / totalCount).toFixed(2) : '0.00',
        totalLeaseDays,
        avgLeaseDays: totalCount > 0 ? (totalLeaseDays / totalCount).toFixed(1) : '0.0',
        rentingCount,
        completedCount,
        cancelledCount
      }
    })

    // 预览弹窗
    const previewVisible = ref(false)
    const previewItem = ref(null)

    // 存储所有搜索结果，用于前端分页
    const allSearchResults = ref([])
    const isSearchMode = ref(false)

    const filteredRentalData = computed(() => {
      // 如果是搜索模式，进行前端分页
      if (isSearchMode.value && allSearchResults.value.length > 0) {
        let filtered = allSearchResults.value
        
        // 状态筛选
        if (statusFilter.value && statusFilter.value !== 'all') {
          filtered = filtered.filter(item => item.status === statusFilter.value)
        }
        
        // 更新总数以反映筛选后的结果
        // 仅在搜索模式下需要根据筛选结果调整 total
        totalItems.value = filtered.length

        // 前端分页
        const start = (currentPage.value - 1) * pageSize.value
        const end = start + pageSize.value
        return filtered.slice(start, end)
      }

      // 非搜索模式的筛选
      let filtered = rentalData.value
      if (statusFilter.value && statusFilter.value !== 'all') {
        filtered = filtered.filter(item => item.status === statusFilter.value)
      }
      if (statusSubFilter.value && statusSubFilter.value !== 'all') {
        // 子状态对应 status_sub 字段
        filtered = filtered.filter(item => (item.status_sub || '') === statusSubFilter.value)
      }
      if (platformFilter.value && platformFilter.value !== 'all') {
        filtered = filtered.filter(item => (item.from || '') === platformFilter.value)
      }
      if (lessorFilter.value && lessorFilter.value !== 'all') {
        filtered = filtered.filter(item => (item.data_user || '') === lessorFilter.value)
      }
      return filtered
    })

    const formatTime = (time) => {
      if (!time) return ''
      return new Date(time).toLocaleString('zh-CN')
    }

    const getStatusType = (status) => {
      const statusMap = {
        '已完成': 'success',
        '租赁中': 'warning',
        '已取消': 'danger',
        '已归还': 'success',
        '已转租': 'success'
      }
      return statusMap[status] || 'info'
    }

    const getStatusColor = (status) => {
      const colorMap = {
        '已完成': '#52c41a',    // 更鲜明的绿色
        '租赁中': '#faad14',    // 更鲜明的橙色
        '已取消': '#ff4d4f',    // 更鲜明的红色
        '进行中': '#1890ff',    // 蓝色
        '已归还': '#52c41a',
        '已转租': '#52c41a'
      }
      return colorMap[status] || '#909399'
    }

    const getStatusTextColor = (status) => {
      return '#FFFFFF'
    }

    const mapSource = (val) => {
      if (!val) return '-'
      if (val.toLowerCase() === 'yyyp') return '悠悠有品'
      return val
    }

    // 获取武器图片路径
    const getWeaponImage = (steamHashName) => {
      if (!steamHashName) {
        return null
      }
      const imageName = steamHashName
        .replace(/\s*\|\s*/g, '___')
        .replace(/\s/g, '_')
        + '.png'
      return apiUrls.weaponImage(imageName)
    }

    // 组合标题：武器名 | 饰品名 （磨损）；若两者相同，仅显示一次
    const getItemTitle = (item) => {
      const weaponName = (item.weapon_name || '').trim()
      const itemName = (item.item_name || '').trim()
      const parts = []

      if (weaponName && itemName) {
        if (weaponName === itemName) {
          parts.push(itemName)
        } else {
          parts.push(weaponName)
          parts.push(itemName)
        }
      } else if (weaponName) {
        parts.push(weaponName)
      } else if (itemName) {
        parts.push(itemName)
      }

      let title = parts.join(' | ')
      if (item.float_range) {
        title += ` （${item.float_range}）`
      }
      return title || item.ID || ''
    }

    // 检查是否有额外信息（印花、挂件、改名）
    const hasExtras = (item) => {
      return !!(item.sticker || item.pendant || item.rename)
    }

    // 解析印花数据
    const parseStickers = (stickerData) => {
      if (!stickerData) return []
      try {
        const parsed = typeof stickerData === 'string' ? JSON.parse(stickerData) : stickerData
        if (!Array.isArray(parsed)) return []
        
        return parsed.map(sticker => {
          const name = sticker.name || '未知贴纸'
          const hashName = sticker.hashName || sticker.steam_hash_name || sticker.steamHashName
          
          let imageUrl = null
          if (hashName) {
            const imageName = hashName
              .replace(/\s*\|\s*/g, '___')
              .replace(/\s/g, '_')
              .replace(/\*/g, '_')
              .replace(/™/g, '?')
            imageUrl = apiUrls.weaponImage(`Sticker___${imageName}.png`)
          }
          
          return {
            name: name,
            image: imageUrl
          }
        })
      } catch (e) {
        console.error('解析印花数据失败:', e)
        return []
      }
    }

    // 解析挂件数据
    const parsePendant = (pendantData) => {
      if (!pendantData) return null
      try {
        const parsed = typeof pendantData === 'string' ? JSON.parse(pendantData) : pendantData
        
        let pendantObj = Array.isArray(parsed) ? parsed[0] : parsed
        
        if (!pendantObj || typeof pendantObj !== 'object') return null
        
        const hashName = pendantObj.hashName || pendantObj.steam_hash_name || pendantObj.steamHashName
        
        let imageUrl = null
        if (hashName) {
          const imageName = hashName
            .replace(/\s*\|\s*/g, '___')
            .replace(/\s/g, '_')
            .replace(/\*/g, '_')
            .replace(/™/g, '?')
            + '.png'
          imageUrl = apiUrls.weaponImage(imageName)
        }
        
        return {
          name: pendantObj.name || '挂件',
          image: imageUrl
        }
      } catch (e) {
        console.error('解析挂件数据失败:', e)
        return null
      }
    }

    const createAbortSignal = (controllerRef) => {
      if (controllerRef.value) {
        controllerRef.value.abort()
      }
      controllerRef.value = new AbortController()
      return controllerRef.value.signal
    }

    const searchByName = async (itemName) => {
      loading.value = true
      try {
        console.log('正在搜索借入武器(过滤接口):', itemName)
        const count = await fetchRentalDataFiltered({
          min: 0,
          max: 10000,
          keywordOverride: itemName,
          storeInSearch: true
        })

        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const rawData = await response.json()
        console.log('搜索结果:', rawData)

        if (!Array.isArray(rawData)) {
          throw new Error('搜索结果格式错误')
        }

        // 转换搜索结果并存储所有数据
        const searchResults = rawData.map((item, index) => ({
          id: index + 1,
          ID: item[0] || '',
          weapon_name: item[1] || '',
          weapon_type: item[2] || '',
          item_name: item[3] || '',
          weapon_float: item[4] || 0,
          float_range: item[5] || '',
          price: item[6] || 0,
          lessor_name: item[7] || '',
          status: item[8] || '',
          status_sub: item[9] || '',
          from: item[10] || '',
          lean_start_time: item[11] || '',
          lean_end_time: item[12] || '',
          total_Lease_Days: item[13] || 0,
          max_Lease_Days: item[14] || 0,
          steam_hash_name: item[15] || '',
          sticker: item[16] || null,
          pendant: item[17] || null,
          rename: item[18] || '',
          data_user: item[19] || ''
        }))

        // 进入搜索模式
        isSearchMode.value = true
        totalItems.value = count
        currentPage.value = 1

        if (count === 0) {
          ElMessage.info(`未找到包含"${itemName}"的武器`)
        } else {
          ElMessage.success(`找到 ${count} 条相关记录`)
        }
        
      } catch (error) {
        if (error.name === 'AbortError') return
        console.error('搜索失败:', error)
        ElMessage.error(`搜索失败: ${error.message}`)
        rentalData.value = []
        allSearchResults.value = []
        totalItems.value = 0
      } finally {
        loading.value = false
        await loadFilteredStats()
      }
    }

    const buildStatFilters = () => {
      const filters = {}
      if (statusFilter.value && statusFilter.value !== 'all') {
        filters.status = statusFilter.value
      }
      if (statusSubFilter.value && statusSubFilter.value !== 'all') {
        filters.status_sub = statusSubFilter.value
      }
      if (platformFilter.value && platformFilter.value !== 'all') {
        filters.platform = platformFilter.value
      }
      if (lessorFilter.value && lessorFilter.value !== 'all') {
        filters.data_user = lessorFilter.value
      }
      if (weaponTypeFilter.value && weaponTypeFilter.value.length > 0) {
        filters.weapon_types = weaponTypeFilter.value
      }
      if (floatRangeFilter.value && floatRangeFilter.value.length > 0) {
        filters.float_ranges = floatRangeFilter.value
      }
      if (searchText.value && searchText.value.trim()) {
        filters.search = searchText.value.trim()
      }
      if (dateRange.value && dateRange.value.length === 2) {
        filters.start_date = dateRange.value[0]
        filters.end_date = dateRange.value[1]
      }
      return filters
    }

    const loadFilteredStats = async () => {
      try {
        // 使用 rental 统计接口
        const response = await fetch('/api/webRentalV1/getRentalStats', {
          method: 'GET',
          mode: 'cors',
          signal: createAbortSignal(statsController),
          headers: {
            'Accept': 'application/json',
          },
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const statsData = await response.json()

        allDataStats.value = {
          totalCount: statsData.total_count ?? 0,
          totalAmount: (statsData.total_amount ?? 0).toFixed(2),
          avgPrice: (statsData.avg_price ?? 0).toFixed(2),
          totalLeaseDays: statsData.total_lease_days ?? 0,
          avgLeaseDays: (statsData.avg_lease_days ?? 0).toFixed(1),
          rentingCount: statsData.renting_count ?? 0,
          completedCount: statsData.completed_count ?? 0,
          cancelledCount: statsData.cancelled_count ?? 0
        }

        // 复用统计返回的总数作为分页总数，减少额外计数请求
        if (typeof statsData.total_count === 'number') {
          totalItems.value = statsData.total_count
        }
      } catch (error) {
        if (error.name === 'AbortError') return
        console.error('加载统计数据失败:', error)
        allDataStats.value = {
          totalCount: 0,
          totalAmount: '0.00',
          avgPrice: '0.00',
          totalLeaseDays: 0,
          avgLeaseDays: '0.0',
          rentingCount: 0,
          completedCount: 0,
          cancelledCount: 0
        }
      }
    }

    // 向后兼容旧调用
    const loadAllDataStats = () => loadFilteredStats()

    const buildDataFilters = (keywordOverride = null) => {
      const filters = {
        status: statusFilter.value && statusFilter.value !== 'all' ? statusFilter.value : null,
        status_sub: statusSubFilter.value && statusSubFilter.value !== 'all' ? statusSubFilter.value : null,
        platform: platformFilter.value && platformFilter.value !== 'all' ? platformFilter.value : null,
        lessor_name: lessorFilter.value && lessorFilter.value !== 'all' ? lessorFilter.value : null,
        weapon_types: weaponTypeFilter.value && weaponTypeFilter.value.length > 0 ? weaponTypeFilter.value : null,
        float_ranges: floatRangeFilter.value && floatRangeFilter.value.length > 0 ? floatRangeFilter.value : null,
        search: keywordOverride !== null
          ? (keywordOverride || null)
          : (searchText.value && searchText.value.trim() ? searchText.value.trim() : null),
      }

      if (dateRange.value && dateRange.value.length === 2) {
        filters.start_date = dateRange.value[0]
        filters.end_date = dateRange.value[1]
      }

      return filters
    }

    const fetchRentalDataFiltered = async ({ min, max, keywordOverride = null, storeInSearch = false }) => {
      const response = await fetch(`/api/webRentalV1/selectRentalWeaponName/${encodeURIComponent(keywordOverride || searchText.value.trim())}`, {
        method: 'GET',
        mode: 'cors',
        signal: createAbortSignal(dataController),
        headers: {
          'Accept': 'application/json',
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const rawData = await response.json()
      if (!Array.isArray(rawData)) {
        throw new Error('数据格式错误')
      }

      const mapped = rawData.map((item, index) => {
        if (!Array.isArray(item)) return null
        return {
          id: index + 1,
          ID: item[0] || '',
          weapon_name: item[1] || '',
          weapon_type: item[2] || '',
          item_name: item[3] || '', 
          weapon_float: item[4] || 0,
          float_range: item[5] || '',
          price: item[6] || 0,
          lessor_name: item[7] || '',
          status: item[8] || '',
          last_status: item[9] || '',
          from: item[10] || '',
          lean_start_time: item[11] || '',
          lean_end_time: item[12] || '',
          total_Lease_Days: item[13] || 0,
          max_Lease_Days: item[14] || 0,
          steam_hash_name: item[15] || '',
          sticker: item[16] || null,
          pendant: item[17] || null,
          rename: item[18] || '',
          data_user: item[19] || ''
        }
      }).filter(Boolean)

      if (storeInSearch) {
        allSearchResults.value = mapped
        rentalData.value = []
      } else {
        rentalData.value = mapped
      }

      return mapped.length
    }

    const loadRentalData = async () => {
      // 如果是搜索模式且有搜索关键词，不需要重新加载数据
      if (isSearchMode.value && searchText.value.trim()) {
        console.log('搜索模式下，使用现有搜索结果进行分页')
        return
      }
      
      loading.value = true
      try {
        // 如果有搜索关键词但不在搜索模式，执行搜索
        if (searchText.value.trim()) {
          await searchByName(searchText.value.trim())
          return
        }
        
        // 退出搜索模式，进入普通模式
        isSearchMode.value = false
        allSearchResults.value = []
        
        // 计算分页参数
        const min = (currentPage.value - 1) * pageSize.value
        const max = pageSize.value
        

        console.log(`正在请求数据... 页码: ${currentPage.value}, 每页: ${pageSize.value}, min: ${min}, max: ${max}`)
        
        // 根据状态/子状态筛选选择不同的API（子状态优先）
        let apiUrl = `/api/webRentalV1/getRentalData/${min}/${max}`
        if (statusSubFilter.value && statusSubFilter.value !== 'all') {
          apiUrl = `/api/webRentalV1/getRentalDataByStatusSub/${encodeURIComponent(statusSubFilter.value)}/${min}/${max}`
        } else if (statusFilter.value && statusFilter.value !== 'all') {
          apiUrl = `/api/webRentalV1/getRentalDataByStatus/${statusFilter.value}/${min}/${max}`
        }
        
        const response = await fetch(apiUrl, {
          method: 'GET',
          mode: 'cors',
          signal: createAbortSignal(dataController),
          headers: {
            'Accept': 'application/json',
          },
        })
        
        console.log('响应状态:', response.status)
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const rawData = await response.json()
        console.log('接收到的原始数据:', rawData)
        
        // 检查数据格式
        if (!Array.isArray(rawData)) {
          console.error('数据格式错误，期望数组格式，实际收到:', typeof rawData)
          throw new Error('数据格式错误')
        }
        
        // 转换数组格式数据为对象格式
        rentalData.value = rawData.map((item, index) => {
          if (!Array.isArray(item)) {
            console.error('数据项格式错误，期望数组，实际收到:', item)
            return null
          }

          return {
            id: index + 1,
            ID: item[0] || '',
            weapon_name: item[1] || '',
            weapon_type: item[2] || '',
            item_name: item[3] || '',
            weapon_float: item[4] || 0,
            float_range: item[5] || '',
            price: item[6] || 0,
            lessor_name: item[7] || '',
            status: item[8] || '',
            status_sub: item[9] || '',
            from: item[10] || '',
            lean_start_time: item[11] || '',
            lean_end_time: item[12] || '',
            total_Lease_Days: item[13] || 0,
            max_Lease_Days: item[14] || 0,
            steam_hash_name: item[15] || '',
            sticker: item[16] || null,
            pendant: item[17] || null,
            rename: item[18] || '',
            data_user: item[19] || ''
          }
        }).filter(item => item !== null)
        
        console.log('转换后的数据:', rentalData.value)

        // 并行刷新统计（内部会更新 totalItems）
        await loadFilteredStats()

        if (rentalData.value.length === 0) {
          ElMessage.info('暂无借入数据')
        } else {
          ElMessage.success(`加载成功，共 ${rentalData.value.length} 条记录`)
        }
        
      } catch (error) {
        if (error.name === 'AbortError') return
        console.error('加载出租数据失败:', error)
        
        // 根据错误类型显示不同的错误信息
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
          ElMessage.error('无法连接到服务器，请检查网络连接')
        } else if (error.message.includes('HTTP error')) {
          ElMessage.error(`服务器响应错误: ${error.message}`)
        } else if (error.message.includes('数据格式错误')) {
          ElMessage.error('服务器返回数据格式错误')
        } else {
          ElMessage.error(`加载数据失败: ${error.message}`)
        }
        
        // API调用失败时清空数据
        rentalData.value = []
        totalItems.value = 0
      } finally {
        loading.value = false
      }
    }

    const handleSizeChange = (val) => {
      pageSize.value = val
      currentPage.value = 1
      loadRentalData()
    }

    const handleCurrentChange = (val) => {
      currentPage.value = val
      loadRentalData()
    }

    const handleSortChange = ({ prop, order }) => {
      if (prop === 'lean_start_time') {
        sortOrder.value = order || 'descending'
        const sortFn = (a, b) => {
          const ta = new Date(a.lean_start_time || 0).getTime()
          const tb = new Date(b.lean_start_time || 0).getTime()
          return sortOrder.value === 'ascending' ? ta - tb : tb - ta
        }

        if (isSearchMode.value && allSearchResults.value.length > 0) {
          allSearchResults.value.sort(sortFn)
        } else {
          rentalData.value.sort(sortFn)
        }
      }
    }

    const handleSearch = () => {
      handleAdvancedSearch()
    }

    const handleClearSearch = async () => {
      searchText.value = ''
      statusFilter.value = ''
      statusSubFilter.value = ''
      statusSubList.value = []
      weaponTypeFilter.value = []
      floatRangeFilter.value = []
      dateRange.value = null
      currentPage.value = 1
      isSearchMode.value = false
      isTimeSearchMode.value = false
      allSearchResults.value = []

      // 优化：并行执行，避免重复调用
      await Promise.all([
        loadStatusSubList(),
        loadRentalData(),
        loadFilteredStats()
      ])
    }

    const handleStatusChange = async () => {
      // 未选择时为空，接口内部会将空转换为 all
      currentPage.value = 1
      // 重置子状态并立即刷新子状态列表
      statusSubFilter.value = ''
      statusSubList.value = []

      // 如果是搜索模式，只需要更新分页，不需要重新加载数据
      if (isSearchMode.value && searchText.value.trim()) {
        await loadStatusSubList()
        // 状态变更会自动通过computed属性重新计算filteredLentData
        return
      } else {
        // 非搜索模式，并行加载数据
        await Promise.all([
          loadStatusSubList(),
          loadRentalData(),
          loadFilteredStats()
        ])
      }
    }
    const handleStatusSubChange = async () => {
      currentPage.value = 1
      // 空子状态表示全部
      if (!statusSubFilter.value) {
        statusSubFilter.value = ''
      }
      // 优化：并行加载
      await Promise.all([
        loadRentalData(),
        loadFilteredStats()
      ])
    }

    const handlePlatformChange = async () => {
      currentPage.value = 1
      // 优化：并行加载
      await Promise.all([
        loadRentalData(),
        loadFilteredStats()
      ])
    }

    const handleLessorChange = async () => {
      currentPage.value = 1
      // 优化：并行加载
      await Promise.all([
        loadRentalData(),
        loadFilteredStats()
      ])
    }

    const handleStatusSubVisibleChange = (visible) => {
      if (visible) {
        loadStatusSubList()
      }
    }

    const handleDateRangeChange = (value) => {
      console.log('日期范围变更:', value)
    }

    // 高级搜索处理
    const handleAdvancedSearch = async () => {
      loading.value = true
      currentPage.value = 1

      try {
        const hasTypeFilter = weaponTypeFilter.value && weaponTypeFilter.value.length > 0
        const hasWearFilter = floatRangeFilter.value && floatRangeFilter.value.length > 0
        const hasDateRange = dateRange.value && dateRange.value.length === 2
        const hasKeyword = searchText.value && searchText.value.trim()

        if (hasTypeFilter || hasWearFilter) {
          await searchByTypeAndWear()
        } else if (hasDateRange) {
          await handleTimeSearch()
        } else if (hasKeyword) {
          await searchByName(searchText.value.trim())
        } else {
          await loadRentalData()
        }

        ElMessage.success('搜索完成')
      } catch (error) {
        console.error('搜索失败:', error)
        ElMessage.error(error.message || '搜索失败')
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
        const [startDate, endDate] = dateRange.value
        console.log('按时间搜索:', startDate, '至', endDate)
        
        const response = await fetch(`/api/webRentalV1/searchRentalByTimeRange/${startDate}/${endDate}`, {
          method: 'GET',
          mode: 'cors',
          signal: createAbortSignal(dataController),
          headers: {
            'Accept': 'application/json',
          },
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const rawData = await response.json()
        console.log('时间搜索结果:', rawData)

        if (!Array.isArray(rawData)) {
          throw new Error('搜索结果格式错误')
        }

        // 转换搜索结果并存储所有数据
        const searchResults = rawData.map((item, index) => ({
          id: index + 1,
          ID: item[0] || '',
          weapon_name: item[1] || '',
          weapon_type: item[2] || '',
          item_name: item[3] || '',
          weapon_float: item[4] || 0,
          float_range: item[5] || '',
          price: item[6] || 0,
          lessor_name: item[7] || '',
          status: item[8] || '',
          status_sub: item[9] || '',
          from: item[10] || '',
          lean_start_time: item[11] || '',
          lean_end_time: item[12] || '',
          total_Lease_Days: item[13] || 0,
          max_Lease_Days: item[14] || 0,
          steam_hash_name: item[15] || '',
          sticker: item[16] || null,
          pendant: item[17] || null,
          rename: item[18] || '',
          data_user: item[19] || ''
        }))
        
        // 进入时间搜索模式
        isTimeSearchMode.value = true
        isSearchMode.value = true
        allSearchResults.value = searchResults
        rentalData.value = [] // 清空普通数据
        totalItems.value = rawData.length
        currentPage.value = 1
        
        // 获取时间搜索结果的统计
        await loadTimeRangeStats(startDate, endDate)
        
        if (searchResults.length === 0) {
          ElMessage.info(`在 ${startDate} 至 ${endDate} 期间未找到出租记录`)
        } else {
          ElMessage.success(`找到 ${searchResults.length} 条出租记录`)
        }
        
      } catch (error) {
        if (error.name === 'AbortError') return
        console.error('时间搜索失败:', error)
        ElMessage.error(`时间搜索失败: ${error.message}`)
        isSearchMode.value = false
        isTimeSearchMode.value = false
        allSearchResults.value = []
        rentalData.value = []
        totalItems.value = 0
      } finally {
        loading.value = false
      }
    }

    const loadTimeRangeStats = async (startDate, endDate) => {
      try {
        console.log('正在获取时间范围统计...', { startDate, endDate })
        
        const response = await fetch(`/api/webRentalV1/getRentalStatsByTimeRange/${startDate}/${endDate}`, {
          method: 'GET',
          mode: 'cors',
          signal: createAbortSignal(statsController),
          headers: {
            'Accept': 'application/json',
          },
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const statsData = await response.json()
        console.log('获取到的时间范围统计:', statsData)
        
        if (statsData) {
          allDataStats.value = {
            totalCount: statsData.total_count || 0,
            totalAmount: statsData.total_amount?.toFixed(2) || '0.00',
            avgPrice: statsData.avg_price?.toFixed(2) || '0.00',
            totalLeaseDays: statsData.total_lease_days || 0,
            avgLeaseDays: statsData.avg_lease_days?.toFixed(1) || '0.0',
            rentingCount: statsData.renting_count || 0,
            completedCount: statsData.completed_count || 0,
            cancelledCount: statsData.cancelled_count || 0
          }
          console.log('设置时间范围统计为:', allDataStats.value)
        } else {
          console.error('时间范围统计API返回数据格式错误:', statsData)
        }
      } catch (error) {
        if (error.name === 'AbortError') return
        console.error('获取时间范围统计失败:', error)
        allDataStats.value = {
          totalCount: 0,
          totalAmount: '0.00',
          avgPrice: '0.00',
          totalLeaseDays: 0,
          avgLeaseDays: '0.0',
          rentingCount: 0,
          completedCount: 0,
          cancelledCount: 0
        }
      }
    }

    // 加载武器类型数据（带缓存）
    const loadWeaponTypes = async () => {
      try {
        const cacheKey = 'rentalWeaponTypes'
        const cached = getCachedData(cacheKey)
        if (cached) {
          weaponTypes.value = cached
          return
        }

        const response = await fetch('/api/webRentalV1/getRentalWeaponTypes')
        const result = await response.json()
        if (result.success) {
          weaponTypes.value = result.data
          setCachedData(cacheKey, result.data)
        }
      } catch (error) {
        console.error('获取武器类型失败:', error)
      }
    }

    // 加载磨损等级数据（带缓存）
    const loadFloatRanges = async () => {
      try {
        const cacheKey = 'rentalFloatRanges'
        const cached = getCachedData(cacheKey)
        if (cached) {
          floatRanges.value = cached
          return
        }

        const response = await fetch('/api/webRentalV1/getRentalFloatRanges')
        const result = await response.json()
        if (result.success) {
          floatRanges.value = result.data
          setCachedData(cacheKey, result.data)
        }
      } catch (error) {
        console.error('获取磨损等级失败:', error)
      }
    }

    // 加载状态列表数据（status）- 带缓存
    const loadStatusList = async () => {
      try {
        const cacheKey = 'rentalStatusList'
        const cached = getCachedData(cacheKey)
        if (cached) {
          statusList.value = cached
          return
        }

        const response = await fetch('/api/webRentalV1/getRentalStatusList')
        const result = await response.json()
        console.log('借入 status 列表原始返回:', result)
        if (result && result.success && Array.isArray(result.data)) {
          statusList.value = result.data
          setCachedData(cacheKey, result.data)
        } else {
          statusList.value = []
        }
      } catch (error) {
        console.error('获取状态列表失败:', error)
      }
    }

    // 加载子状态列表数据（status_sub），依据当前 statusFilter
    const loadStatusSubList = async () => {
      try {
        const statusParam = statusFilter.value || 'all'
        const response = await fetch(`/api/webRentalV1/getRentalStatusSubList/${statusParam}`)
        const result = await response.json()
        console.log('借入 status_sub 列表原始返回:', statusParam, result)
        if (result && result.success && Array.isArray(result.data)) {
          statusSubList.value = result.data
        } else {
          statusSubList.value = []
        }
      } catch (error) {
        console.error('获取子状态列表失败:', error)
        statusSubList.value = []
      }
    }

    const loadPlatformList = async () => {
      try {
        const cacheKey = 'rentalPlatformList'
        const cached = getCachedData(cacheKey)
        if (cached) {
          platformList.value = cached
          return
        }

        const response = await fetch('/api/webRentalV1/getRentalPlatformList')
        const result = await response.json()
        if (result.success && Array.isArray(result.data)) {
          platformList.value = result.data
          setCachedData(cacheKey, result.data)
        } else {
          platformList.value = []
        }
      } catch (error) {
        console.error('获取平台列表失败:', error)
        platformList.value = []
      }
    }

    const loadLenterList = async () => {
      try {
        const cacheKey = 'rentalUserList'
        const cached = getCachedData(cacheKey)
        if (cached) {
          lenterList.value = cached
          lessorList.value = cached
          return
        }

        // 使用 getRentalUserList 接口读取 data_user 列
        const response = await fetch('/api/webRentalV1/getRentalUserList')
        const result = await response.json()
        if (result.success && Array.isArray(result.data)) {
          lenterList.value = result.data
          lessorList.value = result.data
          setCachedData(cacheKey, result.data)
        } else {
          lenterList.value = []
          lessorList.value = []
        }
      } catch (error) {
        console.error('获取用户列表失败:', error)
        lenterList.value = []
        lessorList.value = []
      }
    }

    // 类型筛选处理
    const handleTypeChange = async () => {
      if (weaponTypeFilter.value && weaponTypeFilter.value.length > 0 || 
          floatRangeFilter.value && floatRangeFilter.value.length > 0) {
        await searchByTypeAndWear()
      } else {
        await loadRentalData()
      }
    }

    // 磨损等级筛选处理
    const handleWearChange = async () => {
      if (weaponTypeFilter.value && weaponTypeFilter.value.length > 0 || 
          floatRangeFilter.value && floatRangeFilter.value.length > 0) {
        await searchByTypeAndWear()
      } else {
        await loadRentalData()
      }
    }

    // 移除单个武器类型
    const removeWeaponType = (type) => {
      const index = weaponTypeFilter.value.indexOf(type)
      if (index > -1) {
        weaponTypeFilter.value.splice(index, 1)
        handleTypeChange()
      }
    }

    // 移除单个磨损等级
    const removeFloatRange = (range) => {
      const index = floatRangeFilter.value.indexOf(range)
      if (index > -1) {
        floatRangeFilter.value.splice(index, 1)
        handleWearChange()
      }
    }

    // 按类型和磨损等级搜索 - rental暂不支持，保留空实现
    const searchByTypeAndWear = async () => {
      ElMessage.warning('借入数据暂不支持按类型和磨损筛选')
      await loadRentalData()
    }

    // 获取按类型和磨损筛选的统计数据 - rental暂不支持，保留空实现
    const loadStatsByTypeAndWear = async () => {
      // rental暂不支持
    }

    const openPreview = (item) => {
      previewItem.value = item
      previewVisible.value = true
    }

    onMounted(async () => {
      // 优化：先加载主数据，其他数据按需加载
      // 立即加载主数据和统计
      const criticalRequests = [
        loadRentalData(),
        loadFilteredStats()
      ]

      // 延迟加载非关键数据（如下拉列表选项）
      setTimeout(async () => {
        const lazyRequests = [
          loadWeaponTypes(),
          loadFloatRanges(),
          loadStatusList(),
          loadStatusSubList(),
          loadPlatformList(),
          loadLenterList()
        ]
        await Promise.allSettled(lazyRequests)
      }, 100)

      await Promise.allSettled(criticalRequests)
    })

    onBeforeUnmount(() => {
      dataController.value?.abort()
      statsController.value?.abort()
    })

    return {
      loading,
      rentalData,
      filteredRentalData,
      allDataStats,
      currentPageStats,
      searchText,
      statusFilter,
      weaponTypeFilter,
      floatRangeFilter,
      weaponTypes,
      floatRanges,
      statusList,
      statusSubList,
      statusSubFilter,
      platformList,
      lessorList,
      platformFilter,
      lessorFilter,
      dateRange,
      isTimeSearchMode,
      currentPage,
      pageSize,
      totalItems,
      isSearchMode,
      allSearchResults,
      sortOrder,
      previewVisible,
      previewItem,
      formatTime,
      getStatusType,
      getStatusColor,
      getStatusTextColor,
      mapSource,
      handleSizeChange,
      handleCurrentChange,
      handleSortChange,
      handleSearch,
      handleClearSearch,
      handleStatusChange,
      handleStatusSubChange,
      handlePlatformChange,
      handleLessorChange,
      handleTypeChange,
      handleWearChange,
      removeWeaponType,
      removeFloatRange,
      handleStatusSubVisibleChange,
      handleAdvancedSearch,
      handleDateRangeChange,
      hasAdvancedFilters,
      handleTimeSearch,
      getWeaponImage,
      getItemTitle,
      hasExtras,
      parseStickers,
      parsePendant,
      openPreview
    }
  }
}
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: clamp(1rem, 3vw, 1.25rem);
}

.page-header h2 {
  margin: 0;
  font-size: 1.25rem;
  color: var(--text-primary);
}

.search-input {
  width: 200px;
  min-width: 200px;
  max-width: 200px;
  --el-input-height: 36px;
}

.status-select,
.type-select,
.wear-select {
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

.table-container {
  margin-bottom: clamp(1rem, 3vw, 1.25rem);
}

.pagination {
  margin-top: clamp(1rem, 3vw, 1.25rem);
  display: flex;
  justify-content: center;
}

.pagination-top {
  margin-top: 0;
  margin-bottom: clamp(1rem, 3vw, 1.25rem);
}

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

.stats-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border-default) 20%, var(--border-default) 80%, transparent);
  margin: 0.5rem 0;
}

.stats-grid-3x2 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: clamp(0.75rem, 2vw, 1rem);
  align-items: stretch;
}

@media (min-width: 1024px) {
  .stats-container {
    flex-direction: row;
    gap: 2rem;
    align-items: flex-start;
  }
  
  .stats-divider {
    width: 1px;
    height: auto;
    min-height: 120px;
    background: linear-gradient(180deg, transparent, var(--border-default) 20%, var(--border-default) 80%, transparent);
    margin: 0;
  }
  
  .stats-section {
    flex: 1;
    min-width: 0;
  }
}

.grid-3 {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: clamp(0.75rem, 2vw, 1rem);
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

/* 图片与名称样式，保持与 /buy 一致 */
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
}

.weapon-img {
  width: 100%;
  height: auto;
  max-width: 100%;
  max-height: 90px;
  object-fit: contain;
  object-position: center;
  background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
  border-radius: 4px;
  display: block;
}

.no-image {
  color: #666;
  font-size: 0.75rem;
}

.item-name-cell {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.item-title {
  line-height: 1.4;
}

.item-extras {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

/* 印花列表样式 */
.sticker-list {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.sticker-item {
  position: relative;
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.sticker-item:hover {
  transform: scale(2);
  z-index: 10;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
  border-color: rgba(76, 175, 80, 0.5);
}

.sticker-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.5));
}

.sticker-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 1rem;
  font-weight: bold;
  background: rgba(255, 255, 255, 0.05);
}

/* 挂件样式 */
.pendant-list {
  display: flex;
  gap: 4px;
}

.pendant-img {
  width: 32px;
  height: 32px;
  object-fit: contain;
  border-radius: 2px;
  background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
}

/* 改名标签样式 */
.rename-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  background: rgba(76, 175, 80, 0.1);
  border: 1px solid rgba(76, 175, 80, 0.3);
  border-radius: 3px;
  font-size: 0.75rem;
}

.rename-icon {
  font-size: 0.875rem;
}

.rename-text {
  color: #4CAF50;
  font-weight: 500;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 磨损值进度条，与 /buy 一致 */
.float-bar {
  position: relative;
  height: 8px;
  display: flex;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.float-segment {
  height: 100%;
  transition: opacity 0.2s;
}

.float-segment:hover {
  opacity: 0.8;
}

.float-segment.fn {
  flex: 7;
  background: linear-gradient(to right, #4CAF50, #66BB6A);
}

.float-segment.mw {
  flex: 8;
  background: linear-gradient(to right, #8BC34A, #9CCC65);
}

.float-segment.ft {
  flex: 23;
  background: linear-gradient(to right, #FFC107, #FFB300);
}

.float-segment.ww {
  flex: 7;
  background: linear-gradient(to right, #FF9800, #FB8C00);
}

.float-segment.bs {
  flex: 55;
  background: linear-gradient(to right, #F44336, #E53935);
}

.float-pointer {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 3px;
  height: 16px;
  background: #fff;
  border-radius: 2px;
  box-shadow: 0 0 4px rgba(0, 0, 0, 0.5), 0 0 8px rgba(255, 255, 255, 0.8);
  z-index: 10;
  pointer-events: none;
  transition: all 0.2s ease;
}

.float-pointer::before {
  content: '';
  position: absolute;
  top: -4px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 5px solid #fff;
}

.float-pointer::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-bottom: 5px solid #fff;
}

.rent-time-range {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.85rem;
}

.rent-time-separator {
  color: #888;
}

/* 预览弹窗样式，参考 /buy */
.preview-dialog :deep(.el-dialog__header) {
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-color);
  padding: 1rem 1.5rem;
}

.preview-dialog :deep(.el-dialog__title) {
  color: #fff;
  font-weight: bold;
  font-size: 1.1rem;
}

.preview-dialog :deep(.el-dialog__body) {
  background: var(--bg-secondary);
  padding: 1.5rem;
}

.preview-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.preview-main-layout {
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;
}

.preview-left-section,
.preview-right-section {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.preview-image-section {
  position: relative;
  width: 100%;
  height: 300px;
  background: var(--bg-tertiary);
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
}

.preview-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 1.2rem;
  background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
}

.preview-info-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.preview-float-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.preview-float-bar-container {
  width: 100%;
}

.preview-float-value {
  font-size: 1.1rem;
  font-family: monospace;
  color: #fff;
  font-weight: bold;
}

.preview-float-range {
  font-size: 0.9rem;
  color: #999;
}

.preview-prices {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.preview-price-row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.preview-price-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.preview-price-label {
  color: #999;
  font-size: 0.9rem;
  white-space: nowrap;
}

.preview-price-value {
  color: #fff;
  font-weight: bold;
  font-size: 1rem;
}

.preview-price-value.buy-price {
  color: #4CAF50;
}

.preview-info-row {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
}

.preview-info-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.preview-info-label {
  color: #999;
  font-size: 0.9rem;
  white-space: nowrap;
}

.preview-info-value {
  color: #fff;
  font-size: 0.9rem;
}

.preview-order-id {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 6px;
}

.preview-order-icon {
  font-size: 1.2rem;
}

.preview-order-text {
  color: #fff;
  font-size: 1rem;
  font-weight: 500;
}

.preview-rename {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  margin-top: 1rem;
}

.preview-rename-icon {
  font-size: 1.2rem;
}

.preview-rename-text {
  color: #fff;
  font-size: 1rem;
  font-weight: 500;
}

.preview-order-id {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  margin-top: 1rem;
}

.preview-order-icon {
  font-size: 1.2rem;
}

.preview-order-text {
  color: #fff;
  font-size: 1rem;
  font-weight: 500;
}

/* 预览弹窗中的贴纸列表 */
.preview-sticker-list-section {
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 6px;
}

.preview-sticker-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.preview-sticker-list-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  transition: all 0.2s ease;
}

.preview-sticker-list-item:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(76, 175, 80, 0.5);
}

.preview-sticker-list-img-wrapper {
  position: relative;
  width: 50px;
  height: 50px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.2s ease;
}

.preview-sticker-list-img-wrapper:hover {
  transform: scale(1.2);
  border-color: rgba(76, 175, 80, 0.8);
  z-index: 10;
}

.preview-sticker-list-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.preview-sticker-list-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 1.5rem;
  font-weight: bold;
}

.preview-sticker-list-name {
  color: #fff;
  font-size: 0.9rem;
  flex: 1;
  word-break: break-word;
}

/* 预览弹窗中的挂件 */
.preview-pendant-section {
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 6px;
}

.preview-pendant-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.preview-pendant-list-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  transition: all 0.2s ease;
}

.preview-pendant-list-item:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 215, 0, 0.5);
}

.preview-pendant-list-img-wrapper {
  position: relative;
  width: 50px;
  height: 50px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.2s ease;
}

.preview-pendant-list-img-wrapper:hover {
  transform: scale(1.2);
  border-color: rgba(255, 215, 0, 0.8);
  z-index: 10;
}

.preview-pendant-list-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.preview-pendant-list-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 1.5rem;
}

.preview-pendant-list-name {
  color: #fff;
  font-size: 0.9rem;
  flex: 1;
  word-break: break-word;
}

:deep(.el-table) {
  background-color: transparent;
  color: #fff;
  font-size: clamp(0.75rem, 1.2vw, 0.875rem);
  min-width: 1200px;
}

:deep(.el-table th) {
  background-color: var(--bg-tertiary);
  color: #fff;
  border-bottom: 1px solid var(--border-default);
  padding: clamp(0.5rem, 1.5vw, 0.75rem);
}

:deep(.el-table td) {
  background-color: transparent !important;
  border-bottom: 1px solid var(--border-default);
  color: #ccc;
  padding: clamp(0.5rem, 1.5vw, 0.75rem);
}

:deep(.el-table tr:hover > td) {
  background-color: transparent !important;
}

:deep(.el-input__inner) {
  background-color: #2a2a2a;
  border-color: #333;
  color: #fff;
}

:deep(.el-select .el-input__inner) {
  background-color: #2a2a2a;
  border-color: #333;
  color: #fff;
}

/* 日期选择器样式 */
:deep(.el-date-editor .el-input__inner) {
  background-color: #2a2a2a !important;
  border-color: #333 !important;
  color: #fff !important;
}

:deep(.el-date-editor .el-input__prefix) {
  color: #ccc;
}

:deep(.el-date-editor .el-input__suffix) {
  color: #ccc;
}

/* 日历面板整体样式 */
:deep(.el-picker-panel) {
  background-color: #2a2a2a !important;
  border: 1px solid #333 !important;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.3) !important;
}

:deep(.el-picker-panel__content) {
  background-color: #2a2a2a !important;
  color: #fff;
}

/* 日历头部 */
:deep(.el-date-picker__header) {
  background-color: #2a2a2a !important;
  border-bottom: 1px solid #333;
  color: #fff;
}

:deep(.el-picker-panel__icon-btn) {
  color: #ccc !important;
}

:deep(.el-picker-panel__icon-btn:hover) {
  color: #409eff !important;
}

/* 年月选择 */
:deep(.el-date-picker__header-label) {
  color: #fff !important;
}

:deep(.el-date-picker__header-label:hover) {
  color: #409eff !important;
}

/* 星期标题 */
:deep(.el-date-table th) {
  background-color: #2a2a2a !important;
  color: #ccc !important;
  border-bottom: 1px solid #333;
}

/* 日期单元格 */
:deep(.el-date-table td) {
  color: #fff !important;
  background-color: #2a2a2a !important;
}

:deep(.el-date-table td span) {
  color: #fff !important;
}

:deep(.el-date-table td.available:hover) {
  background-color: #333 !important;
}

:deep(.el-date-table td.current:not(.disabled)) {
  background-color: #409eff !important;
  color: #fff !important;
  font-weight: bold;
}

:deep(.el-date-table td.today span) {
  color: #409eff !important;
  font-weight: bold;
}

:deep(.el-date-table td.disabled) {
  background-color: #2a2a2a !important;
  color: #666 !important;
}

:deep(.el-date-table td.prev-month),
:deep(.el-date-table td.next-month) {
  color: #666 !important;
}

/* 范围选择 */
:deep(.el-date-table td.in-range) {
  background-color: #3a3a3a !important;
}

:deep(.el-date-table td.start-date) {
  background-color: #409eff !important;
  color: #fff !important;
}

:deep(.el-date-table td.end-date) {
  background-color: #409eff !important;
  color: #fff !important;
}

/* 底部操作区 */
:deep(.el-picker-panel__footer) {
  background-color: #2a2a2a !important;
  border-top: 1px solid #333;
}

:deep(.el-button--text) {
  color: #409eff !important;
}

:deep(.el-button--text:hover) {
  color: #66b1ff !important;
}

/* 时间范围选择器的左右面板 */
:deep(.el-date-range-picker__content) {
  background-color: #2a2a2a !important;
}

:deep(.el-date-range-picker__content.is-left) {
  border-right: 1px solid #333;
}

/* 月份/年份选择面板 */
:deep(.el-month-table td) {
  color: #fff !important;
  background-color: #2a2a2a !important;
}

:deep(.el-month-table td:hover) {
  background-color: #333 !important;
}

:deep(.el-month-table td.current:not(.disabled)) {
  background-color: #409eff !important;
  color: #fff !important;
}

:deep(.el-year-table td) {
  color: #fff !important;
  background-color: #2a2a2a !important;
}

:deep(.el-year-table td:hover) {
  background-color: #333 !important;
}

:deep(.el-year-table td.current:not(.disabled)) {
  background-color: #409eff !important;
  color: #fff !important;
}

:deep(.el-tabs__item) {
  color: #ccc;
}

:deep(.el-tabs__item.is-active) {
  color: #409eff;
}

:deep(.el-tabs__nav-wrap::after) {
  background-color: #333;
}

:deep(.el-tabs__active-bar) {
  background-color: #409eff;
}

@media (max-width: 768px) {
  .search-input {
    min-width: unset;
    width: 100%;
    max-width: none;
  }
  
  .status-select,
  .type-select,
  .wear-select {
    min-width: unset;
    width: 100%;
    max-width: none;
  }
  
  .stats-grid-3x2 {
    grid-template-columns: 1fr;
    grid-template-rows: repeat(6, 1fr);
  }
  
  .grid-3 {
    grid-template-columns: 1fr;
  }
  
  .stat-item {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }
  
  :deep(.el-table) {
    font-size: 0.75rem;
    min-width: 1000px;
  }

  .preview-dialog {
    width: 95% !important;
  }

  .preview-main-layout {
    flex-direction: column;
  }

  .preview-image-section {
    height: 200px;
  }

  .preview-sticker-list {
    height: auto;
  }
}
</style>

<style>
/* 全局日历面板样式 - 无scoped以确保最高优先级 */
.el-picker-panel,
.el-date-picker,
.el-date-range-picker,
.el-popper {
  background-color: #2a2a2a !important;
  border-color: #333 !important;
}

.el-picker-panel .el-picker-panel__content,
.el-picker-panel .el-picker-panel__body,
.el-date-picker .el-picker-panel__content {
  background-color: #2a2a2a !important;
}

.el-date-picker__header,
.el-date-picker__time-header {
  background-color: #2a2a2a !important;
  border-bottom-color: #333 !important;
}

.el-date-table th,
.el-date-table td,
.el-month-table td,
.el-year-table td {
  background-color: #2a2a2a !important;
  color: #fff !important;
}

.el-date-table th {
  color: #ccc !important;
}

.el-picker-panel__footer {
  background-color: #2a2a2a !important;
  border-top-color: #333 !important;
}

/* 修复加载遮罩白色背景问题 */
.el-loading-mask {
  background-color: rgba(42, 42, 42, 0.8) !important;
}

.el-loading-spinner {
  color: #409eff !important;
}

.el-loading-text {
  color: #fff !important;
}

.el-loading-spinner .circular {
  color: #409eff !important;
}
</style>