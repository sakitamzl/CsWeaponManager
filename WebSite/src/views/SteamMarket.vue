<template>
  <div>
    <!-- Tab切换 -->
    <div class="tab-container">
      <el-tabs v-model="activeTab" @tab-click="handleTabClick" class="steam-tabs">
        <el-tab-pane label="Steam购买" name="buy">
          <!-- Steam购买内容 -->
          <div class="filters card">
            <div class="flex flex-wrap gap-4 items-center">
              <el-input
                v-model="buySearchText"
                placeholder="搜索饰品名称..."
                prefix-icon="Search"
                class="search-input"
                @keyup.enter="handleBuySearch"
                @clear="handleBuyClearSearch"
                clearable
              />
              <el-button type="primary" @click="handleBuySearch" :loading="buyLoading">
                搜索
              </el-button>
              <el-button @click="handleBuyClearSearch" :disabled="buyLoading">
                重置
              </el-button>
              <el-select 
                v-model="buyGameNameFilter" 
                placeholder="选择游戏" 
                class="game-select" 
                @change="handleBuyGameChange"
                clearable
              >
                <el-option label="全部游戏" value="all" />
                <el-option v-for="game in buyGameNamesList" :key="game" :label="game" :value="game" />
              </el-select>
              <el-date-picker
                v-model="buyDateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                class="date-picker"
                @change="handleBuyDateRangeChange"
                clearable
              />
              <el-button type="success" @click="handleBuyTimeSearch" :loading="buyLoading">
                按时间搜索
              </el-button>
            </div>
          </div>

          <!-- Steam购买统计数据 -->
          <div class="stats-summary">
            <div class="card">
              <div class="stats-container">
                <div class="stats-section">
                  <h3>Steam购买统计</h3>
                  <div class="grid grid-3">
                    <div class="stat-item">
                      <span class="stat-label">总购买数量:</span>
                      <span class="stat-value">{{ buyTotalStats.totalCount }} 件</span>
                    </div>
                    <div class="stat-item">
                      <span class="stat-label">总购买金额:</span>
                      <span class="stat-value">¥{{ buyTotalStats.totalAmount }}</span>
                    </div>
                    <div class="stat-item">
                      <span class="stat-label">平均购买价格:</span>
                      <span class="stat-value">¥{{ buyTotalStats.avgPrice }}</span>
                    </div>
                  </div>
                </div>
                
                <div class="stats-divider"></div>
                
                <div class="stats-section">
                  <h3>当前页面统计</h3>
                  <div class="grid grid-3">
                    <div class="stat-item">
                      <span class="stat-label">页面数量:</span>
                      <span class="stat-value">{{ buyCurrentPageStats.totalCount }} 件</span>
                    </div>
                    <div class="stat-item">
                      <span class="stat-label">页面金额:</span>
                      <span class="stat-value">¥{{ buyCurrentPageStats.totalAmount }}</span>
                    </div>
                    <div class="stat-item">
                      <span class="stat-label">平均购买价格:</span>
                      <span class="stat-value">¥{{ buyCurrentPageStats.avgPrice }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="table-container">
            <div class="pagination pagination-top">
              <el-pagination
                v-model:current-page="buyCurrentPage"
                v-model:page-size="buyPageSize"
                :page-sizes="[10, 20, 50, 100]"
                :total="buyTotalItems"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleBuySizeChange"
                @current-change="handleBuyCurrentChange"
              />
            </div>
            
            <el-table
              :data="filteredBuyData"
              v-loading="buyLoading"
              element-loading-text="加载中..."
              style="width: 100%"
              :row-style="{ backgroundColor: 'transparent' }"
              :header-row-style="{ backgroundColor: 'var(--bg-tertiary)' }"
              :flexible="true"
              :scrollbar-always-on="true"
            >
              <el-table-column prop="order_id" label="交易ID" min-width="150" show-overflow-tooltip align="left" />
              <el-table-column label="游戏" min-width="120" show-overflow-tooltip>
                <template #default="scope">
                  {{ scope.row.game_name || 'Counter-Strike 2' }}
                </template>
              </el-table-column>
              <el-table-column prop="weapon_type" label="类型" min-width="50" />
              <el-table-column prop="item_name" label="饰品名称" min-width="150" show-overflow-tooltip />
              <el-table-column prop="weapon_name" label="武器名称" min-width="100" />
              <el-table-column prop="weapon_float" label="Float" min-width="180" align="left">
                <template #default="scope">
                  {{ scope.row.weapon_float }}
                </template>
              </el-table-column>
              <el-table-column prop="float_range" label="磨损等级" min-width="100" />
              <el-table-column prop="price" label="购买价格" min-width="100">
                <template #default="scope">
                  ¥{{ scope.row.price }}
                </template>
              </el-table-column>
              <el-table-column prop="order_time" label="购买时间" min-width="160">
                <template #default="scope">
                  {{ formatTime(scope.row.order_time) }}
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" min-width="80">
                <template #default="scope">
                  <el-tag 
                    type="success"
                    size="small"
                    :style="{
                      backgroundColor: '#52c41a',
                      borderColor: '#52c41a',
                      color: '#FFFFFF'
                    }"
                  >
                    {{ scope.row.status }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
            
            <div class="pagination">
              <el-pagination
                v-model:current-page="buyCurrentPage"
                v-model:page-size="buyPageSize"
                :page-sizes="[10, 20, 50, 100]"
                :total="buyTotalItems"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleBuySizeChange"
                @current-change="handleBuyCurrentChange"
              />
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="Steam销售" name="sell">
          <!-- Steam销售内容 -->
          <div class="filters card">
            <div class="flex flex-wrap gap-4 items-center">
              <el-input
                v-model="sellSearchText"
                placeholder="搜索饰品名称..."
                prefix-icon="Search"
                class="search-input"
                @keyup.enter="handleSellSearch"
                @clear="handleSellClearSearch"
                clearable
              />
              <el-button type="primary" @click="handleSellSearch" :loading="sellLoading">
                搜索
              </el-button>
              <el-button @click="handleSellClearSearch" :disabled="sellLoading">
                重置
              </el-button>
              <el-select 
                v-model="sellGameNameFilter" 
                placeholder="选择游戏" 
                class="game-select" 
                @change="handleSellGameChange"
                clearable
              >
                <el-option label="全部游戏" value="all" />
                <el-option v-for="game in sellGameNamesList" :key="game" :label="game" :value="game" />
              </el-select>
              <el-date-picker
                v-model="sellDateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                class="date-picker"
                @change="handleSellDateRangeChange"
                clearable
              />
              <el-button type="success" @click="handleSellTimeSearch" :loading="sellLoading">
                按时间搜索
              </el-button>
            </div>
          </div>

          <!-- Steam销售统计数据 -->
          <div class="stats-summary">
            <div class="card">
              <div class="stats-container">
                <div class="stats-section">
                  <h3>Steam销售统计</h3>
                  <div class="grid grid-3">
                    <div class="stat-item">
                      <span class="stat-label">总销售数量:</span>
                      <span class="stat-value">{{ sellTotalStats.totalCount }} 件</span>
                    </div>
                    <div class="stat-item">
                      <span class="stat-label">总销售金额:</span>
                      <span class="stat-value">¥{{ sellTotalStats.totalAmount }}</span>
                    </div>
                    <div class="stat-item">
                      <span class="stat-label">平均销售价格:</span>
                      <span class="stat-value">¥{{ sellTotalStats.avgPrice }}</span>
                    </div>
                  </div>
                </div>
                
                <div class="stats-divider"></div>
                
                <div class="stats-section">
                  <h3>当前页面统计</h3>
                  <div class="grid grid-3">
                    <div class="stat-item">
                      <span class="stat-label">页面数量:</span>
                      <span class="stat-value">{{ sellCurrentPageStats.totalCount }} 件</span>
                    </div>
                    <div class="stat-item">
                      <span class="stat-label">页面金额:</span>
                      <span class="stat-value">¥{{ sellCurrentPageStats.totalAmount }}</span>
                    </div>
                    <div class="stat-item">
                      <span class="stat-label">平均销售价格:</span>
                      <span class="stat-value">¥{{ sellCurrentPageStats.avgPrice }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="table-container">
            <div class="pagination pagination-top">
              <el-pagination
                v-model:current-page="sellCurrentPage"
                v-model:page-size="sellPageSize"
                :page-sizes="[10, 20, 50, 100]"
                :total="sellTotalItems"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleSellSizeChange"
                @current-change="handleSellCurrentChange"
              />
            </div>
            
            <el-table
              :data="filteredSellData"
              v-loading="sellLoading"
              element-loading-text="加载中..."
              style="width: 100%"
              :row-style="{ backgroundColor: 'transparent' }"
              :header-row-style="{ backgroundColor: 'var(--bg-tertiary)' }"
              :flexible="true"
              :scrollbar-always-on="true"
            >
              <el-table-column prop="order_id" label="交易ID" min-width="150" show-overflow-tooltip align="left" />
              <el-table-column label="游戏" min-width="120" show-overflow-tooltip>
                <template #default="scope">
                  {{ scope.row.game_name || 'Counter-Strike 2' }}
                </template>
              </el-table-column>
              <el-table-column prop="weapon_type" label="类型" min-width="50" />
              <el-table-column prop="item_name" label="饰品名称" min-width="150" show-overflow-tooltip />
              <el-table-column prop="weapon_name" label="武器名称" min-width="100" />
              <el-table-column prop="weapon_float" label="Float" min-width="180" align="left">
                <template #default="scope">
                  {{ scope.row.weapon_float }}
                </template>
              </el-table-column>
              <el-table-column prop="float_range" label="磨损等级" min-width="100" />
              <el-table-column prop="price" label="销售价格" min-width="100">
                <template #default="scope">
                  ¥{{ scope.row.price }}
                </template>
              </el-table-column>
              <el-table-column prop="order_time" label="销售时间" min-width="160">
                <template #default="scope">
                  {{ formatTime(scope.row.order_time) }}
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" min-width="80">
                <template #default="scope">
                  <el-tag 
                    type="success"
                    size="small"
                    :style="{
                      backgroundColor: '#52c41a',
                      borderColor: '#52c41a',
                      color: '#FFFFFF'
                    }"
                  >
                    {{ scope.row.status }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
            
            <div class="pagination">
              <el-pagination
                v-model:current-page="sellCurrentPage"
                v-model:page-size="sellPageSize"
                :page-sizes="[10, 20, 50, 100]"
                :total="sellTotalItems"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleSellSizeChange"
                @current-change="handleSellCurrentChange"
              />
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { apiUrls } from '@/config/api'

export default {
  name: 'SteamMarket',
  setup() {
    const activeTab = ref('buy')
    const buyGameNamesList = ref([])
    const sellGameNamesList = ref([])

    // Buy相关状态
    const buyLoading = ref(false)
    const buyData = ref([])
    const buySearchText = ref('')
    const buyGameNameFilter = ref('all')
    const buyCurrentPage = ref(1)
    const buyPageSize = ref(20)
    const buyTotalItems = ref(0)
    const buyDateRange = ref(null)
    const buyIsTimeSearchMode = ref(false)
    const buyTotalStats = ref({
      totalCount: 0,
      totalAmount: '0.00',
      avgPrice: '0.00'
    })
    const buyAllSearchResults = ref([])
    const buyIsSearchMode = ref(false)

    // Sell相关状态
    const sellLoading = ref(false)
    const sellData = ref([])
    const sellSearchText = ref('')
    const sellGameNameFilter = ref('all')
    const sellCurrentPage = ref(1)
    const sellPageSize = ref(20)
    const sellTotalItems = ref(0)
    const sellDateRange = ref(null)
    const sellIsTimeSearchMode = ref(false)
    const sellTotalStats = ref({
      totalCount: 0,
      totalAmount: '0.00',
      avgPrice: '0.00'
    })
    const sellAllSearchResults = ref([])
    const sellIsSearchMode = ref(false)

    // 计算属性
    const buyCurrentPageStats = computed(() => {
      const currentData = filteredBuyData.value
      const totalCount = currentData.length
      const totalAmount = currentData.reduce((sum, item) => sum + (parseFloat(item.price) || 0), 0).toFixed(2)
      const avgPrice = totalCount > 0 ? (totalAmount / totalCount).toFixed(2) : '0.00'

      return {
        totalCount,
        totalAmount,
        avgPrice
      }
    })

    const sellCurrentPageStats = computed(() => {
      const currentData = filteredSellData.value
      const totalCount = currentData.length
      const totalAmount = currentData.reduce((sum, item) => sum + (parseFloat(item.price) || 0), 0).toFixed(2)
      const avgPrice = totalCount > 0 ? (totalAmount / totalCount).toFixed(2) : '0.00'

      return {
        totalCount,
        totalAmount,
        avgPrice
      }
    })

    const filteredBuyData = computed(() => {
      let filtered = buyData.value

      if (buyIsSearchMode.value && buyAllSearchResults.value.length > 0) {
        filtered = buyAllSearchResults.value
        
        const start = (buyCurrentPage.value - 1) * buyPageSize.value
        const end = start + buyPageSize.value
        return filtered.slice(start, end)
      }

      return filtered
    })

    const filteredSellData = computed(() => {
      let filtered = sellData.value

      if (sellIsSearchMode.value && sellAllSearchResults.value.length > 0) {
        filtered = sellAllSearchResults.value
        
        const start = (sellCurrentPage.value - 1) * sellPageSize.value
        const end = start + sellPageSize.value
        return filtered.slice(start, end)
      }

      return filtered
    })

    // 工具函数
    const formatTime = (time) => {
      if (!time) return ''
      
      // 处理Steam的时间格式 "2025年9月2日"
      if (typeof time === 'string' && time.includes('年') && time.includes('月') && time.includes('日')) {
        // 直接返回Steam的原始格式，因为它已经是中文格式
        return time
      }
      
      // 处理标准时间格式
      try {
        return new Date(time).toLocaleString('zh-CN')
      } catch (error) {
        return time || ''
      }
    }

    // Buy相关方法
    const loadBuyTotalStats = async (searchKeyword = null) => {
      try {
        let apiUrl
        
        const keyword = searchKeyword || buySearchText.value.trim()
        
        if (keyword) {
          apiUrl = apiUrls.steamBuyStatsBySearch(keyword)
        } else {
          apiUrl = apiUrls.steamBuyStats()
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
        
        if (statsData) {
          buyTotalStats.value = {
            totalCount: statsData.total_count || 0,
            totalAmount: statsData.total_amount?.toFixed(2) || '0.00',
            avgPrice: statsData.avg_price?.toFixed(2) || '0.00'
          }
          buyTotalItems.value = statsData.total_count || 0
        }
      } catch (error) {
        console.error('获取Steam购买统计失败:', error)
        buyTotalStats.value = {
          totalCount: 0,
          totalAmount: '0.00',
          avgPrice: '0.00'
        }
        buyTotalItems.value = 0
      }
    }

    const searchBuyByName = async (itemName) => {
      buyLoading.value = true
      try {
        const response = await fetch(apiUrls.steamBuySearchByName(itemName), {
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
        
        if (!Array.isArray(rawData)) {
          throw new Error('搜索结果格式错误')
        }
        
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
          game_name: item[10] || ''
        }))
        
        buyIsSearchMode.value = true
        buyAllSearchResults.value = searchResults
        buyData.value = []
        buyTotalItems.value = rawData.length
        buyCurrentPage.value = 1
        
        await loadBuyTotalStats(itemName)
        
        if (searchResults.length === 0) {
          ElMessage.info(`未找到包含"${itemName}"的Steam购买记录`)
        } else {
          ElMessage.success(`找到 ${searchResults.length} 条Steam购买记录`)
        }
        
      } catch (error) {
        console.error('搜索Steam购买记录失败:', error)
        ElMessage.error(`搜索失败: ${error.message}`)
        buyIsSearchMode.value = false
        buyAllSearchResults.value = []
        buyData.value = []
        buyTotalItems.value = 0
      } finally {
        buyLoading.value = false
      }
    }

    const loadBuyData = async () => {
      if (buyIsSearchMode.value && buySearchText.value.trim()) {
        return
      }
      
      buyLoading.value = true
      try {
        if (buySearchText.value.trim()) {
          await searchBuyByName(buySearchText.value.trim())
          return
        }
        
        buyIsSearchMode.value = false
        buyAllSearchResults.value = []
        
        const min = (buyCurrentPage.value - 1) * buyPageSize.value
        const max = buyPageSize.value
        
        let apiUrl
        if (buyGameNameFilter.value !== 'all') {
          apiUrl = `/api/webSteamMarketV1/getSteamBuyDataByGameName/${encodeURIComponent(buyGameNameFilter.value)}/${min}/${max}`
        } else {
          apiUrl = `/api/webSteamMarketV1/getSteamBuyData/${min}/${max}`
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
        
        const rawData = await response.json()
        
        if (!Array.isArray(rawData)) {
          throw new Error('数据格式错误')
        }
        
        buyData.value = rawData.map((item, index) => {
          if (!Array.isArray(item)) {
            return null
          }
          
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
            status: item[9] || ''
          }
        }).filter(item => item !== null)
        
        if (buyGameNameFilter.value !== 'all') {
          await loadBuyStatsByGameName(buyGameNameFilter.value)
        } else {
          await loadBuyTotalStats()
        }
        
        if (buyData.value.length === 0) {
          ElMessage.info('暂无Steam购买数据')
        } else {
          ElMessage.success(`加载成功，共 ${buyData.value.length} 条Steam购买记录`)
        }
        
      } catch (error) {
        console.error('加载Steam购买数据失败:', error)
        ElMessage.error(`加载数据失败: ${error.message}`)
        buyData.value = []
        buyTotalItems.value = 0
      } finally {
        buyLoading.value = false
      }
    }

    const handleBuyTimeSearch = async () => {
      if (!buyDateRange.value || buyDateRange.value.length !== 2) {
        ElMessage.warning('请选择时间范围')
        return
      }

      buyLoading.value = true
      try {
        const [startDate, endDate] = buyDateRange.value
        
        const response = await fetch(`/api/webSteamMarketV1/searchSteamBuyByTimeRange/${startDate}/${endDate}`, {
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
        
        if (!Array.isArray(rawData)) {
          throw new Error('搜索结果格式错误')
        }
        
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
          game_name: item[10] || ''
        }))
        
        buyIsTimeSearchMode.value = true
        buyIsSearchMode.value = true
        buyAllSearchResults.value = searchResults
        buyData.value = []
        buyTotalItems.value = rawData.length
        buyCurrentPage.value = 1
        
        await loadBuyTimeRangeStats(startDate, endDate)
        
        if (searchResults.length === 0) {
          ElMessage.info(`在 ${startDate} 至 ${endDate} 期间未找到Steam购买记录`)
        } else {
          ElMessage.success(`找到 ${searchResults.length} 条Steam购买记录`)
        }
        
      } catch (error) {
        console.error('时间搜索失败:', error)
        ElMessage.error(`时间搜索失败: ${error.message}`)
        buyIsSearchMode.value = false
        buyIsTimeSearchMode.value = false
        buyAllSearchResults.value = []
        buyData.value = []
        buyTotalItems.value = 0
      } finally {
        buyLoading.value = false
      }
    }

    const loadBuyTimeRangeStats = async (startDate, endDate) => {
      try {
        const response = await fetch(`/api/webSteamMarketV1/getSteamBuyStatsByTimeRange/${startDate}/${endDate}`, {
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
        
        if (statsData) {
          buyTotalStats.value = {
            totalCount: statsData.total_count || 0,
            totalAmount: statsData.total_amount?.toFixed(2) || '0.00',
            avgPrice: statsData.avg_price?.toFixed(2) || '0.00'
          }
        }
      } catch (error) {
        console.error('获取时间范围统计失败:', error)
        buyTotalStats.value = {
          totalCount: 0,
          totalAmount: '0.00',
          avgPrice: '0.00'
        }
      }
    }

    // Sell相关方法（类似Buy方法）
    const loadSellTotalStats = async (searchKeyword = null) => {
      try {
        let apiUrl = '/api/webSteamMarketV1/getSteamSellStats'
        
        const keyword = searchKeyword || sellSearchText.value.trim()
        
        if (keyword) {
          apiUrl = `/api/webSteamMarketV1/getSteamSellStatsBySearch/${encodeURIComponent(keyword)}`
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
        
        if (statsData) {
          sellTotalStats.value = {
            totalCount: statsData.total_count || 0,
            totalAmount: statsData.total_amount?.toFixed(2) || '0.00',
            avgPrice: statsData.avg_price?.toFixed(2) || '0.00'
          }
          sellTotalItems.value = statsData.total_count || 0
        }
      } catch (error) {
        console.error('获取Steam销售统计失败:', error)
        sellTotalStats.value = {
          totalCount: 0,
          totalAmount: '0.00',
          avgPrice: '0.00'
        }
        sellTotalItems.value = 0
      }
    }

    const searchSellByName = async (itemName) => {
      sellLoading.value = true
      try {
        const response = await fetch(`/api/webSteamMarketV1/selectSteamSellWeaponName/${encodeURIComponent(itemName)}`, {
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
        
        if (!Array.isArray(rawData)) {
          throw new Error('搜索结果格式错误')
        }
        
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
          game_name: item[10] || ''
        }))
        
        sellIsSearchMode.value = true
        sellAllSearchResults.value = searchResults
        sellData.value = []
        sellTotalItems.value = rawData.length
        sellCurrentPage.value = 1
        
        await loadSellTotalStats(itemName)
        
        if (searchResults.length === 0) {
          ElMessage.info(`未找到包含"${itemName}"的Steam销售记录`)
        } else {
          ElMessage.success(`找到 ${searchResults.length} 条Steam销售记录`)
        }
        
      } catch (error) {
        console.error('搜索Steam销售记录失败:', error)
        ElMessage.error(`搜索失败: ${error.message}`)
        sellIsSearchMode.value = false
        sellAllSearchResults.value = []
        sellData.value = []
        sellTotalItems.value = 0
      } finally {
        sellLoading.value = false
      }
    }

    const loadSellData = async () => {
      if (sellIsSearchMode.value && sellSearchText.value.trim()) {
        return
      }
      
      sellLoading.value = true
      try {
        if (sellSearchText.value.trim()) {
          await searchSellByName(sellSearchText.value.trim())
          return
        }
        
        sellIsSearchMode.value = false
        sellAllSearchResults.value = []
        
        const min = (sellCurrentPage.value - 1) * sellPageSize.value
        const max = sellPageSize.value
        
        let apiUrl
        if (sellGameNameFilter.value !== 'all') {
          apiUrl = `/api/webSteamMarketV1/getSteamSellDataByGameName/${encodeURIComponent(sellGameNameFilter.value)}/${min}/${max}`
        } else {
          apiUrl = `/api/webSteamMarketV1/getSteamSellData/${min}/${max}`
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
        
        const rawData = await response.json()
        
        if (!Array.isArray(rawData)) {
          throw new Error('数据格式错误')
        }
        
        sellData.value = rawData.map((item, index) => {
          if (!Array.isArray(item)) {
            return null
          }
          
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
            status: item[9] || ''
          }
        }).filter(item => item !== null)
        
        if (sellGameNameFilter.value !== 'all') {
          await loadSellStatsByGameName(sellGameNameFilter.value)
        } else {
          await loadSellTotalStats()
        }
        
        if (sellData.value.length === 0) {
          ElMessage.info('暂无Steam销售数据')
        } else {
          ElMessage.success(`加载成功，共 ${sellData.value.length} 条Steam销售记录`)
        }
        
      } catch (error) {
        console.error('加载Steam销售数据失败:', error)
        ElMessage.error(`加载数据失败: ${error.message}`)
        sellData.value = []
        sellTotalItems.value = 0
      } finally {
        sellLoading.value = false
      }
    }

    const handleSellTimeSearch = async () => {
      if (!sellDateRange.value || sellDateRange.value.length !== 2) {
        ElMessage.warning('请选择时间范围')
        return
      }

      sellLoading.value = true
      try {
        const [startDate, endDate] = sellDateRange.value
        
        const response = await fetch(`/api/webSteamMarketV1/searchSteamSellByTimeRange/${startDate}/${endDate}`, {
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
        
        if (!Array.isArray(rawData)) {
          throw new Error('搜索结果格式错误')
        }
        
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
          game_name: item[10] || ''
        }))
        
        sellIsTimeSearchMode.value = true
        sellIsSearchMode.value = true
        sellAllSearchResults.value = searchResults
        sellData.value = []
        sellTotalItems.value = rawData.length
        sellCurrentPage.value = 1
        
        await loadSellTimeRangeStats(startDate, endDate)
        
        if (searchResults.length === 0) {
          ElMessage.info(`在 ${startDate} 至 ${endDate} 期间未找到Steam销售记录`)
        } else {
          ElMessage.success(`找到 ${searchResults.length} 条Steam销售记录`)
        }
        
      } catch (error) {
        console.error('时间搜索失败:', error)
        ElMessage.error(`时间搜索失败: ${error.message}`)
        sellIsSearchMode.value = false
        sellIsTimeSearchMode.value = false
        sellAllSearchResults.value = []
        sellData.value = []
        sellTotalItems.value = 0
      } finally {
        sellLoading.value = false
      }
    }

    const loadSellTimeRangeStats = async (startDate, endDate) => {
      try {
        const response = await fetch(`/api/webSteamMarketV1/getSteamSellStatsByTimeRange/${startDate}/${endDate}`, {
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
        
        if (statsData) {
          sellTotalStats.value = {
            totalCount: statsData.total_count || 0,
            totalAmount: statsData.total_amount?.toFixed(2) || '0.00',
            avgPrice: statsData.avg_price?.toFixed(2) || '0.00'
          }
        }
      } catch (error) {
        console.error('获取时间范围统计失败:', error)
        sellTotalStats.value = {
          totalCount: 0,
          totalAmount: '0.00',
          avgPrice: '0.00'
        }
      }
    }

    // 事件处理函数
    const handleTabClick = (tab) => {
      if (tab.paneName === 'buy') {
        loadBuyData()
      } else if (tab.paneName === 'sell') {
        loadSellData()
      }
    }

    // Buy事件处理
    const handleBuySizeChange = (val) => {
      buyPageSize.value = val
      buyCurrentPage.value = 1
      loadBuyData()
    }

    const handleBuyCurrentChange = (val) => {
      buyCurrentPage.value = val
      loadBuyData()
    }

    const handleBuySearch = () => {
      buyCurrentPage.value = 1
      loadBuyData()
    }

    const handleBuyClearSearch = () => {
      buySearchText.value = ''
      buyGameNameFilter.value = 'all'
      buyDateRange.value = null
      buyCurrentPage.value = 1
      buyIsSearchMode.value = false
      buyIsTimeSearchMode.value = false
      buyAllSearchResults.value = []
      loadBuyData()
    }

    const handleBuyGameChange = () => {
      buyCurrentPage.value = 1
      loadBuyData()
    }

    const loadBuyStatsByGameName = async (gameName) => {
      try {
        const response = await fetch(`/api/webSteamMarketV1/getSteamBuyStatsByGameName/${encodeURIComponent(gameName)}`, {
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
        
        if (statsData) {
          buyTotalStats.value = {
            totalCount: statsData.total_count || 0,
            totalAmount: statsData.total_amount?.toFixed(2) || '0.00',
            avgPrice: statsData.avg_price?.toFixed(2) || '0.00'
          }
          buyTotalItems.value = statsData.total_count || 0
        }
      } catch (error) {
        console.error('根据游戏名称获取Steam购买统计失败:', error)
        buyTotalStats.value = {
          totalCount: 0,
          totalAmount: '0.00',
          avgPrice: '0.00'
        }
        buyTotalItems.value = 0
      }
    }

    const handleBuyDateRangeChange = (value) => {
      console.log('购买日期范围变更:', value)
    }

    // Sell事件处理
    const handleSellSizeChange = (val) => {
      sellPageSize.value = val
      sellCurrentPage.value = 1
      loadSellData()
    }

    const handleSellCurrentChange = (val) => {
      sellCurrentPage.value = val
      loadSellData()
    }

    const handleSellSearch = () => {
      sellCurrentPage.value = 1
      loadSellData()
    }

    const handleSellClearSearch = () => {
      sellSearchText.value = ''
      sellGameNameFilter.value = 'all'
      sellDateRange.value = null
      sellCurrentPage.value = 1
      sellIsSearchMode.value = false
      sellIsTimeSearchMode.value = false
      sellAllSearchResults.value = []
      loadSellData()
    }

    const handleSellGameChange = () => {
      sellCurrentPage.value = 1
      loadSellData()
    }

    const loadSellStatsByGameName = async (gameName) => {
      try {
        const response = await fetch(`/api/webSteamMarketV1/getSteamSellStatsByGameName/${encodeURIComponent(gameName)}`, {
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
        
        if (statsData) {
          sellTotalStats.value = {
            totalCount: statsData.total_count || 0,
            totalAmount: statsData.total_amount?.toFixed(2) || '0.00',
            avgPrice: statsData.avg_price?.toFixed(2) || '0.00'
          }
          sellTotalItems.value = statsData.total_count || 0
        }
      } catch (error) {
        console.error('根据游戏名称获取Steam销售统计失败:', error)
        sellTotalStats.value = {
          totalCount: 0,
          totalAmount: '0.00',
          avgPrice: '0.00'
        }
        sellTotalItems.value = 0
      }
    }

    const handleSellDateRangeChange = (value) => {
      console.log('销售日期范围变更:', value)
    }

    // 加载Buy游戏名称列表
    const loadBuyGameNames = async () => {
      try {
        const response = await fetch('/api/webSteamMarketV1/getBuyGameNames', {
          method: 'GET',
          mode: 'cors',
          headers: {
            'Accept': 'application/json',
          },
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        buyGameNamesList.value = data || []
      } catch (error) {
        console.error('加载Buy游戏名称列表失败:', error)
        buyGameNamesList.value = []
      }
    }

    // 加载Sell游戏名称列表
    const loadSellGameNames = async () => {
      try {
        const response = await fetch('/api/webSteamMarketV1/getSellGameNames', {
          method: 'GET',
          mode: 'cors',
          headers: {
            'Accept': 'application/json',
          },
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        sellGameNamesList.value = data || []
      } catch (error) {
        console.error('加载Sell游戏名称列表失败:', error)
        sellGameNamesList.value = []
      }
    }

    onMounted(() => {
      loadBuyGameNames() // 加载Buy游戏名称列表
      loadSellGameNames() // 加载Sell游戏名称列表
      loadBuyData() // 默认加载购买数据
    })

    return {
      activeTab,
      buyGameNamesList,
      sellGameNamesList,
      // Buy相关
      buyLoading,
      buyData,
      filteredBuyData,
      buyTotalStats,
      buyCurrentPageStats,
      buySearchText,
      buyGameNameFilter,
      buyDateRange,
      buyIsTimeSearchMode,
      buyCurrentPage,
      buyPageSize,
      buyTotalItems,
      buyIsSearchMode,
      buyAllSearchResults,
      // Sell相关
      sellLoading,
      sellData,
      filteredSellData,
      sellTotalStats,
      sellCurrentPageStats,
      sellSearchText,
      sellGameNameFilter,
      sellDateRange,
      sellIsTimeSearchMode,
      sellCurrentPage,
      sellPageSize,
      sellTotalItems,
      sellIsSearchMode,
      sellAllSearchResults,
      // 方法
      formatTime,
      handleTabClick,
      // Buy方法
      handleBuySizeChange,
      handleBuyCurrentChange,
      handleBuySearch,
      handleBuyClearSearch,
      handleBuyGameChange,
      handleBuyDateRangeChange,
      handleBuyTimeSearch,
      // Sell方法
      handleSellSizeChange,
      handleSellCurrentChange,
      handleSellSearch,
      handleSellClearSearch,
      handleSellGameChange,
      handleSellDateRangeChange,
      handleSellTimeSearch
    }
  }
}
</script>

<style scoped>
.tab-container {
  margin-bottom: 1rem;
}

.steam-tabs {
  background-color: transparent;
}

:deep(.el-tabs__header) {
  background-color: transparent;
  margin-bottom: 1rem;
}

:deep(.el-tabs__nav-wrap::after) {
  background-color: var(--border-default);
}

:deep(.el-tabs__item) {
  color: var(--text-secondary);
  font-size: clamp(0.875rem, 1.5vw, 1rem);
  font-weight: 500;
  padding: 0 clamp(1rem, 3vw, 1.5rem);
}

:deep(.el-tabs__item:hover) {
  color: var(--text-primary);
}

:deep(.el-tabs__item.is-active) {
  color: var(--text-accent);
  font-weight: 600;
}

:deep(.el-tabs__active-bar) {
  background-color: var(--text-accent);
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

.game-select {
  min-width: 150px;
  max-width: 200px;
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

.stats-summary {
  margin-bottom: clamp(1rem, 3vw, 1.25rem);
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
  
  :deep(.el-table th),
  :deep(.el-table td) {
    padding: 0.5rem 0.25rem;
  }
  
  :deep(.el-button) {
    font-size: 0.625rem;
    padding: 0.25rem 0.5rem;
  }
}

/* 继承现有样式 */
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

/* 日历面板整体样式 */
:deep(.el-picker-panel) {
  background-color: #1a1a1a !important;
  border: 1px solid #333 !important;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.3) !important;
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
