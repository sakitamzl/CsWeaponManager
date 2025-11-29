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
              clearable
            >
              <el-option v-for="sub in statusSubList" :key="sub" :label="sub" :value="sub" />
            </el-select>
            <el-select
              v-model="sourceFilter"
              placeholder="选择平台"
              class="status-select"
              @change="handleSourceChange"
              clearable
            >
              <el-option v-for="src in sourceList" :key="src" :label="sourceLabel(src)" :value="src" />
            </el-select>
            <el-select
              v-model="dataUserFilter"
              placeholder="选择用户"
              class="status-select"
              @change="handleDataUserChange"
              clearable
            >
              <el-option v-for="u in dataUserList" :key="u" :label="u" :value="u" />
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
          <el-tag v-if="statusFilter" type="success" size="small" closable @close="statusFilter = ''">
            状态: {{ statusFilter }}
          </el-tag>
          <el-tag v-if="statusSubFilter" type="success" size="small" closable @close="statusSubFilter = ''">
            子状态: {{ statusSubFilter }}
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
          <el-tag v-if="sourceFilter" type="info" size="small" closable @close="sourceFilter = ''">
            平台: {{ sourceLabel(sourceFilter) }}
          </el-tag>
          <el-tag v-if="dataUserFilter" type="info" size="small" closable @close="dataUserFilter = ''">
            用户: {{ dataUserFilter }}
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
                <span class="stat-label">总购买数量:</span>
                <span class="stat-value">{{ totalStats.totalCount }} 件</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">总购买金额:</span>
                <span class="stat-value">¥{{ totalStats.totalAmount }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">平均购买价格:</span>
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
                <span class="stat-label">待收货数量:</span>
                <span class="stat-value">{{ totalStats.pendingCount }} 件</span>
              </div>
            </div>
          </div>
          
          <div class="stats-divider"></div>
          
          <div class="stats-section">
            <h3>当前页面统计</h3>
            <div class="stats-grid-3x2">
              <div class="stat-item">
                <span class="stat-label">页面数量:</span>
                <span class="stat-value">{{ currentPageStats.totalCount }} 件</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">页面金额:</span>
                <span class="stat-value">¥{{ currentPageStats.totalAmount }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">平均购买价格:</span>
                <span class="stat-value">¥{{ currentPageStats.avgPrice }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">已完成数量:</span>
                <span class="stat-value">{{ currentPageStats.completedCount }} 件</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">已取消数量:</span>
                <span class="stat-value">{{ currentPageStats.cancelledCount }} 件</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">待收货数量:</span>
                <span class="stat-value">{{ currentPageStats.pendingCount }} 件</span>
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
        :data="filteredBuyData"
        v-loading="loading"
        element-loading-text="加载中..."
        style="width: 100%"
        :row-style="{ backgroundColor: 'transparent' }"
        :header-row-style="{ backgroundColor: 'var(--bg-tertiary)' }"
        :flexible="true"
        :scrollbar-always-on="true"
      >
        <el-table-column label="图片" width="144" align="center">
          <template #default="scope">
            <div class="weapon-image-cell" @click="openPreview(scope.row)" style="cursor: pointer;">
              <img
                v-if="getWeaponImage(scope.row.steam_hash_name)"
                :src="getWeaponImage(scope.row.steam_hash_name)"
                :alt="scope.row.item_name"
                class="weapon-img"
                @error="(e) => e.target.style.display = 'none'"
              />
              <span v-else class="no-image">无图</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="商品名称" min-width="250" show-overflow-tooltip>
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
                    v-if="parsePendant(scope.row.pendant)"
                    :src="getPendantImage(parsePendant(scope.row.pendant))"
                    :alt="parsePendant(scope.row.pendant)?.name"
                    class="pendant-img"
                    @error="(e) => e.target.style.display = 'none'"
                  />
                </div>
                <!-- 改名显示 -->
                <div class="rename-text" v-if="scope.row.rename">
                  <span class="rename-value">{{ scope.row.rename }}</span>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="weapon_float" label="磨损值" width="200" align="left">
          <template #default="scope">
            <div v-if="scope.row.weapon_float">
              <div style="font-family: monospace; font-size: 0.85rem; margin-bottom: 4px;">
                {{ scope.row.weapon_float }}
              </div>
              <!-- 磨损值显示条 -->
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
        <el-table-column prop="price" label="购入价格" min-width="100">
          <template #default="scope">
            ¥{{ scope.row.price }}
          </template>
        </el-table-column>
        <el-table-column prop="from" label="来源" min-width="80" />
        <el-table-column prop="order_time" label="购入时间" min-width="160" sortable="custom" @sort-change="handleSortChange">
          <template #default="scope">
            {{ formatTime(scope.row.order_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" min-width="80">
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

    <!-- 预览弹窗 -->
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
          <!-- 左侧区域 -->
          <div class="preview-left-section">
            <!-- 图片区域 -->
            <div class="preview-image-section">
              <img
                v-if="getWeaponImage(previewItem.steam_hash_name)"
                :src="getWeaponImage(previewItem.steam_hash_name)"
                :alt="previewItem.item_name"
                class="preview-image"
              />
              <div v-else class="preview-image-placeholder">
                <span>无图片</span>
              </div>
            </div>

            <!-- 详细信息区域 -->
            <div class="preview-info-section">
              <!-- 磨损信息 -->
              <div v-if="previewItem.weapon_float" class="preview-float-section">
                <div class="preview-float-bar-container">
                  <div class="float-bar">
                    <div class="float-segment fn"></div>
                    <div class="float-segment mw"></div>
                    <div class="float-segment ft"></div>
                    <div class="float-segment ww"></div>
                    <div class="float-segment bs"></div>
                    <div
                      class="float-pointer"
                      :style="{ left: `${parseFloat(previewItem.weapon_float) * 100}%` }"
                    ></div>
                  </div>
                </div>
                <div class="preview-float-value">{{ previewItem.weapon_float }}</div>
                <div class="preview-float-range" v-if="previewItem.float_range">
                  {{ previewItem.float_range }}
                </div>
              </div>

              <!-- 价格信息 -->
              <div class="preview-prices">
                <div class="preview-price-row">
                  <div class="preview-price-item" v-if="previewItem.price">
                    <span class="preview-price-label">购入价格:</span>
                    <span class="preview-price-value buy-price">¥{{ parseFloat(previewItem.price).toFixed(2) }}</span>
                  </div>
                </div>
                <div class="preview-info-row" v-if="previewItem.order_id">
                  <div class="preview-info-item">
                    <span class="preview-info-label">订单编号:</span>
                    <span class="preview-info-value">{{ previewItem.order_id }}</span>
                  </div>
                </div>
                <div class="preview-info-row">
                  <div class="preview-info-item" v-if="previewItem.weapon_type">
                    <span class="preview-info-label">类型:</span>
                    <span class="preview-info-value">{{ previewItem.weapon_type }}</span>
                  </div>
                  <div class="preview-info-item" v-if="previewItem.from">
                    <span class="preview-info-label">来源:</span>
                    <span class="preview-info-value">{{ sourceLabel(previewItem.from) }}</span>
                  </div>
                </div>
                <div class="preview-info-row" v-if="previewItem.order_time">
                  <div class="preview-info-item">
                    <span class="preview-info-label">购入时间:</span>
                    <span class="preview-info-value">{{ formatTime(previewItem.order_time) }}</span>
                  </div>
                </div>
                <div class="preview-info-row" v-if="previewItem.status">
                  <div class="preview-info-item">
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
                </div>
              </div>
            </div>
          </div>

          <!-- 右侧区域 -->
          <div class="preview-right-section">
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
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { apiUrls } from '@/config/api'

export default {
  name: 'Buy',
  setup() {
    const loading = ref(false)
    const buyData = ref([])
    const searchText = ref('')
    const statusFilter = ref('')
    const sourceFilter = ref('')
    const dataUserFilter = ref('')
    const weaponTypeFilter = ref([])
    const floatRangeFilter = ref([])
    const weaponTypes = ref([])
    const floatRanges = ref([])
    const statusList = ref([])
    const statusSubList = ref([])
    const sourceList = ref([])
    sourceList.value = ['yyyp', 'buff', 'csfloat', 'SMK', 'ING']
    const dataUserList = ref([])
    const statusSubFilter = ref('')
    const currentPage = ref(1)
    const pageSize = ref(20)
    const totalItems = ref(0)
    const dateRange = ref(null)
    const isTimeSearchMode = ref(false)
    const sortOrder = ref('descending') // 'ascending' 或 'descending'
    
    // 预览弹窗相关
    const previewVisible = ref(false)
    const previewItem = ref(null)
    
    // 高级搜索相关
    const hasAdvancedFilters = computed(() => {
      return (searchText.value && searchText.value.trim()) || 
             !!statusFilter.value ||
             !!statusSubFilter.value ||
             !!sourceFilter.value ||
             !!dataUserFilter.value ||
             (weaponTypeFilter.value && weaponTypeFilter.value.length > 0) ||
             (floatRangeFilter.value && floatRangeFilter.value.length > 0) ||
             (dateRange.value && dateRange.value.length === 2)
    })
    const totalStats = ref({
      totalCount: 0,
      totalAmount: '0.00',
      avgPrice: '0.00',
      completedCount: 0,
      cancelledCount: 0,
      pendingCount: 0
    })

    const computeStatsFromData = (data) => {
      if (!Array.isArray(data) || data.length === 0) {
        return {
          totalCount: 0,
          totalAmount: '0.00',
          avgPrice: '0.00',
          completedCount: 0,
          cancelledCount: 0,
          pendingCount: 0
        }
      }

      let totalAmount = 0
      let sumForAvg = 0
      let avgCount = 0
      let completedCount = 0
      let cancelledCount = 0
      let pendingCount = 0

      data.forEach(item => {
        const price = Number(item.price) || 0
        if (item.status !== '已取消') {
          totalAmount += price
          sumForAvg += price
          avgCount += 1
        }
        if (item.status === '已完成') {
          completedCount += 1
        } else if (item.status === '已取消') {
          cancelledCount += 1
        } else if (item.status === '待收货') {
          pendingCount += 1
        }
      })

      const avgPrice = avgCount > 0 ? (sumForAvg / avgCount) : 0

      return {
        totalCount: data.length,
        totalAmount: totalAmount.toFixed(2),
        avgPrice: avgPrice.toFixed(2),
        completedCount,
        cancelledCount,
        pendingCount
      }
    }

    const currentPageStats = computed(() => {
      // 基于当前页面显示的数据计算统计信息
      const currentData = filteredBuyData.value
      const totalCount = currentData.length
      // 只计算非取消状态的金额
      const validData = currentData.filter(item => item.status !== '已取消')
      const totalAmount = validData.reduce((sum, item) => sum + (parseFloat(item.price) || 0), 0).toFixed(2)
      const avgPrice = validData.length > 0 ? (totalAmount / validData.length).toFixed(2) : '0.00'
      const completedCount = currentData.filter(item => item.status === '已完成').length
      const cancelledCount = currentData.filter(item => item.status === '已取消').length
      const pendingCount = currentData.filter(item => item.status === '待收货').length

      return {
        totalCount,
        totalAmount,
        avgPrice,
        completedCount,
        cancelledCount,
        pendingCount
      }

    })

    // 加载 data_user 列表
    const loadDataUserList = async () => {
      try {
        const response = await fetch(apiUrls.buyDataUserList(), {
          method: 'GET',
          headers: { 'Accept': 'application/json' }
        })
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
        const users = await response.json()
        if (Array.isArray(users)) {
          dataUserList.value = users
        }
      } catch (e) {
        console.error('加载数据用户列表失败:', e)
      }
    }

    // 存储所有搜索结果，用于前端分页
    const allSearchResults = ref([])
    const isSearchMode = ref(false)

    const filteredBuyData = computed(() => {
      let filtered = buyData.value

      // 如果是搜索模式，进行前端分页
      if (isSearchMode.value && allSearchResults.value.length > 0) {
        filtered = allSearchResults.value
        
        // 状态筛选
        if (statusFilter.value) {
          filtered = filtered.filter(item => item.status === statusFilter.value)
        }
        if (statusSubFilter.value) {
          filtered = filtered.filter(item => (item.status_sub || '') === statusSubFilter.value)
        }
        
        // 前端分页
        const start = (currentPage.value - 1) * pageSize.value
        const end = start + pageSize.value
        return filtered.slice(start, end)
      }

      // 非搜索模式的筛选（原有逻辑）
      if (statusFilter.value) {
        filtered = filtered.filter(item => item.status === statusFilter.value)
      }
      if (statusSubFilter.value) {
        filtered = filtered.filter(item => (item.status_sub || '') === statusSubFilter.value)
      }

      return filtered
    })

    const formatTime = (time) => {
      return new Date(time).toLocaleString('zh-CN')
    }

    const getStatusType = (status) => {
      const statusMap = {
        '已完成': 'success',
        '已取消': 'danger',
        '待收货': 'info',
        '预售待交付': 'warning'
      }
      return statusMap[status] || 'info'
    }

    const getStatusColor = (status) => {
      const colorMap = {
        '已完成': '#52c41a',    // 更鲜明的绿色
        '已取消': '#ff4d4f',    // 更鲜明的红色
        '待收货': '#1890ff',    // 蓝色
        '预售待交付': '#f5a623' // 黄色
      }
      return colorMap[status] || '#909399'
    }

    const getStatusTextColor = (status) => {
      // 对于所有状态都使用白色文字以确保对比度
      return '#FFFFFF'
    }

    // 来源显示映射
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

    const loadTotalStats = async () => {
      if (isSearchMode.value) {
        const stats = computeStatsFromData(allSearchResults.value)
        totalStats.value = stats
        totalItems.value = stats.totalCount
        return
      }

      try {
        const payload = {
          source: sourceFilter.value || null,
          status: statusFilter.value || null,
          status_sub: statusSubFilter.value || null,
          data_user: dataUserFilter.value || null,
          weapon_types: weaponTypeFilter.value && weaponTypeFilter.value.length > 0 ? weaponTypeFilter.value : null,
          float_ranges: floatRangeFilter.value && floatRangeFilter.value.length > 0 ? floatRangeFilter.value : null,
          search: searchText.value && searchText.value.trim() ? searchText.value.trim() : null
        }

        if (dateRange.value && dateRange.value.length === 2) {
          payload.start_date = dateRange.value[0]
          payload.end_date = dateRange.value[1]
        }

        const response = await fetch(apiUrls.buyStatsFiltered(), {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const statsData = await response.json()

        if (statsData && statsData.success) {
          totalStats.value = {
            totalCount: statsData.total_count || 0,
            totalAmount: Number(statsData.total_amount || 0).toFixed(2),
            avgPrice: Number(statsData.avg_price || 0).toFixed(2),
            completedCount: statsData.completed_count || 0,
            cancelledCount: statsData.cancelled_count || 0,
            pendingCount: statsData.pending_count || 0
          }
          totalItems.value = totalStats.value.totalCount
        } else {
          throw new Error(statsData?.message || '统计接口返回失败')
        }
      } catch (error) {
        console.error('获取总统计失败:', error)
        const fallbackStats = computeStatsFromData(buyData.value)
        totalStats.value = fallbackStats
        totalItems.value = fallbackStats.totalCount
      }
    }

    const loadTotalCount = async () => {
      try {
        console.log('正在获取总数...')
        const response = await fetch('/api/webBuyV1/countBuyNumber', {
          method: 'GET',
          mode: 'cors',
          headers: {
            'Accept': 'application/json',
          },
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const countData = await response.json()
        console.log('获取到的总数:', countData)
        
        if (countData && typeof countData.count === 'number') {
          totalItems.value = countData.count
          console.log('设置总数为:', totalItems.value)
        } else {
          console.error('总数API返回数据格式错误:', countData)
        }
      } catch (error) {
        console.error('获取总数失败:', error)
        // 如果获取总数失败，使用保守估计
        totalItems.value = buyData.value.length > 0 ? 1000 : 0
      }
    }

    const searchByName = async (itemName) => {
      loading.value = true
      try {
        console.log('正在搜索武器:', itemName)
        
        // 构建过滤条件，包含搜索关键词和其他过滤条件
        const filters = {
          source: sourceFilter.value || null,
          status: statusFilter.value || null,
          status_sub: statusSubFilter.value || null,
          data_user: dataUserFilter.value || null,
          weapon_types: weaponTypeFilter.value && weaponTypeFilter.value.length > 0 ? weaponTypeFilter.value : null,
          float_ranges: floatRangeFilter.value && floatRangeFilter.value.length > 0 ? floatRangeFilter.value : null,
          search: itemName.trim() || null
        }
        
        if (dateRange.value && dateRange.value.length === 2) {
          filters.start_date = dateRange.value[0]
          filters.end_date = dateRange.value[1]
        }
        
        // 使用组合查询接口获取所有搜索结果（不分页）
        const response = await fetch(apiUrls.buyDataFiltered(), {
          method: 'POST',
          mode: 'cors',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          body: JSON.stringify({
            filters: filters,
            min: 0,
            max: 10000  // 获取所有搜索结果
          })
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
          order_id: item[0] || '',
          item_name: item[1] || '',
          weapon_name: item[2] || '',
          weapon_type: item[3] || '',
          weapon_float: item[4] || 0,
          float_range: item[5] || '',
          price: item[6] || 0,
          from: item[7] || '',
          order_time: item[8] || '',
          status: item[9] || '',
          status_sub: item[10] || '',
          steam_hash_name: item[11] || '',
          sticker: item[12] || null,
          pendant: item[13] || null,
          rename: item[14] || null
        }))

        // 进入搜索模式
        isSearchMode.value = true
        allSearchResults.value = searchResults
        buyData.value = [] // 清空普通数据
        totalItems.value = rawData.length
        currentPage.value = 1
        
        // 获取搜索结果的统计
        await loadTotalStats()
        
        if (searchResults.length === 0) {
          ElMessage.info(`未找到包含"${itemName}"的武器`)
        } else {
          ElMessage.success(`找到 ${searchResults.length} 条相关记录`)
        }
        
      } catch (error) {
        console.error('搜索失败:', error)
        ElMessage.error(`搜索失败: ${error.message}`)
        isSearchMode.value = false
        allSearchResults.value = []
        buyData.value = []
        totalItems.value = 0
      } finally {
        loading.value = false
      }
    }


    const loadBuyData = async () => {
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
        
        // 构建过滤条件
        const filters = {
          source: sourceFilter.value || null,
          status: statusFilter.value || null,
          status_sub: statusSubFilter.value || null,
          data_user: dataUserFilter.value || null,
          weapon_types: weaponTypeFilter.value && weaponTypeFilter.value.length > 0 ? weaponTypeFilter.value : null,
          float_ranges: floatRangeFilter.value && floatRangeFilter.value.length > 0 ? floatRangeFilter.value : null,
          search: null  // 搜索关键词在搜索模式下单独处理
        }
        
        if (dateRange.value && dateRange.value.length === 2) {
          filters.start_date = dateRange.value[0]
          filters.end_date = dateRange.value[1]
        }
        
        // 使用组合查询接口
        const response = await fetch(apiUrls.buyDataFiltered(), {
          method: 'POST',
          mode: 'cors',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          body: JSON.stringify({
            filters: filters,
            min: min,
            max: max
          })
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
        let transformedData = rawData.map((item, index) => {
          if (!Array.isArray(item)) {
            console.error('数据项格式错误，期望数组，实际收到:', item)
            return null
          }

          return {
            id: index + 1,
            order_id: item[0] || '',     // 订单ID
            item_name: item[1] || '',
            weapon_name: item[2] || '',   // 饰品名称
            weapon_type: item[3] || '',  // 武器类型
            weapon_float: item[4] || 0,  // Float值
            float_range: item[5] || '',  // 磨损等级
            price: item[6] || 0,         // 价格
            from: item[7] || '',         // 来源
            order_time: item[8] || '',   // 订单时间
            status: item[9] || '',       // 状态
            status_sub: item[10] || '',  // 状态详情
            steam_hash_name: item[11] || '',
          sticker: item[12] || null,
          pendant: item[13] || null,
          rename: item[14] || null,  // Steam Hash Name
            sticker: item[12] || null,    // 印花信息
            pendant: item[13] || null,    // 挂件信息
            rename: item[14] || null      // 改名信息
          }
        }).filter(item => item !== null)

        // 根据当前排序状态进行排序
        if (sortOrder.value === 'ascending') {
          transformedData.sort((a, b) => {
            const timeA = new Date(a.order_time).getTime()
            const timeB = new Date(b.order_time).getTime()
            return timeA - timeB
          })
        }

        buyData.value = transformedData
        
        console.log('转换后的数据:', buyData.value)
        
        // 获取总数统计（子状态优先）
        await loadTotalStats()
        
        if (buyData.value.length === 0) {
          ElMessage.info('暂无购入数据')
        } else {
          ElMessage.success(`加载成功，共 ${buyData.value.length} 条记录`)
        }
        
      } catch (error) {
        console.error('加载购入数据失败:', error)
        
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
        buyData.value = []
        totalItems.value = 0
      } finally {
        loading.value = false
      }
    }

    const handleSell = (item) => {
      ElMessage.info(`准备出售: ${item.item_name}`)
      // 这里应该跳转到出售页面或打开出售对话框
    }

    const handleRent = (item) => {
      ElMessage.info(`准备出租: ${item.item_name}`)
      // 这里应该跳转到出租页面或打开出租对话框
    }

    const handleViewDetails = (item) => {
      ElMessage.info(`查看详情: ${item.item_name}`)
      // 这里应该打开详情对话框或跳转到详情页面
    }

    const handleSizeChange = (val) => {
      pageSize.value = val
      currentPage.value = 1
      loadBuyData()
    }

    const handleCurrentChange = (val) => {
      currentPage.value = val
      loadBuyData()
    }

    const handleSearch = () => {
      handleAdvancedSearch()
    }

    const handleClearSearch = () => {
      searchText.value = ''
      statusFilter.value = ''
      statusSubFilter.value = ''
      sourceFilter.value = ''
      dataUserFilter.value = ''
      weaponTypeFilter.value = []
      floatRangeFilter.value = []
      dateRange.value = null
      currentPage.value = 1
      isSearchMode.value = false
      isTimeSearchMode.value = false
      allSearchResults.value = []
      loadStatusSubList()
      loadBuyData()
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

    const handleStatusChange = () => {
      currentPage.value = 1
      // 重置并加载子状态
      statusSubFilter.value = ''
      loadStatusSubList()
      loadBuyData()
    }
    
    const handleStatusSubChange = () => {
      currentPage.value = 1
      loadBuyData()
    }

    const handleSourceChange = () => {
      currentPage.value = 1
      loadBuyData()
      // 更新统计
      loadTotalStats()
    }

    const handleDataUserChange = () => {
      // 目前仅更新UI状态，后续可在有后端支持时据此筛选或请求数据
      currentPage.value = 1
      loadBuyData()
    }

    const handleSortChange = ({ column, prop, order }) => {
      console.log('排序变更:', { column, prop, order })
      if (prop === 'order_time') {
        sortOrder.value = order || 'descending'
        // 如果在搜索模式，对当前结果进行前端排序
        if (isSearchMode.value && allSearchResults.value.length > 0) {
          allSearchResults.value.sort((a, b) => {
            const timeA = new Date(a.order_time).getTime()
            const timeB = new Date(b.order_time).getTime()
            return sortOrder.value === 'ascending' ? timeA - timeB : timeB - timeA
          })
        } else {
          // 非搜索模式，重新加载数据
          loadBuyData()
        }
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
          await loadBuyData()
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

        const response = await fetch(`/api/webBuyV1/searchBuyByTimeRange/${startDate}/${endDate}`, {
          method: 'GET',
          mode: 'cors',
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
          order_id: item[0] || '',
          item_name: item[1] || '',
          weapon_name: item[2] || '',
          weapon_type: item[3] || '',
          weapon_float: item[4] || 0,
          float_range: item[5] || '',
          price: item[6] || 0,
          from: item[7] || '',
          order_time: item[8] || '',
          status: item[9] || '',
          status_sub: item[10] || '',
          steam_hash_name: item[11] || '',
          sticker: item[12] || null,
          pendant: item[13] || null,
          rename: item[14] || null
        }))

        // 进入时间搜索模式
        isTimeSearchMode.value = true
        isSearchMode.value = true
        allSearchResults.value = searchResults
        buyData.value = [] // 清空普通数据
        totalItems.value = rawData.length
        currentPage.value = 1

        // 获取时间搜索结果的统计
        await loadTimeRangeStats(startDate, endDate)

        if (searchResults.length === 0) {
          ElMessage.info(`在 ${startDate} 至 ${endDate} 期间未找到购买记录`)
        } else {
          ElMessage.success(`找到 ${searchResults.length} 条购买记录`)
        }

      } catch (error) {
        console.error('时间搜索失败:', error)
        ElMessage.error(`时间搜索失败: ${error.message}`)
        isSearchMode.value = false
        isTimeSearchMode.value = false
        allSearchResults.value = []
        buyData.value = []
        totalItems.value = 0
      } finally {
        loading.value = false
      }
    }

    const loadTimeRangeStats = async (startDate, endDate) => {
      try {
        console.log('正在获取时间范围统计...', { startDate, endDate })
        
        const response = await fetch(`/api/webBuyV1/getBuyStatsByTimeRange/${startDate}/${endDate}`, {
          method: 'GET',
          mode: 'cors',
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
          totalStats.value = {
            totalCount: statsData.total_count || 0,
            totalAmount: statsData.total_amount?.toFixed(2) || '0.00',
            avgPrice: statsData.avg_price?.toFixed(2) || '0.00',
            completedCount: statsData.completed_count || 0,
            cancelledCount: statsData.cancelled_count || 0,
            pendingCount: statsData.pending_count || 0
          }
          console.log('设置时间范围统计为:', totalStats.value)
        } else {
          console.error('时间范围统计API返回数据格式错误:', statsData)
        }
      } catch (error) {
        console.error('获取时间范围统计失败:', error)
        totalStats.value = {
          totalCount: 0,
          totalAmount: '0.00',
          avgPrice: '0.00',
          completedCount: 0,
          cancelledCount: 0,
          pendingCount: 0
        }
      }
    }

    // 加载武器类型数据
    const loadWeaponTypes = async () => {
      try {
        const response = await fetch(apiUrls.buyWeaponTypes())
        const result = await response.json()
        if (result.success) {
          weaponTypes.value = result.data
        }
      } catch (error) {
        console.error('获取武器类型失败:', error)
      }
    }

    // 加载磨损等级数据
    const loadFloatRanges = async () => {
      try {
        const response = await fetch(apiUrls.buyFloatRanges())
        const result = await response.json()
        if (result.success) {
          floatRanges.value = result.data
        }
      } catch (error) {
        console.error('获取磨损等级失败:', error)
      }
    }

    // 加载状态列表数据
    const loadStatusList = async () => {
      try {
        const response = await fetch(apiUrls.buyStatusList())
        const result = await response.json()
        if (result.success) {
          statusList.value = result.data
        }
      } catch (error) {
        console.error('获取状态列表失败:', error)
      }
    }
    
    // 加载指定状态对应的子状态列表
    const loadStatusSubList = async () => {
      try {
        const response = await fetch(apiUrls.buyStatusSubList(statusFilter.value))
        const result = await response.json()
        if (result && result.success && Array.isArray(result.data)) {
          statusSubList.value = result.data
        } else if (Array.isArray(result)) {
          // 兼容直接返回数组
          statusSubList.value = result
        } else {
          statusSubList.value = []
        }
      } catch (error) {
        console.error('获取子状态列表失败:', error)
        statusSubList.value = []
      }
    }

    // 类型筛选处理
    const handleTypeChange = async () => {
      if ((weaponTypeFilter.value && weaponTypeFilter.value.length > 0) || 
          (floatRangeFilter.value && floatRangeFilter.value.length > 0)) {
        await searchByTypeAndWear()
      } else {
        await loadBuyData()
      }
    }

    // 磨损等级筛选处理
    const handleWearChange = async () => {
      if ((weaponTypeFilter.value && weaponTypeFilter.value.length > 0) || 
          (floatRangeFilter.value && floatRangeFilter.value.length > 0)) {
        await searchByTypeAndWear()
      } else {
        await loadBuyData()
      }
    }

    // 按类型和磨损等级搜索
    const searchByTypeAndWear = async () => {
      if ((!weaponTypeFilter.value || weaponTypeFilter.value.length === 0) && 
          (!floatRangeFilter.value || floatRangeFilter.value.length === 0)) {
        return
      }

      loading.value = true
      try {
        const requestData = {
          weapon_types: weaponTypeFilter.value,
          float_ranges: floatRangeFilter.value,
          page: currentPage.value,
          page_size: pageSize.value
        }

        const response = await fetch(apiUrls.buySearchByTypeWear(), {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestData)
        })
        
        const result = await response.json()
        
        if (result.success) {
          // 格式化数据
          const formattedData = result.data.map((item, index) => {
            return {
              id: index + 1,
              order_id: item[0] || '',
              item_name: item[1] || '',
              weapon_name: item[2] || '',
              weapon_type: item[3] || '',
              weapon_float: item[4] || 0,
              float_range: item[5] || '',
              price: item[6] || 0,
              from: item[7] || '',
              order_time: item[8] || '',
              status: item[9] || '',
              status_sub: item[10] || '',
              steam_hash_name: item[11] || '',
          sticker: item[12] || null,
          pendant: item[13] || null,
          rename: item[14] || null
            }
          })
          
          buyData.value = formattedData
          totalItems.value = result.total
          
          // 获取筛选后的统计数据
          await loadStatsByTypeAndWear()
        } else {
          ElMessage.error(result.message || '搜索失败')
        }
      } catch (error) {
        console.error('按类型和磨损搜索失败:', error)
        ElMessage.error('搜索失败')
      } finally {
        loading.value = false
      }
    }

    // 获取按类型和磨损筛选的统计数据
    const loadStatsByTypeAndWear = async () => {
      try {
        const requestData = {
          weapon_types: weaponTypeFilter.value,
          float_ranges: floatRangeFilter.value
        }

        const response = await fetch(apiUrls.buyStatsByTypeWear(), {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestData)
        })
        
        const result = await response.json()
        
        if (result.success) {
          totalStats.value = {
            totalCount: result.data.totalCount,
            totalAmount: result.data.totalAmount.toFixed(2),
            avgPrice: result.data.avgPrice.toFixed(2),
            completedCount: result.data.completedCount,
            cancelledCount: result.data.cancelledCount,
            pendingCount: result.data.pendingCount
          }
        }
      } catch (error) {
        console.error('获取筛选统计数据失败:', error)
      }
    }

    const normalizeFilters = () => {
      if (statusFilter.value === 'all') statusFilter.value = ''
      if (statusSubFilter.value === 'all') statusSubFilter.value = ''
      if (sourceFilter.value === 'all') sourceFilter.value = ''
      if (dataUserFilter.value === 'all') dataUserFilter.value = ''
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
      return `/weapon_imgs/${imageName}`
    }

    // 获取组合后的商品标题
    const getItemTitle = (item) => {
      const parts = []
      if (item.weapon_name) {
        parts.push(item.weapon_name)
      }
      if (item.item_name) {
        parts.push(item.item_name)
      }
      // 组合格式: "AK-47 | 轨道 Mk01 （崭新出厂）"
      let title = parts.join(' | ')
      if (item.float_range) {
        title += ` （${item.float_range}）`
      }
      return title
    }

    // 检查是否有额外信息（印花、挂件、改名）
    const hasExtras = (item) => {
      return !!(item.sticker || item.pendant || item.rename)
    }

    // 解析印花数据 - 与Inventory页面逻辑一致
    const parseStickers = (stickerData) => {
      if (!stickerData) return []
      try {
        const parsed = typeof stickerData === 'string' ? JSON.parse(stickerData) : stickerData
        if (!Array.isArray(parsed)) return []
        
        // 返回贴纸数组，每个贴纸包含name和image
        return parsed.map(sticker => {
          const name = sticker.name || '未知贴纸'
          const hashName = sticker.hashName || sticker.steam_hash_name
          
          // 根据hashName生成图片URL，添加"Sticker___"前缀
          let imageUrl = null
          if (hashName) {
            const imageName = hashName
              .replace(/\s*\|\s*/g, '___')
              .replace(/\s/g, '_')
            imageUrl = `/weapon_imgs/Sticker___${imageName}.png`
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
        return parsed && typeof parsed === 'object' ? parsed : null
      } catch (e) {
        console.error('解析挂件数据失败:', e)
        return null
      }
    }


    // 获取挂件图片路径 - 使用hashName获取图片，与武器图片获取方式一致
    const getPendantImage = (pendant) => {
      if (!pendant) return null
      // 从pendant对象中获取hashName字段
      const hashName = pendant.hashName || pendant.steam_hash_name
      if (!hashName) return null
      // 使用与武器图片相同的转换方式
      const imageName = hashName
        .replace(/\s*\|\s*/g, '___')
        .replace(/\s/g, '_')
        + '.png'
      return `/weapon_imgs/${imageName}`
    }

    // 打开预览弹窗
    const openPreview = (item) => {
      previewItem.value = item
      previewVisible.value = true
    }

    onMounted(() => {
      normalizeFilters()
      loadBuyData()
      loadWeaponTypes()
      loadFloatRanges()
      loadStatusList()
      loadStatusSubList()
      loadDataUserList()
    })

    return {
      loading,
      buyData,
      filteredBuyData,
      totalStats,
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
      dataUserFilter,
      dateRange,
      isTimeSearchMode,
      currentPage,
      pageSize,
      totalItems,
      isSearchMode,
      allSearchResults,
      dataUserList,
      formatTime,
      getStatusType,
      getStatusColor,
      getStatusTextColor,
      handleSell,
      handleRent,
      handleViewDetails,
      handleSizeChange,
      handleCurrentChange,
      handleSearch,
      handleClearSearch,
      handleStatusChange,
      handleStatusSubChange,
      sourceFilter,
      sourceList,
      handleSourceChange,
      handleDataUserChange,
      sourceLabel,
      handleTypeChange,
      handleWearChange,
      removeWeaponType,
      removeFloatRange,
      handleAdvancedSearch,
      hasAdvancedFilters,
      handleDateRangeChange,
      handleTimeSearch,
      handleSortChange,
      sortOrder,
      getWeaponImage,
      getItemTitle,
      hasExtras,
      parseStickers,
      parsePendant,
      getPendantImage,
      previewVisible,
      previewItem,
      openPreview
    }
  }
}
</script>

<style scoped>
/* 武器图片单元格样式 */
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

.pagination {
  margin-top: clamp(1rem, 3vw, 1.25rem);
  display: flex;
  justify-content: center;
}

.pagination-top {
  margin-top: 0;
  margin-bottom: clamp(1rem, 3vw, 1.25rem);
}

@media (max-width: 768px) {
  .search-input {
    min-width: unset;
    width: 100%;
    max-width: none;
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

:deep(.el-pagination .el-select .el-input .el-input__inner) {
  background-color: #484848 !important;
  color: #fff;
}

:deep(.el-pagination .el-input .el-input__inner) {
  background-color: #484848 !important;
  color: #fff;
}

:deep(.el-select-dropdown) {
  background-color: #484848 !important;
}

:deep(.el-select-dropdown .el-select-dropdown__item) {
  background-color: #484848 !important;
  color: #3b3b3b;
}

:deep(.el-select-dropdown .el-select-dropdown__item:hover) {
  background-color: #3b3b3b !important;
}

:deep(.el-table) {
  background-color: transparent;
  color: #fff;
  font-size: clamp(0.75rem, 1.2vw, 0.875rem);
}

/* 确保表格行有足够的高度显示完整图片 */
:deep(.el-table .el-table__row) {
  min-height: 90px;
}

/* 确保图片列单元格有足够空间 */
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

:deep(.el-table thead th) {
  background-color: var(--bg-tertiary) !important;
}

:deep(.el-table .el-table__header th) {
  background-color: var(--bg-tertiary) !important;
}

:deep(.el-table td) {
  background-color: transparent !important;
  border-bottom: 1px solid var(--border-default);
  color: #fff;
  padding: 0.375rem 2px;
  overflow: visible;
}

/* 确保图片列有足够的空间显示完整图片 */
:deep(.el-table td:first-child) {
  overflow: visible !important;
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

/* 日期选择器样式 */
:deep(.el-date-editor .el-input__inner) {
  background-color: #1a1a1a !important;
  border-color: #333 !important;
  color: #fff !important;
}

:deep(.el-date-editor .el-input__prefix) {
  color: #ccc;
}

:deep(.el-date-editor .el-input__suffix) {
  color: #ccc;
}

/* 日历面板整体样式 - 增强优先级 */
:deep(.el-picker-panel),
:deep(.el-date-picker),
:deep(.el-date-range-picker) {
  background-color: #1a1a1a !important;
  border: 1px solid #333 !important;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.3) !important;
}

:deep(.el-popper.is-pure) {
  background-color: #1a1a1a !important;
  border: 1px solid #333 !important;
}

:deep(.el-popper.is-pure .el-popper__arrow::before) {
  background-color: #1a1a1a !important;
  border: 1px solid #333 !important;
}

:deep(.el-picker-panel__content) {
  background-color: #1a1a1a !important;
  color: #fff;
}

/* 日历头部 */
:deep(.el-date-picker__header) {
  background-color: #1a1a1a !important;
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
  background-color: #1a1a1a !important;
  color: #ccc !important;
  border-bottom: 1px solid #333;
}

/* 日期单元格 */
:deep(.el-date-table td) {
  color: #fff !important;
  background-color: #1a1a1a !important;
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
  background-color: #1a1a1a !important;
  color: #666 !important;
}

:deep(.el-date-table td.prev-month),
:deep(.el-date-table td.next-month) {
  color: #666 !important;
}

/* 范围选择 */
:deep(.el-date-table td.in-range) {
  background-color: #2a2a2a !important;
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
  background-color: #1a1a1a !important;
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
  background-color: #1a1a1a !important;
}

:deep(.el-date-range-picker__content.is-left) {
  border-right: 1px solid #333;
}

/* 月份/年份选择面板 */
:deep(.el-month-table td) {
  color: #fff !important;
  background-color: #1a1a1a !important;
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
  background-color: #1a1a1a !important;
}

:deep(.el-year-table td:hover) {
  background-color: #333 !important;
}

:deep(.el-year-table td.current:not(.disabled)) {
  background-color: #409eff !important;
  color: #fff !important;
}

/* 全局日历面板样式覆盖 - 最高优先级 */
:deep(.el-picker-panel.el-date-picker),
:deep(.el-picker-panel.el-date-range-picker),
:deep(.el-picker-panel.el-picker-panel),
:deep(div.el-picker-panel) {
  background: #1a1a1a !important;
  background-color: #1a1a1a !important;
  border-color: #333 !important;
}

:deep(.el-picker-panel .el-picker-panel__body),
:deep(.el-picker-panel .el-picker-panel__content),
:deep(.el-date-picker__time-header),
:deep(.el-date-picker .el-picker-panel__content) {
  background: #1a1a1a !important;
  background-color: #1a1a1a !important;
}

/* 确保弹出层容器也是深色 */
.el-popper,
.el-picker-panel {
  background: #1a1a1a !important;
}

/* 额外的全局样式覆盖 */
:deep(.el-picker-panel),
:deep(.el-picker-panel *),
:deep(.el-date-picker),
:deep(.el-date-range-picker) {
  background-color: #1a1a1a !important;
}

:deep(.el-date-table th),
:deep(.el-date-table td),
:deep(.el-month-table td),
:deep(.el-year-table td) {
  background-color: #1a1a1a !important;
}

.action-buttons {
  display: flex;
  gap: 0.25rem;
  flex-wrap: wrap;
  justify-content: center;
}

:deep(.el-button) {
  font-size: clamp(0.625rem, 1vw, 0.75rem);
  padding: clamp(0.375rem, 1vw, 0.5rem) clamp(0.5rem, 1.5vw, 0.75rem);
}

:deep(.el-table) {
  min-width: 1000px;
}

:deep(.el-table .el-table__cell) {
  
  word-break: break-word;
}

@media (max-width: 1200px) {
  :deep(.el-table) {
    min-width: 900px;
  }
}

@media (max-width: 768px) {
  .search-input {
    min-width: unset;
    width: 100%;
    max-width: none;
  }
  
  .status-select {
    min-width: unset;
    width: 100%;
    max-width: none;
  }
  
  :deep(.el-table) {
    font-size: 0.75rem;
    min-width: 800px;
  }
  
  :deep(.el-table th),
  :deep(.el-table td) {
    padding: 0.5rem 2px;
  }
  
  :deep(.el-button) {
    font-size: 0.625rem;
    padding: 0.25rem 0.5rem;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .action-buttons .el-button {
    width: 100%;
    min-width: 0;
  }
}

@media (max-width: 480px) {
  :deep(.el-table) {
    min-width: 700px;
  }
  
  :deep(.el-table th),
  :deep(.el-table td) {
    padding: 0.375rem 2px;
    font-size: 0.625rem;
  }
  
  :deep(.el-button) {
    font-size: 0.5rem;
    padding: 0.125rem 0.25rem;
  }
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
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
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

@media (max-width: 768px) {
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
}

/* 磨损值显示条样式 */
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

/* CS2 标准磨损等级颜色 */
.float-segment.fn {
  flex: 7;  /* 0.00 - 0.07 */
  background: linear-gradient(to right, #4CAF50, #66BB6A);
}

.float-segment.mw {
  flex: 8;  /* 0.07 - 0.15 */
  background: linear-gradient(to right, #8BC34A, #9CCC65);
}

.float-segment.ft {
  flex: 23; /* 0.15 - 0.38 */
  background: linear-gradient(to right, #FFC107, #FFB300);
}

.float-segment.ww {
  flex: 7;  /* 0.38 - 0.45 */
  background: linear-gradient(to right, #FF9800, #FB8C00);
}

.float-segment.bs {
  flex: 55; /* 0.45 - 1.00 */
  background: linear-gradient(to right, #F44336, #E53935);
}

/* 磨损值指针 */
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

/* 商品名称单元格样式 */
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
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
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

/* 改名文本样式 */
.rename-text {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  color: #999;
}

.rename-label {
  color: #666;
}

.rename-value {
  color: #4CAF50;
  font-weight: 500;
}

/* 预览弹窗样式 */
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

.preview-left-section {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

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

/* 预览弹窗中的贴纸列表 */
.preview-sticker-list-section {
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.preview-sticker-list-title {
  color: #fff;
  font-size: 1rem;
  font-weight: bold;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

.preview-sticker-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  height: auto;
}

.preview-sticker-list-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.1);
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
  flex-shrink: 0;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: transform 0.2s ease;
  cursor: pointer;
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
  font-size: 1.2rem;
  font-weight: bold;
}

.preview-sticker-list-name {
  color: #fff;
  font-size: 0.9rem;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 预览弹窗中的挂件信息 */
.preview-pendant-section {
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.preview-pendant-title {
  color: #fff;
  font-size: 1rem;
  font-weight: bold;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

.preview-pendant-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  height: auto;
}

.preview-pendant-list-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.1);
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
  flex-shrink: 0;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid rgba(255, 215, 0, 0.2);
  transition: transform 0.2s ease;
  cursor: pointer;
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
  color: #ffd700;
  font-size: 1.5rem;
  font-weight: bold;
}

.preview-pendant-list-name {
  color: #fff;
  font-size: 0.9rem;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.preview-info-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* 改名标签 */
.preview-rename {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: rgba(64, 158, 255, 0.1);
  border: 1px solid rgba(64, 158, 255, 0.3);
  border-radius: 6px;
}

.preview-rename-icon {
  font-size: 1.2rem;
}

.preview-rename-text {
  color: #fff;
  font-size: 1rem;
  font-weight: 500;
}

/* 磨损信息 */
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

/* 价格信息 */
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

/* 响应式调整 */
@media (max-width: 768px) {
  .preview-dialog {
    width: 95% !important;
  }

  .preview-main-layout {
    flex-direction: column;
  }

  .preview-image-section {
    height: 200px;
  }

  .preview-pendant-item {
    width: 50px;
    height: 50px;
  }

  .preview-price-row {
    flex-direction: column;
    gap: 0.5rem;
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

/* 修复加载遮罩白色背景问题 */
.el-loading-mask {
  background-color: rgba(26, 26, 26, 0.8) !important;
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