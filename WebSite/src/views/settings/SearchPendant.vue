<template>
  <div class="spider-pendant-container">
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
                  :type="config.platformType === 'buff' ? 'warning' : (config.platformType === 'youpin' ? 'success' : 'info')" 
                  size="small"
                >
                  {{ getSourceLabel(config.platformType) }}
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
                </el-select>
              </el-form-item>

              <el-form-item label="爬取账号" required class="form-item-quarter">
                <el-select 
                  v-model="crawlForm.crawlAccountId" 
                  placeholder="选择爬取账号"
                  style="width: 100%;"
                  filterable
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

            <el-form-item>
              <div class="custom-config-grid">
                <div class="custom-config-field">
                  <div class="field-label">饰品自动查询间隔 (秒)</div>
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
                  <div class="field-label">最大差价百分比 (%)</div>
                  <div class="field-control no-spinner">
                    <el-input
                      v-model.number="customConfigForm['最大差价百分比']"
                      type="number"
                      placeholder="例如 80"
                      min="0"
                      style="width: 100px;"
                    />
                  </div>
                </div>

                <div class="custom-config-field">
                  <div class="field-label">最大溢价 (元)</div>
                  <div class="field-control no-spinner">
                    <el-input
                      v-model.number="customConfigForm['最大溢价']"
                      type="number"
                      placeholder="例如 200"
                      min="0"
                      style="width: 100px;"
                    />
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
                        :key="`auto-buy-${option.value}`"
                        :label="option.label"
                        :value="option.value"
                      />
                    </el-select>
                  </div>
                </div>

                <div class="custom-config-field">
                  <div class="field-label">是否全部返回</div>
                  <div class="field-control">
                    <el-select
                      v-model="customConfigForm['是否全部返回']"
                      placeholder="请选择"
                      style="width: 100px;"
                    >
                      <el-option
                        v-for="option in booleanOptions"
                        :key="`return-all-${option.value}`"
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
          <h2 class="section-title">查询结果 ({{ allCrawlItems.length }} 件)</h2>
          <el-button 
            type="danger" 
            size="small"
            @click="clearCrawlHistory"
            :disabled="isCrawling"
          >
            <el-icon><Delete /></el-icon>
            清空列表
          </el-button>
        </div>
        
        <!-- 统一商品列表 -->
        <el-table 
          :data="allCrawlItems" 
          style="width: 100%; min-width: max(1200px, 100%);"
          stripe
        >
          <el-table-column label="图标" width="80" fixed="left" align="center">
            <template #default="scope">
              <template v-if="getItemIconUrl(scope.row)">
                <a 
                  :href="getItemIconUrl(scope.row)" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  class="icon-link"
                >
                  <img 
                    :src="getItemIconUrl(scope.row)" 
                    class="weapon-icon"
                    :alt="scope.row.weapon_name || 'icon'"
                    referrerpolicy="no-referrer"
                  />
                </a>
              </template>
              <span v-else class="no-icon">-</span>
            </template>
          </el-table-column>
          
          <el-table-column label="武器名称" min-width="260" fixed="left">
            <template #default="scope">
              <el-tooltip 
                :content="scope.row.weapon_name" 
                placement="top"
                :disabled="!scope.row.weapon_name || scope.row.weapon_name.length <= 20"
              >
                <div class="weapon-name-cell">{{ scope.row.weapon_name }}</div>
              </el-tooltip>
            </template>
          </el-table-column>
          
          <el-table-column label="价格" width="100">
              <template #default="scope">
                <span class="price">¥{{ scope.row.price }}</span>
              </template>
            </el-table-column>
            
            <el-table-column label="溢价" width="100">
              <template #default="scope">
                <el-tag type="danger" size="small">
                  {{ scope.row.spread.toFixed(2) }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column label="手续费" width="100" align="center">
              <template #default="scope">
                <span class="commission-fee">¥{{ scope.row.commissionFee ? scope.row.commissionFee.toFixed(2) : '0.00' }}</span>
              </template>
            </el-table-column>
            
            <el-table-column label="收益" width="120" align="center">
              <template #default="scope">
                <el-tag 
                  :type="scope.row.priceDiff < 0 ? 'danger' : (scope.row.priceDiff < 3 ? 'warning' : 'success')" 
                  size="small"
                >
                  {{ scope.row.priceDiff >= 0 ? '+' : '' }}{{ scope.row.priceDiff.toFixed(2) }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column label="磨损" width="240">
              <template #default="scope">
                {{ scope.row.abrade }}
              </template>
            </el-table-column>
            
            <el-table-column label="挂件" min-width="250">
              <template #default="scope">
                <div class="pendant-list">
                  <div
                    v-for="(pendant, index) in scope.row.pendants" 
                    :key="index"
                    class="pendant-item"
                  >
                    <img v-if="pendant.img" :src="pendant.img" class="pendant-img" :alt="pendant.name" />
                    <div class="pendant-info">
                      <div class="pendant-name">{{ pendant.name }}</div>
                      <div class="pendant-details">
                        <span class="pendant-price">¥{{ pendant.price }}</span>
                        <span class="pendant-pattern">模板: {{ pendant.pattern }}</span>
                      </div>
                    </div>
                  </div>
                  <span v-if="!scope.row.pendants || scope.row.pendants.length === 0" class="no-pendant">无挂件</span>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column label="卖家" min-width="150">
              <template #default="scope">
                {{ scope.row.userNickName || '未知' }}
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="100" fixed="right">
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
import { Document, Delete, Refresh, ArrowUp, ArrowDown, InfoFilled, Loading } from '@element-plus/icons-vue'
import { API_CONFIG } from '@/config/api.js'
import WeaponSearch from '@/views/Units/weapon_search.vue'

export default {
  name: 'SpiderPendant',
  components: {
    WeaponSearch,
    Document,
    Delete,
    Refresh,
    ArrowUp,
    ArrowDown,
    InfoFilled,
    Loading
  },
  setup() {
    const router = useRouter()
    const crawlFormRef = ref(null)
    const platformAccountLists = ref({})
    const accountLoadingStates = ref({})
    const isProgrammaticPlatformChange = ref(false)
    const isCrawling = ref(false)
    const crawlResult = ref(null)
    
    const pollingTimer = ref(null)
    const POLL_INTERVAL = 1000
    const noDataCount = ref(0)
    const MAX_NO_DATA_COUNT = 60
    const lastPollingTime = ref(0)
    
    const getItemIconUrl = (item) => {
      if (!item) return ''
      const raw = item.iconUrl ?? item.icon_url
      if (!raw) return ''
      const url = typeof raw === 'string' ? raw.trim() : ''
      if (!url) return ''
      if (url.startsWith('http://') || url.startsWith('https://')) {
        return url
      }
      if (url.startsWith('//')) {
        return `https:${url}`
      }
      return url
    }

    const parsePendants = (rawPendants) => {
      if (!rawPendants) {
        return []
      }
      if (Array.isArray(rawPendants)) {
        return rawPendants
      }
      if (typeof rawPendants === 'string') {
        try {
          const parsed = JSON.parse(rawPendants)
          return Array.isArray(parsed) ? parsed : []
        } catch (error) {
          console.warn('[挂件] 无法解析 pendants 字段:', rawPendants, error)
          return []
        }
      }
      return []
    }

    const normalizeApiItems = (items = []) => {
      return items.map(item => ({
        id: item.commodityId,
        commodityNo: item.commodityNo,
        price: parseFloat(item.price) || 0,
        lowest_price: parseFloat(item.lowestPrice) || 0,
        spread: parseFloat(item.spread) || 0,
        abrade: item.abrade,
        paintSeed: item.paintSeed,
        nameTag: item.nameTag,
        userNickName: item.sellerName,
        assetId: item.assetId,
        iconUrl: item.iconUrl || item.icon_url,
        weapon_name: item.weaponName,
        weaponName: item.weaponName,
        weaponId: item.weaponId,
        commissionFee: parseFloat(item.commissionFee) || 0,
        priceDiff: parseFloat(item.priceDiff) || 0,
        pendants: parsePendants(item.pendants),
        pendantTotalPrice: parseFloat(item.pendantTotalPrice) || 0,
        priceDiffPercentage: parseFloat(item.priceDiffPercentage) || 0
      }))
    }

    const rebuildCrawlResult = (items = []) => {
      const weaponGroups = {}
      items.forEach(item => {
        const weaponDisplayName = item.weapon_name || item.weaponName || '未知饰品'
        if (!weaponGroups[weaponDisplayName]) {
          weaponGroups[weaponDisplayName] = []
        }
        weaponGroups[weaponDisplayName].push(item)
      })

      const weapons = Object.keys(weaponGroups).map(name => ({
        weapon_name: name,
        items: weaponGroups[name]
      }))

      crawlResult.value = { weapons }
    }

    const loadRecentSearchResults = async () => {
      try {
        console.log('[挂件] 尝试加载历史结果...')
        const params = new URLSearchParams({
          dataType: 'pendant'
        })
        const response = await fetch(`${API_CONFIG.BASE_URL}/searchRename/items/list?${params.toString()}`)
        if (!response.ok) {
          console.warn('[挂件] 历史数据请求失败')
          return
        }
        const result = await response.json()
        if (result.success && Array.isArray(result.items) && result.items.length > 0) {
          const mappedItems = normalizeApiItems(result.items)
          rebuildCrawlResult(mappedItems)
          console.log(`[挂件] 已加载 ${mappedItems.length} 条历史结果`)
        } else {
          console.log('[挂件] 没有找到历史结果')
        }
      } catch (error) {
        console.error('[挂件] 加载历史数据失败:', error)
      }
    }

    const updateCrawlResultWithItems = (newItems) => {
      const currentItems = crawlResult.value?.weapons?.flatMap(weapon => weapon.items) || []
      const itemMap = new Map()
      currentItems.forEach(item => itemMap.set(item.id, item))
      newItems.forEach(item => itemMap.set(item.id, item))
      const mergedItems = Array.from(itemMap.values())
      mergedItems.sort((a, b) => {
        const diffA = a.priceDiff !== undefined ? a.priceDiff : -Infinity
        const diffB = b.priceDiff !== undefined ? b.priceDiff : -Infinity
        return diffB - diffA
      })
      rebuildCrawlResult(mergedItems)
    }

    const pollSearchResults = async () => {
      try {
        lastPollingTime.value = Date.now()
        const params = new URLSearchParams({
          dataType: 'pendant'
        })
        const response = await fetch(`${API_CONFIG.BASE_URL}/searchRename/items/list?${params.toString()}`)
        if (!response.ok) {
          console.error('[挂件] 轮询失败: HTTP', response.status)
          return
        }
        const result = await response.json()
        if (result.success && Array.isArray(result.items) && result.items.length > 0) {
          const mappedItems = normalizeApiItems(result.items)
          updateCrawlResultWithItems(mappedItems)
          if (isCrawling.value) {
            noDataCount.value = 0
          }
        } else if (isCrawling.value) {
          noDataCount.value++
          if (noDataCount.value >= MAX_NO_DATA_COUNT) {
            console.log('[挂件] 连续无新数据，结束搜索状态')
            isCrawling.value = false
            const totalItems = crawlResult.value?.weapons?.flatMap(w => w.items).length || 0
            ElMessage.success(`搜索完成！找到 ${totalItems} 个符合条件的商品`)
          }
        }
      } catch (error) {
        console.error('[挂件] 轮询出错:', error)
      }
    }

    const startPolling = () => {
      if (pollingTimer.value) {
        return
      }
      console.log(`[挂件] 启动轮询，间隔 ${POLL_INTERVAL}ms`)
      pollingTimer.value = setInterval(pollSearchResults, POLL_INTERVAL)
      pollSearchResults()
    }

    const stopPolling = () => {
      if (pollingTimer.value) {
        clearInterval(pollingTimer.value)
        pollingTimer.value = null
        console.log('[挂件] 已停止轮询')
      }
    }

    const clearCrawlHistory = async (skipConfirm = false) => {
      try {
        // 如果有选中的配置，只清空该配置的数据；否则清空所有数据
        const clearMessage = selectedConfigId.value
          ? '确定要清空当前配置的挂件搜索结果吗？此操作将删除该配置的所有挂件数据，不可恢复。'
          : '确定要清空所有挂件搜索结果吗？此操作不可恢复。'
        
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
          dataType: 'pendant'
        }
        
        // 如果有选中的配置，只清空该配置的数据
        if (selectedConfigId.value) {
          requestBody.configId = selectedConfigId.value
        }

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
          crawlResult.value = null
          purchasedItems.value.clear()
          if (!skipConfirm) {
            ElMessage.success(result.message || '已清空挂件数据')
          }
        } else {
          throw new Error(result.message || '清空失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('清空挂件数据失败:', error)
          if (!skipConfirm) {
            ElMessage.error(error.message || '清空失败')
          }
        }
      }
    }

    // 合并所有武器的items到一个统一列表，并按差价从高到低排序
    const allCrawlItems = computed(() => {
      if (!crawlResult.value || !crawlResult.value.weapons) {
        return []
      }
      
      const items = []
      crawlResult.value.weapons.forEach(weapon => {
        if (weapon.items && weapon.items.length > 0) {
          weapon.items.forEach(item => {
            items.push({
              ...item,
              weapon_name: weapon.weapon_name,  // 添加武器名称
              weapon_id: weapon.weapon_id
            })
          })
        }
      })
      
      // 按差价从高到低排序
      items.sort((a, b) => {
        const diffA = a.priceDiff !== undefined ? a.priceDiff : -Infinity
        const diffB = b.priceDiff !== undefined ? b.priceDiff : -Infinity
        return diffB - diffA  // 从高到低
      })
      
      return items
    })
    
    // 配置管理相关
    const savedConfigs = ref([])
    const selectedConfigId = ref(null)

    // 饰品搜索相关
    const weaponSearchKeyword = ref('')
    const weaponSearchResults = ref([])
    const isSearchingWeapon = ref(false)
    const isLoadingMore = ref(false)  // 加载更多数据中
    const currentPage = ref(1)  // 当前页码
    const pageSize = ref(50)  // 每页数量
    const hasMore = ref(true)  // 是否还有更多数据
    const weaponSearchFilters = ref({
      weaponType: '',  // 武器类型筛选
      weaponName: '',  // 武器名称筛选
      rarity: '',      // 稀有度筛选
      priceMin: null,  // 最低价格
      priceMax: null,  // 最高价格
      minOnSaleCount: null  // 最小在售数量
    })
    const weaponNameList = ref([])  // 武器名称列表
    const isLoadingWeaponNames = ref(false)  // 加载武器名称中
    
    // 购买相关
    const buyingItems = ref({})  // 正在购买的商品 {itemId: true/false}
    const purchasedItems = ref(new Set())  // 已成功购买的商品ID集合
    
    // 工具与配置区域联动折叠状态
    const isConfigSectionsCollapsed = ref(false)
    const isSearchResultsCollapsed = ref(false)  // 搜索结果列表折叠状态
    const isWeaponListCollapsed = ref(true)  // 饰品列表折叠状态（默认折叠）
    
    const createDefaultCustomConfig = () => ({
      '饰品自动查询间隔': 3,
      '是否自动购买': false,
      '最大差价百分比': 80,
      '最大溢价': 200,
      '是否全部返回': false
    })

    const booleanOptions = [
      { label: '是', value: true },
      { label: '否', value: false }
    ]

    const customConfigForm = ref(createDefaultCustomConfig())
    const isProgrammaticCustomConfigChange = ref(false)

    const crawlForm = ref({
      configName: '',      // 对应 dataName
      steamId: '',         // 购买账号
      crawlAccountId: '',  // 爬取账号
      platformType: '',    // 平台类型：youpin 或 buff
      weaponId: []         // 改为数组，存储 {id, name} 对象
    })

    // 计算属性：获取饰品列表
    const weaponIdList = computed(() => {
      return crawlForm.value.weaponId || []
    })

    // 计算是否可以开始爬取
    const canStartCrawl = computed(() => {
      if (!crawlForm.value.configName) return false
      if (!crawlForm.value.platformType) return false
      if (!crawlForm.value.crawlAccountId) return false
      if (!crawlForm.value.steamId) return false
      if (!crawlForm.value.weaponId || crawlForm.value.weaponId.length === 0) return false
      return true
    })

    const normalizePlatformKey = (value) => {
      if (!value && value !== 0) return ''
      const normalized = value.toString().trim().toLowerCase()
      if (['youpin', 'yyyp', 'you_pin', 'you-pin', '悠悠有品'].some(k => normalized === k.toLowerCase())) {
        return 'youpin'
      }
      if (['buff', 'buff平台'].some(k => normalized === k.toLowerCase())) {
        return 'buff'
      }
      return normalized
    }

    const PLATFORM_ACCOUNT_SOURCE_MAP = {
      youpin: { key1: 'youpin', key2: 'config', label: '悠悠有品' },
      buff: { key1: 'buff', key2: 'config', label: 'BUFF' }
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
      '是否自动购买': normalizeBooleanValue(
        customConfigForm.value['是否自动购买'],
        false
      ),
      '最大差价百分比': normalizeNumberValue(
        customConfigForm.value['最大差价百分比'],
        80
      ),
      '最大溢价': normalizeNumberValue(
        customConfigForm.value['最大溢价'],
        200
      ),
      '是否全部返回': normalizeBooleanValue(
        customConfigForm.value['是否全部返回'],
        false
      ),
      '是否授权': true
    })

    const validateCustomConfig = () => {
      const config = buildCustomConfig()

      if (config['饰品自动查询间隔'] <= 0) {
        return { valid: false, message: '饰品自动查询间隔必须大于 0 秒' }
      }
      if (config['最大差价百分比'] < 0) {
        return { valid: false, message: '最大差价百分比不能为负数' }
      }
      if (config['最大溢价'] < 0) {
        return { valid: false, message: '最大溢价不能为负数' }
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
        '是否自动购买': normalizeBooleanValue(
          config['是否自动购买'],
          defaults['是否自动购买']
        ),
        '最大差价百分比': normalizeNumberValue(
          config['最大差价百分比'],
          defaults['最大差价百分比']
        ),
        '最大溢价': normalizeNumberValue(
          config['最大溢价'],
          defaults['最大溢价']
        ),
        '是否全部返回': normalizeBooleanValue(
          config['是否全部返回'],
          defaults['是否全部返回']
        )
      }
      nextTick(() => {
        isProgrammaticCustomConfigChange.value = false
      })
    }

    // 联动切换配置管理与爬取配置
    const toggleConfigSections = () => {
      isConfigSectionsCollapsed.value = !isConfigSectionsCollapsed.value
    }

    // 切换搜索结果列表显示/隐藏
    const toggleSearchResults = () => {
      isSearchResultsCollapsed.value = !isSearchResultsCollapsed.value
    }
    
    // 切换饰品列表显示/隐藏
    const toggleWeaponList = () => {
      isWeaponListCollapsed.value = !isWeaponListCollapsed.value
    }

    const handleSidebarAreaClick = (event) => {
      const target = event.target
      if (!target) return

      if (target.closest && target.closest('.config-item')) {
        return
      }

      toggleConfigSections()
    }

    // 开始爬取（流式接收）
    const startCrawl = async () => {
      // 开始搜索时自动折叠工具与配置区域
      isConfigSectionsCollapsed.value = true
      // 清空已购买记录
      purchasedItems.value.clear()
      // 验证基本配置
      if (!crawlForm.value.configName) {
        ElMessage.warning('请输入配置名称')
        return
      }

      if (!crawlForm.value.platformType) {
        ElMessage.warning('请选择平台类型')
        return
      }
      
      if (!crawlForm.value.crawlAccountId) {
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

      // 验证自定义配置
      const customConfigResult = validateCustomConfig()
      if (!customConfigResult.valid) {
        ElMessage.error(customConfigResult.message)
        return
      }
      const customConfig = customConfigResult.config

      // 确认对话框
      try {
        let confirmMessage = `确定要开始查询带挂件饰品吗？\n\n`
        confirmMessage += `配置名称: ${crawlForm.value.configName}\n`
        confirmMessage += `爬取账号: ${crawlForm.value.crawlAccountId}\n`
        confirmMessage += `购买账号: ${crawlForm.value.steamId}\n`
        confirmMessage += `平台类型: ${getSourceLabel(crawlForm.value.platformType)}\n`
        confirmMessage += `监控饰品数量: ${crawlForm.value.weaponId.length} 个`
        
        confirmMessage += `\n查询间隔: ${customConfig['饰品自动查询间隔']} 秒`
        confirmMessage += `\n是否自动购买: ${customConfig['是否自动购买'] ? '是' : '否'}`
        confirmMessage += `\n最大差价百分比: ${customConfig['最大差价百分比']}%`
        confirmMessage += `\n最大溢价: ${customConfig['最大溢价']} 元`
        confirmMessage += `\n是否全部返回: ${customConfig['是否全部返回'] ? '是' : '否'}`

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

      await clearCrawlHistory(true)
      isCrawling.value = true
      crawlResult.value = { weapons: [] }
      noDataCount.value = 0
      ElMessage.info('正在启动查询任务...')
      startPolling()
      pollSearchResults()

      try {
        const spiderConfig = {
          weapon_id: crawlForm.value.weaponId,
          steam_id: crawlForm.value.crawlAccountId,
          最大差价: 5,
          饰品自动查询间隔: 3,
          ...customConfig
        }

        const requestData = {
          steamId: crawlForm.value.crawlAccountId,
          spider_config: spiderConfig
        }

        fetch(
          `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/auto_buy_pendant_weapon`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
          }
        ).then(async response => {
          let result = null
          try {
            result = await response.json()
          } catch (parseError) {
            console.warn('[挂件] 响应解析失败:', parseError)
          }

          if (!response.ok || !result?.success) {
            const errMsg = result?.message || `HTTP ${response.status}`
            throw new Error(errMsg)
          }

          console.log('[挂件] 搜索任务响应:', result)
        }).catch(error => {
          console.error('[挂件] 搜索任务启动失败:', error)
          ElMessage.error(`启动搜索失败: ${error.message}`)
          isCrawling.value = false
        })

        setTimeout(() => {
          if (isCrawling.value) {
            console.log('[挂件] 搜索超时，结束搜索状态')
            isCrawling.value = false
            const totalItems = crawlResult.value?.weapons?.flatMap(w => w.items).length || 0
            ElMessage.warning(`搜索已超时结束，找到 ${totalItems} 个商品`)
          }
        }, 5 * 60 * 1000)

      } catch (error) {
        console.error('搜索失败:', error)
        ElMessage.error(error.message || '搜索失败')
        isCrawling.value = false
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

    const getSourceLabel = (source) => {
      const labels = {
        youpin: '悠悠有品',
        buff: 'BUFF',
        steam: 'Steam库存'
      }
      if (!source) {
        return '未设置'
      }
      return labels[source] || source
    }

    // 加载配置列表
    const loadConfigList = async () => {
      try {
        // 只加载 key1 = 'spider_pendant' 的配置
        const response = await axios.get(`${API_CONFIG.BASE_URL}/configV1/list`, {
          params: {
            key1: 'spider_pendant'
          }
        })
        
        console.log('配置列表响应:', response.data)
        
        // 保存平台类型
        savedConfigs.value = (response.data.data || []).map(config => ({
          ...config,
          platformType: config.key2 || ''
        }))
        
        // 按ID降序排序
        savedConfigs.value.sort((a, b) => b.id - a.id)
        
        console.log('加载的配置列表:', savedConfigs.value)
      } catch (error) {
        console.error('加载配置列表失败:', error)
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

      try {
        const config = savedConfigs.value.find(c => c.id === configId)
        console.log('找到的配置对象:', config)
        
        if (config && config.value) {
          const platformType = config.platformType || ''
          if (platformType) {
            await loadAccountsForPlatform(platformType)
          }
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
            platformType: platformType,
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
          console.log('=== 配置加载完成 ===')
          
          ElMessage.success(`已加载配置: ${config.dataName}`)
        } else {
          console.warn('配置缺少value字段:', config)
          ElMessage.warning('配置数据为空')
        }
      } catch (error) {
        console.error('加载配置失败:', error)
        console.error('错误堆栈:', error.stack)
        ElMessage.error(`加载配置失败: ${error.message}`)
      }
    }

    // 创建新配置（清空表单）
    const createNewConfig = () => {
      selectedConfigId.value = null
      resetForm()
      ElMessage.info('已清空表单，可以创建新配置')
    }

    // 平台类型改变处理
    const handlePlatformTypeChange = async () => {
      if (isProgrammaticPlatformChange.value) {
        isProgrammaticPlatformChange.value = false
      } else {
        crawlForm.value.crawlAccountId = ''
        crawlForm.value.steamId = ''
      }
      
      if (crawlForm.value.platformType) {
        await loadAccountsForPlatform(crawlForm.value.platformType)
      }
      
      if (selectedConfigId.value) {
        autoSaveConfig()
      }
    }

    // 自动保存配置
    const autoSaveConfig = async () => {
      if (!selectedConfigId.value) {
        return
      }

      if (!crawlForm.value.configName || !crawlForm.value.platformType) {
        return
      }

      try {
        const customConfigResult = validateCustomConfig()
        if (!customConfigResult.valid) {
          console.log('自定义配置错误，跳过自动保存:', customConfigResult.message)
          return
        }

        const valueObj = {
          weapon_id: crawlForm.value.weaponId,
          steam_id: crawlForm.value.steamId,
          crawl_account_id: crawlForm.value.crawlAccountId,
          ...customConfigResult.config
        }

        const key2 = crawlForm.value.platformType

        const configData = {
          id: selectedConfigId.value,
          dataName: crawlForm.value.configName,
          key1: 'spider_pendant',
          key2: key2,
          value: JSON.stringify(valueObj)
        }

        const response = await axios.post(`${API_CONFIG.BASE_URL}/webConfigV1/updateConfig`, configData)
        
        if (response.data.success) {
          console.log('配置已自动保存')
        }
      } catch (error) {
        console.error('自动保存失败:', error)
      }
    }

    watch(
      customConfigForm,
      () => {
        if (isProgrammaticCustomConfigChange.value) {
          return
        }
        if (selectedConfigId.value) {
          autoSaveConfig()
        }
      },
      { deep: true }
    )

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
          key1: 'spider_pendant',
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
          } else if (!isUpdating) {
            const newId = response.data.data?.id
            if (newId) {
              selectedConfigId.value = newId
              await selectConfig(newId)
            }
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

    // 武器类型改变时，加载对应的武器名称列表
    const handleWeaponTypeChange = async (weaponType) => {
      // 清空武器名称选择
      weaponSearchFilters.value.weaponName = ''
      weaponNameList.value = []
      
      // 无论是否选择武器类型，都加载武器名称列表
      await loadWeaponNames(weaponType)
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
        if (weaponSearchKeyword.value.trim()) {
          params.keyword = weaponSearchKeyword.value.trim()
        }
        
        // 如果选择了武器类型，添加到查询参数
        if (weaponSearchFilters.value.weaponType) {
          params.weaponType = weaponSearchFilters.value.weaponType
        }
        
        // 如果选择了武器名称，添加到查询参数
        if (weaponSearchFilters.value.weaponName) {
          params.weaponName = weaponSearchFilters.value.weaponName
        }
        
        // 如果选择了稀有度，添加到查询参数
        if (weaponSearchFilters.value.rarity) {
          params.rarity = weaponSearchFilters.value.rarity
        }
        
        // 如果设置了最低价格，添加到查询参数
        if (weaponSearchFilters.value.priceMin !== null && weaponSearchFilters.value.priceMin !== '') {
          params.priceMin = weaponSearchFilters.value.priceMin
        }
        
        // 如果设置了最高价格，添加到查询参数
        if (weaponSearchFilters.value.priceMax !== null && weaponSearchFilters.value.priceMax !== '') {
          params.priceMax = weaponSearchFilters.value.priceMax
        }
        
        // 如果设置了最小在售数量，添加到查询参数
        if (weaponSearchFilters.value.minOnSaleCount !== null && weaponSearchFilters.value.minOnSaleCount !== '') {
          params.minOnSaleCount = weaponSearchFilters.value.minOnSaleCount
        }
        
        const response = await axios.get(`${API_CONFIG.BASE_URL}/webSelectWeaponV1/searchWeaponDetail`, {
          params: params
        })
        
        if (response.data.success) {
          const newData = response.data.data || []
          const total = response.data.total || 0
          
          console.log('📦 加载数据响应', {
            page: currentPage.value,
            newDataLength: newData.length,
            total,
            pageSize: pageSize.value
          })
          
          if (currentPage.value === 1) {
            weaponSearchResults.value = newData
            if (newData.length === 0) {
              ElMessage.info('未找到匹配的饰品')
              hasMore.value = false
            } else {
              ElMessage.success(`找到 ${total} 件饰品，已加载 ${newData.length} 件`)
            }
          } else {
            weaponSearchResults.value.push(...newData)
            console.log(`📥 追加 ${newData.length} 条数据，总计 ${weaponSearchResults.value.length} 条`)
          }
          
          // 判断是否还有更多数据
          const hasMoreData = newData.length >= pageSize.value
          hasMore.value = hasMoreData
          
          console.log('📊 加载状态', {
            hasMore: hasMore.value,
            currentTotal: weaponSearchResults.value.length,
            newDataLength: newData.length,
            pageSize: pageSize.value
          })
          
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

    // 加载更多数据
    const loadMoreWeapons = async () => {
      if (isLoadingMore.value || !hasMore.value) {
        return
      }
      
      // 记录加载前的滚动位置和页面高度
      const oldScrollHeight = document.documentElement.scrollHeight
      const oldScrollTop = window.pageYOffset || document.documentElement.scrollTop
      
      console.log('🔄 开始加载更多', {
        currentPage: currentPage.value,
        oldScrollHeight,
        oldScrollTop
      })
      
      currentPage.value++
      await loadWeaponData()
      
      // 等待 DOM 更新后调整滚动位置
      await nextTick()
      
      // 加载完成后，将滚动位置向上调整，避免立即触发下一次加载
      const newScrollHeight = document.documentElement.scrollHeight
      const addedHeight = newScrollHeight - oldScrollHeight
      
      if (addedHeight > 0 && hasMore.value) {
        // 将滚动位置设置到距离底部 300px 的位置
        const clientHeight = window.innerHeight
        const targetScrollTop = newScrollHeight - clientHeight - 300
        
        // 确保新的滚动位置不会小于原来的位置
        if (targetScrollTop > oldScrollTop) {
          window.scrollTo({
            top: targetScrollTop,
            behavior: 'auto'  // 使用 auto 立即跳转，不使用平滑滚动
          })
          
          console.log('📍 调整滚动位置', {
            oldScrollHeight,
            newScrollHeight,
            addedHeight,
            oldScrollTop,
            targetScrollTop,
            distanceToBottom: newScrollHeight - targetScrollTop - clientHeight
          })
        }
      }
    }

    // 页面滚动事件处理
    let scrollTimer = null
    const handlePageScroll = () => {
      // 如果没有搜索结果，不处理滚动
      if (weaponSearchResults.value.length === 0) {
        console.log('❌ 跳过滚动检查：没有搜索结果')
        return
      }
      
      // 只有在爬取配置区域是展开状态时，才触发自动加载
      if (isConfigSectionsCollapsed.value) {
        console.log('❌ 跳过滚动检查：配置区域已收起')
        return
      }
      
      // 防抖处理，避免频繁触发
      if (scrollTimer) {
        clearTimeout(scrollTimer)
      }
      
      scrollTimer = setTimeout(() => {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop
        const scrollHeight = document.documentElement.scrollHeight
        const clientHeight = window.innerHeight
        const distanceToBottom = scrollHeight - scrollTop - clientHeight
        
        console.log('📏 滚动位置检查', {
          scrollTop: Math.round(scrollTop),
          scrollHeight,
          clientHeight,
          distanceToBottom: Math.round(distanceToBottom),
          hasMore: hasMore.value,
          isLoadingMore: isLoadingMore.value,
          isConfigSectionsCollapsed: isConfigSectionsCollapsed.value,
          currentPage: currentPage.value,
          resultsCount: weaponSearchResults.value.length
        })
        
        // 滚动到底部触发加载更多（距离底部200px时触发）
        if (distanceToBottom < 200 && hasMore.value && !isLoadingMore.value) {
          console.log('✅ 触发加载更多数据')
          loadMoreWeapons()
        } else {
          console.log('⏸️ 未触发加载', {
            '距离是否<200': distanceToBottom < 200,
            '有更多数据': hasMore.value,
            '未在加载中': !isLoadingMore.value
          })
        }
      }, 100) // 100ms 防抖延迟
    }

    // 清除搜索结果
    const clearWeaponSearch = () => {
      weaponSearchResults.value = []
      weaponSearchKeyword.value = ''
      weaponSearchFilters.value.weaponType = ''
      weaponSearchFilters.value.weaponName = ''
      weaponSearchFilters.value.rarity = ''
      weaponSearchFilters.value.priceMin = null
      weaponSearchFilters.value.priceMax = null
      weaponNameList.value = []
      currentPage.value = 1
      hasMore.value = true
    }

    // 根据平台类型获取对应的饰品ID
    const getWeaponIdByPlatform = (row) => {
      if (crawlForm.value.platformType === 'buff') {
        return row.buff_id || row.yyyp_id || row.id || ''
      }
      if (crawlForm.value.platformType === 'youpin') {
        return row.yyyp_id || row.buff_id || row.id || ''
      }
      return row.yyyp_id || row.buff_id || row.id || ''
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

    // 一键添加全部饰品ID
    const addAllWeaponIds = async () => {
      if (!crawlForm.value.platformType) {
        ElMessage.warning('请先选择平台类型')
        return
      }

      if (!weaponSearchResults.value || weaponSearchResults.value.length === 0) {
        ElMessage.warning('没有可添加的饰品')
        return
      }

      try {
        const platformName = getSourceLabel(crawlForm.value.platformType) || '当前平台'
        
        await ElMessageBox.confirm(
          `确定要添加全部 ${weaponSearchResults.value.length} 个饰品吗？`,
          '确认添加',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'info'
          }
        )

        let addedCount = 0
        let skippedCount = 0
        let noIdCount = 0

        weaponSearchResults.value.forEach(row => {
          const weaponId = getWeaponIdByPlatform(row)
          
          // 没有ID的跳过
          if (!weaponId) {
            noIdCount++
            return
          }

          // 已存在的跳过
          if (crawlForm.value.weaponId.some(w => w.id === weaponId.toString())) {
            skippedCount++
            return
          }
          
          // 添加饰品对象
          crawlForm.value.weaponId.push({
            id: weaponId.toString(),
            name: row.market_listing_item_name || row.name || '未知饰品'
          })
          
          addedCount++
        })

        let message = `添加完成！成功添加 ${addedCount} 个饰品`
        if (skippedCount > 0) {
          message += `，跳过 ${skippedCount} 个已存在的饰品`
        }
        if (noIdCount > 0) {
          message += `，${noIdCount} 个饰品没有${platformName}ID`
        }
        
        ElMessage.success(message)
      } catch {
        // 用户取消操作
      }
    }

    // 删除饰品ID
    const removeWeaponId = (idToRemove) => {
      crawlForm.value.weaponId = crawlForm.value.weaponId.filter(w => w.id !== idToRemove)
      ElMessage.success('已删除饰品')
    }

    // 一键清空饰品列表
    const clearAllWeaponIds = async () => {
      try {
        await ElMessageBox.confirm(
          `确定要清空所有饰品吗？此操作将清除 ${weaponIdList.value.length} 个饰品。`,
          '确认清空',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        crawlForm.value.weaponId = []
        ElMessage.success('已清空所有饰品')
      } catch {
        // 用户取消操作
      }
    }

    // 购买饰品
    const handleBuyWeapon = async (item) => {
      console.log('购买商品:', item)
      
      // 确认购买
      try {
        const pendantNames = item.pendants ? item.pendants.map(p => p.name).join(', ') : '无'
        const priceDiffText = item.priceDiff >= 0 ? `+${item.priceDiff.toFixed(2)}` : `${item.priceDiff.toFixed(2)}`
        await ElMessageBox.confirm(
          `确认购买该商品吗？\n\n挂件：${pendantNames}\n价格：¥${item.price}\n磨损：${item.abrade || '-'}\n溢价：${item.spread.toFixed(2)}\n收益：${priceDiffText}`,
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
      
      // 设置购买中状态
      buyingItems.value[item.id] = true
      
      // 开始购买流程
      const loadingMessage = ElMessage({
        message: '正在创建订单...',
        type: 'info',
        duration: 0
      })
      
      try {
        const requestData = {
          steamId: crawlForm.value.steamId,  // ✅ 使用购买账号
          commodityId: item.id,
          buyQuantity: 1,
          price: item.price,
          autoConfirmPayment: true,  // 自动使用余额支付
          pollPayment: true  // 轮询支付状态
        }
        
        console.log('购买请求数据 (使用购买账号):', requestData)
        console.log('  - 购买账号:', crawlForm.value.steamId)
        console.log('  - 爬取账号:', crawlForm.value.crawlAccountId)
        
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
            message = `购买成功！\n\n商品：挂件饰品\n订单号：${orderNo}\n金额：¥${paymentAmount}\n状态：支付成功✅\n\n饰品将发送至您的库存。`
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
      } finally {
        // 移除购买中状态
        buyingItems.value[item.id] = false
      }
    }

    // 表格行样式
    const getRowClassName = () => {
      return 'weapon-row'
    }

    // 判断挂件是否包含"高光时刻"
    const hasHighlightMoment = (item) => {
      if (!item.pendants || item.pendants.length === 0) {
        return false
      }
      // 检查任意一个挂件名称是否包含"高光时刻"
      return item.pendants.some(pendant => 
        pendant.name && pendant.name.includes('高光时刻')
      )
    }
    
    // 获取购买按钮类型
    const getBuyButtonType = (item) => {
      if (purchasedItems.value.has(item.id)) {
        return 'success'  // 已购买：绿色
      }
      if (hasHighlightMoment(item)) {
        return 'warning'  // 包含高光时刻：黄色
      }
      if (item.priceDiff < 0) {
        return 'danger'   // 亏损：红色
      }
      if (item.priceDiff < 3) {
        return 'warning'  // 低收益：黄色
      }
      return 'success'    // 高收益：绿色
    }
    
    // 获取稀有度颜色样式（与ItemSearch保持一致）
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

    // 组件挂载时加载数据并启动轮询
    onMounted(() => {
      if (crawlForm.value.platformType) {
        loadAccountsForPlatform(crawlForm.value.platformType)
      }
      loadConfigList()
      loadRecentSearchResults()
      startPolling()
      // 添加页面滚动监听
      window.addEventListener('scroll', handlePageScroll)
    })

    onUnmounted(() => {
      // 移除页面滚动监听
      window.removeEventListener('scroll', handlePageScroll)
      stopPolling()
    })

    return {
      crawlFormRef,
      filteredSteamIdList,
      isCrawling,
      crawlForm,
      customConfigForm,
      booleanOptions,
      crawlResult,
      allCrawlItems,
      canStartCrawl,
      startCrawl,
      resetForm,
      // 配置管理
      savedConfigs,
      selectedConfigId,
      loadConfigList,
      selectConfig,
      createNewConfig,
      saveConfig,
      autoSaveConfig,
      handlePlatformTypeChange,
      deleteConfig,
      deleteCurrentConfig,
      formatTime,
      // 饰品搜索
      weaponSearchKeyword,
      weaponSearchResults,
      isSearchingWeapon,
      isLoadingMore,
      hasMore,
      weaponSearchFilters,
      weaponNameList,
      isLoadingWeaponNames,
      handleWeaponTypeChange,
      loadWeaponNames,
      loadWeaponNamesIfNeeded,
      handleSearchWeapon,
      loadMoreWeapons,
      clearWeaponSearch,
      handleAddWeaponFromSearch,
      handleAddAllWeaponsFromSearch,
      getWeaponIdByPlatform,
      getSourceLabel,
      addWeaponId,
      addAllWeaponIds,
      removeWeaponId,
      clearAllWeaponIds,
      weaponIdList,
      getRowClassName,
      getRarityColor,
      // 购买相关
      buyingItems,
      purchasedItems,
      handleBuyWeapon,
      hasHighlightMoment,
      getBuyButtonType,
      getItemIconUrl,
      // 历史结果管理
      clearCrawlHistory,
      // 工具区域折叠
      isConfigSectionsCollapsed,
      toggleConfigSections,
      isSearchResultsCollapsed,
      toggleSearchResults,
      isWeaponListCollapsed,
      toggleWeaponList,
      handleSidebarAreaClick,
      // 自定义配置
      resetCustomConfigForm
    }
  }
}
</script>

<style scoped>
.spider-pendant-container {
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

.collapse-btn {
  padding: 0.25rem;
  color: #4CAF50;
  transition: transform 0.3s ease;
}

.collapse-btn:hover {
  color: #66BB6A;
  transform: scale(1.1);
}

.main-section-title {
  color: #fff;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
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

.search-results-table {
  margin-top: 1rem;
  border: 1px solid #333;
  border-top: none;
  border-radius: 0 0 0.5rem 0.5rem;
  overflow: hidden;
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
  user-select: none;
  transition: all 0.3s ease;
}

.results-header:hover {
  background-color: #333;
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

/* 可折叠标签样式 */
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

.collapsible-label .collapse-icon-inline {
  font-size: 0.875rem;
  transition: transform 0.3s ease;
  color: inherit;
}

.collapsible-label .collapse-icon-inline.is-collapsed {
  transform: rotate(0deg);
}

.weapon-name {
  color: #fff;
  font-weight: 500;
}

.weapon-name-cell {
  color: #409eff;
  font-weight: 500;
  font-size: 0.9rem;
  white-space: normal;
  word-break: break-word;
  overflow: visible;
  line-height: 1.4;
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
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

.no-icon {
  color: #666;
  font-size: 0.875rem;
}

.hash-name-text {
  color: #aaa;
  font-size: 0.875rem;
}

.no-data {
  color: #666;
  font-size: 0.875rem;
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

.rarity-text {
  font-weight: 600;
  font-size: 0.9rem;
  text-shadow: 0 0 2px rgba(0, 0, 0, 0.3);
}

.platform-tip {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  margin-top: 0.5rem;
  color: #E6A23C;
  font-size: 0.75rem;
}

.load-more-container {
  text-align: center;
  padding: 1rem;
  color: #909399;
  font-size: 0.875rem;
}

.loading-more {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: #409EFF;
}

.no-more-data {
  color: #909399;
}

.can-load-more {
  color: #606266;
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

.form-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 0;
}

/* 垂直堆叠的表单行 */
.form-row-stacked {
  flex-direction: column;
  gap: 0;
}

.form-item-full {
  width: 100%;
  margin-bottom: 18px;
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

.weapon-id-section {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  width: 100%;
}

.weapon-id-tags {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  flex: 1;
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
  overflow-x: auto;
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

.commission-fee {
  font-size: 0.875rem;
  color: #909399;
  font-weight: 500;
}

/* 挂件样式 */
.pendant-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.pendant-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  transition: all 0.2s;
}

.pendant-item:hover {
  background: rgba(255, 255, 255, 0.08);
}

.pendant-img {
  width: 60px;
  height: 60px;
  max-width: 60px;
  max-height: 60px;
  min-width: 60px;
  min-height: 60px;
  object-fit: contain;
  background: rgba(0, 0, 0, 0.4);
  border-radius: 6px;
  padding: 4px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.pendant-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.pendant-name {
  color: #67c23a;
  font-weight: 600;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.pendant-details {
  display: flex;
  gap: 12px;
  font-size: 12px;
  flex-wrap: wrap;
}

.pendant-price {
  color: #f56c6c;
  font-weight: 700;
  font-size: 13px;
}

.pendant-pattern {
  color: #909399;
  font-size: 12px;
}

.no-pendant {
  color: #909399;
  font-size: 13px;
  font-style: italic;
  padding: 8px;
  text-align: center;
}

/* 价格区间提示样式 */
.price-range-hint {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
}

/* 隐藏数字输入框的加减器 */
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

.no-spinner :deep(input[type="number"]::-webkit-inner-spin-button),
.no-spinner :deep(input[type="number"]::-webkit-outer-spin-button) {
  -webkit-appearance: none;
  margin: 0;
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

/* 自定义配置表单 */
.custom-config-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 1.25rem 2.5rem;
  align-items: center;
}

.custom-config-field {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-height: 48px;
  flex: 0 0 auto;
}

.custom-config-field .field-label {
  min-width: 120px;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
}

.custom-config-field .field-control {
  flex: 0 0 100px;
  width: 100px;
}

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
  .spider-sticker-container {
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

  .sidebar-header-actions {
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


