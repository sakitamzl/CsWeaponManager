<template>
  <div class="spider-weapon-rename-container">
    <div class="page-layout">
      <!-- 左侧配置管理栏 -->
      <aside class="config-sidebar">
        <div class="sidebar-header">
          <h3>配置管理</h3>
        </div>

        <div class="config-list">
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
                <el-tag :type="config.platformType === 'buff' ? 'warning' : 'success'" size="small">
                  {{ config.platformType === 'buff' ? 'BUFF' : '悠悠有品' }}
                </el-tag>
              </div>
            </div>
            <div class="config-item-meta">
              <span class="config-time">{{ formatTime(config.updated_at) }}</span>
            </div>
            <div v-if="config.description" class="config-description">
              {{ config.description }}
            </div>
          </div>

          <div v-if="savedConfigs.length === 0" class="empty-config">
            <el-empty description="暂无保存的配置" :image-size="80" />
          </div>
        </div>

        <div class="sidebar-actions">
          <el-button 
            type="success" 
            @click="createNewConfig"
            :disabled="isCrawling"
          >
            <el-icon><Document /></el-icon>
            新建
          </el-button>
          
          <el-button 
            type="info" 
            @click="loadConfigList"
          >
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </aside>

      <!-- 右侧主内容区域 -->
      <div class="main-content-area">

      <!-- 饰品搜索区域 -->
      <!-- 统一的工具区域 -->
      <div class="unified-tool-section" :class="{ collapsed: isToolSectionCollapsed }">
        <div class="tool-section-header" @click="toggleToolSection">
          <h2 class="main-section-title">配置区域</h2>
          <el-button type="text" class="collapse-btn">
            <el-icon :size="20">
              <ArrowUp v-if="!isToolSectionCollapsed" />
              <ArrowDown v-else />
            </el-icon>
          </el-button>
        </div>
        
        <div class="tool-section-content" v-show="!isToolSectionCollapsed">
        <div class="tool-section">
        <h2 class="section-title">爬取配置</h2>
        
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
                  :disabled="!!selectedConfigId"
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

            <el-form-item label="饰品列表">
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
            </el-form-item>

            <el-form-item label="自定义配置">
              <div class="json-editor-container">
                <!-- JSON 编辑器 -->
                <div class="json-editor-wrapper">
                  <div class="json-editor-preview" v-if="crawlForm.customConfig" v-html="highlightedJson"></div>
                  <textarea 
                    v-model="crawlForm.customConfig" 
                    class="json-textarea"
                    placeholder='请输入 JSON 配置...'
                    @blur="formatJson"
                    @input="updateHighlight"
                    rows="8"
                  ></textarea>
                </div>
                <div v-if="jsonValidationMessage" class="json-validation">
                  <el-alert 
                    :type="jsonValidationStatus" 
                    :title="jsonValidationMessage"
                    :closable="false"
                    show-icon
                  />
                </div>
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
              <img 
                v-if="scope.row.iconUrl" 
                :src="scope.row.iconUrl" 
                class="weapon-icon"
                :alt="scope.row.weapon_name"
              />
              <span v-else class="no-icon">-</span>
            </template>
          </el-table-column>
          
          <el-table-column label="武器名称" width="200" fixed="left">
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
                  {{ scope.row.spread !== undefined && scope.row.spread !== null ? scope.row.spread.toFixed(2) : '0.00' }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column label="手续费" width="100" align="center">
              <template #default="scope">
                <span class="commission-fee">¥{{ scope.row.commissionFee !== undefined && scope.row.commissionFee !== null ? scope.row.commissionFee.toFixed(2) : '0.00' }}</span>
              </template>
            </el-table-column>
            
            <el-table-column label="收益" width="120" align="center">
              <template #default="scope">
                <el-tag 
                  :type="(scope.row.priceDiff !== undefined && scope.row.priceDiff !== null && scope.row.priceDiff < 0) ? 'danger' : ((scope.row.priceDiff !== undefined && scope.row.priceDiff !== null && scope.row.priceDiff < 3) ? 'warning' : 'success')" 
                  size="small"
                >
                  {{ scope.row.priceDiff !== undefined && scope.row.priceDiff !== null ? (scope.row.priceDiff >= 0 ? '+' : '') + scope.row.priceDiff.toFixed(2) : '0.00' }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column label="磨损" width="240">
              <template #default="scope">
                {{ scope.row.abrade }}
              </template>
            </el-table-column>
            
            <el-table-column label="改名" min-width="200">
              <template #default="scope">
                <span class="name-tag">{{ scope.row.nameTag || '-' }}</span>
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
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
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
    const steamIdList = ref([])
    const isCrawling = ref(false)
    const crawlResult = ref(null)
    
    // 轮询相关变量
    const sessionId = ref('') // 搜索会话ID
    const pollingTimer = ref(null) // 轮询定时器
    const lastItemId = ref(0) // 最后一条记录的ID（用于增量更新）
    const POLL_INTERVAL = 1000 // 轮询间隔（毫秒）- 1秒
    const noDataCount = ref(0) // 连续无数据次数
    const MAX_NO_DATA_COUNT = 10 // 连续10次无数据（10秒）后认为完成
    const lastPollingTime = ref(0) // 最后轮询时间
    
    // 将 weapons 转换为扁平列表，与 SearchPendant 保持一致
    const allCrawlItems = computed(() => {
      if (!crawlResult.value || !crawlResult.value.weapons) {
        console.log('[allCrawlItems] 📊 crawlResult 为空或无 weapons 数据')
        return []
      }

      console.log(`[allCrawlItems] 🔄 开始计算，weapons 数量: ${crawlResult.value.weapons.length}`)

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

            items.push({
              ...item,
              weapon_name: weapon.weapon_name,  // 添加武器名称
              yyyp_id: weapon.yyyp_id || weapon.weapon_id,
              commissionFee: commissionFee,  // 手续费
              priceDiff: priceDiff  // 收益
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

      console.log(`[allCrawlItems] ✅ 计算完成，总计 ${items.length} 件商品`)

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
    const clearCrawlHistory = () => {
      ElMessageBox.confirm(
        '确定要清空所有查询结果吗？此操作不可恢复。',
        '确认清空',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(() => {
        crawlResult.value = null
        localStorage.removeItem(STORAGE_KEY)
        ElMessage.success('已清空查询结果')
      }).catch(() => {
        // 用户取消
      })
    }

    // 实时日志处理
    const scrollLogPanelToBottom = () => {
      if (!logAutoScroll.value) return
      nextTick(() => {
        if (logPanelRef.value) {
          logPanelRef.value.scrollTop = logPanelRef.value.scrollHeight
        }
      })
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
    
    // 工具区域折叠状态
    const isToolSectionCollapsed = ref(false)
    
    // JSON 验证相关
    const jsonValidationMessage = ref('')
    const jsonValidationStatus = ref('success')
    const highlightedJson = ref('')

    const crawlForm = ref({
      configName: '',      // 对应 dataName
      steamId: '',         // 购买账号
      crawlAccountId: '',  // 爬取账号
      platformType: 'youpin',  // 平台类型：youpin 或 buff
      weaponId: [],        // 改为数组，存储 {id, name} 对象
      customConfig: ''     // 对应 value，JSON字符串
    })

    // 计算属性：获取饰品列表
    const weaponIdList = computed(() => {
      return crawlForm.value.weaponId || []
    })

    // 根据平台类型过滤Steam ID列表
    const filteredSteamIdList = computed(() => {
      console.log('原始Steam ID列表:', steamIdList.value)
      console.log('当前平台类型:', crawlForm.value.platformType)
      
      if (!crawlForm.value.platformType) {
        return steamIdList.value
      }
      
      // 根据平台类型过滤
      const filtered = steamIdList.value.filter(item => {
        console.log(`检查账号: ${item.dataName}, key1=${item.key1}, 平台=${crawlForm.value.platformType}`)
        return item.key1 === crawlForm.value.platformType
      })
      
      console.log(`过滤后的Steam ID列表 (${crawlForm.value.platformType}):`, filtered)
      
      // 如果过滤后为空，返回所有账号
      if (filtered.length === 0) {
        console.warn(`没有找到 key1='${crawlForm.value.platformType}' 的账号，显示所有账号`)
        return steamIdList.value
      }
      
      return filtered
    })

    // 计算是否可以开始爬取
    const canStartCrawl = computed(() => {
      // 检查必填字段
      if (!crawlForm.value.configName) return false
      if (!crawlForm.value.steamId) return false
      if (!crawlForm.value.weaponId || crawlForm.value.weaponId.length === 0) return false
      return true
    })

    // 加载Steam ID列表
    const loadSteamIdList = async () => {
      try {
        const response = await axios.get(`${API_CONFIG.BASE_URL}/webInventoryV1/steam_ids`)
        console.log('Steam ID API 响应:', response.data)
        if (response.data.success && response.data.data.length > 0) {
          steamIdList.value = response.data.data
          console.log('已加载 Steam ID 列表:', steamIdList.value)
          // 默认选择第一个符合平台类型的
          updateDefaultSteamId()
        }
      } catch (error) {
        console.error('加载Steam ID列表失败:', error)
        console.error('错误详情:', error.response)
        // 暂时不显示错误提示，避免干扰用户
        // ElMessage.error('加载Steam ID列表失败')
      }
    }
    
    // 更新默认Steam ID（根据当前平台类型）
    const updateDefaultSteamId = () => {
      if (filteredSteamIdList.value.length > 0) {
        const firstItem = filteredSteamIdList.value[0]
        const steamId = firstItem.steamID || firstItem.steam_id || ''
        
        // 设置爬取账号和购买账号为同一个账号
        crawlForm.value.crawlAccountId = steamId
        crawlForm.value.steamId = steamId
        
        console.log(`已设置默认账号: ${steamId}`)
        console.log(`  - 爬取账号: ${crawlForm.value.crawlAccountId}`)
        console.log(`  - 购买账号: ${crawlForm.value.steamId}`)
      } else {
        crawlForm.value.crawlAccountId = ''
        crawlForm.value.steamId = ''
        console.warn(`没有找到平台类型为 ${crawlForm.value.platformType} 的Steam ID`)
      }
    }
    
    // 平台类型改变处理
    const handlePlatformTypeChange = () => {
      // 切换平台类型时，自动更新Steam ID为该平台的第一个
      updateDefaultSteamId()
    }

    // 验证JSON配置
    const validateJsonConfig = () => {
      if (!crawlForm.value.customConfig || crawlForm.value.customConfig.trim() === '') {
        return { valid: true, config: null }
      }

      try {
        const config = JSON.parse(crawlForm.value.customConfig)
        return { valid: true, config: config }
      } catch (error) {
        return { valid: false, error: error.message }
      }
    }

    // 切换工具区域显示/隐藏
    const toggleToolSection = () => {
      isToolSectionCollapsed.value = !isToolSectionCollapsed.value
    }

    // 加载数据库中最近的搜索结果（页面加载时）
    const loadRecentSearchResults = async () => {
      try {
        console.log('[页面加载] 尝试加载历史搜索结果...')
        
        // 获取所有搜索结果（不指定sessionId）
        const url = `${API_CONFIG.BASE_URL}/searchRename/items/list`
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
          
          // 转换数据格式（数据库返回的是蛇形命名）
          const historyItems = result.items.map(item => ({
            id: item.commodity_id || item.commodityId,
            commodityNo: item.commodity_no || item.commodityNo,
            price: item.price,
            lowest_price: item.lowest_price || item.lowestPrice,
            spread: item.spread,
            abrade: item.abrade,
            paintSeed: item.paint_seed || item.paintSeed,
            nameTag: item.name_tag || item.nameTag,
            userNickName: item.seller_name || item.sellerName,
            assetId: item.asset_id || item.assetId,
            iconUrl: item.icon_url || item.iconUrl,
            weapon_name: item.weapon_name || item.weaponName,
            weapon_id: item.weapon_id || item.weaponId,
            commissionFee: item.commission_fee || item.commissionFee,
            priceDiff: item.price_diff || item.priceDiff
          }))
          
          // 按收益排序
          historyItems.sort((a, b) => (b.priceDiff || 0) - (a.priceDiff || 0))
          
          // 按武器名称分组显示历史数据
          const weaponGroups = {}
          historyItems.forEach(item => {
            const weaponName = item.weapon_name || '未知武器'
            if (!weaponGroups[weaponName]) {
              weaponGroups[weaponName] = []
            }
            weaponGroups[weaponName].push(item)
          })
          
          // 转换为weapons数组格式
          const weapons = Object.keys(weaponGroups).map(weaponName => ({
            weapon_name: weaponName,
            items: weaponGroups[weaponName]
          }))
          
          crawlResult.value = { weapons }
          
          console.log(`[页面加载] 已加载 ${result.items.length} 条历史搜索结果`)
          await nextTick()
        } else {
          console.log('[页面加载] 没有找到历史数据')
        }
      } catch (error) {
        console.error('[页面加载] 加载历史数据失败:', error)
      }
    }

    // 轮询获取数据库中的搜索结果（持续轮询，只要页面在前台）
    const pollSearchResults = async () => {
      try {
        lastPollingTime.value = Date.now()
        
        // 如果有 sessionId，使用增量查询
        let url
        if (sessionId.value) {
          // 正在搜索中，只获取当前会话的新数据
          url = `${API_CONFIG.BASE_URL}/searchRename/items/latest?sessionId=${sessionId.value}&sinceId=${lastItemId.value}`
        } else {
          // 没有会话ID，获取所有数据
          url = `${API_CONFIG.BASE_URL}/searchRename/items/list`
        }
        
        const response = await fetch(url)
        
        if (!response.ok) {
          console.error('[轮询] HTTP错误:', response.status)
          return
        }

        const result = await response.json()
        console.log('[轮询] API返回:', result)
        
        if (result.success && result.items && result.items.length > 0) {
          console.log(`[轮询] 获取到 ${result.items.length} 条数据`)
          console.log('[轮询] 第一条数据示例:', result.items[0])
          console.log('[轮询] 第一条weapon_name:', result.items[0].weapon_name)
          
          // 如果正在搜索，重置无数据计数
          if (isCrawling.value) {
            noDataCount.value = 0
          }
          
          // 获取当前的所有商品列表
          const currentItems = crawlResult.value?.weapons?.[0]?.items || []
          
          // 添加新数据（数据库返回的是蛇形命名）
          const newItems = result.items.map(item => ({
            id: item.commodity_id || item.commodityId,
            commodityNo: item.commodity_no || item.commodityNo,
            price: item.price,
            lowest_price: item.lowest_price || item.lowestPrice,
            spread: item.spread,
            abrade: item.abrade,
            paintSeed: item.paint_seed || item.paintSeed,
            nameTag: item.name_tag || item.nameTag,
            userNickName: item.seller_name || item.sellerName,
            assetId: item.asset_id || item.assetId,
            iconUrl: item.icon_url || item.iconUrl,
            weapon_name: item.weapon_name || item.weaponName,
            weapon_id: item.weapon_id || item.weaponId,
            commissionFee: item.commission_fee || item.commissionFee,
            priceDiff: item.price_diff || item.priceDiff
          }))
          
          // 去重合并（基于 commodityId）
          const itemMap = new Map()
          currentItems.forEach(item => itemMap.set(item.id, item))
          newItems.forEach(item => itemMap.set(item.id, item))
          const allItems = Array.from(itemMap.values())
          
          // 按收益排序
          allItems.sort((a, b) => (b.priceDiff || 0) - (a.priceDiff || 0))
          
          // 按武器名称分组显示数据
          const weaponGroups = {}
          allItems.forEach(item => {
            const weaponName = item.weapon_name || '未知武器'
            if (!weaponGroups[weaponName]) {
              weaponGroups[weaponName] = []
            }
            weaponGroups[weaponName].push(item)
          })
          
          // 转换为weapons数组格式
          const weapons = Object.keys(weaponGroups).map(weaponName => ({
            weapon_name: weaponName,
            items: weaponGroups[weaponName]
          }))
          
          crawlResult.value = { weapons }
          
          // 更新lastItemId
          if (result.items.length > 0) {
            const maxId = Math.max(...result.items.map(item => item.id))
            if (maxId > lastItemId.value) {
              lastItemId.value = maxId
            }
          }
          
          await nextTick()
        } else {
          // 没有新数据
          if (isCrawling.value) {
            // 只有在搜索中才增加计数
            noDataCount.value++
            
            // 如果连续多次无数据，认为搜索完成
            if (noDataCount.value >= MAX_NO_DATA_COUNT) {
              console.log('[轮询] 连续无新数据，认为搜索完成')
              isCrawling.value = false
              sessionId.value = '' // 清空sessionId
              
              const totalItems = crawlResult.value?.weapons?.[0]?.items?.length || 0
              console.log(`[轮询] 搜索完成，共找到 ${totalItems} 个符合条件的商品`)
              ElMessage.success(`搜索完成！找到 ${totalItems} 个符合条件的商品`)
              
              if (crawlResult.value) {
                saveCrawlResultToStorage(crawlResult.value)
              }
            }
          }
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
      // 开始搜索时自动折叠工具区域
      isToolSectionCollapsed.value = true
      
      // 验证基本配置
      if (!crawlForm.value.configName) {
        ElMessage.warning('请输入配置名称')
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

      // 验证JSON配置
      const jsonValidation = validateJsonConfig()
      if (!jsonValidation.valid) {
        ElMessage.error(`自定义配置JSON格式错误: ${jsonValidation.error}`)
        return
      }

      // 确认对话框
      try {
        const weaponNames = crawlForm.value.weaponId.map(w => w.name).join('、')
        let confirmMessage = `确定要开始查询改名饰品吗？\n\n`
        confirmMessage += `配置名称: ${crawlForm.value.configName}\n`
        confirmMessage += `爬取账号: ${crawlForm.value.crawlAccountId}\n`
        confirmMessage += `购买账号: ${crawlForm.value.steamId}\n`
        confirmMessage += `平台类型: ${crawlForm.value.platformType === 'buff' ? 'BUFF' : '悠悠有品'}\n`
        confirmMessage += `监控饰品: ${weaponNames}\n`
        confirmMessage += `饰品数量: ${crawlForm.value.weaponId.length} 个`
        
        if (jsonValidation.config) {
          const config = jsonValidation.config
          if (config['最大差价']) {
            confirmMessage += `\n最大溢价: ${config['最大差价']} 元`
          }
          if (config['饰品自动查询间隔']) {
            confirmMessage += `\n查询间隔: ${config['饰品自动查询间隔']} 秒`
          }
        }

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

      // 初始化状态
      isCrawling.value = true
      crawlResult.value = { weapons: [] }
      sessionId.value = '' // 清空sessionId
      lastItemId.value = 0 // 重置lastItemId
      noDataCount.value = 0 // 重置无数据计数
      stopPolling() // 停止之前的轮询
      console.log('[前端] 正在启动查询任务...')

      try {
        // 构建请求
        const spiderConfig = {
          weapon_id: crawlForm.value.weaponId,
          steam_id: crawlForm.value.crawlAccountId,
          最大差价: 5,
          饰品自动查询间隔: 3,
          ...jsonValidation.config
        }
        
        const requestData = {
          steamId: crawlForm.value.crawlAccountId,
          spider_config: spiderConfig
        }
        
        console.log('[前端] 发送搜索请求:', requestData)

        // 先创建会话
        const createSessionResponse = await fetch(
          `${API_CONFIG.BASE_URL}/searchRename/session/create`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ steamId: crawlForm.value.crawlAccountId })
          }
        )

        if (!createSessionResponse.ok) {
          throw new Error('创建搜索会话失败')
        }

        const sessionResult = await createSessionResponse.json()
        if (!sessionResult.success || !sessionResult.sessionId) {
          throw new Error('获取会话ID失败')
        }

        sessionId.value = sessionResult.sessionId
        console.log(`[前端] 创建会话成功: ${sessionId.value}`)
        console.log(`[前端] 会话ID: ${sessionId.value}`)
        console.log('[前端] 轮询已自动运行，将持续获取搜索结果...')

        // 发起搜索请求（后台执行）
        fetch(
          `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/auto_buy_renamed_weapon`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
          }
        ).then(async response => {
          if (response.ok) {
            const result = await response.json()
            console.log('[前端] 搜索任务响应:', result)
            
            if (result.success) {
              console.log(`[前端] 搜索任务已启动 - Session: ${result.sessionId}`)
              console.log('[前端] 后台搜索任务已启动，开始轮询数据...')
            } else {
              throw new Error(result.message || '启动搜索失败')
            }
          } else {
            throw new Error(`HTTP ${response.status}`)
          }
        }).catch(error => {
          console.error('[前端] 启动搜索任务失败:', error)
          console.error(`[前端] 启动搜索任务失败: ${error.message}`)
          ElMessage.error(`启动搜索失败: ${error.message}`)
          isCrawling.value = false
          sessionId.value = '' // 清空sessionId
        })

        // 设置最大搜索时间（5分钟后自动停止搜索状态，但轮询继续）
        setTimeout(() => {
          if (isCrawling.value) {
            console.log('[前端] 搜索超时，结束搜索状态')
            isCrawling.value = false
            sessionId.value = '' // 清空sessionId
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
        sessionId.value = '' // 清空sessionId
      }
    }

    // 重置表单
    const resetForm = () => {
      const defaultSteamId = steamIdList.value.length > 0 
        ? (steamIdList.value[0].steamID || steamIdList.value[0].steam_id || '') 
        : ''
      
      crawlForm.value = {
        configName: '',
        steamId: defaultSteamId,
        platformType: 'youpin',
        weaponId: [],
        customConfig: ''
      }
      crawlResult.value = null
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
        steam: 'Steam库存'
      }
      return labels[source] || source
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
          platformType: config.key2 === 'buff' ? 'buff' : 'youpin'
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

      try {
        const config = savedConfigs.value.find(c => c.id === configId)
        console.log('找到的配置对象:', config)
        
        if (config && config.value) {
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
          const { weapon_id, steam_id, ...restConfig } = valueObj
          
          // 构建新的表单数据
          const newFormData = {
            configName: config.dataName || '',
            steamId: steamId,
            platformType: config.platformType || 'youpin',
            weaponId: Array.isArray(weaponId) ? weaponId : [],
            customConfig: Object.keys(restConfig).length > 0 ? JSON.stringify(restConfig, null, 2) : ''
          }
          
          console.log('准备填充的表单数据:', newFormData)
          
          // 加载配置数据到表单
          crawlForm.value = newFormData
          
          // 等待下一个tick确保数据已更新
          await new Promise(resolve => setTimeout(resolve, 50))
          
          console.log('表单填充完成，当前表单值:')
          console.log('  - configName:', crawlForm.value.configName)
          console.log('  - steamId:', crawlForm.value.steamId)
          console.log('  - platformType:', crawlForm.value.platformType)
          console.log('  - weaponId:', crawlForm.value.weaponId)
          console.log('  - customConfig:', crawlForm.value.customConfig)
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

    // 保存配置（直接保存，不弹窗）
    const saveConfig = async () => {
      if (!crawlForm.value.configName) {
        ElMessage.warning('请输入配置名称')
        return
      }

      try {
        // 构建 value 对象
        let valueObj = {}
        
        // 如果有自定义配置，先解析
        if (crawlForm.value.customConfig) {
          try {
            valueObj = JSON.parse(crawlForm.value.customConfig)
          } catch (e) {
            ElMessage.error('自定义配置JSON格式错误')
            return
          }
        }
        
        // 将饰品列表添加到 value 对象中
        if (crawlForm.value.weaponId && crawlForm.value.weaponId.length > 0) {
          valueObj.weapon_id = crawlForm.value.weaponId
        }
        
        // 添加其他必要字段
        if (crawlForm.value.steamId) {
          valueObj.steam_id = crawlForm.value.steamId
        }

        // 根据平台类型设置 key2
        const key2 = crawlForm.value.platformType === 'buff' ? 'buff' : 'youpin'

        const configData = {
          dataName: crawlForm.value.configName,
          key1: 'spider_rename',
          key2: key2,
          value: JSON.stringify(valueObj)
        }

        const response = await axios.post(`${API_CONFIG.BASE_URL}/configV1/save`, configData)
        
        if (response.data.success) {
          ElMessage.success('保存配置成功')
          
          // 重新加载配置列表
          await loadConfigList()
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
      if (crawlForm.value.platformType === 'buff') {
        return row.buff_id
      } else {
        return row.yyyp_id
      }
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
      const weaponId = getWeaponIdByPlatform(row)
      
      if (!weaponId) {
        const platformName = crawlForm.value.platformType === 'buff' ? 'BUFF' : '悠悠有品'
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
      
      const platformName = crawlForm.value.platformType === 'buff' ? 'BUFF' : '悠悠有品'
      ElMessage.success(`已添加${platformName}饰品: ${row.market_listing_item_name || row.name}`)
    }

    // 删除饰品ID
    const removeWeaponId = (idToRemove) => {
      crawlForm.value.weaponId = crawlForm.value.weaponId.filter(w => w.id !== idToRemove)
      ElMessage.success('已删除饰品')
    }

    // 购买饰品
    const handleBuyWeapon = async (item) => {
      console.log('购买商品:', item)
      
      // 确认购买
      try {
        await ElMessageBox.confirm(
          `确认购买该商品吗？\n\n改名：${item.nameTag || '无'}\n价格：¥${item.price}\n磨损：${item.abrade || '-'}\n溢价：+¥${item.spread.toFixed(2)}`,
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

    // 格式化 JSON
    const formatJson = () => {
      jsonValidationMessage.value = ''
      
      if (!crawlForm.value.customConfig || crawlForm.value.customConfig.trim() === '') {
        return
      }

      try {
        const parsed = JSON.parse(crawlForm.value.customConfig)
        crawlForm.value.customConfig = JSON.stringify(parsed, null, 2)
        // 格式化成功，不显示提示
      } catch (error) {
        jsonValidationMessage.value = `JSON 格式错误: ${error.message}`
        jsonValidationStatus.value = 'error'
      }
    }

    // 仅验证 JSON
    const validateJsonOnly = () => {
      jsonValidationMessage.value = ''
      
      if (!crawlForm.value.customConfig || crawlForm.value.customConfig.trim() === '') {
        jsonValidationMessage.value = 'JSON 配置为空'
        jsonValidationStatus.value = 'info'
        return
      }

      try {
        JSON.parse(crawlForm.value.customConfig)
        jsonValidationMessage.value = 'JSON 格式验证通过 ✓'
        jsonValidationStatus.value = 'success'
        
        setTimeout(() => {
          jsonValidationMessage.value = ''
        }, 2000)
      } catch (error) {
        jsonValidationMessage.value = `JSON 格式错误: ${error.message}`
        jsonValidationStatus.value = 'error'
      }
    }

    // 清空 JSON
    const clearJson = () => {
      crawlForm.value.customConfig = ''
      jsonValidationMessage.value = ''
      highlightedJson.value = ''
    }

    // 更新语法高亮
    const updateHighlight = () => {
      const json = crawlForm.value.customConfig
      if (!json || json.trim() === '') {
        highlightedJson.value = ''
        return
      }
      
      // 简单的 JSON 语法高亮
      let highlighted = json
        // 转义 HTML 特殊字符
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        // 高亮字符串（键）
        .replace(/"([^"]+)"(\s*:)/g, '<span class="json-key">"$1"</span>$2')
        // 高亮字符串值
        .replace(/:\s*"([^"]*)"/g, ': <span class="json-string">"$1"</span>')
        // 高亮数字
        .replace(/:\s*(\d+\.?\d*)/g, ': <span class="json-number">$1</span>')
        // 高亮布尔值
        .replace(/:\s*(true|false)/g, ': <span class="json-boolean">$1</span>')
        // 高亮 null
        .replace(/:\s*(null)/g, ': <span class="json-null">$1</span>')
        // 高亮括号
        .replace(/([{}[\]])/g, '<span class="json-bracket">$1</span>')
      
      highlightedJson.value = highlighted
    }

    // 组件挂载时加载数据并启动轮询
    onMounted(() => {
      loadSteamIdList()
      loadConfigList()
      
      // 从数据库加载最近的搜索结果
      loadRecentSearchResults()
      
      // 启动持续轮询（只要页面在前台就轮询）
      startPolling()
    })

    // 组件卸载时停止轮询
    onUnmounted(() => {
      stopPolling()
    })

    return {
      crawlFormRef,
      steamIdList,
      filteredSteamIdList,
      isCrawling,
      crawlForm,
      crawlResult,
      allCrawlItems,
      canStartCrawl,
      startCrawl,
      resetForm,
      getModeLabel,
      getSourceLabel,
      handlePlatformTypeChange,
      // 配置管理
      savedConfigs,
      selectedConfigId,
      loadConfigList,
      selectConfig,
      createNewConfig,
      saveConfig,
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
      getRowClassName,
      // 购买相关
      buyingItems,
      purchasedItems,
      handleBuyWeapon,
      getBuyButtonType,
      // 历史结果管理
      clearCrawlHistory,
      clearStreamLogs,
      formatLogTime,
      // 工具区域折叠
      isToolSectionCollapsed,
      toggleToolSection,
      // JSON 编辑器
      jsonValidationMessage,
      jsonValidationStatus,
      highlightedJson,
      formatJson,
      validateJsonOnly,
      clearJson,
      updateHighlight,
      // 从搜索组件添加饰品
      handleAddWeaponFromSearch,
      handleAddAllWeaponsFromSearch
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

.back-button {
  /* 按钮样式 */
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
  max-height: calc(100vh - 150px);
  position: sticky;
  top: 1rem;
}

.sidebar-header {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #333;
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
  -webkit-box-orient: vertical;
}

.empty-config {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
}

.sidebar-actions {
  display: flex;
  gap: 0.5rem;
  padding-top: 1rem;
  border-top: 1px solid #333;
}

.sidebar-actions .el-button {
  flex: 1;
}

/* 右侧主内容区域 */
.main-content-area {
  flex: 1;
  min-width: 0;
  max-width: calc(100% - 280px - 1.5rem);
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
  padding-bottom: 1rem;
  border-bottom: 2px solid #333;
  margin-bottom: 1.5rem;
  user-select: none;
}

.unified-tool-section.collapsed .tool-section-header {
  padding-bottom: 0;
  border-bottom: none;
  margin-bottom: 0;
}

.main-section-title {
  color: #fff;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
}

.collapse-btn {
  color: #909399;
  padding: 0.5rem;
  transition: all 0.3s ease;
}

.collapse-btn:hover {
  color: #409eff;
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
  margin: 0;
}

.no-spinner :deep(input[type="number"]) {
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

.form-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 0;
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
.json-editor-container {
  width: 100%;
}

.json-editor-wrapper {
  position: relative;
  width: 100%;
  min-height: 200px;
  background-color: #1a1a1a;
  border: 1px solid #444;
  border-radius: 4px;
  overflow: hidden;
}

.json-editor-preview {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 8px 11px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: transparent;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow: hidden;
  pointer-events: none;
  z-index: 1;
}

.json-textarea {
  position: relative;
  width: 100%;
  min-height: 200px;
  padding: 8px 11px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  background-color: transparent;
  color: #e8e8e8;
  border: none;
  outline: none;
  resize: vertical;
  z-index: 2;
  caret-color: #e8e8e8;
}

.json-textarea::placeholder {
  color: #666;
  font-size: 12px;
}

/* JSON 语法高亮颜色 */
:deep(.json-key) {
  color: #9cdcfe; /* 键名 - 浅蓝色 */
}

:deep(.json-string) {
  color: #ce9178; /* 字符串值 - 橙色 */
}

:deep(.json-number) {
  color: #b5cea8; /* 数字 - 浅绿色 */
}

:deep(.json-boolean) {
  color: #569cd6; /* 布尔值 - 蓝色 */
}

:deep(.json-null) {
  color: #569cd6; /* null - 蓝色 */
}

:deep(.json-bracket) {
  color: #ffd700; /* 括号 - 金色 */
}

.json-tools {
  margin-top: 8px;
  display: flex;
  gap: 8px;
}

.json-validation {
  margin-top: 8px;
}

/* 响应式设计 */
/* 大屏幕优化 */
@media (min-width: 1920px) {
  .config-sidebar {
    width: 320px;
    min-width: 320px;
  }
  
  .main-content-area {
    max-width: calc(100% - 320px - 1.5rem);
  }
}

/* 中等屏幕 */
@media (max-width: 1440px) {
  .config-sidebar {
    width: 260px;
    min-width: 260px;
    padding: 1rem;
  }
  
  .main-content-area {
    max-width: calc(100% - 260px - 1.5rem);
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
  
  .main-content-area {
    max-width: 100%;
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

