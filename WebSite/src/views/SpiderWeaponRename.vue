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
        <div class="search-section">
          <h2 class="section-title">搜索饰品</h2>
        
        <div class="search-container">
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
            <el-button 
              type="text" 
              size="small"
              @click="clearWeaponSearch"
            >
              清除结果
            </el-button>
          </div>
          
          <el-table 
            :data="weaponSearchResults" 
            style="width: 100%"
            max-height="400"
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
            
            <el-table-column label="悠悠有品ID" width="130" align="center">
              <template #default="{ row }">
                <el-tag type="warning" v-if="row.yyyp_id">{{ row.yyyp_id }}</el-tag>
                <span v-else class="no-data">-</span>
              </template>
            </el-table-column>
            
            <el-table-column label="BUFF ID" width="110" align="center">
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
        </div>
        </div>

        <div class="tool-section">
        <h2 class="section-title">爬取配置</h2>
        
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
                >
                  <el-option 
                    v-for="steamId in steamIdList" 
                    :key="steamId.steam_id" 
                    :label="steamId.steam_id" 
                    :value="steamId.steam_id"
                  />
                </el-select>
              </el-form-item>

              <el-form-item label="平台类型" required class="form-item-third">
                <el-select 
                  v-model="crawlForm.platformType" 
                  placeholder="选择平台类型"
                  style="width: 100%;"
                  :disabled="!!selectedConfigId"
                >
                  <el-option label="悠悠有品" value="youpin" />
                  <el-option label="BUFF" value="buff" />
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
              <el-input 
                v-model="crawlForm.customConfig" 
                type="textarea"
                :autosize="{ minRows: 3, maxRows: 20 }"
                clearable
              />
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
        </div>
        <!-- 结束 tool-section-content -->
      </div>
      <!-- 结束 unified-tool-section -->

      <!-- 查询结果区域 -->
      <div v-if="crawlResult && crawlResult.weapons && crawlResult.weapons.length > 0" class="result-section">
        <h2 class="section-title">查询结果</h2>
        
        <!-- 每个饰品的结果 -->
        <div v-for="weapon in crawlResult.weapons" :key="weapon.yyyp_id" class="weapon-result-card">
          <div class="weapon-header">
            <h3 class="weapon-name">{{ weapon.weapon_name }}</h3>
            <div class="weapon-stats">
              <el-tag size="small">总在售: {{ weapon.total_count }}</el-tag>
              <el-tag size="small" type="warning">最低价: ¥{{ weapon.lowest_price }}</el-tag>
              <el-tag size="small" type="info">改名数: {{ weapon.renamed_count }}</el-tag>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, Delete, Refresh, ArrowUp, ArrowDown } from '@element-plus/icons-vue'
import { API_CONFIG } from '@/config/api.js'

export default {
  name: 'SpiderWeaponRename',
  components: {
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
    
    // 配置管理相关
    const savedConfigs = ref([])
    const selectedConfigId = ref(null)

    // 饰品搜索相关
    const weaponSearchKeyword = ref('')
    const weaponSearchResults = ref([])
    const isSearchingWeapon = ref(false)
    
    // 购买相关
    const buyingItems = ref({})
    
    // 工具区域折叠状态
    const isToolSectionCollapsed = ref(false)

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
            crawlForm.value.steamId = steamIdList.value[0].steam_id
          }
        }
      } catch (error) {
        console.error('加载Steam ID列表失败:', error)
        console.error('错误详情:', error.response)
        // 暂时不显示错误提示，避免干扰用户
        // ElMessage.error('加载Steam ID列表失败')
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
        let confirmMessage = `确定要开始查询改名饰品吗？\n\n`
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
          `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/auto_buy_renamed_weapon`,
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
                  const yyypId = eventData.yyyp_id
                  
                  console.log(`[前端] 收到 item 事件:`, eventData)

                  if (!weaponsMap.has(yyypId)) {
                    console.log(`[前端] 创建新饰品条目: ${eventData.weapon_name} (${yyypId})`)
                    weaponsMap.set(yyypId, {
                      yyyp_id: yyypId,
                      weapon_name: eventData.weapon_name,
                      total_count: eventData.total_count,
                      lowest_price: eventData.lowest_price,
                      renamed_count: 0,
                      target_count: 0,
                      items: []
                    })
                  }

                  const weaponData = weaponsMap.get(yyypId)
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
                  console.log(`[前端] ✅ 新增商品: ${eventData.item.nameTag}，${eventData.weapon_name} 当前共 ${weaponData.items.length} 个`)
                  console.log(`[前端] 📊 当前 crawlResult.value:`, crawlResult.value)
                  break

                case 'weapon_complete':
                  // 某个饰品查询完成，更新统计信息
                  const completeYyypId = eventData.yyyp_id

                  if (!weaponsMap.has(completeYyypId)) {
                    weaponsMap.set(completeYyypId, {
                      yyyp_id: completeYyypId,
                      weapon_name: eventData.weapon_name,
                      total_count: eventData.total_count,
                      lowest_price: eventData.lowest_price,
                      renamed_count: eventData.renamed_count || 0,
                      target_count: eventData.target_count || 0,
                      items: []
                    })
                  } else {
                    const weaponData = weaponsMap.get(completeYyypId)
                    weaponData.total_count = eventData.total_count
                    weaponData.lowest_price = eventData.lowest_price
                    weaponData.renamed_count = eventData.renamed_count || 0
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
                  const totalRenamed = Array.from(weaponsMap.values()).reduce((sum, w) => sum + w.renamed_count, 0)
                  const totalTarget = Array.from(weaponsMap.values()).reduce((sum, w) => sum + w.target_count, 0)
                  ElMessage.success(`查询完成！共找到 ${totalRenamed} 个改名饰品，其中 ${totalTarget} 个符合条件`)
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
      crawlForm.value = {
        configName: '',
        steamId: steamIdList.value.length > 0 ? steamIdList.value[0].steam_id : '',
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
        // 只加载 key2 = spider 的配置
        const response = await axios.get(`${API_CONFIG.BASE_URL}/configV1/list`, {
          params: {
            key2: 'spider'
          }
        })
        
        console.log('配置列表响应:', response.data)
        
        // 根据 key1 字段判断平台类型
        savedConfigs.value = (response.data.data || []).map(config => ({
          ...config,
          platformType: config.key1 === 'spider_buff' ? 'buff' : 'youpin'
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

        // 根据平台类型设置 key1
        const key1 = crawlForm.value.platformType === 'buff' ? 'spider_buff' : 'spider_youpin'

        const configData = {
          dataName: crawlForm.value.configName,
          key1: key1,
          key2: 'spider',
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

    // 搜索饰品
    const handleSearchWeapon = async () => {
      if (!weaponSearchKeyword.value.trim()) {
        ElMessage.warning('请输入搜索关键词')
        return
      }

      isSearchingWeapon.value = true
      
      try {
        const response = await axios.get(`${API_CONFIG.BASE_URL}/webSelectWeaponV1/searchWeaponDetail`, {
          params: {
            keyword: weaponSearchKeyword.value.trim()
          }
        })
        
        if (response.data.success) {
          weaponSearchResults.value = response.data.data || []
          
          if (weaponSearchResults.value.length === 0) {
            ElMessage.info('未找到匹配的饰品')
          } else {
            ElMessage.success(`找到 ${weaponSearchResults.value.length} 件饰品`)
          }
        } else {
          ElMessage.error(response.data.message || '搜索失败')
        }
      } catch (error) {
        console.error('搜索饰品失败:', error)
        const errorMessage = error.response?.data?.message || error.message || '搜索饰品失败'
        ElMessage.error(errorMessage)
      } finally {
        isSearchingWeapon.value = false
      }
    }

    // 清除搜索结果
    const clearWeaponSearch = () => {
      weaponSearchResults.value = []
      weaponSearchKeyword.value = ''
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

    // 组件挂载时加载数据
    onMounted(() => {
      loadSteamIdList()
      loadConfigList()
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
      getModeLabel,
      getSourceLabel,
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
      handleSearchWeapon,
      clearWeaponSearch,
      getWeaponIdByPlatform,
      addWeaponId,
      removeWeaponId,
      weaponIdList,
      getRowClassName,
      // 购买相关
      buyingItems,
      handleBuyWeapon,
      // 工具区域折叠
      isToolSectionCollapsed,
      toggleToolSection
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

.weapon-search-input {
  width: 100%;
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
}

.results-title {
  font-size: 1rem;
  font-weight: 600;
  color: #4CAF50;
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

