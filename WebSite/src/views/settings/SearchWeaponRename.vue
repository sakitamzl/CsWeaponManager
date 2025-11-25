<template>
  <div class="spider-weapon-rename-container">
    <div class="page-layout">
      <!-- 左侧配置管理栏 -->
      <aside 
        class="config-sidebar" 
        :class="{ collapsed: isConfigSectionsCollapsed }"
        @click="handleSidebarAreaClick"
      >
        <div class="sidebar-header clickable" @click.stop="toggleConfigSections">
          <div class="sidebar-header-row" :class="{ collapsed: isConfigSectionsCollapsed }">
            <div class="sidebar-header-title">配置管理</div>
            <div class="sidebar-header-actions">
              <el-button 
                type="success" 
                @click.stop="createNewConfig"
                :disabled="isCrawling"
              >
                <el-icon><Document /></el-icon>
                新建
              </el-button>
              
              <el-button 
                type="info" 
                @click.stop="loadConfigList"
              >
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </div>
        </div>

        <div class="sidebar-divider" v-show="!isConfigSectionsCollapsed"></div>

        <div class="config-list" v-show="!isConfigSectionsCollapsed">
          <div 
            v-for="config in savedConfigs" 
            :key="config.id"
            class="config-item"
            :class="{ active: selectedConfigId === config.id }"
            @click="selectConfig(config.id)"
          >
            <div class="config-item-header">
              <div style="display: flex; align-items: center; gap: 8px; flex: 1;">
                <span class="config-name">{{ config.dataName }}</span>
                <el-tag 
                  :type="getPlatformTagType(config.platformType)" 
                  size="small"
                >
                  {{ getSourceLabel(config.platformType) || '未设置' }}
                </el-tag>
              </div>
            </div>
            <div v-if="config.description" class="config-description">
              {{ config.description }}
            </div>
          </div>

          <div v-if="savedConfigs.length === 0" class="empty-config">
            <el-empty description="暂无保存的配置" :image-size="80" />
          </div>
        </div>
      </aside>

      <!-- 右侧主内容区域 -->
      <div class="main-content-area">

      <!-- 饰品搜索区域 -->
      <!-- 统一的工具区域 -->
      <div class="unified-tool-section" :class="{ collapsed: isConfigSectionsCollapsed }">
        <div class="tool-section-header" @click="toggleConfigSections">
          <h2 class="section-title">爬取配置</h2>
          <el-button type="text" class="collapse-btn">
            <el-icon :size="20">
              <ArrowUp v-if="!isConfigSectionsCollapsed" />
              <ArrowDown v-else />
            </el-icon>
          </el-button>
        </div>
        
        <div class="tool-section-content" v-show="!isConfigSectionsCollapsed">
        <div class="tool-section">
        
        <div class="form-container">
          <el-form :model="crawlForm" label-width="120px" ref="crawlFormRef">
            <div class="form-row">
              <el-form-item label="配置名称" required class="form-item-quarter">
                <el-input 
                  v-model="crawlForm.configName" 
                  placeholder="请输入配置名称"
                  clearable
                />
              </el-form-item>

              <el-form-item label="平台类型" required class="form-item-quarter">
                <el-select 
                  v-model="crawlForm.platformType" 
                  placeholder="选择平台类型"
                  style="width: 100%;"
                  :disabled="!!selectedConfigId || (weaponIdList && weaponIdList.length > 0)"
                  @change="handlePlatformTypeChange"
                >
                  <el-option label="悠悠有品" value="youpin" />
                  <el-option label="BUFF" value="buff" />
                  <el-option label="Steam 市场" value="steam" />
                </el-select>
              </el-form-item>

              <el-form-item label="爬取账号" required class="form-item-quarter">
                <el-select 
                  v-model="crawlForm.crawlAccountId" 
                  placeholder="选择爬取账号"
                  style="width: 100%;"
                  filterable
                  allow-create
                  default-first-option
                >
                  <el-option 
                    v-for="item in filteredSteamIdList" 
                    :key="item.steamID || item.steam_id" 
                    :label="`${item.dataName || '未命名'} (${item.steamID || item.steam_id || '无ID'})`" 
                    :value="item.steamID || item.steam_id"
                  />
                </el-select>
              </el-form-item>

              <el-form-item label="购买账号" required class="form-item-quarter">
                <el-select 
                  v-model="crawlForm.steamId" 
                  placeholder="选择购买账号"
                  style="width: 100%;"
                  filterable
                  allow-create
                  default-first-option
                >
                  <el-option 
                    v-for="item in filteredSteamIdList" 
                    :key="item.steamID || item.steam_id" 
                    :label="`${item.dataName || '未命名'} (${item.steamID || item.steam_id || '无ID'})`" 
                    :value="item.steamID || item.steam_id"
                  />
                </el-select>
              </el-form-item>
            </div>

            <el-form-item label-width="0px" class="custom-config-form-item">
              <div class="custom-config-grid">
                <div class="custom-config-field">
                  <div class="field-label">自动查询间隔</div>
                  <div class="field-control no-spinner">
                    <el-input
                      v-model.number="customConfigForm['饰品自动查询间隔']"
                      type="number"
                      placeholder="例如 3"
                      min="1"
                      style="width: 100px;"
                    />
                  </div>
                </div>

                <div class="custom-config-field">
                  <div class="field-label">最大差价 (元)</div>
                  <div class="field-control no-spinner">
                    <el-input
                      v-model.number="customConfigForm['最大差价']"
                      type="number"
                      placeholder="例如 8"
                      min="0"
                      style="width: 100px;"
                    />
                  </div>
                </div>

                <div class="custom-config-field">
                  <div class="field-label">参考价来源</div>
                  <div class="field-control">
                    <el-select
                      v-model="customConfigForm['参考价来源']"
                      placeholder="请选择"
                      style="width: 120px;"
                    >
                      <el-option
                        v-for="option in referencePriceSources"
                        :key="`reference-source-${option.value}`"
                        :label="option.label"
                        :value="option.value"
                      />
                    </el-select>
                  </div>
                </div>

                <div class="custom-config-field">
                  <div class="field-label">是否自动购买</div>
                  <div class="field-control">
                    <el-select
                      v-model="customConfigForm['是否自动购买']"
                      placeholder="请选择"
                      style="width: 100px;"
                    >
                      <el-option
                        v-for="option in booleanOptions"
                        :key="`rename-auto-buy-${option.value}`"
                        :label="option.label"
                        :value="option.value"
                      />
                    </el-select>
                  </div>
                </div>

                <div class="custom-config-field">
                  <div class="field-label">只查询中文</div>
                  <div class="field-control">
                    <el-select
                      v-model="customConfigForm['只查询中文改名']"
                      placeholder="请选择"
                      style="width: 100px;"
                    >
                      <el-option
                        v-for="option in booleanOptions"
                        :key="`rename-chinese-only-${option.value}`"
                        :label="option.label"
                        :value="option.value"
                      />
                    </el-select>
                  </div>
                </div>
              </div>
            </el-form-item>

            <el-form-item>
              <template #label>
                <div class="collapsible-label">
                  <span class="label-text" @click="toggleWeaponList">
                    饰品列表 ({{ weaponIdList.length }})
                    <el-icon 
                      class="collapse-icon-inline" 
                      :class="{ 'is-collapsed': isWeaponListCollapsed }"
                    >
                      <ArrowUp v-if="!isWeaponListCollapsed" />
                      <ArrowDown v-else />
                    </el-icon>
                  </span>
                </div>
              </template>
              <div class="weapon-id-section" v-show="!isWeaponListCollapsed">
                <div class="weapon-id-tags">
                  <el-tag
                    v-for="weapon in weaponIdList"
                    :key="weapon.id"
                    closable
                    @close="removeWeaponId(weapon.id)"
                    type="primary"
                    size="large"
                  >
                    {{ weapon.name }} (ID: {{ weapon.id }})
                  </el-tag>
                </div>
                <el-button 
                  v-if="weaponIdList && weaponIdList.length > 0"
                  type="danger" 
                  size="small"
                  @click="clearAllWeaponIds"
                  style="margin-left: 10px;"
                >
                  <el-icon><Delete /></el-icon>
                  一键清空
                </el-button>
              </div>
            </el-form-item>
          </el-form>
        </div>

        <div class="action-buttons">
          <el-button 
            type="success" 
            size="large"
            @click="saveConfig"
            :disabled="isCrawling"
          >
            <el-icon><Document /></el-icon>
            保存当前配置
          </el-button>

          <el-button 
            type="danger" 
            size="large"
            @click="deleteCurrentConfig"
            :disabled="isCrawling || !selectedConfigId"
          >
            <el-icon><Delete /></el-icon>
            删除当前配置
          </el-button>

          <el-button 
            type="primary" 
            size="large"
            @click="startCrawl"
            :disabled="isCrawling || !canStartCrawl"
            :loading="isCrawling"
          >
            {{ isCrawling ? '搜索中...' : '开始搜索' }}
          </el-button>
        </div>
        </div>

        <!-- 搜索饰品组件 -->
        <WeaponSearch 
          :platformType="crawlForm.platformType"
          @add-weapon="handleAddWeaponFromSearch"
          @add-all-weapons="handleAddAllWeaponsFromSearch"
        />

        </div>
        <!-- 结束 tool-section-content -->
      </div>
      <!-- 结束 unified-tool-section -->


      <!-- 查询结果区域 -->
      <div v-if="allCrawlItems && allCrawlItems.length > 0" class="result-section">
        <div class="result-header">
          <h2 class="section-title">查询结果 ({{ allCrawlItems?.length || 0 }} 件)</h2>
          <el-button 
            type="danger" 
            size="small"
            @click="clearCrawlHistory"
          >
            <el-icon><Delete /></el-icon>
            清空列表
          </el-button>
        </div>
        
        <!-- 统一商品列表 -->
        <el-table 
          :data="allCrawlItems" 
          style="width: 100%;"
          stripe
          table-layout="auto"
          :header-cell-style="tableHeaderStyle"
        >
          <el-table-column label="图标" width="80" fixed="left" align="center" resizable>
            <template #default="scope">
              <img 
                v-if="scope.row.iconUrl" 
                :src="scope.row.iconUrl" 
                class="weapon-icon"
                :alt="getWeaponDisplayName(scope.row)"
              />
              <span v-else class="no-icon">-</span>
            </template>
          </el-table-column>
          
          <el-table-column label="武器名称" :min-width="280" fixed="left" resizable>
            <template #default="scope">
              <el-tooltip 
                :content="getWeaponDisplayName(scope.row)" 
                placement="top"
                :disabled="!getWeaponDisplayName(scope.row) || getWeaponDisplayName(scope.row).length <= 20"
              >
                <div class="weapon-name-cell">{{ getWeaponDisplayName(scope.row) }}</div>
              </el-tooltip>
            </template>
          </el-table-column>
          
            <el-table-column label="价格" width="110" resizable>
              <template #default="scope">
                <span class="price">¥{{ scope.row.price }}</span>
              </template>
            </el-table-column>
            
            <el-table-column 
              v-if="crawlForm.platformType === 'steam'"
              label="参考价" 
              width="110" 
              resizable
            >
              <template #default="scope">
                <span class="reference-price">
                  {{ scope.row.referencePrice !== null && scope.row.referencePrice !== undefined 
                    ? '¥' + (typeof scope.row.referencePrice === 'number' ? scope.row.referencePrice.toFixed(2) : scope.row.referencePrice)
                    : '-' }}
                </span>
              </template>
            </el-table-column>
            
            <el-table-column label="溢价" width="120" resizable>
              <template #default="scope">
                <el-tag type="danger" size="small">
                  {{ scope.row.spread !== undefined && scope.row.spread !== null && typeof scope.row.spread === 'number' ? scope.row.spread.toFixed(2) : '0.00' }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column label="手续费" width="130" align="center" resizable>
              <template #default="scope">
                <span class="commission-fee">¥{{ scope.row.commissionFee !== undefined && scope.row.commissionFee !== null && typeof scope.row.commissionFee === 'number' ? scope.row.commissionFee.toFixed(2) : '0.00' }}</span>
              </template>
            </el-table-column>
            
            <el-table-column label="磨损" width="240" resizable>
              <template #default="scope">
                {{ scope.row.abrade }}
              </template>
            </el-table-column>
            
            <el-table-column label="改名" min-width="220" resizable>
              <template #default="scope">
                <span class="name-tag">{{ scope.row.nameTag || '-' }}</span>
              </template>
            </el-table-column>
            
            <el-table-column label="卖家" min-width="180" resizable>
              <template #default="scope">
                {{ scope.row.userNickName || '未知' }}
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="120" fixed="right" resizable>
              <template #default="scope">
                <el-button 
                  :type="getBuyButtonType(scope.row)"
                  size="small"
                  @click="handleBuyWeapon(scope.row)"
                  :loading="buyingItems[scope.row.id]"
                  :disabled="purchasedItems.has(scope.row.id)"
                >
                  {{ purchasedItems.has(scope.row.id) ? '已购买' : '购买' }}
                </el-button>
              </template>
            </el-table-column>
        </el-table>
      </div>

      </div>
      <!-- 结束 main-content-area -->
    </div>
    <!-- 结束 page-layout -->

  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, Delete, Refresh, ArrowUp, ArrowDown } from '@element-plus/icons-vue'
import { API_CONFIG } from '@/config/api.js'
import WeaponSearch from '@/views/Units/weapon_search.vue'

export default {
  name: 'SpiderWeaponRename',
  components: {
    WeaponSearch,
    Document,
    Delete,
    Refresh,
    ArrowUp,
    ArrowDown
  },
  setup() {
    const router = useRouter()
    const crawlFormRef = ref(null)
    const platformAccountLists = ref({})
    const isProgrammaticPlatformChange = ref(false)
    const isApplyingConfigState = ref(false)
    const accountLoadingStates = ref({})
    const isCrawling = ref(false)
    const crawlResult = ref(null)
    const referencePriceCache = ref({})
    const referencePriceSources = [
      { label: '悠悠有品', value: 'youpin' },
      { label: 'BUFF', value: 'buff' }
    ]
    
    // 轮询相关变量
    const pollingTimer = ref(null) // 轮询定时器
    const lastItemId = ref(0) // 最后一条记录的ID（用于增量更新）
    const POLL_INTERVAL = 1000 // 轮询间隔（毫秒）- 1秒
    const noDataCount = ref(0) // 连续无数据次数
    const MAX_NO_DATA_COUNT = 60 // 连续60次无数据（60秒/1分钟）后认为完成
    const lastPollingTime = ref(0) // 最后轮询时间
    
    // 将 weapons 转换为扁平列表，与 SearchPendant 保持一致
    const allCrawlItems = computed(() => {
      console.log('[allCrawlItems] 🔄 计算开始，crawlResult.value:', crawlResult.value)
      
      if (!crawlResult.value || !crawlResult.value.weapons) {
        console.log('[allCrawlItems] 📊 crawlResult 为空或无 weapons 数据')
        return []
      }

      console.log(`[allCrawlItems] 🔄 开始计算，weapons 数量: ${crawlResult.value.weapons.length}`)
      console.log('[allCrawlItems] weapons 数据:', crawlResult.value.weapons)

      const items = []
      crawlResult.value.weapons.forEach(weapon => {
        if (weapon.items && weapon.items.length > 0) {
          console.log(`[allCrawlItems] 📦 处理武器: ${weapon.weapon_name}, items: ${weapon.items.length}`)
          weapon.items.forEach(item => {
            // 计算手续费（通常为价格的 2.5%）
            const commissionRate = 0.025 // 2.5% 手续费率
            const price = item.price || 0
            const commissionFee = price * commissionRate

            // 计算收益（溢价 - 手续费）
            const spread = item.spread || 0
            const priceDiff = spread - commissionFee

            const weaponDisplayName = weapon.weapon_name || weapon.weaponName || '未知饰品'
            items.push({
              ...item,
              weapon_name: weaponDisplayName,
              weaponName: weaponDisplayName,  // 兼容旧字段
              yyyp_id: weapon.yyyp_id || weapon.weapon_id,
              commissionFee: commissionFee,  // 手续费
              priceDiff: priceDiff  // 收益
            })
          })
        }
      })

      // 按溢价从小到大排序（溢价最小的在最上面）
      items.sort((a, b) => {
        const spreadA = a.spread !== undefined ? a.spread : Infinity
        const spreadB = b.spread !== undefined ? b.spread : Infinity
        return spreadA - spreadB  // 从小到大
      })

      console.log(`[allCrawlItems] ✅ 计算完成，总计 ${items.length} 件商品`)
      if (items.length > 0) {
        console.log(`[allCrawlItems] 第一条商品数据:`, items[0])
        console.log(`[allCrawlItems] 第一条weapon_name:`, items[0].weapon_name)
        console.log(`[allCrawlItems] 第一条iconUrl:`, items[0].iconUrl)
      }

      return items
    })
    
    // 配置管理相关
    const savedConfigs = ref([])
    const selectedConfigId = ref(null)
    
    // 本地存储相关
    const STORAGE_KEY = 'spider_weapon_rename_result'
    
    // 保存爬虫结果到 localStorage
    const saveCrawlResultToStorage = (result) => {
      try {
        if (result && result.weapons) {
          const dataToSave = {
            result: result,
            timestamp: Date.now(),
            configName: crawlForm.value.configName || '未命名配置'
          }
          localStorage.setItem(STORAGE_KEY, JSON.stringify(dataToSave))
          console.log('✅ 爬虫结果已保存到本地存储')
        }
      } catch (error) {
        console.error('保存爬虫结果失败:', error)
      }
    }
    
    // 从 localStorage 恢复爬虫结果
    const loadCrawlResultFromStorage = () => {
      try {
        const savedData = localStorage.getItem(STORAGE_KEY)
        if (savedData) {
          const parsed = JSON.parse(savedData)
          crawlResult.value = parsed.result
          console.log('✅ 已恢复历史爬虫结果')
          console.log(`📅 保存时间: ${new Date(parsed.timestamp).toLocaleString()}`)
          console.log(`📝 配置名称: ${parsed.configName}`)
          
          // 显示提示信息
          ElMessage.info(`已恢复上次查询结果 (${new Date(parsed.timestamp).toLocaleString()})`)
          return true
        }
      } catch (error) {
        console.error('恢复爬虫结果失败:', error)
      }
      return false
    }
    
    // 清空爬虫历史
    const clearCrawlHistory = async (skipConfirm = false) => {
      try {
        // 如果有选中的配置，只清空该配置的数据；否则清空所有数据
        const clearMessage = selectedConfigId.value
          ? '确定要清空当前配置的查询结果吗？此操作将删除该配置的所有改名饰品数据，不可恢复。'
          : '确定要清空所有查询结果吗？此操作将删除数据库中所有改名饰品数据，不可恢复。'
        
        if (!skipConfirm) {
          await ElMessageBox.confirm(
            clearMessage,
            '确认清空',
            {
              confirmButtonText: '确定',
              cancelButtonText: '取消',
              type: 'warning'
            }
          )
        }
        
        // 构建请求体
        const requestBody = {
          dataType: 'rename'
        }
        
        // 如果有选中的配置，只清空该配置的数据
        if (selectedConfigId.value) {
          requestBody.configId = selectedConfigId.value
        }
        
        // 调用后端 API 清空数据库
        const response = await fetch(`${API_CONFIG.BASE_URL}/searchRename/clear`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestBody)
        })
        
        if (!response.ok) {
          throw new Error('清空失败')
        }
        
        const result = await response.json()
        
        if (result.success) {
          // 清空前端数据
          crawlResult.value = null
          localStorage.removeItem(STORAGE_KEY)
          if (!skipConfirm) {
            ElMessage.success(result.message || `已清空 ${result.count} 条数据`)
          }
        } else {
          throw new Error(result.message || '清空失败')
        }
      } catch (error) {
        if (error !== 'cancel' && !skipConfirm) {
          console.error('清空失败:', error)
          ElMessage.error(error.message || '清空失败')
        }
      }
    }



    // 饰品搜索相关
    const weaponSearchKeyword = ref('')
    const weaponSearchResults = ref([])
    const isSearchingWeapon = ref(false)
    const weaponSearchFilters = ref({
      weaponType: '',
      weaponName: '',
      rarity: '',
      priceMin: null,
      priceMax: null,
      minOnSaleCount: null
    })
    const weaponNameList = ref([])
    const isLoadingWeaponNames = ref(false)
    const isSearchResultsCollapsed = ref(false)
    const currentPage = ref(1)
    const pageSize = ref(50)
    const hasMore = ref(true)
    const isLoadingMore = ref(false)
    
    // 购买相关
    const buyingItems = ref({})  // 正在购买的商品 {itemId: true/false}
    const purchasedItems = ref(new Set())  // 已成功购买的商品ID集合
    
    const normalizeReferencePriceSource = (value, defaultValue = 'youpin') => {
      const normalized = (value || '').toString().trim().toLowerCase()
      if (normalized === 'buff') {
        return 'buff'
      }
      if (normalized === 'youpin') {
        return 'youpin'
      }
      return defaultValue
    }

    const ensureCacheBucket = (sourceKey) => {
      if (!referencePriceCache.value[sourceKey]) {
        referencePriceCache.value = {
          ...referencePriceCache.value,
          [sourceKey]: {}
        }
      }
      return referencePriceCache.value[sourceKey]
    }

    const normalizeReferencePrice = (value) => {
      const numericValue = Number(value)
      return Number.isFinite(numericValue) ? numericValue : 0
    }

    const applyReferencePricesToItems = (items) => {
      if (!items || items.length === 0) {
        return
      }
      const sourceKey = referencePriceSource.value
      const cacheBucket = ensureCacheBucket(sourceKey)
      items.forEach(item => {
        const hashName = item.steam_hash_name || item.steamHashName
        if (!hashName) {
          return
        }
        const cachedValue = cacheBucket[hashName]
        if (cachedValue !== undefined) {
          item.referencePrice = normalizeReferencePrice(cachedValue)
        }
      })
    }

    // 批量查询参考价（Steam Hash Name -> weapon_classID.yyyp_Price）
    const loadReferencePrices = async (items = []) => {
      const targetItems = items && items.length > 0 ? items : allCrawlItems.value
      if (!targetItems || targetItems.length === 0) {
        return
      }
      const sourceKey = referencePriceSource.value
      const cacheBucket = ensureCacheBucket(sourceKey)

      const steamHashNames = targetItems
        .map(item => item.steam_hash_name || item.steamHashName)
        .filter(name => !!(name && name.trim()))

      if (steamHashNames.length === 0) {
        return
      }

      const uniqueHashNames = Array.from(new Set(steamHashNames))
      const namesToFetch = uniqueHashNames.filter(name => cacheBucket[name] === undefined)

      // 先尝试应用已有缓存，避免界面闪烁
      applyReferencePricesToItems(targetItems)

      if (namesToFetch.length === 0) {
        return
      }

      try {
        const response = await axios.post(
          `${API_CONFIG.BASE_URL}/webSelectWeaponV1/getReferencePrices`,
          {
            steamHashNames: namesToFetch,
            referencePriceSource: sourceKey
          }
        )

        if (response.data.success && response.data.data) {
          const priceMap = response.data.data
          const normalizedPriceMap = {}

          Object.keys(priceMap).forEach(key => {
            normalizedPriceMap[key] = normalizeReferencePrice(priceMap[key])
          })

          namesToFetch.forEach(name => {
            if (normalizedPriceMap[name] === undefined) {
              normalizedPriceMap[name] = 0
            }
          })

          referencePriceCache.value = {
            ...referencePriceCache.value,
            [sourceKey]: {
              ...cacheBucket,
              ...normalizedPriceMap
            }
          }

          applyReferencePricesToItems(targetItems)
          console.log(`[参考价] 已更新 ${Object.keys(normalizedPriceMap).length} 个商品的参考价`)
        }
      } catch (error) {
        console.error('[参考价] 查询失败:', error)
        // 不影响主流程，静默失败
      }
    }
    
    // 获取购买按钮类型
    const getBuyButtonType = (item) => {
      if (purchasedItems.value.has(item.id)) {
        return 'success'  // 已购买：绿色
      }
      if (item.priceDiff < 0) {
        return 'danger'   // 亏损：红色
      }
      if (item.priceDiff < 3) {
        return 'warning'  // 收益低：黄色
      }
      return 'primary'    // 正常：蓝色
    }

    const getWeaponDisplayName = (item) => {
      if (!item) return ''
      return item.weapon_name || item.weaponName || item.market_listing_item_name || item.name || ''
    }
    
    // 工具与配置区域联动折叠状态
    const isConfigSectionsCollapsed = ref(false)
    // 饰品列表折叠状态（默认折叠）
    const isWeaponListCollapsed = ref(true)
    
    const crawlForm = ref({
      configName: '',      // 对应 dataName
      steamId: '',         // 购买账号
      crawlAccountId: '',  // 爬取账号
      platformType: '',    // 平台类型：youpin 或 buff
      weaponId: []         // 改为数组，存储 {id, name} 对象
    })

    const booleanOptions = [
      { label: '是', value: true },
      { label: '否', value: false }
    ]

    const createDefaultCustomConfig = () => ({
      '饰品自动查询间隔': 3,
      '最大差价': 8,
      '是否自动购买': false,
      '只查询中文改名': true,
      '参考价来源': 'youpin'
    })

    const customConfigForm = ref(createDefaultCustomConfig())
    const referencePriceSource = computed(() => normalizeReferencePriceSource(customConfigForm.value['参考价来源']))
    const isProgrammaticCustomConfigChange = ref(false)

    const weaponIdList = computed(() => {
      return crawlForm.value.weaponId || []
    })

    const normalizePlatformKey = (value) => {
      if (!value && value !== 0) return ''
      const normalized = value.toString().trim().toLowerCase()
      if (['youpin', 'yyyp', 'yyp', 'you_pin', 'you-pin', '悠悠有品'].some(k => normalized === k.toLowerCase())) {
        return 'youpin'
      }
      if (['buff', 'buff平台'].some(k => normalized === k.toLowerCase())) {
        return 'buff'
      }
      if (['steam', 'steam市场', 'steam-market'].some(k => normalized === k.toLowerCase())) {
        return 'steam'
      }
      return normalized
    }

    const filteredSteamIdList = computed(() => {
      const platformKey = normalizePlatformKey(crawlForm.value.platformType || '')
      if (!platformKey) {
        console.log('[账号列表] 未选择平台，返回空账号列表')
        return []
      }
      const accounts = platformAccountLists.value[platformKey] || []
      console.log(`[账号列表] 平台: ${platformKey}, 账号数量: ${accounts.length}`, accounts)
      return accounts
    })

    // 计算是否可以开始爬取
    const canStartCrawl = computed(() => {
      if (!crawlForm.value.configName) return false
      if (!crawlForm.value.platformType) return false
      const platformKey = normalizePlatformKey(crawlForm.value.platformType)
      const requiresCrawler = platformKey !== 'steam'
      if (requiresCrawler && !crawlForm.value.crawlAccountId) return false
      if (!crawlForm.value.steamId) return false
      if (!crawlForm.value.weaponId || crawlForm.value.weaponId.length === 0) return false
      return true
    })

    const resetCustomConfigForm = () => {
      isProgrammaticCustomConfigChange.value = true
      customConfigForm.value = createDefaultCustomConfig()
      nextTick(() => {
        isProgrammaticCustomConfigChange.value = false
      })
    }

    const normalizeBooleanValue = (value, defaultValue) => {
      if (value === true || value === false) return value
      if (typeof value === 'string') {
        const normalized = value.trim().toLowerCase()
        if (['true', '1', '是', 'yes', 'y'].includes(normalized)) return true
        if (['false', '0', '否', 'no', 'n'].includes(normalized)) return false
      }
      return defaultValue
    }

    const normalizeNumberValue = (value, defaultValue) => {
      const num = Number(value)
      return Number.isFinite(num) ? num : defaultValue
    }

    const buildCustomConfig = () => ({
      '饰品自动查询间隔': normalizeNumberValue(
        customConfigForm.value['饰品自动查询间隔'],
        3
      ),
      '最大差价': normalizeNumberValue(
        customConfigForm.value['最大差价'],
        8
      ),
      '是否自动购买': normalizeBooleanValue(
        customConfigForm.value['是否自动购买'],
        false
      ),
      '只查询中文改名': normalizeBooleanValue(
        customConfigForm.value['只查询中文改名'],
        true
      ),
      '参考价来源': normalizeReferencePriceSource(
        customConfigForm.value['参考价来源'],
        'youpin'
      ),
      '是否授权': true
    })

    const validateCustomConfig = () => {
      const config = buildCustomConfig()

      if (config['饰品自动查询间隔'] <= 0) {
        return { valid: false, message: '饰品自动查询间隔必须大于 0 秒' }
      }
      if (config['最大差价'] < 0) {
        return { valid: false, message: '最大差价不能为负数' }
      }

      return { valid: true, config }
    }

    const applyCustomConfig = (config = {}) => {
      const defaults = createDefaultCustomConfig()
      isProgrammaticCustomConfigChange.value = true
      customConfigForm.value = {
        '饰品自动查询间隔': normalizeNumberValue(
          config['饰品自动查询间隔'],
          defaults['饰品自动查询间隔']
        ),
        '最大差价': normalizeNumberValue(
          config['最大差价'],
          defaults['最大差价']
        ),
        '是否自动购买': normalizeBooleanValue(
          config['是否自动购买'],
          defaults['是否自动购买']
        ),
        '只查询中文改名': normalizeBooleanValue(
          config['只查询中文改名'],
          defaults['只查询中文改名']
        ),
        '参考价来源': normalizeReferencePriceSource(
          config['参考价来源'],
          defaults['参考价来源']
        )
      }
      nextTick(() => {
        isProgrammaticCustomConfigChange.value = false
      })
    }

    const PLATFORM_ACCOUNT_SOURCE_MAP = {
      youpin: { key1: 'youpin', key2: 'config', label: '悠悠有品' },
      buff: { key1: 'buff', key2: 'config', label: 'BUFF' },
      steam: { key1: 'steam', key2: 'config', label: 'Steam市场' }
    }

    const PLATFORM_SPIDER_ENDPOINT_MAP = {
      youpin: `${API_CONFIG.SPIDER_BASE_URL}${API_CONFIG.ENDPOINTS.AUTO_BUY_RENAMED_WEAPON}`,
      steam: `${API_CONFIG.SPIDER_BASE_URL}${API_CONFIG.ENDPOINTS.STEAM_SEARCH_RENAME}`
    }

    const loadAccountsForPlatform = async (platformType) => {
      const platformKey = normalizePlatformKey(platformType)
      if (!platformKey) {
        return
      }

      const sourceConfig = PLATFORM_ACCOUNT_SOURCE_MAP[platformKey]
      if (!sourceConfig) {
        console.warn(`[平台账号] 未配置平台 ${platformKey} 的数据源`)
        return
      }

      if (accountLoadingStates.value[platformKey]) {
        return
      }

      const cachedList = platformAccountLists.value[platformKey]
      if (cachedList && cachedList.length > 0) {
        return
      }

      accountLoadingStates.value = {
        ...accountLoadingStates.value,
        [platformKey]: true
      }

      try {
        const response = await axios.get(`${API_CONFIG.BASE_URL}/configV1/list`, {
          params: {
            key1: sourceConfig.key1,
            key2: sourceConfig.key2
          }
        })
        console.log(`[平台账号] ${platformKey} 配置API响应:`, response.data)
        if (response.data.success && Array.isArray(response.data.data)) {
          const mappedList = response.data.data.map(item => {
            let parsedValue = {}
            if (item.value) {
              try {
                parsedValue = typeof item.value === 'string'
                  ? JSON.parse(item.value)
                  : (item.value || {})
              } catch (parseError) {
                console.error(`[平台账号] 解析配置 value 失败 (${platformKey}):`, parseError)
              }
            }

            const steamId = parsedValue.steam_id || parsedValue.steamId || item.steamId || item.steamID || ''
            const displayName = item.dataName || parsedValue.accountName || parsedValue.name || `配置账号 #${item.id}`

            return {
              ...item,
              steamID: steamId,
              steam_id: steamId,
              dataName: displayName,
              platformKey,
              platformLabel: sourceConfig.label,
              rawConfig: parsedValue
            }
          })

          platformAccountLists.value = {
            ...platformAccountLists.value,
            [platformKey]: mappedList
          }
        }
      } catch (error) {
        console.error(`[平台账号] 加载 ${platformKey} 账号配置失败:`, error)
      } finally {
        accountLoadingStates.value = {
          ...accountLoadingStates.value,
          [platformKey]: false
        }
      }
    }
    
    // 平台类型改变处理
    const handlePlatformTypeChange = async () => {
      if (isProgrammaticPlatformChange.value) {
        isProgrammaticPlatformChange.value = false
      } else {
        crawlForm.value.crawlAccountId = ''
        crawlForm.value.steamId = ''
      }
      
      if (!crawlForm.value.platformType) {
        return
      }
      
      await loadAccountsForPlatform(crawlForm.value.platformType)
    }

    // 验证JSON配置
    // 联动切换配置管理与爬取配置区域
    const toggleConfigSections = () => {
      isConfigSectionsCollapsed.value = !isConfigSectionsCollapsed.value
    }

    const toggleWeaponList = () => {
      isWeaponListCollapsed.value = !isWeaponListCollapsed.value
    }

    const clearAllWeaponIds = () => {
      crawlForm.value.weaponId = []
    }

    // 加载数据库中最近的搜索结果（页面加载时）
    const loadRecentSearchResults = async () => {
      try {
        console.log('[页面加载] 尝试加载历史搜索结果...')
        
        // 获取搜索结果，根据选中的配置ID过滤
        const params = new URLSearchParams({
          dataType: 'rename'
        })
        // 如果选中了配置，则只查询该配置的数据
        if (selectedConfigId.value) {
          params.append('configId', selectedConfigId.value.toString())
        }
        const url = `${API_CONFIG.BASE_URL}/searchRename/items/list?${params.toString()}`
        const response = await fetch(url)
        
        if (!response.ok) {
          console.log('[页面加载] 无法获取历史数据')
          return
        }

        const result = await response.json()
        console.log('[页面加载] API返回:', result)
        
        if (result.success && result.items && result.items.length > 0) {
          console.log(`[页面加载] 加载到 ${result.items.length} 条历史数据`)
          console.log('[页面加载] 第一条数据示例:', result.items[0])
          
          // 后端已通过 to_dict() 返回驼峰命名，直接使用
          const historyItems = result.items.map(item => {
            console.log('[数据映射] 原始item (驼峰命名):', item)
            console.log('[数据映射] item.weaponName:', item.weaponName)
            console.log('[数据映射] item.weaponId:', item.weaponId)
            console.log('[数据映射] item 的所有键:', Object.keys(item))
            // 后端返回的已经是驼峰命名，直接使用
            const mappedItem = {
              id: item.id,  // 数据库主键，用于后端查询商品详情
              commodityId: item.commodityId,  // Steam的listing_id或悠悠有品的商品ID
              commodityNo: item.commodityNo,
              price: parseFloat(item.price) || 0,
              lowest_price: parseFloat(item.lowestPrice) || 0,
              spread: parseFloat(item.spread) || 0,
              abrade: item.abrade,
              paintSeed: item.paintSeed,
              nameTag: item.nameTag,
              userNickName: item.sellerName,
              assetId: item.assetId,
              iconUrl: item.iconUrl || item.icon_url || '',
              weapon_name: item.weaponName,
              weaponName: item.weaponName,
              weaponId: item.weaponId,
              commissionFee: parseFloat(item.commissionFee) || 0,
              priceDiff: parseFloat(item.priceDiff) || 0,
              steam_hash_name: item.steamHashName || item.steam_hash_name || '',
              // 关键字段：用于判断数据来源和购买逻辑
              dataType: item.dataType,  // 数据类型，Steam搜索结果可能为空或特定值
              listing_id: item.listingId || item.listing_id || '',  // Steam市场的listing_id
              listingId: item.listingId || item.listing_id || '',   // 兼容驼峰命名
              configId: item.configId,  // 配置ID
              referencePrice: null // 参考价，稍后通过查询填充
            }
            console.log('[数据映射] 映射后item:', mappedItem)
            return mappedItem
          })
          
          // 按溢价从小到大排序（溢价最小的在最上面）
          historyItems.sort((a, b) => (a.spread || 0) - (b.spread || 0))
          
          // 按武器名称分组显示历史数据
          const weaponGroups = {}
          historyItems.forEach(item => {
            const weaponDisplayName = item.weapon_name || item.weaponName || '未知武器'
            if (!weaponGroups[weaponDisplayName]) {
              weaponGroups[weaponDisplayName] = []
            }
            weaponGroups[weaponDisplayName].push(item)
          })
          
          // 转换为weapons数组格式
          const weapons = Object.keys(weaponGroups).map(name => ({
            weapon_name: name,
            items: weaponGroups[name]
          }))
          
          crawlResult.value = { weapons }
          
          // 查询参考价
          await loadReferencePrices(historyItems)
          
          console.log(`[页面加载] 已加载 ${result.items.length} 条历史搜索结果`)
          console.log(`[页面加载] 第一条原始数据:`, result.items[0])
          console.log(`[页面加载] 第一条转换后数据:`, historyItems[0])
          console.log(`[页面加载] 分组后的weapons:`, weapons)
          console.log(`[页面加载] crawlResult.value:`, crawlResult.value)
          await nextTick()
        } else {
          console.log('[页面加载] 没有找到历史数据')
        }
      } catch (error) {
        console.error('[页面加载] 加载历史数据失败:', error)
      }
    }

    // 轮询获取数据库中的搜索结果（页面打开期间持续执行）
    const pollSearchResults = async () => {
      // 如果搜索已完成，停止轮询
      if (!isCrawling.value && pollingTimer.value) {
        console.log('[轮询] 搜索已完成，停止轮询')
        stopPolling()
        return
      }
      
      try {
        lastPollingTime.value = Date.now()
        
        // 获取所有数据，根据选中的配置ID过滤
        const params = new URLSearchParams({
          dataType: 'rename'
        })
        // 如果选中了配置，则只查询该配置的数据
        if (selectedConfigId.value) {
          params.append('configId', selectedConfigId.value.toString())
        }
        const url = `${API_CONFIG.BASE_URL}/searchRename/items/list?${params.toString()}`
        
        const response = await fetch(url)
        
        if (!response.ok) {
          console.error('[轮询] HTTP错误:', response.status)
          return
        }

        const result = await response.json()
        console.log('[轮询] API返回:', result)
        
        // 如果没有查询到数据，直接返回，不进行其他操作
        if (!result.success || !result.items || result.items.length === 0) {
          return
        }
        
        if (result.items.length > 0) {
          console.log(`[轮询] 获取到 ${result.items.length} 条数据`)
          console.log('[轮询] 第一条数据示例 (驼峰命名):', result.items[0])
          console.log('[轮询] 第一条weaponName:', result.items[0].weaponName)
          
          // 如果正在搜索，重置无数据计数
          if (isCrawling.value) {
            noDataCount.value = 0
          }
          
          // 获取当前的所有商品列表
          const currentItems = crawlResult.value?.weapons?.[0]?.items || []
          
          // 后端已通过 to_dict() 返回驼峰命名，直接使用
          const newItems = result.items.map(item => {
            return {
              id: item.id,  // 数据库主键，用于后端查询商品详情
              commodityId: item.commodityId,  // Steam的listing_id或悠悠有品的商品ID
              commodityNo: item.commodityNo,
              price: parseFloat(item.price) || 0,
              lowest_price: parseFloat(item.lowestPrice) || 0,
              spread: parseFloat(item.spread) || 0,
              abrade: item.abrade,
              paintSeed: item.paintSeed,
              nameTag: item.nameTag,
              userNickName: item.sellerName,
              assetId: item.assetId,
              iconUrl: item.iconUrl || item.icon_url || '',
              weapon_name: item.weaponName,
              weaponName: item.weaponName,
              weaponId: item.weaponId,
              commissionFee: parseFloat(item.commissionFee) || 0,
              priceDiff: parseFloat(item.priceDiff) || 0,
              steam_hash_name: item.steamHashName || item.steam_hash_name || '',
              // 关键字段：用于判断数据来源和购买逻辑
              dataType: item.dataType,
              listing_id: item.listingId || item.listing_id || '',
              listingId: item.listingId || item.listing_id || '',
              configId: item.configId,
              referencePrice: null // 参考价，稍后通过查询填充
            }
          })
          
          // 去重合并（基于 commodityId）
          const itemMap = new Map()
          currentItems.forEach(item => itemMap.set(item.id, item))
          newItems.forEach(item => itemMap.set(item.id, item))
          const allItems = Array.from(itemMap.values())
          
          // 按溢价从小到大排序（溢价最小的在最上面）
          allItems.sort((a, b) => (a.spread || 0) - (b.spread || 0))
          
          // 按武器名称分组显示数据
          const weaponGroups = {}
          allItems.forEach(item => {
            const weaponDisplayName = item.weapon_name || item.weaponName || '未知武器'
            if (!weaponGroups[weaponDisplayName]) {
              weaponGroups[weaponDisplayName] = []
            }
            weaponGroups[weaponDisplayName].push(item)
          })
          
          // 转换为weapons数组格式
          const weapons = Object.keys(weaponGroups).map(name => ({
            weapon_name: name,
            items: weaponGroups[name]
          }))
          
          crawlResult.value = { weapons }
          
          // 更新lastItemId
          if (result.items.length > 0) {
            const maxId = Math.max(...result.items.map(item => item.id))
            if (maxId > lastItemId.value) {
              lastItemId.value = maxId
            }
          }
          
          // 查询参考价
          await loadReferencePrices(allItems)
          
          await nextTick()
        }
      } catch (error) {
        console.error('[轮询] 请求失败:', error)
      }
    }

    // 启动轮询（页面在前台时持续轮询）
    const startPolling = () => {
      if (pollingTimer.value) {
        return // 已经在轮询中
      }
      
      console.log(`[轮询] 启动持续轮询，间隔 ${POLL_INTERVAL}ms (${POLL_INTERVAL/1000}秒)`)
      pollingTimer.value = setInterval(pollSearchResults, POLL_INTERVAL)
      
      // 立即执行一次
      pollSearchResults()
    }

    // 停止轮询
    const stopPolling = () => {
      if (pollingTimer.value) {
        console.log('[轮询] 停止轮询')
        clearInterval(pollingTimer.value)
        pollingTimer.value = null
      }
    }

    // 开始爬取（流式接收）- 全新重构版本
    const startCrawl = async () => {
      // 开始搜索时自动折叠工具区域与配置栏
      isConfigSectionsCollapsed.value = true
      
      // 验证基本配置
      if (!crawlForm.value.configName) {
        ElMessage.warning('请输入配置名称')
        return
      }

      if (!crawlForm.value.platformType) {
        ElMessage.warning('请选择平台类型')
        return
      }
      const platformKey = normalizePlatformKey(crawlForm.value.platformType)
      if (!platformKey) {
        ElMessage.warning('请选择有效的平台类型')
        return
      }
      
      const requiresCrawler = platformKey !== 'steam'
      if (requiresCrawler && !crawlForm.value.crawlAccountId) {
        ElMessage.warning('请选择爬取账号')
        return
      }
      
      if (!crawlForm.value.steamId) {
        ElMessage.warning('请选择购买账号')
        return
      }
      
      if (!crawlForm.value.weaponId || crawlForm.value.weaponId.length === 0) {
        ElMessage.warning('请至少添加一个饰品ID')
        return
      }

      const customConfigResult = validateCustomConfig()
      if (!customConfigResult.valid) {
        ElMessage.error(customConfigResult.message)
        return
      }
      const customConfig = customConfigResult.config

      const spiderEndpoint = PLATFORM_SPIDER_ENDPOINT_MAP[platformKey]
      if (!spiderEndpoint) {
        ElMessage.error('该平台暂不支持自动查询')
        return
      }

      // 确认对话框
      try {
        const weaponNames = crawlForm.value.weaponId.map(w => w.name).join('、')
        let confirmMessage = `确定要开始查询改名饰品吗？\n\n`
        confirmMessage += `配置名称: ${crawlForm.value.configName}\n`
        confirmMessage += `爬取账号: ${crawlForm.value.crawlAccountId || (platformKey === 'steam' ? '（无需选择）' : '')}\n`
        confirmMessage += `购买账号: ${crawlForm.value.steamId}\n`
        const platformLabel = getSourceLabel(crawlForm.value.platformType) || '未选择'
        confirmMessage += `平台类型: ${platformLabel}\n`
        confirmMessage += `监控饰品: ${weaponNames}\n`
        confirmMessage += `饰品数量: ${crawlForm.value.weaponId.length} 个`
        
        confirmMessage += `\n最大差价: ${customConfig['最大差价']} 元`
        confirmMessage += `\n查询间隔: ${customConfig['饰品自动查询间隔']} 秒`
        confirmMessage += `\n是否自动购买: ${customConfig['是否自动购买'] ? '是' : '否'}`

        await ElMessageBox.confirm(
          confirmMessage,
          '确认执行',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
      } catch {
        return
      }

      // 自动清空历史结果列表（无需确认）
      await clearCrawlHistory(true)

      // 初始化状态
      isCrawling.value = true
      crawlResult.value = { weapons: [] }
      lastItemId.value = 0 // 重置lastItemId
      noDataCount.value = 0 // 重置无数据计数
      console.log('[前端] 正在启动查询任务...')

      try {
        // 构建请求
        const spiderConfig = {
          weapon_id: crawlForm.value.weaponId,
          ...customConfig
        }

        // 如果有选中的配置ID，传递给后端
        if (selectedConfigId.value) {
          spiderConfig.config_id = selectedConfigId.value
        }

        if (platformKey === 'steam') {
          spiderConfig.steam_id = crawlForm.value.steamId
        } else {
          spiderConfig.steam_id = crawlForm.value.crawlAccountId
        }
        if (crawlForm.value.crawlAccountId) {
          spiderConfig.crawl_account_id = crawlForm.value.crawlAccountId
        }

        const requestSteamId = platformKey === 'steam'
          ? crawlForm.value.steamId
          : crawlForm.value.crawlAccountId
        
        const requestData = {
          steamId: requestSteamId,
          spider_config: spiderConfig
        }
        
        console.log('[前端] 发送搜索请求:', requestData)

        // 启动轮询（只有在开始搜索时才启动）
        startPolling()
        pollSearchResults()
        console.log('[前端] 轮询已启动，将持续获取搜索结果...')

        // 发起搜索请求（后台执行）
        fetch(
          spiderEndpoint,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
          }
        ).then(async response => {
          let result = null
          try {
            result = await response.json()
          } catch (parseError) {
            console.warn('[前端] 响应解析失败:', parseError)
          }

          if (!response.ok || !result?.success) {
            const errMsg = result?.message || `HTTP ${response.status}`
            throw new Error(errMsg)
          }

          console.log('[前端] 搜索任务响应:', result)
          console.log('[前端] 搜索任务已启动')
          console.log('[前端] 后台搜索任务已启动，开始轮询数据...')
        }).catch(error => {
          console.error('[前端] 启动搜索任务失败:', error)
          console.error(`[前端] 启动搜索任务失败: ${error.message}`)
          ElMessage.error(`启动搜索失败: ${error.message}`)
          isCrawling.value = false
          stopPolling() // 停止轮询
        })

        // 设置最大搜索时间（5分钟后自动停止搜索状态和轮询）
        setTimeout(() => {
          if (isCrawling.value) {
            console.log('[前端] 搜索超时，结束搜索状态')
            isCrawling.value = false
            stopPolling() // 停止轮询
            const totalItems = crawlResult.value?.weapons?.[0]?.items?.length || 0
            console.log(`[前端] 搜索超时结束，共找到 ${totalItems} 个商品`)
            ElMessage.warning(`搜索已超时结束，找到 ${totalItems} 个商品`)
            
            if (crawlResult.value) {
              saveCrawlResultToStorage(crawlResult.value)
            }
          }
        }, 5 * 60 * 1000) // 5分钟

      } catch (error) {
        console.error('搜索失败:', error)
        let errorMessage = '搜索失败'

        if (error.message) {
          errorMessage = error.message
        }

        ElMessage.error(errorMessage)
        console.error(`[前端] 搜索失败: ${errorMessage}`)
        isCrawling.value = false
        stopPolling() // 停止轮询
      }
    }

    // 重置表单
    const resetForm = () => {
      isProgrammaticPlatformChange.value = true
      crawlForm.value = {
        configName: '',
        steamId: '',
        crawlAccountId: '',
        platformType: '',
        weaponId: []
      }
      crawlResult.value = null
      resetCustomConfigForm()
    }

    // 获取模式标签
    const getModeLabel = (mode) => {
      const labels = {
        all: '爬取所有已改名饰品',
        new: '仅爬取新改名饰品',
        incremental: '增量更新'
      }
      return labels[mode] || mode
    }

    // 获取来源标签
    const getSourceLabel = (source) => {
      const labels = {
        youpin: '悠悠有品',
        buff: 'BUFF',
        steam: 'Steam市场'
      }
      if (!source) {
        return '未设置'
      }
      return labels[source] || source
    }

    const getPlatformTagType = (platform) => {
      const key = normalizePlatformKey(platform)
      if (key === 'youpin') return 'success'
      if (key === 'buff') return 'warning'
      if (key === 'steam') return 'info'
      return ''
    }

    // 加载配置列表
    const loadConfigList = async () => {
      try {
        // 只加载 key1 = 'spider_rename' 的配置
        const response = await axios.get(`${API_CONFIG.BASE_URL}/configV1/list`, {
          params: {
            key1: 'spider_rename'
          }
        })
        
        console.log('配置列表响应:', response.data)
        
        // 根据 key2 字段判断平台类型
        savedConfigs.value = (response.data.data || []).map(config => ({
          ...config,
          platformType: config.key2 || ''
        }))
        
        // 按ID降序排序
        savedConfigs.value.sort((a, b) => b.id - a.id)
        
        console.log('加载的配置列表:', savedConfigs.value)
      } catch (error) {
        console.error('加载配置列表失败:', error)
        // ElMessage.error('加载配置列表失败')
      }
    }

    // 选择并加载配置
    const selectConfig = async (configId) => {
      console.log('=== 开始加载配置 ===')
      console.log('配置ID:', configId)
      
      if (!configId) {
        console.warn('配置ID为空')
        return
      }

      selectedConfigId.value = configId
      console.log('已设置selectedConfigId:', selectedConfigId.value)
      
      // 切换配置时，先清空当前结果，避免显示混合数据
      crawlResult.value = { weapons: [] }
      lastItemId.value = 0

      try {
        isApplyingConfigState.value = true
        const config = savedConfigs.value.find(c => c.id === configId)
        console.log('找到的配置对象:', config)
        
        if (config && config.value) {
          await loadAccountsForPlatform(config.platformType || crawlForm.value.platformType)
          // 解析 value 字段（JSON字符串）
          let valueObj
          try {
            valueObj = typeof config.value === 'string' 
              ? JSON.parse(config.value) 
              : config.value
            console.log('解析后的配置值:', valueObj)
          } catch (parseError) {
            console.error('JSON解析失败:', parseError)
            ElMessage.error('配置数据格式错误')
            return
          }
          
          // 从 value 对象中提取饰品列表和Steam ID
          const weaponId = valueObj.weapon_id || []
          const steamId = valueObj.steam_id || ''
          
          console.log('提取的数据:')
          console.log('  - weaponId:', weaponId)
          console.log('  - steamId:', steamId)
          console.log('  - platformType:', config.platformType)
          
          // 移除 weapon_id 和 steam_id，剩余的作为自定义配置
          const { weapon_id, steam_id, crawl_account_id, ...restConfig } = valueObj
          
          // 构建新的表单数据
          const newFormData = {
            configName: config.dataName || '',
            steamId: steamId,
            crawlAccountId: crawl_account_id || steamId || '',
            platformType: config.platformType || '',
            weaponId: Array.isArray(weaponId) ? weaponId : []
          }
          
          console.log('准备填充的表单数据:', newFormData)
          
          // 加载配置数据到表单
          isProgrammaticPlatformChange.value = true
          crawlForm.value = newFormData
          applyCustomConfig(restConfig)
          
          // 等待下一个tick确保数据已更新
          await new Promise(resolve => setTimeout(resolve, 50))
          
          console.log('表单填充完成，当前表单值:')
          console.log('  - configName:', crawlForm.value.configName)
          console.log('  - steamId:', crawlForm.value.steamId)
          console.log('  - platformType:', crawlForm.value.platformType)
          console.log('  - weaponId:', crawlForm.value.weaponId)
          console.log('  - 自定义配置:', restConfig)
          console.log('=== 配置加载完成 ===')
          
          // 选择配置后，启动轮询并立即刷新结果列表（显示该配置的数据）
          startPolling()
          await pollSearchResults()
          
          ElMessage.success(`已加载配置: ${config.dataName}`)
        } else {
          console.warn('配置缺少value字段:', config)
          ElMessage.warning('配置数据为空')
        }
      } catch (error) {
        console.error('加载配置失败:', error)
        console.error('错误堆栈:', error.stack)
        ElMessage.error(`加载配置失败: ${error.message}`)
      } finally {
        isApplyingConfigState.value = false
      }
    }

    const autoSaveConfig = async () => {
      if (!selectedConfigId.value) {
        return
      }
      if (!crawlForm.value.configName) {
        return
      }
      if (!crawlForm.value.platformType) {
        return
      }

      try {
        const customConfigResult = validateCustomConfig()
        if (!customConfigResult.valid) {
          console.warn('自动保存跳过，自定义配置错误:', customConfigResult.message)
          return
        }
        let valueObj = { ...customConfigResult.config }

        if (crawlForm.value.weaponId && crawlForm.value.weaponId.length > 0) {
          valueObj.weapon_id = crawlForm.value.weaponId
        }

        if (crawlForm.value.steamId) {
          valueObj.steam_id = crawlForm.value.steamId
        }

        if (crawlForm.value.crawlAccountId) {
          valueObj.crawl_account_id = crawlForm.value.crawlAccountId
        }

        const configData = {
          id: selectedConfigId.value,
          dataName: crawlForm.value.configName,
          key1: 'spider_rename',
          key2: crawlForm.value.platformType,
          value: JSON.stringify(valueObj)
        }

        await axios.post(`${API_CONFIG.BASE_URL}/configV1/save`, configData)
      } catch (error) {
        console.error('自动保存配置失败:', error)
      }
    }

    const autoSaveTimer = ref(null)
    const scheduleAutoSave = () => {
      if (isApplyingConfigState.value) {
        return
      }
      if (!selectedConfigId.value) {
        return
      }

      if (autoSaveTimer.value) {
        clearTimeout(autoSaveTimer.value)
      }

      autoSaveTimer.value = setTimeout(() => {
        autoSaveTimer.value = null
        autoSaveConfig()
      }, 800)
    }

    watch(
      () => [
        crawlForm.value.configName,
        crawlForm.value.platformType,
        crawlForm.value.steamId,
        crawlForm.value.crawlAccountId
      ],
      () => {
        scheduleAutoSave()
      }
    )

    watch(
      customConfigForm,
      () => {
        if (isProgrammaticCustomConfigChange.value) {
          return
        }
        scheduleAutoSave()
      },
      { deep: true }
    )

    watch(
      () => allCrawlItems.value,
      (items) => {
        if (items && items.length > 0) {
          loadReferencePrices(items)
        }
      },
      { immediate: true, deep: false }
    )

    watch(
      referencePriceSource,
      () => {
        applyReferencePricesToItems(allCrawlItems.value)
        loadReferencePrices()
      }
    )

    watch(
      () => crawlForm.value.weaponId,
      () => {
        scheduleAutoSave()
      },
      { deep: true }
    )

    // 创建新配置（清空表单）
    const createNewConfig = () => {
      selectedConfigId.value = null
      resetForm()
      ElMessage.info('已清空表单，可以创建新配置')
    }

    // 保存配置（直接保存，不弹窗）
    const saveConfig = async () => {
      if (!crawlForm.value.configName) {
        ElMessage.warning('请输入配置名称')
        return
      }

      if (!crawlForm.value.platformType) {
        ElMessage.warning('请选择平台类型')
        return
      }

      try {
        const customConfigResult = validateCustomConfig()
        if (!customConfigResult.valid) {
          ElMessage.error(customConfigResult.message)
          return
        }

        // 构建 value 对象
        let valueObj = { ...customConfigResult.config }
        
        // 将饰品列表添加到 value 对象中
        if (crawlForm.value.weaponId && crawlForm.value.weaponId.length > 0) {
          valueObj.weapon_id = crawlForm.value.weaponId
        }
        
        // 添加其他必要字段
        if (crawlForm.value.steamId) {
          valueObj.steam_id = crawlForm.value.steamId
        }
        if (crawlForm.value.crawlAccountId) {
          valueObj.crawl_account_id = crawlForm.value.crawlAccountId
        }

        // 根据平台类型设置 key2
        const key2 = crawlForm.value.platformType

        const configData = {
          dataName: crawlForm.value.configName,
          key1: 'spider_rename',
          key2: key2,
          value: JSON.stringify(valueObj)
        }

        const isUpdating = !!selectedConfigId.value
        let response

        if (isUpdating) {
          configData.id = selectedConfigId.value
          response = await axios.post(`${API_CONFIG.BASE_URL}/configV1/update`, configData)
        } else {
          response = await axios.post(`${API_CONFIG.BASE_URL}/configV1/save`, configData)
        }
        
        if (response.data.success) {
          ElMessage.success(isUpdating ? '更新配置成功' : '保存配置成功')
          
          // 重新加载配置列表
          await loadConfigList()

          if (isUpdating && selectedConfigId.value) {
            await selectConfig(selectedConfigId.value)
          } else if (!isUpdating && response.data.data?.id) {
            selectedConfigId.value = response.data.data.id
            await selectConfig(selectedConfigId.value)
          }
        } else {
          throw new Error(response.data.message || '保存配置失败')
        }
      } catch (error) {
        console.error('保存配置失败:', error)
        const errorMessage = error.response?.data?.message || error.message || '保存配置失败'
        ElMessage.error(errorMessage)
      }
    }

    // 删除配置
    // 删除当前配置
    const deleteCurrentConfig = async () => {
      if (!selectedConfigId.value) {
        ElMessage.warning('请先选择一个配置')
        return
      }
      await deleteConfig(selectedConfigId.value)
    }

    const deleteConfig = async (configId) => {
      if (!configId) {
        return
      }

      try {
        const config = savedConfigs.value.find(c => c.id === configId)
        
        await ElMessageBox.confirm(
          `确定要删除配置 "${config.dataName}" 吗？此操作不可恢复。`,
          '确认删除',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        // TODO: 替换为实际的API端点
        const response = await axios.delete(`${API_CONFIG.BASE_URL}/configV1/delete/${configId}`)
        
        if (response.data.success) {
          ElMessage.success('删除配置成功')
          
          // 如果删除的是当前选中的配置，清空选中状态
          if (selectedConfigId.value === configId) {
            selectedConfigId.value = null
          }
          
          // 重新加载配置列表
          await loadConfigList()
        } else {
          throw new Error(response.data.message || '删除配置失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除配置失败:', error)
          const errorMessage = error.response?.data?.message || error.message || '删除配置失败'
          ElMessage.error(errorMessage)
        }
      }
    }

    // 格式化时间
    const formatTime = (timestamp) => {
      if (!timestamp) return '-'
      const date = new Date(timestamp)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    // 切换搜索结果折叠
    const toggleSearchResults = () => {
      isSearchResultsCollapsed.value = !isSearchResultsCollapsed.value
    }
    
    // 武器类型改变时的处理
    const handleWeaponTypeChange = async (value) => {
      // 清空武器名称选择
      weaponSearchFilters.value.weaponName = ''
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
      if (!weaponSearchFilters.value.weaponType) {
        await loadWeaponNames(null)
      }
    }

    // 搜索饰品（重置并开始新搜索）
    const handleSearchWeapon = async () => {
      if (!crawlForm.value.platformType) {
        ElMessage.warning('请先选择平台类型')
        return
      }

      // 验证价格区间
      if (weaponSearchFilters.value.priceMin !== null && 
          weaponSearchFilters.value.priceMax !== null &&
          weaponSearchFilters.value.priceMin > weaponSearchFilters.value.priceMax) {
        ElMessage.warning('最低价格不能大于最高价格')
        return
      }
      
      // 重置分页状态
      currentPage.value = 1
      weaponSearchResults.value = []
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
        isSearchingWeapon.value = true
      } else {
        isLoadingMore.value = true
      }
      
      try {
        const params = {
          page: currentPage.value,
          limit: pageSize.value
        }
        
        // 使用爬取配置中的平台类型
        params.platformType = crawlForm.value.platformType
        
        // 添加关键词（如果有）
        if (weaponSearchKeyword.value && weaponSearchKeyword.value.trim()) {
          params.keyword = weaponSearchKeyword.value.trim()
        }
        
        // 添加武器类型过滤（如果有）
        if (weaponSearchFilters.value.weaponType) {
          params.weaponType = weaponSearchFilters.value.weaponType
        }
        
        // 添加武器名称过滤（如果有）
        if (weaponSearchFilters.value.weaponName) {
          params.weaponName = weaponSearchFilters.value.weaponName
        }
        
        // 添加稀有度过滤（如果有）
        if (weaponSearchFilters.value.rarity) {
          params.rarity = weaponSearchFilters.value.rarity
        }
        
        // 添加价格过滤
        if (weaponSearchFilters.value.priceMin !== null && weaponSearchFilters.value.priceMin !== '') {
          params.priceMin = weaponSearchFilters.value.priceMin
        }
        if (weaponSearchFilters.value.priceMax !== null && weaponSearchFilters.value.priceMax !== '') {
          params.priceMax = weaponSearchFilters.value.priceMax
        }
        
        // 添加最小在售数量过滤
        if (weaponSearchFilters.value.minOnSaleCount !== null && weaponSearchFilters.value.minOnSaleCount !== '') {
          params.minOnSaleCount = weaponSearchFilters.value.minOnSaleCount
        }
        
        const response = await axios.get(`${API_CONFIG.BASE_URL}/webSelectWeaponV1/searchWeaponDetail`, {
          params: params
        })
        
        if (response.data.success) {
          const newData = response.data.data || []
          
          if (currentPage.value === 1) {
            // 首次搜索，替换数据
            weaponSearchResults.value = newData
            if (newData.length === 0) {
              ElMessage.info('未找到匹配的饰品')
            } else {
              ElMessage.success(`找到 ${newData.length} 件饰品`)
            }
          } else {
            // 追加数据
            weaponSearchResults.value.push(...newData)
          }
          
          // 判断是否还有更多数据
          hasMore.value = newData.length >= pageSize.value
        } else {
          ElMessage.error(response.data.message || '搜索失败')
        }
      } catch (error) {
        console.error('搜索饰品失败:', error)
        const errorMessage = error.response?.data?.message || error.message || '搜索饰品失败'
        ElMessage.error(errorMessage)
      } finally {
        isSearchingWeapon.value = false
        isLoadingMore.value = false
      }
    }

    // 清除搜索结果
    const clearWeaponSearch = () => {
      weaponSearchResults.value = []
      weaponSearchKeyword.value = ''
      weaponSearchFilters.value = {
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
    
    // 一键添加全部饰品ID
    const addAllWeaponIds = () => {
      if (!crawlForm.value.platformType) {
        ElMessage.warning('请先选择平台类型')
        return
      }

      if (!weaponSearchResults.value || weaponSearchResults.value.length === 0) {
        ElMessage.warning('没有可添加的饰品')
        return
      }
      
      let addedCount = 0
      weaponSearchResults.value.forEach(row => {
        const id = getWeaponIdByPlatform(row)
        const name = row.market_listing_item_name
        
        if (id && name) {
          // 检查是否已存在
          const exists = crawlForm.value.weaponId.some(w => w.id === id)
          if (!exists) {
            crawlForm.value.weaponId.push({ id, name })
            addedCount++
          }
        }
      })
      
      if (addedCount > 0) {
        ElMessage.success(`成功添加 ${addedCount} 个饰品ID`)
        
        // 自动保存配置
        if (selectedConfigId.value) {
          autoSaveConfig()
        }
      } else {
        ElMessage.info('所有饰品ID已存在')
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

    // 根据平台类型获取对应的饰品ID
    const getWeaponIdByPlatform = (row) => {
      const platformKey = normalizePlatformKey(crawlForm.value.platformType)
      if (platformKey === 'buff') {
        return row.buff_id || row.yyyp_id || row.id || ''
      }
      if (platformKey === 'steam') {
        return row.steam_hash_name || row.steamHashName || row.en_weapon_name || row.id || ''
      }
      // 默认返回悠悠有品 ID
      return row.yyyp_id || row.buff_id || row.id || row.steam_hash_name || ''
    }

    // 添加饰品ID到表单
    // 从搜索组件添加单个饰品
    const handleAddWeaponFromSearch = ({ id, name }) => {
      if (!id || !name) {
        ElMessage.warning('无效的饰品数据')
        return
      }

      // 检查是否已存在
      if (crawlForm.value.weaponId.some(w => w.id === id.toString())) {
        ElMessage.warning('该饰品已存在')
        return
      }

      // 添加饰品对象
      crawlForm.value.weaponId.push({
        id: id.toString(),
        name: name
      })

      ElMessage.success('饰品已添加')

      // 自动保存配置
      if (selectedConfigId.value) {
        autoSaveConfig()
      }
    }

    // 从搜索组件一键添加全部饰品
    const handleAddAllWeaponsFromSearch = (weaponsToAdd) => {
      if (!weaponsToAdd || weaponsToAdd.length === 0) {
        ElMessage.warning('没有可添加的饰品')
        return
      }

      let addedCount = 0
      weaponsToAdd.forEach(({ id, name }) => {
        if (id && name) {
          // 检查是否已存在
          const exists = crawlForm.value.weaponId.some(w => w.id === id.toString())
          if (!exists) {
            crawlForm.value.weaponId.push({ id: id.toString(), name })
            addedCount++
          }
        }
      })

      if (addedCount > 0) {
        ElMessage.success(`成功添加 ${addedCount} 个饰品ID`)

        // 自动保存配置
        if (selectedConfigId.value) {
          autoSaveConfig()
        }
      } else {
        ElMessage.info('所有饰品ID已存在')
      }
    }

    const addWeaponId = (row) => {
      if (!crawlForm.value.platformType) {
        ElMessage.warning('请先选择平台类型')
        return
      }

      const weaponId = getWeaponIdByPlatform(row)
      
      if (!weaponId) {
        const platformName = getSourceLabel(crawlForm.value.platformType) || '当前平台'
        ElMessage.warning(`该饰品没有${platformName}ID`)
        return
      }

      // 检查是否已存在
      if (crawlForm.value.weaponId.some(w => w.id === weaponId.toString())) {
        ElMessage.warning('该饰品已存在')
        return
      }
      
      // 添加饰品对象（包含ID和名称）
      crawlForm.value.weaponId.push({
        id: weaponId.toString(),
        name: row.market_listing_item_name || row.name || '未知饰品'
      })
      
      const platformName = getSourceLabel(crawlForm.value.platformType) || '当前平台'
      ElMessage.success(`已添加${platformName}饰品: ${row.market_listing_item_name || row.name}`)
    }

    // 删除饰品ID
    const removeWeaponId = (idToRemove) => {
      crawlForm.value.weaponId = crawlForm.value.weaponId.filter(w => w.id !== idToRemove)
      ElMessage.success('已删除饰品')
    }

    // 购买饰品
    const handleBuyWeapon = async (item) => {
      // 输出完整的 item 数据用于调试
      console.log('========== 购买商品 ==========')
      console.log('购买商品 (完整数据):', JSON.parse(JSON.stringify(item)))
      console.log('商品ID:', item.id)
      console.log('商品所有字段:', Object.keys(item))
      console.log('steam_hash_name:', item.steam_hash_name || item.steamHashName || '无')
      console.log('listing_id:', item.listing_id || item.listingId || '无')
      console.log('当前表单平台类型:', crawlForm.value.platformType)
      console.log('================================')
      
      // 确认购买
      try {
        await ElMessageBox.confirm(
          `确认购买该商品吗？\n\n改名：${item.nameTag || '无'}\n价格：¥${item.price}\n磨损：${item.abrade || '-'}\n溢价：+¥${typeof item.spread === 'number' ? item.spread.toFixed(2) : '0.00'}`,
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
      
      // 检查购买账号
      if (!crawlForm.value.steamId) {
        ElMessage.warning('请先选择购买账号')
        return
      }
      
      // 设置购买中状态
      buyingItems.value[item.id] = true
      
      // 根据平台类型选择不同的购买流程
      // 1. 优先从选中的配置中获取平台类型
      let configPlatformType = ''
      if (selectedConfigId.value) {
        const selectedConfig = savedConfigs.value.find(c => c.id === selectedConfigId.value)
        if (selectedConfig) {
          configPlatformType = (selectedConfig.platformType || selectedConfig.key2 || '').toLowerCase().trim()
          console.log('[购买] 从配置中获取平台类型:', configPlatformType)
        }
      }
      
      // 2. 检查表单中的平台类型（支持多种可能的格式）
      const formPlatformType = (crawlForm.value.platformType || '').toLowerCase().trim()
      
      // 3. 使用配置中的平台类型（如果存在），否则使用表单中的平台类型
      const platformType = configPlatformType || formPlatformType
      const isSteamPlatform = platformType === 'steam' || platformType === 'steam市场' || platformType.includes('steam')
      
      // 4. 检查 item 中的关键字段
      const hasListingId = !!(item.listing_id || item.listingId)
      const hasAssetId = !!(item.assetId)
      
      // 5. 综合判断：优先使用配置中的平台类型，其次检查是否有 listing_id
      // 注意：不能仅用 steam_hash_name 判断，因为悠悠有品数据也可能包含此字段
      let isSteam = false
      
      // 判断逻辑：
      // 1. 如果配置指定为 Steam 平台，则使用 Steam 购买
      // 2. 如果 item 有 listing_id 和 assetId，说明来自 Steam 市场搜索
      if (isSteamPlatform) {
        isSteam = true
        console.log('[购买] 根据配置判断为 Steam 平台')
      } else if (hasListingId && hasAssetId) {
        isSteam = true
        console.log('[购买] 根据 item 字段判断为 Steam 市场物品')
      }

      // 调试日志：确认平台类型
      console.log('[购买] ========== 平台类型判断 ==========')
      console.log('[购买] 选中的配置ID:', selectedConfigId.value)
      console.log('[购买] 配置中的平台类型:', configPlatformType || '无')
      console.log('[购买] 表单中的平台类型:', formPlatformType || '无')
      console.log('[购买] 是 Steam 平台:', isSteamPlatform)
      console.log('[购买] Item commodityId:', item.id)
      console.log('[购买] Item listing_id:', item.listing_id || item.listingId || '无')
      console.log('[购买] Item assetId:', item.assetId || '无')
      console.log('[购买] Item steam_hash_name:', item.steam_hash_name || item.steamHashName || '无')
      console.log('[购买] 最终判断使用 Steam 购买:', isSteam)
      console.log('[购买] ======================================')
      
      // 开始购买流程
      const loadingMessage = ElMessage({
        message: isSteam ? '正在购买Steam市场物品...' : '正在创建订单...',
        type: 'info',
        duration: 0
      })
      
      try {
        // 使用之前判断的结果（isSteam），确保一致性
        // 如果之前判断是 Steam，这里也应该是 Steam
        console.log('[购买] ========== 开始购买流程 ==========')
        console.log('[购买] 最终判断结果 isSteam:', isSteam)
        console.log('[购买] 将进入:', isSteam ? 'Steam 购买分支' : 'youping 购买分支')
        console.log('[购买] ======================================')
        
        if (isSteam) {
          // Steam市场购买流程
          console.log('[购买] ✅ 进入 Steam 市场购买流程')
          const marketHashName = item.steam_hash_name || item.steamHashName || ''
          const listingId = item.listing_id || item.listingId || ''
          
          console.log('[购买] Steam 物品信息:', {
            marketHashName: marketHashName || '无',
            listingId: listingId || '无',
            price: item.price
          })
          
          if (!marketHashName && !listingId) {
            loadingMessage.close()
            ElMessageBox.alert(
              '无法购买：缺少Steam市场物品信息\n\n请确保物品包含 market_hash_name 或 listing_id 字段。\n\n如果这是 Steam 市场的查询结果，请联系开发者检查数据格式。',
              '购买失败',
              {
                confirmButtonText: '知道了',
                type: 'error'
              }
            )
            return
          }
          
          const requestData = {
            steamId: crawlForm.value.steamId,
            commodityId: item.id, // 传递商品ID，用于从数据库获取 listing_id 和 token（与悠悠有品方法一致）
            market_hash_name: marketHashName,
            listing_id: listingId,
            price: item.price,
            currency: 'USD',
            max_price: item.price ? item.price * 1.2 : undefined  // 允许20%的价格波动
          }
          
          console.log('[购买] Steam市场购买请求数据:', requestData)
          console.log('[购买] 调用接口:', `${API_CONFIG.SPIDER_BASE_URL}${API_CONFIG.ENDPOINTS.STEAM_BUY_MARKET_ITEM}`)
          
          let confirmationTipTimer = null
          let confirmationTipMessage = null
          
          const stopConfirmationTip = () => {
            if (confirmationTipTimer) {
              clearTimeout(confirmationTipTimer)
              confirmationTipTimer = null
            }
            if (confirmationTipMessage) {
              confirmationTipMessage.close?.()
              confirmationTipMessage = null
            }
          }
          
          confirmationTipTimer = setTimeout(() => {
            confirmationTipMessage = ElMessage({
              type: 'warning',
              message: '请在 Steam 手机令牌中确认本次交易，系统会自动轮询直到成功。',
              duration: 0,
              showClose: true
            })
          }, 1200)
          
          // 调用Steam市场购买接口 - 对接 market_buy.py 中的 SteamMarketBuyer
          // 接口路径: /steamSpiderV1/buyMarketItem -> steam_index.py -> SteamMarketBuyer (market_buy.py)
          let response
          try {
            response = await axios.post(
              `${API_CONFIG.SPIDER_BASE_URL}${API_CONFIG.ENDPOINTS.STEAM_BUY_MARKET_ITEM}`,
              requestData
            )
          } finally {
            stopConfirmationTip()
          }
          
          console.log('Steam市场购买响应:', response.data)
          
          loadingMessage.close()
          
          if (response.data.success) {
            // 购买成功 - 标记为已购买
            purchasedItems.value.add(item.id)
            
            // 更新数据库中的状态为 buyed
            try {
              await axios.post(
                `${API_CONFIG.BASE_URL}/searchRename/item/update-status`,
                {
                  commodityId: item.id,
                  status: 'buyed'
                }
              )
              console.log('数据库状态已更新为 buyed')
            } catch (updateError) {
              console.error('更新数据库状态失败:', updateError)
              // 不影响购买成功的提示
            }
            
            const buyData = response.data.data || {}
            if (buyData.confirmation_waited) {
              ElMessage.info('已检测到手机令牌确认，系统完成后已自动继续。')
            }
            const message = `购买成功！\n\n商品：${item.nameTag || '改名饰品'}\n价格：$${buyData.price || item.price}\n状态：购买成功✅\n\n物品将发送至您的Steam库存。`
            
            ElMessageBox.alert(
              message,
              '购买完成',
              {
                confirmButtonText: '知道了',
                type: 'success',
                callback: () => {
                  ElMessage.success('购买成功！')
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
        } else {
          // 悠悠有品购买流程（原有逻辑）
          console.log('[购买] ========== ⚠️ 使用 悠悠有品 购买流程 ==========')
          console.log('[购买] ⚠️ 警告：平台类型不是 steam，使用 youping 接口')
          console.log('[购买] 当前表单平台类型:', crawlForm.value.platformType)
          console.log('[购买] 标准化表单平台类型:', formPlatformType)
          console.log('[购买] 配置平台类型:', configPlatformType || '无')
          console.log('[购买] 最终平台类型:', platformType || '无')
          console.log('[购买] isSteamPlatform:', isSteamPlatform)
          console.log('[购买] isSteamItem:', isSteamItem)
          console.log('[购买] 最终 isSteam:', isSteam)
          console.log('[购买] 如果这是 Steam 市场商品，请检查平台类型设置')
          console.log('[购买] ================================================')
          
          // 如果平台类型明显是 Steam 但进入了 else 分支，给出警告
          if (formPlatformType.includes('steam') || configPlatformType.includes('steam')) {
            console.error('[购买] ❌ 错误：检测到平台类型包含 steam，但进入了 youping 分支！')
            console.error('[购买] 这可能是代码逻辑错误，请检查判断条件')
            ElMessage.warning('检测到平台类型可能是 Steam，但使用了 youping 接口。如果这是 Steam 市场商品，请联系开发者。')
          }
          
          const requestData = {
            steamId: crawlForm.value.steamId,  // ✅ 使用购买账号
            commodityId: item.id,
            buyQuantity: 1,
            price: item.price,
            autoConfirmPayment: true,  // 自动使用余额支付
            pollPayment: true  // 轮询支付状态
          }
          
          console.log('[购买] 购买请求数据 (使用购买账号):', requestData)
          console.log('[购买]   - 购买账号:', crawlForm.value.steamId)
          console.log('[购买]   - 爬取账号:', crawlForm.value.crawlAccountId)
          console.log('[购买] 调用接口:', `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/buyCommodity`)
          
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
            const paymentAmount = item.price || '未知'
            
            // 检查支付状态
            const payStatus = paymentStatus.payStatus
            let message = ''
            
            if (payStatus === 2) {
              // 支付成功 - 标记为已购买
              purchasedItems.value.add(item.id)
              
              // 更新数据库中的状态为 buyed
              try {
                await axios.post(
                  `${API_CONFIG.BASE_URL}/searchRename/item/update-status`,
                  {
                    commodityId: item.id,
                    status: 'buyed'
                  }
                )
                console.log('数据库状态已更新为 buyed')
              } catch (updateError) {
                console.error('更新数据库状态失败:', updateError)
                // 不影响购买成功的提示
              }
              
              message = `购买成功！\n\n商品：${item.nameTag || '改名饰品'}\n订单号：${orderNo}\n金额：¥${paymentAmount}\n状态：支付成功✅\n\n饰品将发送至您的库存。`
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
      } finally {
        // 移除购买中状态
        buyingItems.value[item.id] = false
      }
    }

    // 表格行样式
    const getRowClassName = () => {
      return 'weapon-row'
    }

    const tableHeaderStyle = () => {
      return {
        backgroundColor: '#2a2a2a',
        color: '#fff',
        fontWeight: 600,
        borderBottom: '1px solid #3a3a3a'
      }
    }

    const handleSidebarAreaClick = (event) => {
      const target = event.target
      if (!target) return

      // 点击配置卡片时不触发折叠
      if (target.closest && target.closest('.config-item')) {
        return
      }

      toggleConfigSections()
    }

    // 组件挂载时加载数据（不自动启动搜索和轮询）
    onMounted(() => {
      if (crawlForm.value.platformType) {
        loadAccountsForPlatform(crawlForm.value.platformType)
      }
      loadConfigList()
      
      // 不再自动加载搜索结果和启动轮询，需要点击配置卡片后才进行搜索
    })

    // 组件卸载时停止轮询
    onUnmounted(() => {
      stopPolling()
      if (autoSaveTimer.value) {
        clearTimeout(autoSaveTimer.value)
        autoSaveTimer.value = null
      }
    })

    return {
      crawlFormRef,
      filteredSteamIdList,
      isCrawling,
      crawlForm,
      customConfigForm,
      booleanOptions,
      referencePriceSources,
      crawlResult,
      allCrawlItems,
      canStartCrawl,
      startCrawl,
      resetForm,
      getModeLabel,
      getSourceLabel,
      getPlatformTagType,
      handlePlatformTypeChange,
      // 配置管理
      savedConfigs,
      selectedConfigId,
      loadConfigList,
      selectConfig,
      createNewConfig,
      saveConfig,
      autoSaveConfig,
      deleteConfig,
      deleteCurrentConfig,
      formatTime,
      // 饰品搜索
      weaponSearchKeyword,
      weaponSearchResults,
      isSearchingWeapon,
      weaponSearchFilters,
      weaponNameList,
      isLoadingWeaponNames,
      isSearchResultsCollapsed,
      currentPage,
      pageSize,
      hasMore,
      isLoadingMore,
      handleSearchWeapon,
      handleWeaponTypeChange,
      loadWeaponNames,
      loadWeaponNamesIfNeeded,
      loadWeaponData,
      clearWeaponSearch,
      toggleSearchResults,
      addAllWeaponIds,
      getRarityColor,
      getWeaponIdByPlatform,
      addWeaponId,
      removeWeaponId,
      weaponIdList,
      isWeaponListCollapsed,
      toggleWeaponList,
      clearAllWeaponIds,
      getRowClassName,
      // 购买相关
      buyingItems,
      purchasedItems,
      handleBuyWeapon,
      getBuyButtonType,
      // 历史结果管理
      clearCrawlHistory,
      // 工具区域折叠
      isConfigSectionsCollapsed,
      toggleConfigSections,
      resetCustomConfigForm,
      // 从搜索组件添加饰品
      handleAddWeaponFromSearch,
      handleAddAllWeaponsFromSearch,
      getWeaponDisplayName,
      tableHeaderStyle,
      handleSidebarAreaClick
    }
  }
}
</script>

<style scoped>
.spider-weapon-rename-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%);
  padding: 2rem;
}

.page-header {
  margin-bottom: 1rem;
  padding: 1rem;
}

.page-layout {
  display: flex;
  gap: 1.5rem;
  min-height: calc(100vh - 150px);
  max-width: 100%;
}

/* 左侧配置管理栏 */
.config-sidebar {
  width: 280px;
  min-width: 280px;
  flex-shrink: 0;
  background-color: #1e1e1e;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  height: auto;
  position: sticky;
  top: 1rem;
  transition: width 0.25s ease, min-width 0.25s ease;
}

.config-sidebar.collapsed {
  width: 48px;
  min-width: 48px;
}

.sidebar-header {
  margin-bottom: 1.5rem;
}

.sidebar-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  overflow: hidden;
  max-width: 100%;
  opacity: 1;
  transition: max-width 0.25s ease, opacity 0.25s ease;
}

.sidebar-header-row.collapsed {
  max-width: 0;
  opacity: 0;
  pointer-events: none;
}

.sidebar-header-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #4CAF50;
  white-space: nowrap;
}

.sidebar-divider {
  height: 1px;
  background-color: #2f2f2f;
  border-radius: 1px;
  margin-bottom: 1rem;
}

.sidebar-header-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-shrink: 0;
}

.sidebar-header-actions .el-button {
  min-width: 64px;
}

.sidebar-header.clickable {
  cursor: pointer;
}

.sidebar-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #4CAF50;
  margin: 0;
}

.config-list {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 1rem;
  padding-right: 0.5rem;
}

.config-item {
  background-color: #252525;
  border: 1px solid #333;
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.config-item:hover {
  border-color: #4CAF50;
  background-color: #2a2a2a;
}

.config-item.active {
  border-color: #4CAF50;
  background-color: rgba(76, 175, 80, 0.1);
  box-shadow: 0 0 10px rgba(76, 175, 80, 0.3);
}

.config-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.config-name {
  font-size: 1rem;
  font-weight: 600;
  color: #fff;
  flex: 1;
  margin-right: 0.5rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.config-item-meta {
  margin-bottom: 0.25rem;
}

.config-time {
  font-size: 0.75rem;
  color: #888;
}

.config-description {
  font-size: 0.875rem;
  color: #aaa;
  margin-top: 0.5rem;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
}

.empty-config {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
}

/* 右侧主内容区域 */
.main-content-area {
  flex: 1;
  min-width: 0;
  width: auto;
  overflow-x: hidden;
}

/* 统一工具区域容器 */
.unified-tool-section {
  background-color: #1e1e1e;
  border-radius: 1rem;
  padding: 1.5rem 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
}

.unified-tool-section.collapsed {
  padding: 1rem 2rem;
}

.tool-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  padding: 1rem;
  background-color: #2a2a2a;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
  user-select: none;
  transition: all 0.3s ease;
}

.tool-section-header:hover {
  background-color: #333;
}

.tool-section-header .section-title {
  color: #fff;
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
  flex: 1;
}

.unified-tool-section.collapsed .tool-section-header {
  margin-bottom: 0;
}

.main-section-title {
  color: #fff;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
}

.collapse-btn {
  padding: 0.25rem;
  color: #4CAF50;
  transition: color 0.3s ease, transform 0.3s ease;
}

.collapse-btn:hover {
  color: #66BB6A;
  transform: scale(1.1);
}

.tool-section-content {
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.content-card {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background-color: #252525;
  border-radius: 0.75rem;
  border: 1px solid #333;
}

.search-section {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background-color: #252525;
  border-radius: 0.75rem;
  border: 1px solid #333;
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
  appearance: none;
  margin: 0;
}

.no-spinner :deep(input[type="number"]) {
  -moz-appearance: textfield;
  appearance: textfield;
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

.hash-name-text {
  color: #aaa;
  font-size: 0.875rem;
}

.no-data {
  color: #666;
  font-size: 0.875rem;
}

.weapon-row {
  cursor: pointer;
}

.weapon-row:hover {
  background-color: rgba(76, 175, 80, 0.1) !important;
}

.tool-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #fff;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #444;
}

.form-container {
  background-color: #2a2a2a;
  padding: 1.5rem;
  border-radius: 0.75rem;
  margin-bottom: 1.5rem;
}

.custom-config-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  column-gap: 20px;
  row-gap: 8px;
  width: 100%;
}

.custom-config-field {
  display: flex;
  align-items: center;
  min-height: 44px;
  min-width: 0;
}

.custom-config-field .field-label {
  width: 100px;
  font-size: 0.9rem;
  color: #ffffff;
  text-align: left;
  margin-right: 8px;
}

.custom-config-field .field-control {
  flex: 1;
  min-width: 90px;
}

.custom-config-field .field-control :deep(.el-select),
.custom-config-field .field-control :deep(.el-input) {
  width: 100%;
}

.custom-config-form-item :deep(.el-form-item__content) {
  margin-left: 0 !important;
}

.form-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 0;
}

.form-row :deep(.el-form-item__label) {
  color: #ffffff !important;
}

.form-item-half {
  flex: 1;
  margin-bottom: 18px;
}

.form-item-third {
  flex: 1;
  margin-bottom: 18px;
}

.form-item-quarter {
  flex: 1;
  margin-bottom: 18px;
}

.form-hint {
  color: #888;
  font-size: 0.75rem;
  margin-left: 0.5rem;
}

.weapon-id-tags {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.weapon-id-section {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.collapsible-label {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: 100%;
}

.collapsible-label .label-text {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  cursor: pointer;
  user-select: none;
  transition: color 0.2s ease;
}

.collapsible-label .label-text:hover {
  color: #409EFF;
}

.collapse-icon-inline {
  font-size: 0.875rem;
  transition: transform 0.3s ease;
  color: inherit;
}

.collapse-icon-inline.is-collapsed {
  transform: rotate(0deg);
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.action-buttons .el-button {
  min-width: 140px;
}

/* 结果区域 */
.result-section {
  background-color: #2a2a2a;
  padding: 1.5rem;
  border-radius: 0.75rem;
  margin-bottom: 1.5rem;
}

.weapon-result-card {
  background-color: #1e1e1e;
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.weapon-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #3a3a3a;
}

.weapon-name {
  color: #fff;
  font-size: 1.125rem;
  margin: 0;
}

.weapon-stats {
  display: flex;
  gap: 0.5rem;
}

.price {
  font-weight: 600;
  color: #ffa500;
}

/* 结果区域 */
.result-section {
  background-color: #2a2a2a;
  padding: 1.5rem;
  border-radius: 0.75rem;
  margin-bottom: 1.5rem;
  overflow-x: auto;
}

.log-section {
  background-color: #2a2a2a;
  padding: 1.5rem;
  border-radius: 0.75rem;
  margin-bottom: 1.5rem;
  border: 1px solid #333;
}

.log-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.log-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.log-count {
  color: #bbb;
  font-size: 0.9rem;
}

.log-list {
  max-height: 320px;
  overflow-y: auto;
  background-color: #1e1e1e;
  border-radius: 0.5rem;
  padding: 1rem;
  border: 1px solid #333;
}

.log-entry {
  display: flex;
  gap: 0.75rem;
  padding: 0.35rem 0;
  border-left: 3px solid transparent;
  padding-left: 0.75rem;
  font-size: 0.9rem;
  line-height: 1.4;
}

.log-entry.log-info {
  border-color: #409eff;
}

.log-entry.log-success {
  border-color: #67c23a;
}

.log-entry.log-warning {
  border-color: #e6a23c;
}

.log-entry.log-error {
  border-color: #f56c6c;
}

.log-time {
  color: #999;
  min-width: 72px;
  font-family: 'Consolas', 'Monaco', monospace;
}

.log-message {
  color: #f2f2f2;
  flex: 1;
}

.log-entry.log-success .log-message {
  color: #67c23a;
}

.log-entry.log-warning .log-message {
  color: #e6a23c;
}

.log-entry.log-error .log-message {
  color: #f56c6c;
}

.log-empty {
  display: flex;
  justify-content: center;
  padding: 1.5rem 0;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.result-header .section-title {
  margin: 0;
}

.weapon-name-cell {
  color: #409eff;
  font-weight: 500;
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.weapon-icon {
  width: 60px;
  height: 60px;
  object-fit: contain;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.05);
  padding: 4px;
  transition: all 0.3s ease;
}

.weapon-icon:hover {
  transform: scale(1.1);
  background: rgba(255, 255, 255, 0.1);
}

.no-icon {
  color: #909399;
  font-size: 0.875rem;
}

.name-tag {
  color: #67c23a;
  font-weight: 500;
  font-size: 0.95rem;
}

.result-info {
  display: grid;
  gap: 1rem;
}

.result-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #333;
}

.result-item:last-child {
  border-bottom: none;
}

.result-label {
  color: #888;
  font-weight: 500;
}

.result-value {
  color: #fff;
  font-weight: 600;
}

.result-value.success {
  color: #67C23A;
}

.result-value.error {
  color: #F56C6C;
}

.result-value.highlight {
  color: #E6A23C;
  font-size: 1.1rem;
}

/* Element Plus 组件深色主题适配 */
:deep(.el-input__wrapper) {
  background-color: #1e1e1e;
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

:deep(.el-textarea__inner) {
  background-color: #1e1e1e;
  color: #fff;
  border-color: #444;
}

:deep(.el-textarea__inner:hover) {
  border-color: #4CAF50;
}

:deep(.el-textarea__inner:focus) {
  border-color: #4CAF50;
}

:deep(.el-select .el-input__wrapper) {
  background-color: #1e1e1e;
}

:deep(.el-form-item__label) {
  color: #aaa;
}

:deep(.el-switch) {
  --el-switch-on-color: #4CAF50;
  --el-switch-off-color: #555;
}

/* JSON 编辑器样式 */
/* 响应式设计 */
/* 大屏幕优化 */
@media (min-width: 1920px) {
  .config-sidebar {
    width: 320px;
    min-width: 320px;
  }
}

/* 中等屏幕 */
@media (max-width: 1440px) {
  .config-sidebar {
    width: 260px;
    min-width: 260px;
    padding: 1rem;
  }
}

/* 小屏幕 - 切换为垂直布局 */
@media (max-width: 1024px) {
  .page-layout {
    flex-direction: column;
  }

  .config-sidebar {
    width: 100%;
    min-width: 100%;
    max-width: 100%;
    max-height: 400px;
    position: static;
    margin-bottom: 1rem;
  }
  
  .config-list {
    max-height: 250px;
  }
}

@media (max-width: 768px) {
  .spider-weapon-rename-container {
    padding: 1rem;
  }

  .page-header {
    padding: 0.5rem;
  }

  .back-button {
    width: 100%;
  }

  .config-sidebar {
    padding: 1rem;
  }

  .sidebar-actions {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .search-section {
    padding: 1rem;
  }

  .form-container {
    padding: 1rem;
  }

  .form-row {
    flex-direction: column;
    gap: 0;
  }

  .form-item-half {
    width: 100%;
  }

  .form-item-third {
    width: 100%;
  }

  .form-item-quarter {
    width: 100%;
  }

  .action-buttons {
    flex-direction: column;
  }

  .action-buttons .el-button {
    width: 100%;
  }
}

/* 滚动条样式 */
.config-list::-webkit-scrollbar {
  width: 8px;
}

.config-list::-webkit-scrollbar-track {
  background: #1a1a1a;
  border-radius: 4px;
}

.config-list::-webkit-scrollbar-thumb {
  background: #444;
  border-radius: 4px;
}

.config-list::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>

