<template>
  <div>
    <!-- 二级导航 -->
    <div class="sub-nav card">
      <el-tabs v-model="activeTab" @tab-click="handleTabClick">
        <el-tab-pane label="悠悠有品" name="yyyp"></el-tab-pane>
        <!-- 可以在这里添加更多二级页面 -->
      </el-tabs>
    </div>

    <!-- 悠悠有品子页面 -->
    <div v-if="activeTab === 'yyyp'">
      <!-- 搜索与统计数据 -->
      <div class="stats-summary">
        <div class="card">
          <!-- 搜索栏 -->
          <div class="search-section">
            <div class="flex flex-wrap gap-4 items-center">
              <el-input
                v-model="searchText"
                placeholder="搜索饰品名称..."
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
              <el-select v-model="statusFilter" placeholder="选择状态" class="status-select" @change="handleStatusChange">
                <el-option label="全部" value="all" />
                <el-option v-for="status in statusList" :key="status" :label="status" :value="status" />
              </el-select>
              <el-select 
                v-model="weaponTypeFilter" 
                placeholder="选择武器类型（可多选）" 
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
                placeholder="选择磨损等级（可多选）" 
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
              <el-button type="success" @click="handleTimeSearch" :loading="loading">
                按时间搜索
              </el-button>
              <el-button type="warning" @click="handleAdvancedSearch" :loading="loading" v-if="hasAdvancedFilters">
                高级搜索
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
              <h3>全部出租统计</h3>
              <div class="stats-grid-3x2">
                <div class="stat-item">
                  <span class="stat-label">总出租数量:</span>
                  <span class="stat-value">{{ allDataStats.totalCount }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">总出租收入:</span>
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
        <el-table
          :data="filteredLentData"
          v-loading="loading"
          element-loading-text="加载中..."
          style="width: 100%"
          :row-style="{ backgroundColor: 'transparent' }"
          :header-row-style="{ backgroundColor: 'var(--bg-tertiary)' }"
        >
          <el-table-column prop="ID" label="订单ID" width="180" show-overflow-tooltip />
          <el-table-column prop="weapon_float" label="Float" min-width="160" show-overflow-tooltip>
            <template #default="scope">
              {{ scope.row.weapon_float || '' }}
            </template>
          </el-table-column>
          <el-table-column prop="weapon_type" label="武器类型" width="120" />
          <el-table-column prop="weapon_name" label="武器名称" width="150" />
          <el-table-column prop="item_name" label="饰品名称" min-width="200" show-overflow-tooltip />
          <el-table-column prop="float_range" label="磨损" min-width="80" />
          <el-table-column prop="price" label="租金" min-width="100">
            <template #default="scope">
              ¥{{ scope.row.price }}
            </template>
          </el-table-column>
          <el-table-column prop="lenter_name" label="承租人" width="100" show-overflow-tooltip />
          <el-table-column prop="lean_start_time" label="开始时间" min-width="140">
            <template #default="scope">
              {{ formatTime(scope.row.lean_start_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="lean_end_time" label="结束时间" min-width="140">
            <template #default="scope">
              {{ formatTime(scope.row.lean_end_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="total_Lease_Days" label="租期" min-width="80">
            <template #default="scope">
              {{ scope.row.total_Lease_Days }} 天
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" min-width="80">
            <template #default="scope">
              <el-tooltip 
                :content="scope.row.status_sub || scope.row.status" 
                placement="top"
                :disabled="!scope.row.status_sub"
              >
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
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { apiUrls } from '@/config/api'

export default {
  name: 'Lent',
  setup() {
    const loading = ref(false)
    const lentData = ref([])
    const searchText = ref('')
    const statusFilter = ref('all')
    const weaponTypeFilter = ref([])
    const floatRangeFilter = ref([])
    const weaponTypes = ref([])
    const floatRanges = ref([])
    const statusList = ref([])
    const currentPage = ref(1)
    const pageSize = ref(20)
    const totalItems = ref(0)
    const dateRange = ref(null)
    const isTimeSearchMode = ref(false)
    
    // 高级搜索相关
    const hasAdvancedFilters = computed(() => {
      return (searchText.value && searchText.value.trim()) || 
             (statusFilter.value && statusFilter.value !== 'all') ||
             (weaponTypeFilter.value && weaponTypeFilter.value.length > 0) ||
             (floatRangeFilter.value && floatRangeFilter.value.length > 0) ||
             (dateRange.value && dateRange.value.length === 2)
    })
    const activeTab = ref('yyyp')

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

    // 当前页面统计（基于当前显示的数据计算）
    const currentPageStats = computed(() => {
      const currentData = lentData.value
      const totalCount = currentData.length
      // 修改：总收入 = 租金 * 天数
      const totalAmount = currentData.reduce((sum, item) => {
        const price = item.price || 0
        const days = item.total_Lease_Days || 0
        return sum + (price * days)
      }, 0).toFixed(2)
      const avgPrice = totalCount > 0 ? (totalAmount / totalCount).toFixed(2) : '0.00'
      const totalLeaseDays = currentData.reduce((sum, item) => sum + (item.total_Lease_Days || 0), 0)
      const avgLeaseDays = totalCount > 0 ? (totalLeaseDays / totalCount).toFixed(1) : '0.0'
      const rentingCount = currentData.filter(item => item.status === '租赁中').length
      const completedCount = currentData.filter(item => item.status === '已完成').length
      const cancelledCount = currentData.filter(item => item.status === '已取消').length

      return {
        totalCount,
        totalAmount,
        avgPrice,
        totalLeaseDays,
        avgLeaseDays,
        rentingCount,
        completedCount,
        cancelledCount
      }
    })

    // 存储所有搜索结果，用于前端分页
    const allSearchResults = ref([])
    const isSearchMode = ref(false)

    const filteredLentData = computed(() => {
      // 如果是搜索模式，进行前端分页
      if (isSearchMode.value && allSearchResults.value.length > 0) {
        let filtered = allSearchResults.value
        
        // 状态筛选
        if (statusFilter.value !== 'all') {
          filtered = filtered.filter(item => item.status === statusFilter.value)
        }
        
        // 更新总数以反映筛选后的结果
        totalItems.value = filtered.length
        
        // 前端分页
        const start = (currentPage.value - 1) * pageSize.value
        const end = start + pageSize.value
        return filtered.slice(start, end)
      }

      // 非搜索模式直接返回服务器数据（已经分页）
      return lentData.value
    })

    const formatTime = (time) => {
      if (!time) return ''
      return new Date(time).toLocaleString('zh-CN')
    }

    const getStatusType = (status) => {
      const statusMap = {
        '已完成': 'success',
        '租赁中': 'warning',
        '已取消': 'danger'
      }
      return statusMap[status] || 'info'
    }

    const getStatusColor = (status) => {
      const colorMap = {
        '已完成': '#52c41a',    // 更鲜明的绿色
        '租赁中': '#faad14',    // 更鲜明的橙色
        '已取消': '#ff4d4f',    // 更鲜明的红色
        '进行中': '#1890ff'     // 蓝色
      }
      return colorMap[status] || '#909399'
    }

    const getStatusTextColor = (status) => {
      return '#FFFFFF'
    }

    const searchByName = async (itemName) => {
      loading.value = true
      try {
        console.log('正在搜索出租武器:', itemName)
        
        const response = await fetch(`/api/webLentV1/selectLentWeaponName/${encodeURIComponent(itemName)}`, {
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
          lenter_name: item[7] || '',
          status: item[8] || '',
          last_status: item[9] || '',
          from: item[10] || '',
          lean_start_time: item[11] || '',
          lean_end_time: item[12] || '',
          total_Lease_Days: item[13] || 0,
          max_Lease_Days: item[14] || 0
        }))
        
        // 进入搜索模式
        isSearchMode.value = true
        allSearchResults.value = searchResults
        lentData.value = [] // 清空普通数据
        totalItems.value = rawData.length
        currentPage.value = 1
        
        if (searchResults.length === 0) {
          ElMessage.info(`未找到包含"${itemName}"的武器`)
        } else {
          ElMessage.success(`找到 ${searchResults.length} 条相关记录`)
        }
        
      } catch (error) {
        console.error('搜索失败:', error)
        ElMessage.error(`搜索失败: ${error.message}`)
        lentData.value = []
        totalItems.value = 0
      } finally {
        loading.value = false
      }
    }

    const loadAllDataStats = async () => {
      try {
        console.log('正在加载全部数据统计...')
        
        const response = await fetch('/api/webLentV1/getLentStats', {
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
        console.log('全部数据统计:', statsData)
        
        allDataStats.value = {
          totalCount: statsData.total_count || 0,
          totalAmount: statsData.total_amount || '0.00',
          avgPrice: statsData.avg_price || '0.00',
          totalLeaseDays: statsData.total_lease_days || 0,
          avgLeaseDays: statsData.avg_lease_days || '0.0',
          rentingCount: statsData.renting_count || 0,
          completedCount: statsData.completed_count || 0,
          cancelledCount: statsData.cancelled_count || 0
        }
        
        console.log('全部数据统计加载完成')
        
      } catch (error) {
        console.error('加载全部数据统计失败:', error)
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

    const loadTotalCount = async () => {
      try {
        console.log('正在获取总数...')
        const response = await fetch('/api/webLentV1/countLentNumber', {
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
        totalItems.value = lentData.value.length > 0 ? 1000 : 0
      }
    }

    const loadLentData = async () => {
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
        
        // 根据状态筛选选择不同的API
        let apiUrl = `/api/webLentV1/getLentData/${min}/${max}`
        if (statusFilter.value !== 'all') {
          apiUrl = `/api/webLentV1/getLentDataByStatus/${statusFilter.value}/${min}/${max}`
        }
        
        const response = await fetch(apiUrl, {
          method: 'GET',
          mode: 'cors',
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
        lentData.value = rawData.map((item, index) => {
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
            lenter_name: item[7] || '',
            status: item[8] || '',
            last_status: item[9] || '',
            from: item[10] || '',
            lean_start_time: item[11] || '',
            lean_end_time: item[12] || '',
            total_Lease_Days: item[13] || 0,
            max_Lease_Days: item[14] || 0
          }
        }).filter(item => item !== null)
        
        console.log('转换后的数据:', lentData.value)
        
        // 获取总数（只在第一页或总数为0时调用）
        if (currentPage.value === 1 || totalItems.value === 0) {
          await loadTotalCount()
        }
        
        if (lentData.value.length === 0) {
          ElMessage.info('暂无出租数据')
        } else {
          ElMessage.success(`加载成功，共 ${lentData.value.length} 条记录`)
        }
        
      } catch (error) {
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
        lentData.value = []
        totalItems.value = 0
      } finally {
        loading.value = false
      }
    }

    const handleTabClick = (tab) => {
      console.log('切换到标签页:', tab.name)
      // 可以根据不同的tab加载不同的数据
      if (tab.name === 'yyyp') {
        loadLentData()
      }
    }

    const handleSizeChange = (val) => {
      pageSize.value = val
      currentPage.value = 1
      loadLentData()
    }

    const handleCurrentChange = (val) => {
      currentPage.value = val
      loadLentData()
    }

    const handleSearch = () => {
      currentPage.value = 1
      loadLentData()
    }

    const handleClearSearch = () => {
      searchText.value = ''
      statusFilter.value = 'all'
      weaponTypeFilter.value = []
      floatRangeFilter.value = []
      dateRange.value = null
      currentPage.value = 1
      isSearchMode.value = false
      isTimeSearchMode.value = false
      allSearchResults.value = []
      loadLentData()
    }

    const handleStatusChange = () => {
      currentPage.value = 1
      
      // 如果是搜索模式，只需要更新分页，不需要重新加载数据
      if (isSearchMode.value && searchText.value.trim()) {
        // 状态变更会自动通过computed属性重新计算filteredLentData
        return
      } else {
        // 非搜索模式，重新加载数据
        loadLentData()
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
        // 构建高级搜索参数
        const searchParams = {
          searchText: searchText.value?.trim() || '',
          statusFilter: statusFilter.value !== 'all' ? statusFilter.value : '',
          weaponType: weaponTypeFilter.value || '',
          floatRange: floatRangeFilter.value || '',
          dateRange: dateRange.value || null,
          page: currentPage.value,
          pageSize: pageSize.value
        }
        
        // 如果有类型或磨损筛选，优先使用类型磨损搜索
        if (searchParams.weaponType || searchParams.floatRange) {
          await searchByTypeAndWear()
        } else if (searchParams.dateRange) {
          await handleTimeSearch()
        } else {
          await loadLentData()
        }
        
        ElMessage.success('高级搜索完成')
      } catch (error) {
        console.error('高级搜索失败:', error)
        ElMessage.error('高级搜索失败')
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
        
        const response = await fetch(`/api/webLentV1/searchLentByTimeRange/${startDate}/${endDate}`, {
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
          ID: item[0] || '',
          weapon_name: item[1] || '',
          weapon_type: item[2] || '',
          item_name: item[3] || '', 
          weapon_float: item[4] || 0,
          float_range: item[5] || '',
          price: item[6] || 0,
          lenter_name: item[7] || '',
          status: item[8] || '',
          last_status: item[9] || '',
          from: item[10] || '',
          lean_start_time: item[11] || '',
          lean_end_time: item[12] || '',
          total_Lease_Days: item[13] || 0,
          max_Lease_Days: item[14] || 0
        }))
        
        // 进入时间搜索模式
        isTimeSearchMode.value = true
        isSearchMode.value = true
        allSearchResults.value = searchResults
        lentData.value = [] // 清空普通数据
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
        console.error('时间搜索失败:', error)
        ElMessage.error(`时间搜索失败: ${error.message}`)
        isSearchMode.value = false
        isTimeSearchMode.value = false
        allSearchResults.value = []
        lentData.value = []
        totalItems.value = 0
      } finally {
        loading.value = false
      }
    }

    const loadTimeRangeStats = async (startDate, endDate) => {
      try {
        console.log('正在获取时间范围统计...', { startDate, endDate })
        
        const response = await fetch(`/api/webLentV1/getLentStatsByTimeRange/${startDate}/${endDate}`, {
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

    // 加载武器类型数据
    const loadWeaponTypes = async () => {
      try {
        const response = await fetch(apiUrls.lentWeaponTypes())
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
        const response = await fetch(apiUrls.lentFloatRanges())
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
        const response = await fetch(apiUrls.lentStatusList())
        const result = await response.json()
        if (result.success) {
          statusList.value = result.data
        }
      } catch (error) {
        console.error('获取状态列表失败:', error)
      }
    }

    // 类型筛选处理
    const handleTypeChange = async () => {
      if (weaponTypeFilter.value && weaponTypeFilter.value.length > 0 || 
          floatRangeFilter.value && floatRangeFilter.value.length > 0) {
        await searchByTypeAndWear()
      } else {
        await loadLentData()
      }
    }

    // 磨损等级筛选处理
    const handleWearChange = async () => {
      if (weaponTypeFilter.value && weaponTypeFilter.value.length > 0 || 
          floatRangeFilter.value && floatRangeFilter.value.length > 0) {
        await searchByTypeAndWear()
      } else {
        await loadLentData()
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

    // 按类型和磨损等级搜索
    const searchByTypeAndWear = async () => {
      if ((!weaponTypeFilter.value || weaponTypeFilter.value.length === 0) && 
          (!floatRangeFilter.value || floatRangeFilter.value.length === 0)) {
        return
      }

      loading.value = true
      currentPage.value = 1
      try {
        const requestData = {
          weapon_type: weaponTypeFilter.value || [],
          float_range: floatRangeFilter.value || [],
          page: currentPage.value,
          page_size: pageSize.value
        }

        const response = await fetch(apiUrls.lentSearchByTypeWear(), {
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
              ID: item[0] || '',
              weapon_name: item[1] || '',
              item_name: item[2] || '',
              weapon_float: item[3] || 0,
              float_range: item[4] || '',
              unit_price: item[5] || 0,
              lease_day: item[6] || 0,
              status: item[7] || '',
              create_time: item[8] || '',
              leaser_name: item[9] || '',
              deposit: item[10] || 0
            }
          })
          
          lentData.value = formattedData
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
          weapon_type: weaponTypeFilter.value,
          float_range: floatRangeFilter.value
        }

        const response = await fetch(apiUrls.lentStatsByTypeWear(), {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestData)
        })
        
        const result = await response.json()
        
        if (result.success) {
          allDataStats.value = {
            totalCount: result.data.totalCount,
            totalAmount: result.data.totalAmount.toFixed(2),
            avgPrice: result.data.avgPrice.toFixed(2),
            totalLeaseDays: result.data.totalLeaseDays,
            avgLeaseDays: result.data.avgLeaseDays.toFixed(2),
            rentingCount: result.data.rentingCount
          }
        }
      } catch (error) {
        console.error('获取筛选统计数据失败:', error)
      }
    }

    onMounted(() => {
      loadLentData()
      loadAllDataStats()
      loadWeaponTypes()
      loadFloatRanges()
      loadStatusList()
    })

    return {
      loading,
      lentData,
      filteredLentData,
      allDataStats,
      currentPageStats,
      searchText,
      statusFilter,
      weaponTypeFilter,
      floatRangeFilter,
      weaponTypes,
      floatRanges,
      statusList,
      dateRange,
      isTimeSearchMode,
      currentPage,
      pageSize,
      totalItems,
      activeTab,
      isSearchMode,
      allSearchResults,
      formatTime,
      getStatusType,
      getStatusColor,
      getStatusTextColor,
      handleTabClick,
      handleSizeChange,
      handleCurrentChange,
      handleSearch,
      handleClearSearch,
      handleStatusChange,
      handleTypeChange,
      handleWearChange,
      removeWeaponType,
      removeFloatRange,
      handleAdvancedSearch,
      hasAdvancedFilters,
      handleDateRangeChange,
      handleTimeSearch
    }
  }
}
</script>

<style scoped>
.sub-nav {
  margin-bottom: clamp(1rem, 3vw, 1.25rem);
}

.search-input {
  min-width: 200px;
  flex: 1;
  max-width: 300px;
}

.status-select {
  min-width: 120px;
  max-width: 150px;
}

.type-select {
  min-width: 140px;
  max-width: 160px;
}

.wear-select {
  min-width: 140px;
  max-width: 160px;
}

.date-picker {
  min-width: 240px;
  max-width: 280px;
}

.table-container {
  margin-bottom: clamp(1rem, 3vw, 1.25rem);
}

.pagination {
  margin-top: clamp(1rem, 3vw, 1.25rem);
  display: flex;
  justify-content: center;
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
  
  .status-select {
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