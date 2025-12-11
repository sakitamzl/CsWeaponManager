<template>
  <div class="item-search-container">
    <el-card class="search-card">
      <!-- 搜索区域 -->
      <div class="search-section">
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
        </div>
        
        <el-input
          v-model="keyword"
          placeholder="搜索饰品名称..."
          prefix-icon="Search"
          class="weapon-search-input"
          @keyup.enter="performSearch"
          clearable
        >
          <template #append>
            <el-button 
              type="primary" 
              @click="performSearch" 
              :loading="isSearching"
            >
              搜索
            </el-button>
          </template>
        </el-input>
      </div>

      <!-- 搜索结果 -->
      <div v-if="searchResults.length > 0" class="results-section">
        <div class="results-header">
          <span class="results-title">搜索结果 ({{ searchResults.length }} 件)</span>
          <el-button 
            type="text" 
            size="small"
            @click="handleClear"
          >
            清除结果
          </el-button>
        </div>
        
        <el-table 
          :data="searchResults" 
          style="width: 100%"
          stripe
        >
          <el-table-column type="index" label="#" width="60" align="center" />
          
          <el-table-column label="饰品名称" min-width="300" show-overflow-tooltip>
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
              <span v-else>-</span>
            </template>
          </el-table-column>
          
          <el-table-column label="CSQAQ ID" width="150" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.csqaq_id" type="success" size="large">
                {{ row.csqaq_id }}
              </el-tag>
              <el-tag v-else type="info" size="small">未映射</el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="悠悠有品价格" width="130" align="center">
            <template #default="{ row }">
              <span v-if="row.yyyp_Price" class="price">¥{{ row.yyyp_Price }}</span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          
          <el-table-column label="在售数量" width="110" align="center">
            <template #default="{ row }">
              {{ row.on_sale_count || 0 }}
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="160" align="center" fixed="right">
            <template #default="{ row }">
              <el-button 
                type="primary" 
                size="small"
                @click="handleSearchCSQAQ(row)"
                :disabled="!row.csqaq_id"
                :loading="searchingItems[row.csqaq_id]"
              >
                搜索
              </el-button>
              <el-button 
                type="success" 
                size="small"
                @click="handleOpenCSQAQ(row)"
                :disabled="!row.csqaq_id"
              >
                跳转QAQ
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 空状态 -->
      <div v-if="!isSearching && searchResults.length === 0 && hasSearched" class="empty-state">
        <el-empty description="未找到相关饰品" />
      </div>

      <!-- 详细信息区域 -->
      <div v-if="currentItemDetail" class="detail-section-wrapper">
        <el-card class="detail-card">
          <template #header>
            <div class="detail-card-header">
              <span>饰品详细信息</span>
              <el-button type="text" @click="closeDetail">
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
          </template>

          <div v-if="loadingDetail" class="detail-loading">
            <el-icon class="is-loading" :size="40"><Loading /></el-icon>
            <p>加载中...</p>
          </div>
          
          <div v-else class="detail-content">
        <div class="detail-header">
          <img 
            v-if="currentItemDetail.goods_info.img" 
            :src="currentItemDetail.goods_info.img" 
            class="item-image"
            alt="饰品图片"
          />
          <div class="item-info">
            <h2 class="item-name">{{ currentItemDetail.goods_info.name }}</h2>
            <div class="item-tags">
              <el-tag type="warning">{{ currentItemDetail.goods_info.rarity_localized_name }}</el-tag>
              <el-tag type="info">{{ currentItemDetail.goods_info.exterior_localized_name }}</el-tag>
              <el-tag type="success">{{ currentItemDetail.goods_info.type_localized_name }}</el-tag>
            </div>
          </div>
        </div>

        <el-divider />

        <div class="detail-section">
          <h3 class="section-title">基本信息</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="存世量">
              <span class="highlight-value">{{ currentItemDetail.goods_info.statistic }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="CSQAQ ID">
              {{ currentItemDetail.goods_info.id }}
            </el-descriptions-item>
            <el-descriptions-item label="BUFF ID">
              {{ currentItemDetail.goods_info.buff_id }}
            </el-descriptions-item>
            <el-descriptions-item label="悠悠有品 ID">
              {{ currentItemDetail.goods_info.yyyp_id }}
            </el-descriptions-item>
            <el-descriptions-item label="磨损范围" :span="2">
              {{ currentItemDetail.goods_info.min_float }} - {{ currentItemDetail.goods_info.max_float }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="detail-section">
          <h3 class="section-title">价格信息</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="BUFF售价">
              <span class="price-value">¥{{ currentItemDetail.goods_info.buff_sell_price }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="BUFF在售">
              {{ currentItemDetail.goods_info.buff_sell_num }}
            </el-descriptions-item>
            <el-descriptions-item label="BUFF求购价">
              <span class="price-value">¥{{ currentItemDetail.goods_info.buff_buy_price }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="BUFF求购">
              {{ currentItemDetail.goods_info.buff_buy_num }}
            </el-descriptions-item>
            <el-descriptions-item label="悠悠有品售价">
              <span class="price-value">¥{{ currentItemDetail.goods_info.yyyp_sell_price }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="悠悠有品在售">
              {{ currentItemDetail.goods_info.yyyp_sell_num }}
            </el-descriptions-item>
            <el-descriptions-item label="Steam价格">
              <span class="price-value">¥{{ currentItemDetail.goods_info.steam_buy_price }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="Steam在售">
              {{ currentItemDetail.goods_info.steam_buy_num }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="detail-section">
          <h3 class="section-title">租赁信息</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="租赁价格">
              <span class="price-value">¥{{ currentItemDetail.goods_info.yyyp_lease_price }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="租赁数量">
              {{ currentItemDetail.goods_info.yyyp_lease_num }}
            </el-descriptions-item>
            <el-descriptions-item label="长租价格">
              <span class="price-value">¥{{ currentItemDetail.goods_info.yyyp_long_lease_price }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="租赁年化">
              {{ currentItemDetail.goods_info.yyyp_lease_annual }}%
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- K线图预留区域 -->
        <div class="detail-section">
          <h3 class="section-title">价格走势</h3>
          <div class="chart-placeholder">
            <p>K线图功能开发中...</p>
          </div>
        </div>
          </div>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, Close } from '@element-plus/icons-vue'
import axios from 'axios'
import { API_CONFIG } from '@/config/api.js'

const keyword = ref('')
const isSearching = ref(false)
const searchResults = ref([])
const hasSearched = ref(false)
const weaponNameList = ref([])
const isLoadingWeaponNames = ref(false)
const searchingItems = ref({})
const currentItemDetail = ref(null)
const loadingDetail = ref(false)

const filters = reactive({
  weaponType: '',
  weaponName: '',
  rarity: '',
  priceMin: null,
  priceMax: null
})

// 稀有度颜色映射
const getRarityColor = (rarity) => {
  const colorMap = {
    '违禁': '#e4ae39',
    '隐秘': '#eb4b4b',
    '保密': '#d32ce6',
    '受限': '#8847ff',
    '军规级': '#4b69ff',
    '工业级': '#5e98d9',
    '消费级': '#b0c3d9',
    '普通级': '#b0c3d9'
  }
  return colorMap[rarity] || '#909399'
}

// 搜索饰品（重命名为 performSearch 避免冲突）
const performSearch = async () => {
  if (!keyword.value.trim() && !filters.weaponType && !filters.weaponName && !filters.rarity) {
    ElMessage.warning('请输入搜索关键词或选择筛选条件')
    return
  }

  isSearching.value = true
  hasSearched.value = true

  try {
    const response = await axios.post(
      `${API_CONFIG.BASE_URL}/itemSearchApiV1/api/item-search/search`,
      {
        keyword: keyword.value.trim(),
        weaponType: filters.weaponType,
        weaponName: filters.weaponName,
        rarity: filters.rarity
      }
    )

    if (response.data.success) {
      searchResults.value = response.data.data || []
      if (searchResults.value.length === 0) {
        ElMessage.info('未找到相关饰品')
      } else {
        ElMessage.success(`找到 ${searchResults.value.length} 件饰品`)
      }
    } else {
      throw new Error(response.data.message || '搜索失败')
    }
  } catch (error) {
    console.error('搜索失败:', error)
    ElMessage.error(error.message || '搜索失败，请稍后重试')
    searchResults.value = []
  } finally {
    isSearching.value = false
  }
}

// 加载武器名称列表
const loadWeaponNamesIfNeeded = async () => {
  if (weaponNameList.value.length > 0 || isLoadingWeaponNames.value) {
    return
  }

  if (!filters.weaponType) {
    return
  }

  isLoadingWeaponNames.value = true

  try {
    const response = await axios.post(
      `${API_CONFIG.BASE_URL}/itemSearchApiV1/api/item-search/weapon-names`,
      {
        weaponType: filters.weaponType
      }
    )

    if (response.data.success) {
      weaponNameList.value = response.data.data || []
    }
  } catch (error) {
    console.error('加载武器名称失败:', error)
  } finally {
    isLoadingWeaponNames.value = false
  }
}

// 武器类型变化时重新加载武器名称
const handleWeaponTypeChange = () => {
  filters.weaponName = ''
  weaponNameList.value = []
  if (filters.weaponType) {
    loadWeaponNamesIfNeeded()
  }
}

// 清除搜索结果
const handleClear = () => {
  searchResults.value = []
  hasSearched.value = false
}

// 跳转到 CSQAQ 网站
const handleOpenCSQAQ = (row) => {
  if (!row.csqaq_id) {
    ElMessage.warning('该饰品未映射 CSQAQ ID')
    return
  }
  
  const url = `https://www.csqaq.com/goods/${row.csqaq_id}`
  window.open(url, '_blank')
}

// 搜索 CSQAQ 详细数据
const handleSearchCSQAQ = async (row) => {
  if (!row.csqaq_id) {
    ElMessage.warning('该饰品未映射 CSQAQ ID')
    return
  }
  
  loadingDetail.value = true
  currentItemDetail.value = { loading: true }
  
  try {
    const response = await axios.get(
      `${API_CONFIG.BASE_URL}/itemSearchApiV1/api/item-search/csqaq-detail`,
      {
        params: {
          id: row.csqaq_id
        }
      }
    )
    
    if (response.data.success && response.data.data) {
      currentItemDetail.value = response.data.data
      ElMessage.success('数据加载成功')
      
      // 滚动到详细信息区域
      setTimeout(() => {
        const detailElement = document.querySelector('.detail-section-wrapper')
        if (detailElement) {
          detailElement.scrollIntoView({ behavior: 'smooth', block: 'start' })
        }
      }, 100)
    } else {
      throw new Error(response.data.message || '获取详细信息失败')
    }
  } catch (error) {
    console.error('获取CSQAQ详细信息失败:', error)
    ElMessage.error(error.message || '获取详细信息失败，请稍后重试')
    currentItemDetail.value = null
  } finally {
    loadingDetail.value = false
  }
}

// 关闭详细信息
const closeDetail = () => {
  currentItemDetail.value = null
}
</script>

<style scoped>
.item-search-container {
  padding: 2rem;
  max-width: 1600px;
  margin: 0 auto;
}

.search-card {
  background: #1e1e1e;
  border: 1px solid #333;
}

.card-header {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #ffffff;
  margin: 0;
}

.page-description {
  font-size: 0.9rem;
  color: #909399;
  margin: 0;
}

.search-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.search-filters {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.weapon-search-input {
  width: 100%;
}

.results-section {
  margin-top: 2rem;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #333;
}

.results-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #ffffff;
}

.weapon-name {
  color: #ffffff;
  font-weight: 500;
}

.rarity-tag {
  font-weight: 600;
}

.price {
  color: #67c23a;
  font-weight: 600;
}

.empty-state {
  padding: 3rem 0;
}

:deep(.el-card__header) {
  background-color: #252525;
  border-bottom: 1px solid #333;
}

:deep(.el-card__body) {
  padding: 1.5rem;
}

:deep(.el-input__wrapper) {
  background-color: #2a2a2a;
  box-shadow: 0 0 0 1px #3a3a3a inset;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #4a4a4a inset;
}

:deep(.el-input__inner) {
  color: #ffffff;
}

:deep(.el-select .el-input__wrapper) {
  background-color: #2a2a2a;
}

:deep(.el-table) {
  background-color: #1e1e1e;
  color: #ffffff;
}

:deep(.el-table th) {
  background-color: #252525;
  color: #b0b0b0;
}

:deep(.el-table tr) {
  background-color: #1e1e1e;
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background-color: #252525;
}

:deep(.el-table td),
:deep(.el-table th.is-leaf) {
  border-bottom: 1px solid #333;
}

:deep(.el-table--border::after),
:deep(.el-table--group::after),
:deep(.el-table::before) {
  background-color: #333;
}

.detail-section-wrapper {
  margin-top: 2rem;
}

.detail-card {
  background: #1e1e1e;
  border: 1px solid #333;
}

.detail-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.detail-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #909399;
}

.detail-loading p {
  margin-top: 1rem;
}

.detail-content {
  padding: 0 1rem;
}

.detail-header {
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;
}

.item-image {
  width: 200px;
  height: 150px;
  object-fit: contain;
  background: #2a2a2a;
  border-radius: 8px;
  padding: 1rem;
}

.item-info {
  flex: 1;
}

.item-name {
  font-size: 1.3rem;
  font-weight: 600;
  color: #ffffff;
  margin: 0 0 1rem 0;
}

.item-tags {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.detail-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 1rem;
}

.price-value {
  color: #67c23a;
  font-weight: 600;
  font-size: 1.1rem;
}

.highlight-value {
  color: #409eff;
  font-weight: 600;
  font-size: 1.2rem;
}

.chart-placeholder {
  height: 400px;
  background: #2a2a2a;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
}

:deep(.detail-card .el-card__header) {
  background-color: #252525;
  border-bottom: 1px solid #333;
}

:deep(.detail-card .el-card__body) {
  padding: 1.5rem;
}

:deep(.el-descriptions) {
  background-color: transparent;
}

:deep(.el-descriptions__label) {
  background-color: #252525;
  color: #b0b0b0;
}

:deep(.el-descriptions__content) {
  background-color: #2a2a2a;
  color: #ffffff;
}

:deep(.el-divider) {
  border-color: #333;
}

@media (max-width: 768px) {
  .item-search-container {
    padding: 1rem;
  }

  .search-filters {
    flex-direction: column;
  }

  .search-filters > * {
    width: 100% !important;
  }

  .detail-header {
    flex-direction: column;
  }

  .item-image {
    width: 100%;
  }
}
</style>
