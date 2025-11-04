<template>
  <div class="spider-pendant-container">
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

      <!-- 统一的工具区域 -->
      <div class="unified-tool-section" :class="{ collapsed: isToolSectionCollapsed }">
        <div class="tool-section-header" @click="toggleToolSection">
          <h2 class="section-title">爬取配置</h2>
          <el-button type="text" class="collapse-btn">
            <el-icon :size="20">
              <ArrowUp v-if="!isToolSectionCollapsed" />
              <ArrowDown v-else />
            </el-icon>
          </el-button>
        </div>
        
        <div class="tool-section-content" v-show="!isToolSectionCollapsed">
        <div class="tool-section">
        
        <div class="form-container">
          <el-form :model="crawlForm" label-width="120px" ref="crawlFormRef">
            <div class="form-row">
              <el-form-item label="配置名称" required class="form-item-third">
                <el-input 
                  v-model="crawlForm.configName" 
                  placeholder="请输入配置名称"
                  clearable
                />
              </el-form-item>

              <el-form-item label="Steam ID" required class="form-item-third">
                <el-select 
                  v-model="crawlForm.steamId" 
                  placeholder="选择 Steam ID"
                  style="width: 100%;"
                  filterable
                >
                  <el-option 
                    v-for="item in steamIdList" 
                    :key="item.steamID || item.steam_id" 
                    :label="`${item.dataName || '未命名'} (${item.steamID || item.steam_id || '无ID'})`" 
                    :value="item.steamID || item.steam_id"
                  />
                </el-select>
              </el-form-item>

              <el-form-item label="平台类型" required class="form-item-third">
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
            </div>

            <el-form-item label="饰品列表">
              <div class="weapon-id-section">
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

        <!-- 搜索饰品部分 -->
        <div class="search-section">
          <h2 class="section-title">搜索饰品</h2>
        
        <div class="search-container">
          <div class="search-filters">
            <el-select 
              v-model="weaponSearchFilters.weaponType" 
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
              v-model="weaponSearchFilters.weaponName" 
              placeholder="选择武器名称"
              clearable
              filterable
              style="width: 200px;"
              :loading="isLoadingWeaponNames"
              :disabled="!weaponSearchFilters.weaponType"
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
              v-model="weaponSearchFilters.rarity" 
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
              v-model.number="weaponSearchFilters.priceMin" 
              placeholder="最低价格"
              type="number"
              clearable
              style="width: 150px;"
              class="no-spinner"
            />
            
            <el-input 
              v-model.number="weaponSearchFilters.priceMax" 
              placeholder="最高价格"
              type="number"
              clearable
              style="width: 150px;"
              class="no-spinner"
            />
            
            <el-input 
              v-model.number="weaponSearchFilters.minOnSaleCount" 
              placeholder="最小在售数量"
              type="number"
              clearable
              style="width: 150px;"
              class="no-spinner"
            />
          </div>
          
          <el-input
            v-model="weaponSearchKeyword"
            placeholder="搜索饰品名称..."
            prefix-icon="Search"
            class="weapon-search-input"
            @keyup.enter="handleSearchWeapon"
            clearable
          >
            <template #append>
              <el-button 
                type="primary" 
                @click="handleSearchWeapon" 
                :loading="isSearchingWeapon"
              >
                搜索
              </el-button>
            </template>
          </el-input>
        </div>

        <!-- 搜索结果表格 -->
        <div v-if="weaponSearchResults.length > 0" class="search-results-table">
          <div class="results-header">
            <span class="results-title">
              搜索结果 ({{ weaponSearchResults.length }} 件)
            </span>
            <div class="results-actions">
              <el-button 
                type="success" 
                size="small"
                @click="addAllWeaponIds"
                :disabled="weaponSearchResults.length === 0"
              >
                <el-icon><Document /></el-icon>
                一键添加全部
              </el-button>
              <el-button 
                type="text" 
                size="small"
                @click="clearWeaponSearch"
              >
                清除结果
              </el-button>
            </div>
          </div>
          
          <el-table 
            :data="weaponSearchResults" 
            style="width: 100%"
            :row-class-name="getRowClassName"
          >
            <el-table-column type="index" label="#" width="60" align="center" />
            
            <el-table-column label="饰品名称" min-width="250" show-overflow-tooltip>
              <template #default="{ row }">
                <span class="weapon-name">{{ row.market_listing_item_name }}</span>
              </template>
            </el-table-column>
            
            <el-table-column label="Steam Hash Name" min-width="200" show-overflow-tooltip>
              <template #default="{ row }">
                <span class="hash-name-text">{{ row.steam_hash_name || '-' }}</span>
              </template>
            </el-table-column>
            
            <el-table-column label="武器类型" width="120" align="center">
              <template #default="{ row }">
                <el-tag size="small" type="info">{{ row.weapon_type || '-' }}</el-tag>
              </template>
            </el-table-column>
            
            <el-table-column label="稀有度" width="120" align="center">
              <template #default="{ row }">
                <span v-if="row.Rarity" class="rarity-text" :style="{ color: getRarityColor(row.Rarity) }">
                  {{ row.Rarity }}
                </span>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>
            
            <el-table-column label="价格" width="100" align="center">
              <template #default="{ row }">
                <span class="price-text" v-if="crawlForm.platformType === 'youpin' && row.yyyp_Price">
                  ¥{{ row.yyyp_Price }}
                </span>
                <span class="price-text" v-else-if="crawlForm.platformType === 'buff' && row.buff_Price">
                  ¥{{ row.buff_Price }}
                </span>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>
            
            <el-table-column label="在售数量" width="100" align="center">
              <template #default="{ row }">
                <span class="count-text" v-if="crawlForm.platformType === 'youpin' && row.yyyp_OnSaleCount">
                  {{ row.yyyp_OnSaleCount }}
                </span>
                <span class="count-text" v-else-if="crawlForm.platformType === 'buff' && row.buff_OnSaleCount">
                  {{ row.buff_OnSaleCount }}
                </span>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>
            
            <el-table-column v-if="crawlForm.platformType === 'youpin'" label="悠悠有品ID" width="130" align="center">
              <template #default="{ row }">
                <el-tag type="warning" v-if="row.yyyp_id">{{ row.yyyp_id }}</el-tag>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>
            
            <el-table-column v-if="crawlForm.platformType === 'buff'" label="BUFF ID" width="110" align="center">
              <template #default="{ row }">
                <el-tag type="info" v-if="row.buff_id">{{ row.buff_id }}</el-tag>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="120" align="center" fixed="right">
              <template #default="{ row }">
                <el-button 
                  type="primary" 
                  size="small"
                  @click="addWeaponId(row)"
                  :disabled="!getWeaponIdByPlatform(row)"
                >
                  添加ID
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <!-- 加载更多提示 -->
          <div v-if="weaponSearchResults.length > 0" class="load-more-container">
            <div v-if="isLoadingMore" class="loading-more">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>加载中...</span>
            </div>
            <div v-else-if="!hasMore" class="no-more-data">
              已加载全部 {{ weaponSearchResults.length }} 条数据
            </div>
            <div v-else class="can-load-more">
              已加载 {{ weaponSearchResults.length }} 条，下拉加载更多
            </div>
          </div>
        </div>
        </div>

        </div>
        <!-- 结束 tool-section-content -->
      </div>
      <!-- 结束 unified-tool-section -->

      <!-- 查询结果区域 -->
      <div v-if="crawlResult && crawlResult.weapons && crawlResult.weapons.length > 0" class="result-section">
        <h2 class="section-title">查询结果</h2>
        
        <!-- 每个饰品的结果 -->
        <div v-for="weapon in crawlResult.weapons" :key="weapon.weapon_id" class="weapon-result-card">
          <div class="weapon-header">
            <h3 class="weapon-name">{{ weapon.weapon_name }}</h3>
            <div class="weapon-stats">
              <el-tag size="small">总在售: {{ weapon.total_count }}</el-tag>
              <el-tag size="small" type="warning">最低价: ¥{{ weapon.lowest_price }}</el-tag>
              <el-tag size="small" type="info">挂件数: {{ weapon.pendant_count }}</el-tag>
              <el-tag size="small" type="success">符合条件: {{ weapon.target_count }}</el-tag>
            </div>
          </div>
          
          <!-- 商品列表 -->
          <el-table 
            :data="weapon.items" 
            style="width: 100%"
            stripe
          >
            <el-table-column label="价格" width="100">
              <template #default="scope">
                <span class="price">¥{{ scope.row.price }}</span>
              </template>
            </el-table-column>
            
            <el-table-column label="溢价" width="100">
              <template #default="scope">
                <el-tag type="success" size="small">
                  +¥{{ scope.row.spread.toFixed(2) }}
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
                  type="primary" 
                  size="small"
                  @click="handleBuyWeapon(scope.row)"
                  :loading="buyingItems[scope.row.id]"
                >
                  购买
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
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
import { Document, Delete, Refresh, ArrowUp, ArrowDown, InfoFilled, Loading } from '@element-plus/icons-vue'
import { API_CONFIG } from '@/config/api.js'

export default {
  name: 'SpiderPendant',
  components: {
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
    const steamIdList = ref([])
    const isCrawling = ref(false)
    const crawlResult = ref(null)
    
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
    const buyingItems = ref({})
    
    // 工具区域折叠状态
    const isToolSectionCollapsed = ref(false)
    
    // JSON 验证相关
    const jsonValidationMessage = ref('')
    const jsonValidationStatus = ref('success')
    const highlightedJson = ref('')

    const crawlForm = ref({
      configName: '',      // 对应 dataName
      steamId: '',
      platformType: 'youpin',  // 平台类型：youpin 或 buff
      weaponId: [],        // 改为数组，存储 {id, name} 对象
      customConfig: ''     // 对应 value，JSON字符串
    })

    // 计算属性：获取饰品列表
    const weaponIdList = computed(() => {
      return crawlForm.value.weaponId || []
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
          // 默认选择第一个
          if (!crawlForm.value.steamId && steamIdList.value.length > 0) {
            const firstItem = steamIdList.value[0]
            crawlForm.value.steamId = firstItem.steamID || firstItem.steam_id || ''
          }
        }
      } catch (error) {
        console.error('加载Steam ID列表失败:', error)
        console.error('错误详情:', error.response)
      }
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

    // 开始爬取（流式接收）
    const startCrawl = async () => {
      // 开始搜索时自动折叠工具区域
      isToolSectionCollapsed.value = true
      // 验证基本配置
      if (!crawlForm.value.configName) {
        ElMessage.warning('请输入配置名称')
        return
      }
      
      if (!crawlForm.value.steamId) {
        ElMessage.warning('请选择 Steam ID')
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
        let confirmMessage = `确定要开始查询带挂件饰品吗？\n\n`
        confirmMessage += `配置名称: ${crawlForm.value.configName}\n`
        confirmMessage += `Steam ID: ${crawlForm.value.steamId}\n`
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

      isCrawling.value = true
      crawlResult.value = null
      ElMessage.info('正在启动查询任务...')

      try {
        // 构建爬虫配置
        const spiderConfig = {
          weapon_id: crawlForm.value.weaponId,  // [{"id": "61490", "name": "..."}]
          steam_id: crawlForm.value.steamId,
          最大差价: 5,
          饰品自动查询间隔: 3,
          ...jsonValidation.config  // 合并自定义配置
        }
        
        const requestData = {
          steamId: crawlForm.value.steamId,
          spider_config: spiderConfig
        }
        
        console.log('发送流式请求到后端:', requestData)

        // 使用 fetch 进行流式请求
        const response = await fetch(
          `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/auto_buy_pendant_weapon`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
          }
        )

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }

        // 初始化结果数据结构
        const weaponsMap = new Map()
        let totalWeapons = 0

        // 读取流式数据
        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''
        let chunkCount = 0

        while (true) {
          const { done, value } = await reader.read()

          if (done) {
            console.log('✅ 流式数据接收完成')
            break
          }

          chunkCount++
          const chunk = decoder.decode(value, { stream: true })
          console.log(`[前端] 📦 收到第 ${chunkCount} 个数据块，大小: ${chunk.length} 字节`)
          console.log(`[前端] 📦 数据块内容预览:`, chunk.substring(0, 200))
          
          // 解码数据
          buffer += chunk

          // 按行分割（SSE格式）
          const lines = buffer.split('\n')
          buffer = lines.pop() || '' // 保留最后一个不完整的行

          console.log(`[前端] 📋 本次解析出 ${lines.length} 行`)

          for (let i = 0; i < lines.length; i++) {
            const line = lines[i]
            if (!line.trim()) {
              continue // 跳过空行
            }
            
            if (!line.startsWith('data: ')) {
              console.warn(`[前端] ⚠️ 第 ${i+1} 行不是有效的 SSE 数据:`, line)
              continue
            }

            try {
              const jsonStr = line.substring(6)
              console.log(`[前端] 🔍 第 ${i+1} 行解析 JSON:`, jsonStr)
              const eventData = JSON.parse(jsonStr)
              console.log(`[前端] ✅ 第 ${i+1} 行解析成功:`, eventData)

              switch (eventData.type) {
                case 'start':
                  totalWeapons = eventData.total
                  ElMessage.info(`开始查询 ${totalWeapons} 个饰品...`)
                  break

                case 'processing':
                  console.log(`正在处理 ${eventData.current}/${eventData.total}: ${eventData.weapon_name}`)
                  break

                case 'item':
                  // 收到一个新商品，立即添加到结果中
                  const weaponId = eventData.weapon_id
                  
                  console.log(`[前端] 收到 item 事件:`, eventData)

                  if (!weaponsMap.has(weaponId)) {
                    console.log(`[前端] 创建新饰品条目: ${eventData.weapon_name} (${weaponId})`)
                    weaponsMap.set(weaponId, {
                      weapon_id: weaponId,
                      weapon_name: eventData.weapon_name,
                      total_count: eventData.total_count,
                      lowest_price: eventData.lowest_price,
                      pendant_count: 0,
                      target_count: 0,
                      items: []
                    })
                  }

                  const weaponData = weaponsMap.get(weaponId)
                  console.log(`[前端] 添加商品到 ${eventData.weapon_name}，当前已有 ${weaponData.items.length} 个`)
                  weaponData.items.push(eventData.item)
                  weaponData.target_count = weaponData.items.length

                  // 实时更新显示 - 创建新对象以触发 Vue 响应式更新
                  crawlResult.value = {
                    weapons: Array.from(weaponsMap.values()).map(w => ({
                      ...w,
                      items: [...w.items] // 创建新数组引用
                    }))
                  }
                  
                  console.log(`[前端] 🔄 触发响应式更新`)
                  console.log(`[前端] ✅ 新增商品，${eventData.weapon_name} 当前共 ${weaponData.items.length} 个`)
                  console.log(`[前端] 📊 当前 crawlResult.value:`, crawlResult.value)
                  break

                case 'weapon_complete':
                  // 某个饰品查询完成，更新统计信息
                  const completeWeaponId = eventData.weapon_id

                  if (!weaponsMap.has(completeWeaponId)) {
                    weaponsMap.set(completeWeaponId, {
                      weapon_id: completeWeaponId,
                      weapon_name: eventData.weapon_name,
                      total_count: eventData.total_count,
                      lowest_price: eventData.lowest_price,
                      pendant_count: eventData.pendant_count || 0,
                      target_count: eventData.target_count || 0,
                      items: []
                    })
                  } else {
                    const weaponData = weaponsMap.get(completeWeaponId)
                    weaponData.total_count = eventData.total_count
                    weaponData.lowest_price = eventData.lowest_price
                    weaponData.pendant_count = eventData.pendant_count || 0
                  }

                  // 更新显示 - 创建新对象引用
                  crawlResult.value = {
                    weapons: Array.from(weaponsMap.values()).map(w => ({
                      ...w,
                      items: [...w.items]
                    }))
                  }

                  console.log(`饰品 ${eventData.weapon_name} 查询完成`)
                  break

                case 'complete':
                  const totalPendant = Array.from(weaponsMap.values()).reduce((sum, w) => sum + w.pendant_count, 0)
                  const totalTarget = Array.from(weaponsMap.values()).reduce((sum, w) => sum + w.target_count, 0)
                  ElMessage.success(`查询完成！共找到 ${totalPendant} 个挂件饰品，其中 ${totalTarget} 个符合条件`)
                  break

                case 'error':
                  ElMessage.error(eventData.message || '查询出错')
                  break
              }
            } catch (e) {
              console.error(`[前端] ❌ 第 ${i+1} 行解析失败:`, e)
              console.error(`[前端] ❌ 失败的行内容:`, line)
            }
          }
        }
        
        console.log(`[前端] 📊 最终统计: 共收到 ${chunkCount} 个数据块`)
        console.log(`[前端] 📊 最终饰品数量:`, weaponsMap.size)
        weaponsMap.forEach((weapon, id) => {
          console.log(`[前端] 📊   - ${weapon.weapon_name}: ${weapon.items.length} 个商品`)
        })

      } catch (error) {
        console.error('流式查询失败:', error)
        let errorMessage = '查询失败'

        if (error.message) {
          errorMessage = error.message
        }

        crawlResult.value = {
          success: false,
          message: errorMessage
        }
        ElMessage.error(errorMessage)
      } finally {
        isCrawling.value = false
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

    // 平台类型改变处理
    const handlePlatformTypeChange = () => {
      // 实时保存配置
      if (selectedConfigId.value) {
        autoSaveConfig()
      }
    }

    // 自动保存配置
    const autoSaveConfig = async () => {
      if (!crawlForm.value.configName) {
        return
      }

      try {
        // 验证JSON配置
        const jsonValidation = validateJsonConfig()
        if (!jsonValidation.valid) {
          console.log('JSON配置格式错误，跳过自动保存')
          return
        }

        // 构建配置对象
        const valueObj = {
          weapon_id: crawlForm.value.weaponId,
          steam_id: crawlForm.value.steamId
        }

        // 如果有自定义配置，合并进去
        if (jsonValidation.config) {
          Object.assign(valueObj, jsonValidation.config)
        }

        // 根据平台类型设置 key2
        const key2 = crawlForm.value.platformType === 'buff' ? 'buff' : 'youpin'

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
          key1: 'spider_pendant',
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
      
      if (!weaponType) {
        return
      }
      
      isLoadingWeaponNames.value = true
      
      try {
        const response = await axios.get(`${API_CONFIG.BASE_URL}/webSelectWeaponV1/getWeaponNames`, {
          params: {
            weaponType: weaponType
          }
        })
        
        if (response.data.success) {
          weaponNameList.value = response.data.data || []
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
        return
      }
      
      // 如果爬取配置区域是展开状态，不触发自动加载
      if (!isToolSectionCollapsed.value) {
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
        
        console.log('滚动位置检查', {
          scrollTop: Math.round(scrollTop),
          scrollHeight,
          clientHeight,
          distanceToBottom: Math.round(distanceToBottom),
          hasMore: hasMore.value,
          isLoadingMore: isLoadingMore.value,
          currentPage: currentPage.value,
          resultsCount: weaponSearchResults.value.length
        })
        
        // 滚动到底部触发加载更多（距离底部200px时触发）
        if (distanceToBottom < 200 && hasMore.value && !isLoadingMore.value) {
          console.log('✅ 触发加载更多数据')
          loadMoreWeapons()
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
        return row.buff_id
      } else {
        return row.yyyp_id
      }
    }

    // 添加饰品ID到表单
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

    // 一键添加全部饰品ID
    const addAllWeaponIds = async () => {
      if (!weaponSearchResults.value || weaponSearchResults.value.length === 0) {
        ElMessage.warning('没有可添加的饰品')
        return
      }

      try {
        const platformName = crawlForm.value.platformType === 'buff' ? 'BUFF' : '悠悠有品'
        
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
        await ElMessageBox.confirm(
          `确认购买该商品吗？\n\n挂件：${pendantNames}\n价格：¥${item.price}\n磨损：${item.abrade || '-'}\n溢价：+¥${item.spread.toFixed(2)}`,
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
          steamId: crawlForm.value.steamId,
          commodityId: item.id,
          buyQuantity: 1,
          price: item.price,
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
          const paymentAmount = item.price || '未知'
          
          // 检查支付状态
          const payStatus = paymentStatus.payStatus
          let message = ''
          
          if (payStatus === 2) {
            // 支付成功
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

    // 组件挂载时加载数据
    onMounted(() => {
      loadSteamIdList()
      loadConfigList()
      
      // 添加页面滚动监听
      window.addEventListener('scroll', handlePageScroll)
    })

    onUnmounted(() => {
      // 移除页面滚动监听
      window.removeEventListener('scroll', handlePageScroll)
    })

    return {
      crawlFormRef,
      steamIdList,
      isCrawling,
      crawlForm,
      crawlResult,
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
      handleSearchWeapon,
      loadMoreWeapons,
      clearWeaponSearch,
      getWeaponIdByPlatform,
      addWeaponId,
      addAllWeaponIds,
      removeWeaponId,
      clearAllWeaponIds,
      weaponIdList,
      getRowClassName,
      getRarityColor,
      // 购买相关
      buyingItems,
      handleBuyWeapon,
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
      updateHighlight
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

.back-button {
  /* 按钮样式 */
}

.page-layout {
  display: flex;
  gap: 1.5rem;
  min-height: calc(100vh - 150px);
}

/* 左侧配置管理栏 */
.config-sidebar {
  width: 320px;
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

.form-item-half {
  flex: 1;
  margin-bottom: 18px;
}

.form-item-third {
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
  margin: 0;
}

.no-spinner :deep(input[type="number"]) {
  -moz-appearance: textfield;
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
@media (max-width: 1024px) {
  .page-layout {
    flex-direction: column;
  }

  .config-sidebar {
    width: 100%;
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

