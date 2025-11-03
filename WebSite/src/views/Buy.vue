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
        <el-table-column prop="order_id" label="订单ID" width="180" show-overflow-tooltip align="left" />
        <el-table-column prop="weapon_type" label="类型" width="120" />
        <el-table-column prop="item_name" label="饰品名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="weapon_name" label="武器名称" min-width="100" />
        <el-table-column prop="weapon_float" label="Float" min-width="180" align="left">
          <template #default="scope">
            {{ scope.row.weapon_float }}
          </template>
        </el-table-column>
        <el-table-column prop="float_range" label="磨损等级" min-width="100" />
        <el-table-column prop="price" label="购入价格" min-width="100">
          <template #default="scope">
            ¥{{ scope.row.price }}
          </template>
        </el-table-column>
        <el-table-column prop="from" label="来源" min-width="80" />
        <el-table-column prop="order_time" label="购入时间" min-width="160">
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
    const totalStats = ref({
      totalCount: 0,
      totalAmount: '0.00',
      avgPrice: '0.00',
      completedCount: 0,
      cancelledCount: 0,
      pendingCount: 0
    })

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

    // 存储所有搜索结果，用于前端分页
    const allSearchResults = ref([])
    const isSearchMode = ref(false)

    const filteredBuyData = computed(() => {
      let filtered = buyData.value

      // 如果是搜索模式，进行前端分页
      if (isSearchMode.value && allSearchResults.value.length > 0) {
        filtered = allSearchResults.value
        
        // 状态筛选
        if (statusFilter.value !== 'all') {
          filtered = filtered.filter(item => item.status === statusFilter.value)
        }
        
        // 前端分页
        const start = (currentPage.value - 1) * pageSize.value
        const end = start + pageSize.value
        return filtered.slice(start, end)
      }

      // 非搜索模式的筛选（原有逻辑）
      if (statusFilter.value !== 'all') {
        filtered = filtered.filter(item => item.status === statusFilter.value)
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
        '待收货': 'info'
      }
      return statusMap[status] || 'info'
    }

    const getStatusColor = (status) => {
      const colorMap = {
        '已完成': '#52c41a',    // 更鲜明的绿色
        '已取消': '#ff4d4f',    // 更鲜明的红色
        '待收货': '#1890ff'     // 蓝色
      }
      return colorMap[status] || '#909399'
    }

    const getStatusTextColor = (status) => {
      // 对于所有状态都使用白色文字以确保对比度
      return '#FFFFFF'
    }

    const loadTotalStats = async (searchKeyword = null, filterStatus = null) => {
      try {
        console.log('正在获取总数统计...', { searchKeyword, filterStatus })
        
        let apiUrl = '/api/webBuyV1/getBuyStats'
        
        // 根据传入的参数或当前状态选择不同的API
        const keyword = searchKeyword || searchText.value.trim()
        const status = filterStatus || statusFilter.value
        
        if (keyword) {
          apiUrl = `/api/webBuyV1/getBuyStatsBySearch/${encodeURIComponent(keyword)}`
          console.log('使用搜索统计API:', apiUrl)
        } else if (status !== 'all') {
          apiUrl = `/api/webBuyV1/getBuyStatsByStatus/${status}`
          console.log('使用状态筛选统计API:', apiUrl)
        } else {
          console.log('使用全部数据统计API:', apiUrl)
        }
        
        const response = await fetch(apiUrl, {
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
        console.log('获取到的总统计:', statsData, 'API:', apiUrl)
        
        if (statsData) {
          totalStats.value = {
            totalCount: statsData.total_count || 0,
            totalAmount: statsData.total_amount?.toFixed(2) || '0.00',
            avgPrice: statsData.avg_price?.toFixed(2) || '0.00',
            completedCount: statsData.completed_count || 0,
            cancelledCount: statsData.cancelled_count || 0,
            pendingCount: statsData.pending_count || 0
          }
          totalItems.value = statsData.total_count || 0
          console.log('设置总统计为:', totalStats.value)
        } else {
          console.error('总统计API返回数据格式错误:', statsData)
        }
      } catch (error) {
        console.error('获取总统计失败:', error)
        // 如果获取总统计失败，重置统计数据
        totalStats.value = {
          totalCount: 0,
          totalAmount: '0.00',
          avgPrice: '0.00',
          completedCount: 0,
          cancelledCount: 0,
          pendingCount: 0
        }
        totalItems.value = 0
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
        
        const response = await fetch(`/api/webBuyV1/selectBuyWeaponName/${encodeURIComponent(itemName)}`, {
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
          status_sub: item[10] || ''
        }))
        
        // 进入搜索模式
        isSearchMode.value = true
        allSearchResults.value = searchResults
        buyData.value = [] // 清空普通数据
        totalItems.value = rawData.length
        currentPage.value = 1
        
        // 获取搜索结果的统计
        await loadTotalStats(itemName)
        
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
        
        // 根据状态筛选选择不同的API
        let apiUrl = `/api/webBuyV1/getBuyData/${min}/${max}`
        if (statusFilter.value !== 'all') {
          apiUrl = `/api/webBuyV1/getBuyDataByStatus/${statusFilter.value}/${min}/${max}`
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
        buyData.value = rawData.map((item, index) => {
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
            status_sub: item[10] || ''   // 状态详情
          }
        }).filter(item => item !== null)
        
        console.log('转换后的数据:', buyData.value)
        
        // 获取总数统计
        await loadTotalStats(null, statusFilter.value)
        
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
      currentPage.value = 1
      loadBuyData()
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
      loadBuyData()
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
        if ((weaponTypeFilter.value && weaponTypeFilter.value.length > 0) || 
            (floatRangeFilter.value && floatRangeFilter.value.length > 0)) {
          await searchByTypeAndWear()
        } else if (searchParams.dateRange) {
          await handleTimeSearch()
        } else {
          await loadBuyData()
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
          status_sub: item[10] || ''
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
              seller_name: item[11] || ''
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

    onMounted(() => {
      loadBuyData()
      loadWeaponTypes()
      loadFloatRanges()
      loadStatusList()
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
      dateRange,
      isTimeSearchMode,
      currentPage,
      pageSize,
      totalItems,
      isSearchMode,
      allSearchResults,
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
  min-width: 180px;
  max-width: 260px;
}

.wear-select {
  min-width: 180px;
  max-width: 260px;
}

.date-picker {
  min-width: 240px;
  max-width: 280px;
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

:deep(.el-table th) {
  background-color: var(--bg-tertiary) !important;
  color: #fff;
  border-bottom: 1px solid var(--border-default);
  padding: clamp(0.5rem, 1.5vw, 0.75rem);
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
  padding: clamp(0.5rem, 1.5vw, 0.75rem);
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
    padding: 0.5rem 0.25rem;
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
    padding: 0.375rem 0.125rem;
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