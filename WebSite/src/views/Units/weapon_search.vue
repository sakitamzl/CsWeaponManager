<template>
  <!-- 搜索饰品组件 -->
  <div class="weapon-search-component">
    <div class="search-section">
      <h2 class="section-title">搜索饰品</h2>
    
      <div class="search-container">
        <div class="search-filters">
          <el-select 
            v-model="filters.weaponType" 
            placeholder="选择武器类型"
            clearable
            style="width: 200px;"
            @change="handleWeaponTypeChange"
          >
            <el-option label="全部武器" value="" />
            <el-option label="手枪" value="手枪" />
            <el-option label="步枪" value="步枪" />
            <el-option label="狙击步枪" value="狙击步枪" />
            <el-option label="冲锋枪" value="冲锋枪" />
            <el-option label="霰弹枪" value="霰弹枪" />
            <el-option label="机枪" value="机枪" />
            <el-option label="挂件" value="挂件" />
            <el-option label="挂件（纪念品）" value="挂件（纪念品）" />
            <el-option label="匕首" value="匕首" />
            <el-option label="手套" value="手套" />
            <el-option label="探员" value="探员" />
            <el-option label="印花" value="印花" />
            <el-option label="涂鸦" value="涂鸦" />
            <el-option label="音乐盒" value="音乐盒" />
            <el-option label="收藏品" value="收藏品" />
            <el-option label="容器" value="容器" />
          </el-select>
          
          <el-select 
            v-model="filters.weaponName" 
            placeholder="选择武器名称"
            clearable
            filterable
            style="width: 200px;"
            :loading="isLoadingWeaponNames"
            @focus="loadWeaponNamesIfNeeded"
          >
            <el-option label="全部" value="" />
            <el-option 
              v-for="name in weaponNameList" 
              :key="name" 
              :label="name" 
              :value="name"
            />
          </el-select>
          
          <el-select 
            v-model="filters.rarity" 
            placeholder="选择稀有度"
            clearable
            style="width: 200px;"
          >
            <el-option label="全部稀有度" value="" />
            <el-option label="违禁" value="违禁">
              <span :style="{ color: getRarityColor('违禁'), fontWeight: 600 }">违禁</span>
            </el-option>
            <el-option label="隐秘" value="隐秘">
              <span :style="{ color: getRarityColor('隐秘'), fontWeight: 600 }">隐秘</span>
            </el-option>
            <el-option label="保密" value="保密">
              <span :style="{ color: getRarityColor('保密'), fontWeight: 600 }">保密</span>
            </el-option>
            <el-option label="受限" value="受限">
              <span :style="{ color: getRarityColor('受限'), fontWeight: 600 }">受限</span>
            </el-option>
            <el-option label="军规级" value="军规级">
              <span :style="{ color: getRarityColor('军规级'), fontWeight: 600 }">军规级</span>
            </el-option>
            <el-option label="工业级" value="工业级">
              <span :style="{ color: getRarityColor('工业级'), fontWeight: 600 }">工业级</span>
            </el-option>
            <el-option label="消费级" value="消费级">
              <span :style="{ color: getRarityColor('消费级'), fontWeight: 600 }">消费级</span>
            </el-option>
            <el-option label="普通级" value="普通级">
              <span :style="{ color: getRarityColor('普通级'), fontWeight: 600 }">普通级</span>
            </el-option>
          </el-select>
          
          <el-input 
            v-model.number="filters.priceMin" 
            placeholder="最低价格"
            type="number"
            clearable
            style="width: 150px;"
            class="no-spinner"
          />
          
          <el-input 
            v-model.number="filters.priceMax" 
            placeholder="最高价格"
            type="number"
            clearable
            style="width: 150px;"
            class="no-spinner"
          />
          
          <el-input 
            v-model.number="filters.minOnSaleCount" 
            placeholder="最小在售数量"
            type="number"
            clearable
            style="width: 150px;"
            class="no-spinner"
          />
        </div>
        
        <el-input
          v-model="keyword"
          placeholder="搜索饰品名称..."
          prefix-icon="Search"
          class="weapon-search-input"
          @keyup.enter="handleSearch"
          clearable
        >
          <template #append>
            <el-button 
              type="primary" 
              @click="handleSearch" 
              :loading="isSearching"
            >
              搜索
            </el-button>
          </template>
        </el-input>
      </div>

      <!-- 搜索结果表格 -->
      <div v-if="searchResults.length > 0" class="search-results-table">
        <div class="results-header" @click="toggleResults">
          <span class="results-title">
            搜索结果 ({{ searchResults.length }} 件)
          </span>
          <div class="results-actions" @click.stop>
            <el-button 
              type="success" 
              size="small"
              @click="handleAddAll"
              :disabled="searchResults.length === 0"
            >
              <el-icon><Document /></el-icon>
              一键添加全部
            </el-button>
            <el-button 
              type="text" 
              size="small"
              @click="handleClear"
            >
              清除结果
            </el-button>
            <el-button 
              type="text" 
              class="collapse-indicator"
            >
              <el-icon :size="16">
                <ArrowUp v-if="!isCollapsed" />
                <ArrowDown v-else />
              </el-icon>
            </el-button>
          </div>
        </div>
        
        <div v-show="!isCollapsed">
          <el-table 
              :data="searchResults" 
              style="width: 100%"
              :row-class-name="getRowClassName"
            >
            <el-table-column type="index" label="#" width="60" align="center" />
            
            <el-table-column label="饰品名称" min-width="250" show-overflow-tooltip>
              <template #default="{ row }">
                <span class="weapon-name">{{ row.market_listing_item_name }}</span>
              </template>
            </el-table-column>
            
            <el-table-column label="武器类型" width="120" align="center">
              <template #default="{ row }">
                <el-tag size="small" type="info">{{ row.weapon_type || '-' }}</el-tag>
              </template>
            </el-table-column>
            
            <el-table-column label="稀有度" width="100" align="center">
              <template #default="{ row }">
                <span 
                  v-if="row.rarity"
                  class="rarity-tag"
                  :style="{ color: getRarityColor(row.rarity), fontWeight: 600 }"
                >
                  {{ row.rarity }}
                </span>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>
            
            <el-table-column label="价格" width="100" align="center">
              <template #default="{ row }">
                <span class="price-text" v-if="platformType === 'youpin' && row.yyyp_Price">
                  ¥{{ row.yyyp_Price }}
                </span>
                <span class="price-text" v-else-if="platformType === 'buff' && row.buff_Price">
                  ¥{{ row.buff_Price }}
                </span>
                <span class="price-text" v-else-if="platformType === 'steam' && row.yyyp_Price">
                  ¥{{ row.yyyp_Price }}
                </span>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>
            
            <el-table-column label="在售数量" width="100" align="center">
              <template #default="{ row }">
                <span class="count-text" v-if="platformType === 'youpin' && row.yyyp_OnSaleCount">
                  {{ row.yyyp_OnSaleCount }}
                </span>
                <span class="count-text" v-else-if="platformType === 'buff' && row.buff_OnSaleCount">
                  {{ row.buff_OnSaleCount }}
                </span>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>
            
            <el-table-column v-if="platformType === 'youpin'" label="悠悠有品ID" width="130" align="center">
              <template #default="{ row }">
                <el-tag type="warning" v-if="row.yyyp_id">{{ row.yyyp_id }}</el-tag>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>
            
            <el-table-column v-if="platformType === 'buff'" label="BUFF ID" width="110" align="center">
              <template #default="{ row }">
                <el-tag type="info" v-if="row.buff_id">{{ row.buff_id }}</el-tag>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>
            
            <el-table-column v-if="platformType === 'steam'" label="Steam Hash Name" width="220" align="center">
              <template #default="{ row }">
                <el-tag type="info" v-if="row.steam_hash_name">{{ row.steam_hash_name }}</el-tag>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="120" align="center" fixed="right">
              <template #default="{ row }">
                <el-button 
                  type="primary" 
                  size="small"
                  @click="handleAddWeapon(row)"
                  :disabled="!getWeaponIdByPlatform(row)"
                >
                  添加ID
                </el-button>
              </template>
            </el-table-column>
            </el-table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Document, ArrowUp, ArrowDown } from '@element-plus/icons-vue'
import axios from 'axios'
import { API_CONFIG } from '@/config/api'

// Props
const props = defineProps({
  platformType: {
    type: String,
    required: true,
    default: 'youpin'
  }
})

// Emits
const emit = defineEmits(['add-weapon', 'add-all-weapons'])

// 搜索相关状态
const keyword = ref('')
const searchResults = ref([])
const isSearching = ref(false)
const filters = ref({
  weaponType: '',
  weaponName: '',
  rarity: '',
  priceMin: null,
  priceMax: null,
  minOnSaleCount: null
})
const weaponNameList = ref([])
const isLoadingWeaponNames = ref(false)
const isCollapsed = ref(false)
const currentPage = ref(1)
const pageSize = ref(50)
const hasMore = ref(true)
const isLoadingMore = ref(false)
let scrollTimer = null

// 切换搜索结果折叠
const toggleResults = () => {
  isCollapsed.value = !isCollapsed.value
}

// 武器类型改变时的处理
const handleWeaponTypeChange = async (value) => {
  // 清空武器名称选择
  filters.value.weaponName = ''
  // 清空武器名称列表
  weaponNameList.value = []
  // 加载对应类型的武器名称
  await loadWeaponNames(value)
}

// 加载武器名称列表
const loadWeaponNames = async (weaponType) => {
  isLoadingWeaponNames.value = true
  
  try {
    const params = {}
    
    // 如果指定了武器类型，添加到参数中；否则获取全部
    if (weaponType) {
      params.weaponType = weaponType
    }
    
    const response = await axios.get(`${API_CONFIG.BASE_URL}/webSelectWeaponV1/getWeaponNames`, {
      params: params
    })
    
    if (response.data.success) {
      weaponNameList.value = response.data.data || []
      console.log(`✅ 加载武器名称列表: ${weaponNameList.value.length} 个`, weaponType ? `(类型: ${weaponType})` : '(全部)')
    } else {
      ElMessage.error('获取武器名称失败')
    }
  } catch (error) {
    console.error('获取武器名称失败:', error)
    ElMessage.error('获取武器名称失败')
  } finally {
    isLoadingWeaponNames.value = false
  }
}

// 武器名称下拉框聚焦时，如果列表为空且没有选择武器类型，加载全部武器名称
const loadWeaponNamesIfNeeded = async () => {
  // 如果已经有数据，不重复加载
  if (weaponNameList.value.length > 0) {
    return
  }
  
  // 如果没有选择武器类型，加载全部武器名称
  if (!filters.value.weaponType) {
    await loadWeaponNames(null)
  }
}

// 搜索饰品（重置并开始新搜索）
const handleSearch = async () => {
  // 验证价格区间
  if (filters.value.priceMin !== null && 
      filters.value.priceMax !== null &&
      filters.value.priceMin > filters.value.priceMax) {
    ElMessage.warning('最低价格不能大于最高价格')
    return
  }
  
  // 重置分页状态
  currentPage.value = 1
  searchResults.value = []
  hasMore.value = true
  
  // 执行搜索
  await loadWeaponData()
}

// 加载饰品数据
const loadWeaponData = async () => {
  if (!hasMore.value && currentPage.value > 1) {
    return
  }
  
  const loading = currentPage.value === 1
  if (loading) {
    isSearching.value = true
  } else {
    isLoadingMore.value = true
  }
  
  try {
    const params = {
      page: currentPage.value,
      limit: pageSize.value
    }
    
    // 使用传入的平台类型
    params.platformType = props.platformType
    
    // 添加关键词（如果有）
    if (keyword.value && keyword.value.trim()) {
      params.keyword = keyword.value.trim()
    }
    
    // 添加武器类型过滤（如果有）
    if (filters.value.weaponType) {
      params.weaponType = filters.value.weaponType
    }
    
    // 添加武器名称过滤（如果有）
    if (filters.value.weaponName) {
      params.weaponName = filters.value.weaponName
    }
    
    // 添加稀有度过滤（如果有）
    if (filters.value.rarity) {
      params.rarity = filters.value.rarity
    }
    
    // 添加价格过滤
    if (filters.value.priceMin !== null && filters.value.priceMin !== '') {
      params.priceMin = filters.value.priceMin
    }
    if (filters.value.priceMax !== null && filters.value.priceMax !== '') {
      params.priceMax = filters.value.priceMax
    }
    
    // 添加最小在售数量过滤
    if (filters.value.minOnSaleCount !== null && filters.value.minOnSaleCount !== '') {
      params.minOnSaleCount = filters.value.minOnSaleCount
    }
    
    const response = await axios.get(`${API_CONFIG.BASE_URL}/webSelectWeaponV1/searchWeaponDetail`, {
      params: params
    })
    
    if (response.data.success) {
      const newData = response.data.data || []
      
      if (currentPage.value === 1) {
        // 首次搜索，替换数据
        searchResults.value = newData
        if (newData.length === 0) {
          ElMessage.info('未找到匹配的饰品')
          hasMore.value = false
        } else {
          ElMessage.success(`找到 ${newData.length} 件饰品`)
        }
      } else {
        // 追加数据
        searchResults.value.push(...newData)
        console.log(`📥 追加 ${newData.length} 条数据，总计 ${searchResults.value.length} 条`)
      }
      
      // 判断是否还有更多数据
      hasMore.value = newData.length >= pageSize.value
      
      console.log('📊 加载状态', {
        hasMore: hasMore.value,
        currentTotal: searchResults.value.length,
        newDataLength: newData.length,
        pageSize: pageSize.value,
        currentPage: currentPage.value
      })
    } else {
      ElMessage.error(response.data.message || '搜索失败')
    }
  } catch (error) {
    console.error('搜索饰品失败:', error)
    const errorMessage = error.response?.data?.message || error.message || '搜索饰品失败'
    ElMessage.error(errorMessage)
  } finally {
    isSearching.value = false
    isLoadingMore.value = false
  }
}

// 加载更多数据
const loadMoreWeapons = async () => {
  if (isLoadingMore.value || !hasMore.value) {
    return
  }
  
  console.log('🔄 开始加载更多', {
    currentPage: currentPage.value,
    hasMore: hasMore.value,
    isLoadingMore: isLoadingMore.value
  })
  
  currentPage.value++
  await loadWeaponData()
  
  // 等待 DOM 更新
  await nextTick()
}


// 清除搜索结果
const handleClear = () => {
  searchResults.value = []
  keyword.value = ''
  filters.value = {
    weaponType: '',
    weaponName: '',
    rarity: '',
    priceMin: null,
    priceMax: null,
    minOnSaleCount: null
  }
  weaponNameList.value = []
  currentPage.value = 1
  hasMore.value = true
}

// 添加单个饰品
const handleAddWeapon = (row) => {
  const id = getWeaponIdByPlatform(row)
  const name = row.market_listing_item_name
  
  if (!id || !name) {
    ElMessage.warning('该饰品没有对应平台的ID')
    return
  }
  
  emit('add-weapon', { id: id.toString(), name })
}

// 一键添加全部饰品ID
const handleAddAll = () => {
  if (!searchResults.value || searchResults.value.length === 0) {
    ElMessage.warning('没有可添加的饰品')
    return
  }
  
  const weaponsToAdd = []
  searchResults.value.forEach(row => {
    const id = getWeaponIdByPlatform(row)
    const name = row.market_listing_item_name
    
    if (id && name) {
      weaponsToAdd.push({ id: id.toString(), name })
    }
  })
  
  if (weaponsToAdd.length > 0) {
    emit('add-all-weapons', weaponsToAdd)
  } else {
    ElMessage.warning('没有可添加的饰品ID')
  }
}

// 根据平台类型获取对应的饰品ID
const getWeaponIdByPlatform = (row) => {
  if (props.platformType === 'buff') {
    return row.buff_id
  } else {
    if (props.platformType === 'steam') {
      return row.steam_hash_name || row.steamHashName || row.en_weapon_name
    }
    return row.yyyp_id
  }
}

// 获取稀有度颜色
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

// 表格行类名
const getRowClassName = ({ row, rowIndex }) => {
  return rowIndex % 2 === 0 ? 'even-row' : 'odd-row'
}

// 处理页面滚动事件（监听 window 滚动，因为表格可能没有自己的滚动容器）
const handlePageScroll = () => {
  // 如果没有搜索结果，不处理滚动
  if (searchResults.value.length === 0) {
    return
  }
  
  // 如果正在加载或没有更多数据，不处理
  if (isLoadingMore.value || !hasMore.value) {
    return
  }
  
  // 如果表格区域被折叠，不处理
  if (isCollapsed.value) {
    return
  }
  
  // 防抖处理
  if (scrollTimer) {
    clearTimeout(scrollTimer)
  }
  
  scrollTimer = setTimeout(() => {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop
    const scrollHeight = document.documentElement.scrollHeight
    const clientHeight = window.innerHeight
    const distanceToBottom = scrollHeight - scrollTop - clientHeight
    
    console.log('📏 页面滚动位置检查', {
      scrollTop: Math.round(scrollTop),
      scrollHeight,
      clientHeight,
      distanceToBottom: Math.round(distanceToBottom),
      hasMore: hasMore.value,
      isLoadingMore: isLoadingMore.value,
      currentPage: currentPage.value,
      resultsCount: searchResults.value.length
    })
    
    // 滚动到底部触发加载更多（距离底部200px时触发）
    if (distanceToBottom < 200 && hasMore.value && !isLoadingMore.value) {
      console.log('✅ 触发加载更多数据')
      loadMoreWeapons()
    }
  }, 100) // 100ms 防抖延迟
}

// 组件挂载时添加滚动监听
onMounted(() => {
  window.addEventListener('scroll', handlePageScroll)
})

// 组件卸载时移除滚动监听
onUnmounted(() => {
  window.removeEventListener('scroll', handlePageScroll)
  if (scrollTimer) {
    clearTimeout(scrollTimer)
  }
})

// 暴露方法给父组件
defineExpose({
  handleClear,
  handleSearch,
  searchResults
})
</script>

<style scoped>
.weapon-search-component {
  width: 100%;
}

.search-section {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background-color: #252525;
  border-radius: 0.75rem;
  border: 1px solid #333;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #fff;
  margin: 0 0 1.5rem 0;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #333;
}

.search-container {
  margin-bottom: 1.5rem;
}

.search-filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.weapon-search-input {
  width: 100%;
}

.no-spinner :deep(input[type="number"]::-webkit-outer-spin-button),
.no-spinner :deep(input[type="number"]::-webkit-inner-spin-button) {
  -webkit-appearance: none;
  margin: 0;
}

.no-spinner :deep(input[type="number"]) {
  appearance: textfield;
  -moz-appearance: textfield;
}

.search-results-table {
  margin-top: 1rem;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background-color: #2a2a2a;
  border-radius: 0.5rem 0.5rem 0 0;
  border: 1px solid #333;
  border-bottom: none;
  cursor: pointer;
}

.results-header:hover {
  background-color: rgba(255, 255, 255, 0.03);
}

.results-title {
  font-size: 1rem;
  font-weight: 600;
  color: #4CAF50;
}

.results-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.collapse-indicator {
  padding: 0;
  margin-left: 0.5rem;
}

.price-text {
  color: #67C23A;
  font-weight: 600;
  font-size: 0.95rem;
}

.count-text {
  color: #409EFF;
  font-weight: 500;
  font-size: 0.9rem;
}

.rarity-tag {
  font-weight: 600;
  font-size: 0.9rem;
  text-shadow: 0 0 2px rgba(0, 0, 0, 0.3);
}

.weapon-name {
  color: #fff;
  font-weight: 500;
}

.no-data {
  color: #666;
  font-size: 0.875rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-section {
    padding: 1rem;
  }

  .search-filters {
    flex-direction: column;
    gap: 0.75rem;
  }

  .search-filters > * {
    width: 100% !important;
  }
}
</style>

