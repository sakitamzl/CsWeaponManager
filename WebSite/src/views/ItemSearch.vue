<template>
  <div class="item-search-container">
    <!-- 搜索区域 - 固定在顶部 -->
    <div class="search-wrapper top-left">
      <div class="card search-card">
        <div class="search-section">
          <div class="search-controls compact">
            <el-select 
              v-model="selectedSteamId" 
              placeholder="选择Steam账号" 
              class="steam-id-select"
              @change="handleSteamIdChange"
              filterable
            >
              <el-option
                v-for="item in steamIdList"
                :key="item.steam_id"
                :label="`${item.steam_id} (${item.item_count}件)`"
                :value="item.steam_id"
              >
                <span style="float: left">{{ item.steam_id }}</span>
                <span style="float: right; color: var(--el-text-color-secondary); font-size: 13px">
                  {{ item.item_count }}件
                </span>
              </el-option>
            </el-select>
            
            <el-select 
              v-model="selectedExterior" 
              placeholder="筛选外观" 
              class="exterior-select"
              clearable
              @change="handleExteriorChange"
            >
              <el-option label="全部外观" value="" />
              <el-option label="崭新出厂" value="崭新出厂">
                <span :style="{ color: '#4caf50' }">崭新出厂</span>
              </el-option>
              <el-option label="略有磨损" value="略有磨损">
                <span :style="{ color: '#8bc34a' }">略有磨损</span>
              </el-option>
              <el-option label="久经沙场" value="久经沙场">
                <span :style="{ color: '#ffc107' }">久经沙场</span>
              </el-option>
              <el-option label="破损不堪" value="破损不堪">
                <span :style="{ color: '#ff9800' }">破损不堪</span>
              </el-option>
              <el-option label="战痕累累" value="战痕累累">
                <span :style="{ color: '#f44336' }">战痕累累</span>
              </el-option>
            </el-select>
            
            <el-select 
              v-model="selectedStatTrak" 
              placeholder="StatTrak™" 
              class="stattrak-select"
              @change="handleStatTrakChange"
            >
              <el-option label="非StatTrak™" value="normal">
                <span>非StatTrak™</span>
              </el-option>
              <el-option label="StatTrak™" value="stattrak">
                <span :style="{ color: '#cf6a32' }">StatTrak™</span>
              </el-option>
              <el-option label="全部" value="" />
            </el-select>
            
            <el-input
              v-model="searchKeyword"
              placeholder="搜索饰品名称..."
              prefix-icon="Search"
              class="search-input"
              @keyup.enter="handleSearchWeapon"
              clearable
            />
            
            <div class="button-group">
              <el-button type="primary" @click="handleSearchWeapon" :loading="isSearching && searchSource === 'weapon'">
                搜索武器
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 搜索结果表格 -->
    <div class="card table-card" v-if="searchResults.length > 0">
      <!-- 折叠/展开控制（始终显示） -->
      <div class="collapse-header" @click.stop="toggleSearchResults">
        <span class="collapse-title">
          <el-icon><CaretRight v-if="!showSearchResults" /><CaretBottom v-if="showSearchResults" /></el-icon>
          武器搜索结果 ({{ searchResults.length }} 件)
        </span>
        <el-button 
          type="primary" 
          size="small" 
          :icon="Refresh" 
          @click.stop="handleRefreshSearch"
          :loading="isSearching && searchSource === 'weapon'"
        >
          刷新列表
        </el-button>
      </div>
      
      <el-table 
        v-show="showSearchResults" 
        :data="paginatedResults" 
        style="width: 100%"
        :default-sort="{ prop: 'name', order: 'ascending' }"
        v-loading="isSearching"
        element-loading-text="搜索中..."
        element-loading-background="rgba(0, 0, 0, 0.8)"
      >
        <el-table-column type="index" label="#" width="60" align="center" />
        
        <el-table-column label="饰品名称" min-width="250" show-overflow-tooltip>
          <template #default="{ row }">
            <el-popover
              :visible="activePopoverRow === row"
              placement="bottom"
              :width="200"
              trigger="click"
            >
              <template #reference>
                <span class="clickable-item-name" @click="togglePopover(row)">
                  {{ row.market_listing_item_name }}
                </span>
              </template>
              <div class="search-platform-selector">
                <div class="selector-buttons">
                  <el-button 
                    type="warning" 
                    size="small" 
                    @click="selectPlatform(row, 'yyyp')"
                    :loading="isSearching && searchSource === 'yyyp'"
                  >
                    悠悠有品
                  </el-button>
                  <el-button 
                    type="info" 
                    size="small" 
                    class="buff-button"
                    @click="selectPlatform(row, 'buff')"
                    :loading="isSearching && searchSource === 'buff'"
                  >
                    BUFF
                  </el-button>
                  <el-button 
                    type="success" 
                    size="small" 
                    class="csfloat-button"
                    @click="selectPlatform(row, 'csfloat')"
                    :loading="isSearching && searchSource === 'csfloat'"
                  >
                    CsFloat
                  </el-button>
                  <el-button 
                    type="primary" 
                    size="small" 
                    class="all-button"
                    @click="selectPlatform(row, 'all')"
                    :loading="isSearching && searchSource === 'all'"
                  >
                    全部搜索
                  </el-button>
                </div>
              </div>
            </el-popover>
          </template>
        </el-table-column>
        
        <el-table-column label="Steam Hash Name" min-width="250" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="hash-name-text">{{ row.steam_hash_name || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="weapon_type" label="武器类型" width="120" align="center">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ row.weapon_type || '-' }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="item_name" label="皮肤名称" width="180" align="center" show-overflow-tooltip />
        
        <el-table-column prop="Rarity" label="稀有度" width="120" align="center">
          <template #default="{ row }">
            <span v-if="row.Rarity" class="rarity-text" :style="{ color: getRarityColor(row.Rarity) }">
              {{ row.Rarity }}
            </span>
            <span v-else class="no-data">-</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="yyyp_id" label="悠悠有品ID" width="120" align="center">
          <template #default="{ row }">
            <span class="id-text">{{ row.yyyp_id || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="buff_id" label="BUFF ID" width="100" align="center">
          <template #default="{ row }">
            <span class="id-text">{{ row.buff_id || '-' }}</span>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页器 -->
      <div class="pagination-container" v-show="showSearchResults">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="filteredResults.length"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- BUFF商品列表 -->
    <div v-if="showBuffList" class="card buff-commodity-list">
      <!-- 折叠/展开控制头部 -->
      <div class="buff-collapse-header" @click.stop="toggleBuffList">
        <div class="buff-collapse-left">
          <el-icon class="collapse-icon">
            <CaretRight v-if="!showBuffTable" />
            <CaretBottom v-if="showBuffTable" />
          </el-icon>
          <span class="buff-collapse-title">BUFF商品列表</span>
          <el-button 
            type="primary" 
            size="small" 
            :icon="Refresh" 
            @click.stop="handleRefreshBuff"
            :loading="isSearching && searchSource === 'buff'"
          >
            刷新列表
          </el-button>
        </div>
        <div class="buff-weapon-info">
          <span class="weapon-name">{{ buffCurrentWeapon?.market_listing_item_name }}</span>
          <span class="weapon-id">商品ID: {{ buffCurrentWeapon?.buff_id }}</span>
          <span class="commodity-count">当前页: {{ paginatedBuffCommodities.length }} 件</span>
          <span class="total-count">在售总数: {{ buffTotalCount }} 件</span>
          <span class="buy-count">求购: {{ buffBuyNum }} 件</span>
          <span class="rent-count">租赁: {{ buffRentNum }} 件</span>
        </div>
      </div>
      
      <el-table 
        v-show="showBuffTable"
        :data="paginatedBuffCommodities" 
        style="width: 100%"
        :default-sort="{ prop: 'price', order: 'ascending' }"
        v-loading="isSearching && searchSource === 'buff'"
        element-loading-text="加载中..."
        element-loading-background="rgba(0, 0, 0, 0.8)"
      >
        <el-table-column label="商品图片" width="100" align="center">
          <template #default="{ row }">
            <img :src="row.iconUrl" class="commodity-icon" @error="handleImageError" />
          </template>
        </el-table-column>
        
        <el-table-column label="数据库名称" min-width="200" align="center" show-overflow-tooltip>
          <template #default="{ row }">
            <span>{{ buffCurrentWeapon?.market_listing_item_name || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="磨损值" width="180" align="center" sortable prop="abrade">
          <template #default="{ row }">
            <span>{{ row.abrade || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="价格" width="100" align="center" sortable prop="price">
          <template #default="{ row }">
            <span class="price-text">{{ row.price }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="模板编号" width="100" align="center">
          <template #default="{ row }">
            <span>{{ row.paintSeed || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="印花" width="120" align="center">
          <template #default="{ row }">
            <el-button 
              v-if="row.stickers && row.stickers.length > 0"
              type="info" 
              size="small"
              @click="showStickersDialog(row)"
              style="background-color: #303133; border-color: #303133; color: white;"
            >
              查看({{ row.stickers.length }})
            </el-button>
            <span v-else style="color: #909399;">无</span>
          </template>
        </el-table-column>
        
        <el-table-column label="卖家描述" min-width="200" align="center" show-overflow-tooltip>
          <template #default="{ row }">
            <span>{{ row.description || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="议价" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.allowBargain ? 'success' : 'info'" size="small">
              {{ row.allowBargain ? '可议价' : '不可' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="100" align="center" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="success" 
              size="small" 
              @click="handleBuyBuffCommodity(row)"
            >
              购买
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- BUFF分页器 -->
      <div class="pagination-container" v-show="showBuffTable">
        <el-pagination
          v-model:current-page="buffCurrentPage"
          :page-size="buffPageSize"
          :total="buffCommodities.length"
          layout="total, prev, pager, next, jumper"
          @current-change="handleBuffPageChange"
        />
      </div>
    </div>

    <!-- 悠悠有品商品列表 -->
    <div v-if="showYYYPList" class="card yyyp-commodity-list">
      <!-- 折叠/展开控制头部 -->
      <div class="yyyp-collapse-header" @click.stop="toggleYYYPList">
        <div class="yyyp-collapse-left">
          <el-icon class="collapse-icon">
            <CaretRight v-if="!showYYYPTable" />
            <CaretBottom v-if="showYYYPTable" />
          </el-icon>
          <span class="yyyp-collapse-title">悠悠有品商品列表</span>
          <el-button 
            type="primary" 
            size="small" 
            :icon="Refresh" 
            @click.stop="handleRefreshYYYP"
            :loading="isSearching && searchSource === 'yyyp'"
          >
            刷新列表
          </el-button>
        </div>
        <div class="yyyp-weapon-info">
          <span class="weapon-name">{{ yyypCurrentWeapon?.market_listing_item_name }}</span>
          <span class="weapon-id">模板ID: {{ yyypCurrentWeapon?.yyyp_id }}</span>
          <span class="commodity-count">当前页: {{ paginatedYYYPCommodities.length }} 件</span>
          <span class="total-count">在售总数: {{ yyypTotalCount }} 件</span>
        </div>
      </div>
      
      <el-table 
        v-show="showYYYPTable"
        :data="paginatedYYYPCommodities" 
        style="width: 100%"
        :default-sort="{ prop: 'price', order: 'ascending' }"
        v-loading="isSearching && searchSource === 'yyyp'"
        element-loading-text="加载中..."
        element-loading-background="rgba(0, 0, 0, 0.8)"
      >
        <el-table-column label="商品图片" width="100" align="center">
          <template #default="{ row }">
            <img :src="row.iconUrl" class="commodity-icon" @error="handleImageError" />
          </template>
        </el-table-column>
        
        <el-table-column prop="commodityName" label="商品名称" min-width="200" show-overflow-tooltip />
        
        <el-table-column label="数据库名称" min-width="200" align="center" show-overflow-tooltip>
          <template #default="{ row }">
            <span>{{ yyypCurrentWeapon?.market_listing_item_name || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="磨损值" width="180" align="center" sortable prop="abrade">
          <template #default="{ row }">
            <span>{{ row.abrade || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="价格" width="100" align="center" sortable prop="price">
          <template #default="{ row }">
            <span class="price-text">{{ row.price }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="模板编号" width="100" align="center">
          <template #default="{ row }">
            <span>{{ row.paintSeed || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="印花" width="120" align="center">
          <template #default="{ row }">
            <el-button 
              v-if="row.stickers && row.stickers.length > 0"
              type="info" 
              size="small"
              @click="showStickersDialog(row)"
              style="background-color: #303133; border-color: #303133; color: white;"
            >
              查看({{ row.stickers.length }})
            </el-button>
            <span v-else style="color: #909399;">无</span>
          </template>
        </el-table-column>
        
        <el-table-column label="改名" width="200" align="center">
          <template #default="{ row }">
            <div v-if="row.haveNameTag === 1">
              <!-- 已获取到改名信息，直接显示文本 -->
              <div v-if="row.nameTagText">
                <span style="color: #e6a23c; font-weight: 600; font-size: 13px;" :title="row.nameTagText">
                  {{ row.nameTagText }}
                </span>
              </div>
              <!-- 未获取改名信息，显示图标 -->
              <span 
                v-else
                @click="fetchSingleNameTag(row)"
                style="cursor: pointer; font-size: 13px; user-select: none; color: #e6a23c; font-weight: 600;"
                :style="{ opacity: row.nameTagLoading ? 0.5 : 1 }"
                :title="row.nameTagLoading ? '加载中...' : '点击解析改名'"
              >
                🏷️ 解析名称
              </span>
            </div>
            <span v-else style="color: #909399;">-</span>
          </template>
        </el-table-column>
        
        <el-table-column label="卖家" min-width="120" align="center">
          <template #default="{ row }">
            <span>{{ row.userNickName || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="100" align="center" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="success" 
              size="small" 
              @click="handleBuyCommodity(row)"
            >
              购买
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 悠悠有品分页器 -->
      <div class="pagination-container" v-show="showYYYPTable">
        <el-pagination
          v-model:current-page="yyypCurrentPage"
          :page-size="yyypPageSize"
          :total="yyypCommodities.length"
          layout="total, prev, pager, next, jumper"
          @current-change="handleYYYPPageChange"
        />
      </div>
    </div>

    <!-- 无结果提示 -->
    <div v-if="searchResults.length === 0 && !isSearching && searchKeyword" class="card no-results-card">
      <el-empty description="未找到相关饰品" />
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CaretRight, CaretBottom, Refresh } from '@element-plus/icons-vue'
import { API_CONFIG, apiUrls } from '@/config/api.js'

export default {
  name: 'ItemSearch',
  components: {
    CaretRight,
    CaretBottom,
    Refresh
  },
  setup() {
    const searchKeyword = ref('')
    const searchResults = ref([])
    const isSearching = ref(false)
    const currentPage = ref(1)
    const pageSize = ref(20)
    const searchSource = ref('') // 'yyyp' 或 'buff'
    const steamIdList = ref([])
    const selectedSteamId = ref('')
    const selectedExterior = ref('') // 选择的外观筛选
    const selectedStatTrak = ref('normal') // 选择的StatTrak筛选，默认非StatTrak™
    
    // BUFF商品列表
    const buffCommodities = ref([])
    const buffCurrentWeapon = ref(null)
    const buffTotalCount = ref(0)  // 在售总数量
    const buffBuyNum = ref(0)  // 求购数量
    const buffRentNum = ref(0)  // 租赁数量
    const showBuffList = ref(false)
    const showBuffTable = ref(true)  // 控制BUFF表格的展开/折叠
    const buffCurrentPage = ref(1)  // BUFF分页当前页
    const buffPageSize = ref(5)  // BUFF每页显示5条
    
    // 悠悠有品商品列表
    const yyypCommodities = ref([])
    const yyypCurrentWeapon = ref(null)
    const yyypTotalCount = ref(0)  // 在售总数量
    const showYYYPList = ref(false)
    const showYYYPTable = ref(true)  // 控制悠悠有品表格的展开/折叠
    const yyypCurrentPage = ref(1)  // 悠悠有品分页当前页
    const yyypPageSize = ref(5)  // 悠悠有品每页显示5条
    const showSearchResults = ref(false)  // 控制搜索结果的展开/折叠，默认折叠
    
    // 图片缓存 - 存储已加载的图片URL
    const imageCache = new Set()
    
    // API 基础地址
    const API_BASE = `${API_CONFIG.BASE_URL}/webInventoryV1`

    // 计算属性 - 筛选后的结果
    const filteredResults = computed(() => {
      let results = searchResults.value
      
      // 根据选择的外观筛选（使用 float_range 字段）
      if (selectedExterior.value) {
        results = results.filter(item => {
          const floatRange = item.float_range || ''
          return floatRange === selectedExterior.value
        })
      }
      
      // 根据选择的StatTrak筛选
      if (selectedStatTrak.value === 'stattrak') {
        // 只显示StatTrak™饰品
        results = results.filter(item => {
          const itemName = item.market_listing_item_name || ''
          return itemName.includes('StatTrak™') || itemName.includes('（StatTrak™）')
        })
      } else if (selectedStatTrak.value === 'normal') {
        // 只显示非StatTrak™饰品
        results = results.filter(item => {
          const itemName = item.market_listing_item_name || ''
          return !itemName.includes('StatTrak™') && !itemName.includes('（StatTrak™）')
        })
      }
      // 如果是空值''，显示全部
      
      return results
    })

    // 计算属性 - 分页结果
    const paginatedResults = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return filteredResults.value.slice(start, end)
    })

    // 计算属性 - BUFF商品分页结果
    const paginatedBuffCommodities = computed(() => {
      const start = (buffCurrentPage.value - 1) * buffPageSize.value
      const end = start + buffPageSize.value
      return buffCommodities.value.slice(start, end)
    })

    // 计算属性 - 悠悠有品商品分页结果
    const paginatedYYYPCommodities = computed(() => {
      const start = (yyypCurrentPage.value - 1) * yyypPageSize.value
      const end = start + yyypPageSize.value
      return yyypCommodities.value.slice(start, end)
    })

    const handleImageError = (event) => {
      event.target.src = '/icons/default-weapon.png'
    }

    // 预加载图片（相同URL只加载一次）
    const preloadImages = (commodityList) => {
      const uniqueUrls = new Set()
      
      // 收集所有唯一的图片URL
      commodityList.forEach(item => {
        if (item.iconUrl && !imageCache.has(item.iconUrl)) {
          uniqueUrls.add(item.iconUrl)
        }
      })
      
      // 预加载未缓存的图片
      uniqueUrls.forEach(url => {
        const img = new Image()
        img.onload = () => {
          imageCache.add(url)
          console.log(`图片已缓存: ${url}`)
        }
        img.onerror = () => {
          console.error(`图片加载失败: ${url}`)
        }
        img.src = url
      })
      
      console.log(`开始预加载 ${uniqueUrls.size} 张唯一图片，已缓存 ${imageCache.size} 张`)
    }

    // 实时搜索武器名称
    const querySearchAsync = async (queryString, cb) => {
      if (!queryString || queryString.trim().length === 0) {
        cb([])
        return
      }

      try {
        const response = await axios.get(apiUrls.searchWeapon(queryString.trim()))
        if (response.data.success && response.data.data) {
          const results = response.data.data.map(name => ({
            value: name
          }))
          cb(results)
        } else {
          cb([])
        }
      } catch (error) {
        console.error('搜索武器名称失败:', error)
        cb([])
      }
    }

    // 选择搜索建议
    const handleSelect = (item) => {
      searchKeyword.value = item.value
      console.log('已选择:', item.value)
    }

    // 搜索武器详情
    const handleSearchWeapon = async () => {
      if (!searchKeyword.value.trim()) {
        ElMessage.warning('请输入搜索关键词')
        return
      }

      isSearching.value = true
      searchSource.value = 'weapon'
      currentPage.value = 1
      
      try {
        console.log('搜索武器:', searchKeyword.value)
        
        const response = await axios.get(apiUrls.searchWeaponDetail(searchKeyword.value.trim()))
        
        if (response.data.success) {
          searchResults.value = response.data.data || []
          
          if (searchResults.value.length === 0) {
            ElMessage.info('未找到匹配的武器')
            showSearchResults.value = false
          } else {
            ElMessage.success(`找到 ${searchResults.value.length} 件武器`)
            showSearchResults.value = true  // 搜索成功后自动展开
          }
        } else {
          ElMessage.error('搜索失败: ' + (response.data.error || '未知错误'))
          searchResults.value = []
          showSearchResults.value = false
        }
        
      } catch (error) {
        console.error('搜索武器失败:', error)
        ElMessage.error('搜索失败: ' + (error.response?.data?.error || error.message))
        searchResults.value = []
        showSearchResults.value = false
      } finally {
        isSearching.value = false
      }
    }

    // 刷新搜索结果
    const handleRefreshSearch = async () => {
      if (!searchKeyword.value.trim()) {
        ElMessage.warning('请先输入搜索关键词')
        return
      }

      ElMessage.info('正在刷新数据...')
      await handleSearchWeapon()
    }

    // 刷新悠悠有品商品列表
    const handleRefreshYYYP = async () => {
      if (!yyypCurrentWeapon.value) {
        ElMessage.warning('无法刷新，请重新选择武器')
        return
      }

      yyypCurrentPage.value = 1  // 重置分页到第一页
      ElMessage.info('正在刷新悠悠有品商品数据...')
      await handleSearchYYYPByRow(yyypCurrentWeapon.value)
    }
    
    // 刷新BUFF商品列表
    const handleRefreshBuff = async () => {
      if (!buffCurrentWeapon.value) {
        ElMessage.warning('无法刷新，请重新选择武器')
        return
      }

      buffCurrentPage.value = 1  // 重置分页到第一页
      ElMessage.info('正在刷新BUFF商品数据...')
      await handleSearchBuffByRow(buffCurrentWeapon.value)
    }
    
    // 切换BUFF表格的展开/折叠
    const toggleBuffList = () => {
      showBuffTable.value = !showBuffTable.value
    }
    
    // 购买BUFF商品（暂未对接）
    const handleBuyBuffCommodity = (commodity) => {
      console.log('购买BUFF商品:', commodity)
      ElMessage.info(`购买功能开发中... 订单ID: ${commodity.id}`)
      // TODO: 对接BUFF购买接口
    }

    // 获取稀有度类型（根据CS:GO品质颜色）
    const getRarityType = (rarity) => {
      if (!rarity) return ''
      // 不使用Element Plus的type，使用自定义颜色
      return ''
    }
    
    // 获取稀有度颜色样式
    const getRarityColor = (rarity) => {
      if (!rarity) return ''
      const rarityColorMap = {
        '违禁': '#e4ae39',      // 金色
        '隐秘': '#eb4b4b',      // 红色
        '保密': '#d32ce6',      // 紫色/粉色
        '受限': '#8847ff',      // 紫色
        '军规级': '#4b69ff',    // 蓝色
        '工业级': '#5e98d9',    // 浅蓝色
        '消费级': '#b0c3d9',    // 灰蓝色
        '普通级': '#b0c3d9'     // 灰蓝色
      }
      return rarityColorMap[rarity] || '#fff'
    }

    // 获取外观（磨损）颜色样式
    const getExteriorColor = (itemName) => {
      if (!itemName) return '#fff'
      
      const exteriorColorMap = {
        '崭新出厂': '#4caf50',      // 绿色 - Factory New
        '略有磨损': '#8bc34a',      // 浅绿色 - Minimal Wear
        '久经沙场': '#ffc107',      // 黄色 - Field-Tested
        '破损不堪': '#ff9800',      // 橙色 - Well-Worn
        '战痕累累': '#f44336'       // 红色 - Battle-Scarred
      }
      
      // 检查饰品名称中是否包含外观关键词
      for (const [exterior, color] of Object.entries(exteriorColorMap)) {
        if (itemName.includes(exterior) || itemName.includes(`(${exterior})`)) {
          return color
        }
      }
      
      return '#fff' // 默认白色
    }

    // 加载Steam ID列表
    const loadSteamIdList = async () => {
      try {
        const response = await axios.get(`${API_BASE}/steam_ids`)
        console.log('Steam ID列表响应:', response.data)
        if (response.data.success) {
          steamIdList.value = response.data.data
          if (steamIdList.value.length > 0) {
            // 默认选择第一个
            selectedSteamId.value = steamIdList.value[0].steam_id
            console.log('默认选择Steam ID:', selectedSteamId.value)
          } else {
            ElMessage.warning('没有找到库存数据，请先获取Steam库存')
          }
        }
      } catch (error) {
        console.error('加载Steam ID列表失败:', error)
        ElMessage.error('加载Steam ID列表失败: ' + (error.response?.data?.error || error.message))
      }
    }

    // Steam ID 改变处理
    const handleSteamIdChange = (value) => {
      console.log('Steam ID已改变:', value)
      selectedSteamId.value = value
    }

    // 外观筛选改变处理
    const handleExteriorChange = (value) => {
      console.log('外观筛选已改变:', value)
      selectedExterior.value = value
      currentPage.value = 1 // 重置到第一页
    }

    // StatTrak筛选改变处理
    const handleStatTrakChange = (value) => {
      console.log('StatTrak筛选已改变:', value)
      selectedStatTrak.value = value
      currentPage.value = 1 // 重置到第一页
    }

    // 通过行数据搜索悠悠有品
    const handleSearchYYYPByRow = async (row) => {
      console.log('=== 开始执行 handleSearchYYYPByRow ===')
      console.log('row数据:', row)
      console.log('row.yyyp_id:', row.yyyp_id)
      console.log('selectedSteamId.value:', selectedSteamId.value)
      
      if (!row.yyyp_id) {
        console.log('没有yyyp_id，退出')
        ElMessage.warning('该武器没有悠悠有品ID')
        return
      }

      if (!selectedSteamId.value) {
        console.log('没有选择Steam账号，退出')
        ElMessage.warning('请先选择Steam账号')
        return
      }

      console.log('通过验证，开始请求')
      isSearching.value = true
      searchSource.value = 'yyyp'
      
      try {
        console.log('搜索悠悠有品:', row.market_listing_item_name, 'ID:', row.yyyp_id, 'SteamID:', selectedSteamId.value)
        
        // 构建请求数据
        const requestData = {
          steamId: selectedSteamId.value || '',
          yyypId: row.yyyp_id,
          pageIndex: 1,
          pageSize: 50
        }
        
        const apiUrl = `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/getCommoditiesByTemplateId`
        
        console.log('请求URL:', apiUrl)
        console.log('请求数据:', requestData)
        
        // 调用悠悠有品商品列表API（使用Spider服务器地址）
        const response = await axios.post(apiUrl, requestData)
        
        console.log('API响应:', response.data)
        
        if (response.data.success) {
          const parsedData = response.data.data
          console.log('获取到悠悠有品已解析数据:', parsedData)
          
          // 直接使用Spider解析后的数据
          const commodityList = parsedData.commodityList || []
          const totalCount = parsedData.totalCount || 0
          console.log('商品列表:', commodityList)
          console.log('在售总数:', totalCount)
          
          // 更新状态，显示商品列表
          yyypCurrentWeapon.value = row
          yyypCommodities.value = commodityList
          yyypTotalCount.value = totalCount
          yyypCurrentPage.value = 1  // 重置分页到第一页
          showYYYPList.value = true
          showSearchResults.value = false  // 折叠搜索结果
          
          ElMessage.success(`成功获取 ${commodityList.length} 条商品数据，在售总数: ${totalCount}`)
          
          // 预加载图片（相同URL只加载一次）
          preloadImages(commodityList)
          
          // 滚动到商品列表区域
          setTimeout(() => {
            const listElement = document.querySelector('.yyyp-commodity-list')
            if (listElement) {
              listElement.scrollIntoView({ behavior: 'smooth', block: 'start' })
            }
          }, 100)
          
          // 自动批量获取改名信息
          fetchAllNameTags(commodityList)
        } else {
          console.error('API返回失败:', response.data)
          ElMessage.error(response.data.message || '获取商品列表失败')
        }
        
      } catch (error) {
        console.error('搜索悠悠有品失败 - 完整错误:', error)
        console.error('错误响应:', error.response)
        console.error('错误数据:', error.response?.data)
        
        const errorMessage = error.response?.data?.message || error.message || '搜索失败，请检查网络连接'
        ElMessage.error(errorMessage)
      } finally {
        console.log('请求完成，重置加载状态')
        isSearching.value = false
        searchSource.value = ''
      }
    }

    // 查看商品详情（暂未对接）
    const handleViewDetail = (commodity) => {
      console.log('查看商品详情:', commodity)
      ElMessage.info(`查看详情功能开发中... 商品ID: ${commodity.id}`)
      // TODO: 对接查看详情接口
    }

    // 购买商品
    const handleBuyCommodity = async (commodity) => {
      console.log('购买商品:', commodity)
      
      // 确认购买
      try {
        await ElMessageBox.confirm(
          `确认购买该商品吗？\n\n商品：${commodity.commodityName}\n价格：¥${commodity.price}\n磨损：${commodity.abrade || '-'}`,
          '确认购买',
          {
            confirmButtonText: '确认购买',
            cancelButtonText: '取消',
            type: 'warning',
            distinguishCancelAndClose: true
          }
        )
      } catch (error) {
        // 用户取消
        ElMessage.info('已取消购买')
        return
      }
      
      // 开始购买流程
      const loadingMessage = ElMessage({
        message: '正在创建订单...',
        type: 'info',
        duration: 0,
        customClass: 'buy-loading-message'
      })
      
      try {
        const requestData = {
          steamId: selectedSteamId.value,
          commodityId: commodity.id,
          buyQuantity: 1,
          price: commodity.price,  // 添加商品价格
          autoConfirmPayment: true,  // 自动使用余额支付
          pollPayment: true  // 轮询支付状态
        }
        
        console.log('购买请求数据:', requestData)
        
        // 调用完整购买接口（创建订单+自动支付）
        const response = await axios.post(
          `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/buyCommodity`,
          requestData
        )
        
        console.log('购买响应:', response.data)
        
        loadingMessage.close()
        
        if (response.data.success) {
          const orderData = response.data.data?.order || {}
          const paymentStatus = response.data.data?.payment_status || {}
          const orderNo = orderData.orderNo || '未知'
          const paymentAmount = commodity.price || '未知'
          
          // 检查支付状态
          const payStatus = paymentStatus.payStatus
          let message = ''
          
          if (payStatus === 2) {
            // 支付成功
            message = `购买成功！\n\n订单号：${orderNo}\n金额：¥${paymentAmount}\n状态：支付成功✅\n\n饰品将发送至您的库存。`
          } else if (payStatus === 1) {
            // 支付处理中
            message = `订单已创建！\n\n订单号：${orderNo}\n金额：¥${paymentAmount}\n状态：支付处理中⏳\n\n请稍后查看订单状态。`
          } else {
            // 订单创建成功但支付未完成
            message = `订单创建成功！\n\n订单号：${orderNo}\n金额：¥${paymentAmount}\n\n已自动使用余额支付，请稍后查看订单状态。`
          }
          
          // 显示购买成功信息
          ElMessageBox.alert(
            message,
            '购买完成',
            {
              confirmButtonText: '知道了',
              type: 'success',
              callback: () => {
                ElMessage.success(payStatus === 2 ? '购买成功！' : '订单已创建')
              }
            }
          )
        } else {
          ElMessageBox.alert(
            `购买失败：${response.data.message || '未知错误'}\n\n请检查配置或稍后重试。`,
            '购买失败',
            {
              confirmButtonText: '知道了',
              type: 'error'
            }
          )
        }
      } catch (error) {
        loadingMessage.close()
        console.error('购买商品失败:', error)
        
        const errorMessage = error.response?.data?.message || error.message || '网络错误，请稍后重试'
        
        ElMessageBox.alert(
          `购买失败：${errorMessage}`,
          '购买失败',
          {
            confirmButtonText: '知道了',
            type: 'error'
          }
        )
      }
    }

    // 批量获取改名信息（自动调用，只获取第一条）
    const fetchAllNameTags = async (commodityList) => {
      // 筛选出有改名标签的商品
      const commoditiesWithNameTag = commodityList.filter(item => item.haveNameTag === 1)
      
      if (commoditiesWithNameTag.length === 0) {
        console.log('没有需要获取改名信息的商品')
        return
      }

      // 只自动获取第一条
      console.log(`共有 ${commoditiesWithNameTag.length} 个商品有改名标签，自动获取第一个`)
      
      const commodity = commoditiesWithNameTag[0]
      
      try {
        console.log(`正在获取商品 ${commodity.id} 的改名信息`)
        
        // 调用接口获取详细信息
        const response = await axios.post(
          `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/getWeaponDetail`,
          {
            steamId: selectedSteamId.value,
            id: commodity.id
          }
        )

        if (response.data.success && response.data.data) {
          const detailData = response.data.data.Data
          const nameTags = detailData.NameTags || []
          
          // 缓存改名信息到商品对象中
          commodity.nameTags = nameTags
          commodity.nameTagText = nameTags.length > 0 ? nameTags[0].replace(/^名称标签：[""]?|[""]$/g, '') : ''
          
          console.log(`商品 ${commodity.id} 改名信息:`, nameTags)
        } else {
          console.error(`获取商品 ${commodity.id} 改名信息失败:`, response.data.message)
        }
      } catch (error) {
        console.error(`获取商品 ${commodity.id} 改名信息异常:`, error)
      }
      
      console.log(`自动获取改名信息完成`)
    }

    // 获取单个商品的改名信息（点击按钮时调用）
    const fetchSingleNameTag = async (commodity) => {
      try {
        // 设置加载状态
        commodity.nameTagLoading = true

        console.log('正在获取改名信息，商品ID:', commodity.id)

        // 调用接口获取详细信息
        const response = await axios.post(
          `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/getWeaponDetail`,
          {
            steamId: selectedSteamId.value,
            id: commodity.id
          }
        )

        console.log('改名信息响应:', response.data)

        if (response.data.success && response.data.data) {
          const detailData = response.data.data.Data
          const nameTags = detailData.NameTags || []
          
          // 缓存改名信息到商品对象中
          commodity.nameTags = nameTags
          commodity.nameTagText = nameTags.length > 0 ? nameTags[0].replace(/^名称标签：[""]?|[""]$/g, '') : ''

          if (nameTags.length === 0) {
            ElMessage.info('该商品没有改名信息')
          }
        } else {
          ElMessage.error('获取改名信息失败: ' + (response.data.message || '未知错误'))
        }
      } catch (error) {
        console.error('获取改名信息失败:', error)
        ElMessage.error('获取改名信息失败: ' + (error.response?.data?.message || error.message))
      } finally {
        commodity.nameTagLoading = false
      }
    }

    // 显示印花信息对话框
    const showStickersDialog = (commodity) => {
      const stickers = commodity.stickers || []
      
      if (stickers.length === 0) {
        ElMessage.info('该商品没有印花')
        return
      }

      // 最多显示5个印花
      const displayStickers = stickers.slice(0, 5)

      // 构建印花信息HTML - 横向平铺展示（自适应宽度）
      let stickersHtml = `
        <div style="padding: 20px;">
          <div style="text-align: center; margin-bottom: 20px;">
            <h4 style="margin: 0 0 10px 0; color: #303133; font-size: 16px;">${commodity.commodityName}</h4>
            <p style="margin: 0; color: #909399; font-size: 14px;">印花数量：${stickers.length} 个${stickers.length > 5 ? '（显示前5个）' : ''}</p>
          </div>
          
          <div style="display: flex; justify-content: center; gap: 15px; flex-wrap: nowrap;">
      `
      
      displayStickers.forEach((sticker, index) => {
        stickersHtml += `
          <div style="text-align: center; min-width: 110px; flex-shrink: 0;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; padding: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
              <div style="background: white; border-radius: 8px; padding: 8px; margin-bottom: 8px;">
                <img src="${sticker.ImgUrl}" style="width: 70px; height: 52px; object-fit: contain; display: block; margin: 0 auto;" />
              </div>
              <div style="color: white; font-size: 11px; margin-bottom: 4px;">
                <strong>位置 ${sticker.RawIndex !== null ? sticker.RawIndex + 1 : '-'}</strong>
              </div>
              <div style="background: rgba(255,255,255,0.2); border-radius: 4px; padding: 3px 6px; font-size: 11px; color: white;">
                磨损: ${sticker.Abrade || '-'}
              </div>
              ${sticker.priceV1 ? `
                <div style="margin-top: 6px; background: rgba(255,255,255,0.9); border-radius: 4px; padding: 3px 6px; font-size: 12px; color: #f56c6c; font-weight: 600;">
                  ${sticker.priceV1}
                </div>
              ` : ''}
            </div>
            <div style="margin-top: 6px; font-size: 11px; color: #606266; max-width: 110px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${sticker.Name || '-'}">
              ${sticker.Name || '-'}
            </div>
          </div>
        `
      })
      
      stickersHtml += `
          </div>
        </div>
      `
      
      // 根据印花数量计算对话框宽度（最多5个印花）
      // 每个卡片宽度110px，间距15px，加上对话框内边距和额外空间
      // 计算公式：卡片数量*110 + (卡片数量-1)*15 + 对话框边距和额外空间
      const dialogWidth = displayStickers.length * 110 + (displayStickers.length - 1) * 15 + 160
      
      ElMessageBox({
        title: '印花信息',
        message: stickersHtml,
        dangerouslyUseHTMLString: true,
        confirmButtonText: '关闭',
        customClass: 'stickers-dialog',
        width: `${dialogWidth}px`
      }).catch(() => {
        // 用户点击关闭或取消时，忽略错误
      })
    }

    // 关闭悠悠有品商品列表，返回搜索结果
    const closeYYYPList = () => {
      showYYYPList.value = false
      showSearchResults.value = true
      yyypCommodities.value = []
      yyypCurrentWeapon.value = null
    }

    // 切换搜索结果的展开/折叠
    const toggleSearchResults = () => {
      showSearchResults.value = !showSearchResults.value
    }

    // 切换悠悠有品表格的展开/折叠
    const toggleYYYPList = () => {
      showYYYPTable.value = !showYYYPTable.value
    }

    // 旧的对话框函数（已废弃，保留以防需要）
    const showYYYPCommoditiesDialog_OLD = (row, commodities, total) => {
      // 构建商品列表HTML
      let commoditiesHtml = `
        <div style="max-height: 500px; overflow-y: auto;">
          <p style="margin-bottom: 15px; color: #606266;">
            <strong>武器名称：</strong>${row.market_listing_item_name}<br/>
            <strong>悠悠有品ID：</strong>${row.yyyp_id}<br/>
            <strong>商品总数：</strong>${total} 条
          </p>
          <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
            <thead>
              <tr style="background-color: #f5f7fa; border-bottom: 2px solid #dcdfe6;">
                <th style="padding: 10px; text-align: left; border: 1px solid #dcdfe6;">商品名称</th>
                <th style="padding: 10px; text-align: center; border: 1px solid #dcdfe6; width: 100px;">价格</th>
                <th style="padding: 10px; text-align: center; border: 1px solid #dcdfe6; width: 80px;">磨损</th>
                <th style="padding: 10px; text-align: center; border: 1px solid #dcdfe6; width: 100px;">操作</th>
              </tr>
            </thead>
            <tbody>
      `
      
      if (commodities.length === 0) {
        commoditiesHtml += `
          <tr>
            <td colspan="4" style="padding: 20px; text-align: center; color: #909399;">暂无商品数据</td>
          </tr>
        `
      } else {
        commodities.forEach((item, index) => {
          const price = item.price ? (item.price / 100).toFixed(2) : '-'
          const abrade = item.abrade ? item.abrade.toFixed(4) : '-'
          const commodityUrl = `https://www.youpin898.com/goodInfo?id=${item.id}`
          
          commoditiesHtml += `
            <tr style="border-bottom: 1px solid #ebeef5; ${index % 2 === 0 ? 'background-color: #fafafa;' : ''}">
              <td style="padding: 10px; border: 1px solid #ebeef5;">
                <div style="display: flex; align-items: center;">
                  ${item.iconUrl ? `<img src="${item.iconUrl}" style="width: 40px; height: 30px; margin-right: 10px; object-fit: contain;" />` : ''}
                  <span style="flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${item.commodityName || '-'}</span>
                </div>
              </td>
              <td style="padding: 10px; text-align: center; border: 1px solid #ebeef5;">
                <span style="color: #f56c6c; font-weight: bold;">¥${price}</span>
              </td>
              <td style="padding: 10px; text-align: center; border: 1px solid #ebeef5;">${abrade}</td>
              <td style="padding: 10px; text-align: center; border: 1px solid #ebeef5;">
                <a href="${commodityUrl}" target="_blank" style="color: #409eff; text-decoration: none;">查看详情</a>
              </td>
            </tr>
          `
        })
      }
      
      commoditiesHtml += `
            </tbody>
          </table>
        </div>
      `
      
      ElMessageBox({
        title: '悠悠有品商品列表',
        message: commoditiesHtml,
        dangerouslyUseHTMLString: true,
        confirmButtonText: '关闭',
        customClass: 'yyyp-commodities-dialog',
        width: '900px'
      })
    }

    // 控制popover显示状态
    const activePopoverRow = ref(null)
    
    // 切换popover显示
    const togglePopover = (row) => {
      if (activePopoverRow.value === row) {
        activePopoverRow.value = null
      } else {
        activePopoverRow.value = row
      }
    }
    
    // 选择平台并搜索
    const selectPlatform = (row, platform) => {
      activePopoverRow.value = null // 关闭popover
      
      if (platform === 'yyyp') {
        handleSearchYYYPByRow(row)
      } else if (platform === 'buff') {
        handleSearchBuffByRow(row)
      } else if (platform === 'csfloat') {
        handleSearchCsFloatByRow(row)
      } else if (platform === 'all') {
        handleSearchAllPlatforms(row)
      }
    }

    // 同时搜索悠悠有品和BUFF
    const handleSearchAllPlatforms = async (row) => {
      console.log('=== 开始执行 handleSearchAllPlatforms ===')
      console.log('row数据:', row)
      
      if (!selectedSteamId.value) {
        console.log('没有选择Steam账号，退出')
        ElMessage.warning('请先选择Steam账号')
        return
      }

      // 检查是否有悠悠有品ID或BUFF ID
      const hasYYYPId = row.yyyp_id
      const hasBuffId = row.buff_id
      
      if (!hasYYYPId && !hasBuffId) {
        ElMessage.warning('该武器没有悠悠有品ID和BUFF ID')
        return
      }

      isSearching.value = true
      searchSource.value = 'all'
      
      try {
        ElMessage.info('正在同时搜索悠悠有品和BUFF...')
        
        // 并行请求悠悠有品和BUFF
        const promises = []
        
        if (hasYYYPId) {
          promises.push(handleSearchYYYPByRow(row))
        }
        
        if (hasBuffId) {
          promises.push(handleSearchBuffByRow(row))
        }
        
        await Promise.all(promises)
        
        ElMessage.success('全部平台搜索完成！')
        
      } catch (error) {
        console.error('搜索全部平台失败:', error)
        ElMessage.error('搜索失败，请重试')
      } finally {
        setTimeout(() => {
          isSearching.value = false
          searchSource.value = ''
        }, 300)
      }
    }

    // 通过行数据搜索BUFF
    const handleSearchBuffByRow = async (row) => {
      console.log('=== 开始执行 handleSearchBuffByRow ===')
      console.log('row数据:', row)
      console.log('row.buff_id:', row.buff_id)
      console.log('selectedSteamId.value:', selectedSteamId.value)
      
      if (!row.buff_id) {
        console.log('没有buff_id，退出')
        ElMessage.warning('该武器没有BUFF ID')
        return
      }

      if (!selectedSteamId.value) {
        console.log('没有选择Steam账号，退出')
        ElMessage.warning('请先选择Steam账号')
        return
      }

      console.log('通过验证，开始请求')
      isSearching.value = true
      searchSource.value = 'buff'
      
      try {
        console.log('搜索BUFF:', row.market_listing_item_name, 'ID:', row.buff_id, 'SteamID:', selectedSteamId.value)
        
        // 构建请求数据
        const requestData = {
          steamId: selectedSteamId.value || '',
          goodsId: row.buff_id
        }
        
        const apiUrl = `${API_CONFIG.SPIDER_BASE_URL}/buffSpiderV1/getCommoditiesByGoodsId`
        
        console.log('请求URL:', apiUrl)
        console.log('请求数据:', requestData)
        
        // 调用BUFF商品列表API
        const response = await axios.post(apiUrl, requestData)
        
        console.log('API响应:', response.data)
        
        if (response.data.success) {
          const parsedData = response.data.data
          console.log('获取到BUFF已解析数据:', parsedData)
          
          // 直接使用Spider解析后的数据
          const commodityList = parsedData.commodityList || []
          const totalCount = parsedData.totalCount || 0
          const buyNum = parsedData.buy_num || 0
          const sellNum = parsedData.sell_num || 0
          const rentNum = parsedData.rent_num || 0
          
          console.log('商品列表:', commodityList)
          console.log('在售总数:', totalCount)
          console.log('求购数:', buyNum, '在售数:', sellNum, '租赁数:', rentNum)
          
          // 更新BUFF状态，显示商品列表
          buffCurrentWeapon.value = row
          buffCommodities.value = commodityList
          buffTotalCount.value = totalCount
          buffBuyNum.value = buyNum
          buffRentNum.value = rentNum
          buffCurrentPage.value = 1  // 重置分页到第一页
          showBuffList.value = true
          // showYYYPList.value = false  // 允许同时显示两个列表
          showSearchResults.value = false  // 折叠搜索结果
          
          ElMessage.success(`成功获取 ${commodityList.length} 条商品数据，在售总数: ${totalCount}（求购:${buyNum}, 租赁:${rentNum}）`)
          
          // 预加载图片（相同URL只加载一次）
          preloadImages(commodityList)
          
          // 滚动到商品列表区域
          setTimeout(() => {
            const listElement = document.querySelector('.buff-commodity-list')
            if (listElement) {
              listElement.scrollIntoView({ behavior: 'smooth', block: 'start' })
            }
          }, 100)
          
        } else {
          console.error('API返回失败:', response.data)
          ElMessage.error(response.data.message || '获取商品列表失败')
        }
        
      } catch (error) {
        console.error('搜索BUFF失败 - 完整错误:', error)
        console.error('错误响应:', error.response)
        console.error('错误数据:', error.response?.data)
        
        const errorMessage = error.response?.data?.message || error.message || '搜索失败，请检查网络连接'
        ElMessage.error(errorMessage)
      } finally {
        console.log('请求完成，重置加载状态')
        isSearching.value = false
        searchSource.value = ''
      }
    }

    // 通过行数据搜索CsFloat
    const handleSearchCsFloatByRow = async (row) => {
      if (!row.steam_hash_name) {
        ElMessage.warning('该武器没有Steam Hash Name')
        return
      }

      isSearching.value = true
      searchSource.value = 'csfloat'
      
      try {
        console.log('搜索CsFloat:', row.market_listing_item_name, 'Hash Name:', row.steam_hash_name)
        
        // 对hash name进行URL编码
        const encodedName = encodeURIComponent(row.steam_hash_name)
        
        // 构建CsFloat搜索URL
        const csfloatUrl = `https://csfloat.com/search?name=${encodedName}`
        
        // 在新窗口中打开CsFloat搜索页面
        window.open(csfloatUrl, '_blank')
        
        ElMessage.success(`正在跳转到CsFloat: ${row.market_listing_item_name}`)
        
      } catch (error) {
        console.error('搜索CsFloat失败:', error)
        ElMessage.error('跳转失败,请检查浏览器设置是否允许弹出窗口')
      } finally {
        // 延迟关闭加载状态,给用户反馈
        setTimeout(() => {
          isSearching.value = false
        }, 300)
      }
    }

    const handleClearSearch = () => {
      searchKeyword.value = ''
      searchResults.value = []
      searchSource.value = ''
      selectedExterior.value = ''
      selectedStatTrak.value = 'normal' // 重置为默认值：非StatTrak™
      currentPage.value = 1
      ElMessage.info('已重置搜索')
    }

    const handleViewDetails = (item) => {
      ElMessage.info(`查看详情: ${item.name}`)
      // TODO: 实现详情查看功能
    }

    const handleSizeChange = (val) => {
      pageSize.value = val
      currentPage.value = 1
    }

    const handleCurrentChange = (val) => {
      currentPage.value = val
    }

    // BUFF分页切换
    const handleBuffPageChange = (val) => {
      buffCurrentPage.value = val
    }

    // 悠悠有品分页切换
    const handleYYYPPageChange = (val) => {
      yyypCurrentPage.value = val
    }

    // 页面加载时获取Steam ID列表
    onMounted(async () => {
      await loadSteamIdList()
    })

    return {
      searchKeyword,
      searchResults,
      isSearching,
      searchSource,
      currentPage,
      pageSize,
      paginatedResults,
      filteredResults,
      steamIdList,
      selectedSteamId,
      selectedExterior,
      selectedStatTrak,
      // BUFF商品列表
      buffCommodities,
      buffCurrentWeapon,
      buffTotalCount,
      buffBuyNum,
      buffRentNum,
      showBuffList,
      showBuffTable,
      buffCurrentPage,
      buffPageSize,
      paginatedBuffCommodities,
      toggleBuffList,
      handleRefreshBuff,
      handleBuyBuffCommodity,
      handleBuffPageChange,
      // 悠悠有品商品列表
      yyypCommodities,
      yyypCurrentWeapon,
      yyypTotalCount,
      showYYYPList,
      showYYYPTable,
      yyypCurrentPage,
      yyypPageSize,
      paginatedYYYPCommodities,
      showSearchResults,
      toggleSearchResults,
      toggleYYYPList,
      handleBuyCommodity,
      fetchSingleNameTag,
      showStickersDialog,
      closeYYYPList,
      handleYYYPPageChange,
      handleSearchWeapon,
      handleRefreshSearch,
      handleRefreshYYYP,
      handleSearchYYYPByRow,
      handleSearchBuffByRow,
      handleSearchCsFloatByRow,
      handleSearchAllPlatforms,
      activePopoverRow,
      togglePopover,
      selectPlatform,
      handleClearSearch,
      handleImageError,
      handleViewDetails,
      handleSizeChange,
      handleCurrentChange,
      handleSteamIdChange,
      handleExteriorChange,
      handleStatTrakChange,
      querySearchAsync,
      handleSelect,
      getRarityType,
      getRarityColor,
      getExteriorColor
    }
  }
}
</script>

<style scoped>
.item-search-container {
  position: relative;
  min-height: 100vh;
}

/* 搜索包装器 - 居中或左上角 */
.search-wrapper {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  z-index: 10;
}

.search-wrapper.centered {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90%;
  max-width: 800px;
}

.search-wrapper.top-left {
  margin-bottom: 1.5rem;
  width: 100%;
}

/* 搜索卡片 */
.search-card {
  padding: 2rem;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.search-wrapper.centered .search-card {
  padding: 3rem 2.5rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.search-wrapper.top-left .search-card {
  padding: 1rem 1.5rem;
}

/* 标题样式 */
.search-title {
  text-align: center;
  font-size: 3rem;
  font-weight: 700;
  color: #4CAF50;
  margin: 0 0 2rem 0;
  background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: fadeInDown 0.6s ease-out;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.search-section {
  transition: all 0.5s ease;
}

.search-wrapper.centered .search-section {
  margin-bottom: 0;
}

.search-wrapper.top-left .search-section {
  margin-bottom: 0;
}

/* 搜索控件 */
.search-controls {
  display: flex;
  align-items: stretch;
  gap: 1rem;
  transition: all 0.5s ease;
  flex-direction: row;
  flex-wrap: nowrap;
  align-items: center;
}

.search-controls.compact {
  gap: 0.75rem;
}

/* 按钮组 */
.button-group {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
}

.search-wrapper.top-left .button-group {
  gap: 0.75rem;
}

.search-controls.compact .button-group {
  flex-wrap: nowrap;
}

/* Steam ID 选择框 */
.steam-id-select {
  transition: all 0.5s ease;
  min-width: 180px;
  width: 180px;
}

/* 外观选择框 */
.exterior-select {
  transition: all 0.5s ease;
  min-width: 150px;
  width: 150px;
}

/* StatTrak选择框 */
.stattrak-select {
  transition: all 0.5s ease;
  min-width: 140px;
  width: 140px;
}

/* 搜索输入框 */
.search-input {
  transition: all 0.5s ease;
  min-width: 300px;
  flex: 1;
}

/* el-autocomplete 样式适配 */
.search-input :deep(.el-input__wrapper) {
  background-color: #2a2a2a;
  box-shadow: 0 0 0 1px #444 inset;
}

.search-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #4CAF50 inset;
}

.search-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #4CAF50 inset !important;
}

.search-input :deep(.el-input__inner) {
  color: #fff;
}

.search-wrapper.centered .steam-id-select.large :deep(.el-input__wrapper) {
  padding: 1rem 1.5rem;
  font-size: 1.125rem;
}

.search-wrapper.centered .steam-id-select.large :deep(.el-input__inner) {
  font-size: 1.125rem;
}

.search-wrapper.centered .search-input.large :deep(.el-input__wrapper) {
  padding: 2rem 2.5rem;
  font-size: 2rem;
  height: 80px;
  min-height: 80px;
}

.search-wrapper.centered .search-input.large :deep(.el-input__inner) {
  font-size: 2rem;
  height: 80px;
  min-height: 80px;
}

/* 居中状态下的 autocomplete 样式 */
.search-wrapper.centered .search-input.large :deep(.el-autocomplete) {
  width: 100%;
}

.search-wrapper.centered .search-input.large :deep(.el-input) {
  width: 100%;
}

/* 居中状态下的按钮样式 */
.search-wrapper.centered .button-group {
  width: 100%;
  max-width: 600px;
}

.search-wrapper.centered .button-group .el-button {
  padding: 1rem 2rem;
  font-size: 1.125rem;
  height: auto;
  flex: 1;
  min-width: 160px;
}

.mb-4 {
  margin-bottom: 1rem;
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

.table-card {
  margin-bottom: clamp(1rem, 3vw, 1.25rem);
  animation: fadeInUp 0.5s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.price-text {
  color: #4CAF50;
  font-weight: 600;
}

.no-data {
  color: #888;
}

.id-text {
  color: #4CAF50;
  font-family: monospace;
  font-weight: 500;
}

.rarity-text {
  font-weight: 600;
  text-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
}

.weapon-name-text {
  font-weight: 500;
  text-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
}

.hash-name-text {
  color: #64B5F6;
  font-weight: 500;
  font-size: 0.95rem;
}

.clickable-item-name {
  color: #ffffff;
  cursor: pointer;
  transition: all 0.3s ease;
}

.clickable-item-name:hover {
  color: #4CAF50;
  transform: translateX(2px);
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: nowrap;
  justify-content: center;
  align-items: center;
}

.pagination-container {
  display: flex;
  justify-content: center;
  padding: clamp(1rem, 2vw, 1.5rem) 0;
}

.no-results-card {
  padding: clamp(2rem, 4vw, 3rem);
  text-align: center;
  animation: fadeInUp 0.5s ease-out;
}

/* Element Plus 组件深色主题适配 */
:deep(.el-input__wrapper) {
  background-color: #2a2a2a;
  box-shadow: 0 0 0 1px #444 inset;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #4CAF50 inset;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #4CAF50 inset !important;
}

:deep(.el-input__inner) {
  color: #fff;
}

:deep(.el-select .el-input__wrapper) {
  background-color: #2a2a2a;
}

:deep(.el-button) {
  font-size: clamp(0.75rem, 1vw, 0.875rem);
  padding: clamp(0.5rem, 1vw, 0.625rem) clamp(0.75rem, 1.5vw, 1rem);
}

:deep(.el-table) {
  background-color: transparent;
  color: #fff;
}

:deep(.el-table th.el-table__cell) {
  background-color: #2a2a2a;
  color: #fff;
  border-bottom: 1px solid #444;
}

:deep(.el-table tr) {
  background-color: #1e1e1e;
}

:deep(.el-table td.el-table__cell) {
  border-bottom: 1px solid #333;
}

:deep(.el-table__body tr:hover > td) {
  background-color: #2a2a2a !important;
}

:deep(.el-pagination) {
  color: #fff;
}

:deep(.el-pagination button) {
  background-color: #2a2a2a;
  color: #fff;
}

:deep(.el-pagination .el-pager li) {
  background-color: #2a2a2a;
  color: #fff;
}

:deep(.el-pagination .el-pager li.is-active) {
  background-color: #4CAF50;
  color: #fff;
}

/* 自动完成下拉框样式 */
.autocomplete-item {
  padding: 0;
  color: #fff;
  white-space: normal !important;
  word-wrap: break-word !important;
  word-break: break-word !important;
  line-height: 1.5;
  overflow: visible !important;
  text-overflow: clip !important;
}

:deep(.weapon-autocomplete-popper) {
  background-color: #2a2a2a !important;
  border: 1px solid #444 !important;
  max-width: 800px !important;
  min-width: 400px !important;
  width: auto !important;
}

:deep(.weapon-autocomplete-popper .el-autocomplete-suggestion__wrap) {
  background-color: #2a2a2a;
  max-height: 500px !important;
  overflow-y: auto;
}

:deep(.weapon-autocomplete-popper .el-autocomplete-suggestion__list) {
  padding: 0;
}

:deep(.weapon-autocomplete-popper li) {
  color: #fff !important;
  background-color: #2a2a2a !important;
  white-space: normal !important;
  word-wrap: break-word !important;
  word-break: break-word !important;
  line-height: 1.6 !important;
  padding: 0.75rem 1rem !important;
  min-height: auto !important;
  height: auto !important;
  overflow: visible !important;
  text-overflow: clip !important;
  border-bottom: 1px solid #333;
}

:deep(.weapon-autocomplete-popper li:hover) {
  background-color: #3a3a3a !important;
}

:deep(.weapon-autocomplete-popper li.highlighted) {
  background-color: #3a3a3a !important;
}

:deep(.el-autocomplete-suggestion) {
  background-color: #2a2a2a !important;
}

:deep(.el-autocomplete-suggestion__wrap) {
  background-color: #2a2a2a;
}

:deep(.el-autocomplete-suggestion li) {
  color: #fff;
  background-color: #2a2a2a;
  white-space: normal !important;
  word-wrap: break-word !important;
  line-height: 1.5 !important;
  padding: 0.75rem 1rem !important;
  height: auto !important;
}

:deep(.el-autocomplete-suggestion li:hover) {
  background-color: #3a3a3a !important;
}

:deep(.el-autocomplete-suggestion li.highlighted) {
  background-color: #3a3a3a !important;
}

@media (max-width: 768px) {
  .search-wrapper.centered {
    width: 95%;
    max-width: none;
  }
  
  .search-wrapper.centered .search-card {
    padding: 2rem 1.5rem;
  }
  
  .steam-id-select.large,
  .search-input.large {
    min-width: 100%;
  }
  
  .search-controls {
    flex-wrap: wrap;
  }
  
  .button-group {
    width: 100%;
  }
  
  .button-group .el-button {
    flex: 1;
    min-width: 100px;
  }
  
  .stats-grid-3x2 {
    grid-template-columns: 1fr;
  }
  
  .stat-item {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }
  
  :deep(.yyyp-commodities-dialog) {
    width: 95% !important;
  }
}

/* 折叠头部样式 */
.collapse-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background-color: var(--el-fill-color-light);
  border-bottom: 1px solid var(--el-border-color);
  cursor: pointer;
  border-radius: 8px 8px 0 0;
  transition: all 0.3s ease;
  user-select: none;
}

.collapse-header:hover {
  background-color: var(--el-fill-color);
}

.collapse-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--el-text-color-primary);
  font-weight: 600;
  font-size: 1.1rem;
}

.collapse-title .el-icon {
  font-size: 1.2rem;
  transition: transform 0.3s ease;
}

/* 表格头部样式（无折叠时） */
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background-color: var(--el-fill-color-light);
  border-bottom: 1px solid var(--el-border-color);
  border-radius: 8px 8px 0 0;
  margin-bottom: 0;
}

.table-title {
  color: var(--el-text-color-primary);
  font-weight: 600;
  font-size: 1.1rem;
}

/* BUFF商品列表样式 */
.buff-commodity-list {
  margin-top: 1.5rem;
  animation: fadeInUp 0.5s ease-out;
}

/* BUFF折叠头部样式 */
.buff-collapse-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background-color: var(--el-fill-color-light);
  border-bottom: 1px solid var(--el-border-color);
  cursor: pointer;
  border-radius: 8px 8px 0 0;
  transition: all 0.3s ease;
  user-select: none;
}

.buff-collapse-header:hover {
  background-color: var(--el-fill-color);
}

.buff-collapse-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.buff-collapse-title {
  color: var(--el-text-color-primary);
  font-weight: 600;
  font-size: 1.1rem;
}

.buff-weapon-info {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

.buff-weapon-info .weapon-name {
  font-weight: 600;
  color: var(--el-color-primary);
  font-size: 1.1rem;
}

.buff-weapon-info .weapon-id {
  color: var(--el-text-color-secondary);
  font-size: 0.9rem;
}

.buff-weapon-info .commodity-count {
  color: var(--el-color-success);
  font-weight: 600;
}

.buff-weapon-info .total-count {
  color: var(--el-color-primary);
  font-weight: 600;
  font-size: 1rem;
}

.buff-weapon-info .buy-count {
  color: var(--el-color-warning);
  font-weight: 600;
}

.buff-weapon-info .rent-count {
  color: var(--el-text-color-secondary);
  font-weight: 600;
}

:deep(.buff-commodity-list .el-table) {
  background-color: transparent;
}

:deep(.buff-commodity-list .el-table__header-wrapper) {
  background-color: var(--el-fill-color-light);
}

:deep(.buff-commodity-list .el-table__row:hover) {
  background-color: var(--el-fill-color-light);
}

/* 悠悠有品商品列表样式 */
.yyyp-commodity-list {
  margin-top: 1.5rem;
  animation: fadeInUp 0.5s ease-out;
}

/* 悠悠有品折叠头部样式 */
.yyyp-collapse-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background-color: var(--el-fill-color-light);
  border-bottom: 1px solid var(--el-border-color);
  cursor: pointer;
  border-radius: 8px 8px 0 0;
  transition: all 0.3s ease;
  user-select: none;
}

.yyyp-collapse-header:hover {
  background-color: var(--el-fill-color);
}

.yyyp-collapse-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.yyyp-collapse-title {
  color: var(--el-text-color-primary);
  font-weight: 600;
  font-size: 1.1rem;
}

.collapse-icon {
  color: var(--el-text-color-primary);
  font-size: 1.2rem;
  transition: transform 0.3s ease;
}

.yyyp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 2px solid var(--el-border-color);
  margin-bottom: 1rem;
}

.yyyp-header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.yyyp-header h3 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--el-text-color-primary);
}

.yyyp-weapon-info {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

.yyyp-weapon-info .weapon-name {
  font-weight: 600;
  color: var(--el-color-primary);
  font-size: 1.1rem;
}

.yyyp-weapon-info .weapon-id {
  color: var(--el-text-color-secondary);
  font-size: 0.9rem;
}

.yyyp-weapon-info .commodity-count {
  color: var(--el-color-success);
  font-weight: 600;
}

.yyyp-weapon-info .total-count {
  color: var(--el-color-primary);
  font-weight: 600;
  font-size: 1rem;
}

.commodity-icon {
  width: 80px;
  height: 60px;
  object-fit: contain;
  border-radius: 4px;
  background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
  padding: 5px;
}

.price-text {
  color: #f56c6c;
  font-weight: bold;
  font-size: 1.1rem;
}

:deep(.yyyp-commodity-list .el-table) {
  background-color: transparent;
}

:deep(.yyyp-commodity-list .el-table__header-wrapper) {
  background-color: var(--el-fill-color-light);
}

:deep(.yyyp-commodity-list .el-table__row:hover) {
  background-color: var(--el-fill-color-light);
}

/* 印花对话框样式 */
:deep(.stickers-dialog) {
  border-radius: 8px;
}

:deep(.stickers-dialog .el-message-box__header) {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  padding: 20px;
  border-bottom: none;
}

:deep(.stickers-dialog .el-message-box__title) {
  font-size: 18px;
  font-weight: 600;
  color: white;
}

:deep(.stickers-dialog .el-message-box__headerbtn .el-message-box__close) {
  color: white;
  font-size: 20px;
}

:deep(.stickers-dialog .el-message-box__headerbtn .el-message-box__close:hover) {
  color: #f5f5f5;
}

:deep(.stickers-dialog .el-message-box__content) {
  padding: 20px;
  max-height: 600px;
  overflow-y: auto;
}

:deep(.stickers-dialog .el-message-box__btns) {
  padding: 15px 20px;
  border-top: 1px solid #dcdfe6;
}

/* 改名对话框样式 */
:deep(.nametag-dialog) {
  border-radius: 8px;
}

:deep(.nametag-dialog .el-message-box__header) {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  padding: 20px;
  border-bottom: none;
}

:deep(.nametag-dialog .el-message-box__title) {
  font-size: 18px;
  font-weight: 600;
  color: white;
}

:deep(.nametag-dialog .el-message-box__headerbtn .el-message-box__close) {
  color: white;
  font-size: 20px;
}

:deep(.nametag-dialog .el-message-box__headerbtn .el-message-box__close:hover) {
  color: #f5f5f5;
}

:deep(.nametag-dialog .el-message-box__content) {
  padding: 0;
}

:deep(.nametag-dialog .el-message-box__btns) {
  padding: 15px 20px;
  border-top: 1px solid #dcdfe6;
}

/* 搜索平台选择器样式 */
.search-platform-selector {
  padding: 8px;
}

.selector-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.selector-buttons .el-button {
  flex: 1;
  min-width: 80px;
  font-weight: 600;
}

.selector-buttons .buff-button {
  background-color: #1a1a1a;
  border-color: #1a1a1a;
  color: white;
}

.selector-buttons .buff-button:hover {
  background-color: #2a2a2a;
  border-color: #2a2a2a;
}

.selector-buttons .buff-button:active {
  background-color: #0a0a0a;
  border-color: #0a0a0a;
}

.selector-buttons .csfloat-button {
  background-color: #67c23a;
  border-color: #67c23a;
  color: white;
}

.selector-buttons .csfloat-button:hover {
  background-color: #85ce61;
  border-color: #85ce61;
}

.selector-buttons .csfloat-button:active {
  background-color: #5daf34;
  border-color: #5daf34;
}

.selector-buttons .all-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  font-weight: 700;
  flex-basis: 100%;
  margin-top: 4px;
}

.selector-buttons .all-button:hover {
  background: linear-gradient(135deg, #7c8ff0 0%, #8b5bb8 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.selector-buttons .all-button:active {
  background: linear-gradient(135deg, #5568d3 0%, #63408c 100%);
  transform: translateY(0);
}

/* Popover 样式优化 */
:deep(.el-popover) {
  padding: 0 !important;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}
</style>
