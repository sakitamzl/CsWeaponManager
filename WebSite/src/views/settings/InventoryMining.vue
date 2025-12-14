<template>
  <div class="inventory-mining-container">
    <div class="mining-section">
      <h2 class="section-title">库存挖掘</h2>
      
      <div class="mining-controls">
        <el-input
          v-model="inputSteamId"
          placeholder="请输入Steam ID (例如: 76561198334278515)"
          class="steam-id-input"
          :disabled="isMining"
          clearable
          @keyup.enter="startMining"
        >
          <template #prepend>Steam ID</template>
        </el-input>
        
        <el-button 
          type="primary" 
          @click="startMining"
          :disabled="!inputSteamId || isMining"
          :loading="isMining"
        >
          {{ isMining ? '挖掘中...' : '开始挖掘' }}
        </el-button>

        <el-button 
          type="success" 
          @click="viewMiningHistory"
          :disabled="isMining"
        >
          查看历史记录
        </el-button>
      </div>

      <div v-if="miningProgress" class="progress-info">
        <div class="progress-item">
          <span class="progress-label">当前进度:</span>
          <el-progress 
            :percentage="miningProgress.percentage" 
            :status="miningProgress.status"
          />
        </div>
        <div class="progress-item">
          <span class="progress-label">已处理:</span>
          <span class="progress-value">{{ miningProgress.processed }} / {{ miningProgress.total }}</span>
        </div>
        <div class="progress-item">
          <span class="progress-label">发现潜力饰品:</span>
          <span class="progress-value highlight">{{ miningProgress.found }}</span>
        </div>
      </div>

      <div v-if="lastMiningTime" class="mining-info">
        <span class="mining-time">最后挖掘时间: {{ lastMiningTime }}</span>
      </div>

      <div v-if="miningResult" class="result-section">
        <h3 class="result-title">挖掘结果</h3>
        <div class="result-stats">
          <div class="stat-card">
            <div class="stat-label">总物品数</div>
            <div class="stat-value">{{ miningResult.total_analyzed }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">总价值</div>
            <div class="stat-value success">¥{{ miningResult.total_value || 0 }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">我的价值</div>
            <div class="stat-value highlight">¥{{ miningResult.self_value || 0 }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">好友价值</div>
            <div class="stat-value">¥{{ miningResult.friends_value || 0 }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 用户树形图 -->
    <div v-if="userTreeData.length > 0" class="user-tree-section">
      <h3 class="section-title">用户库存分布</h3>
      <el-tree
        :data="userTreeData"
        :props="treeProps"
        default-expand-all
        class="user-tree"
        node-key="id"
      >
        <template #default="{ node, data }">
          <div class="tree-node">
            <div class="tree-node-content">
              <img v-if="data.avatar" :src="data.avatar" class="tree-avatar" />
              <el-icon v-else :size="24" class="tree-icon">
                <User />
              </el-icon>
              <span class="tree-label">{{ data.label }}</span>
              <el-tag :type="data.type" size="small" class="tree-tag">
                {{ data.count }} 件
              </el-tag>
              <el-tag v-if="data.value && data.value !== '0.00'" type="success" size="small" class="tree-tag">
                ¥{{ data.value }}
              </el-tag>
            </div>
          </div>
        </template>
      </el-tree>
    </div>

    <!-- 挖掘结果展示 -->
    <div v-if="miningItems.length > 0" class="results-table-section">
      <div class="section-header">
        <h3 class="section-title">物品列表</h3>
        <el-switch
          v-model="groupMode"
          active-text="组合模式"
          inactive-text="明细模式"
          @change="handleToggleGroupMode"
        />
      </div>
      
      <div class="table-filters">
        <el-select v-model="selectedUser" placeholder="筛选用户" clearable @change="filterByUser">
          <el-option label="全部用户" value="" />
          <el-option
            v-for="user in userList"
            :key="user.steam_id"
            :label="`${user.name} (${user.count}件)`"
            :value="user.steam_id"
          />
        </el-select>
        <el-select v-model="selectedWeaponType" placeholder="筛选武器类型" clearable @change="filterByWeaponType">
          <el-option label="全部类型" value="" />
          <el-option
            v-for="type in weaponTypes"
            :key="type"
            :label="type"
            :value="type"
          />
        </el-select>
      </div>

      <!-- 表格视图 -->
      <el-table
        ref="tableRef"
        :data="currentDisplayData"
        style="width: 100%"
        :header-row-style="{ backgroundColor: 'var(--bg-tertiary)' }"
        height="500"
        @row-click="handleRowClick"
        :row-key="row => row.steam_hash_name || row.assetid"
      >
        <el-table-column v-if="groupMode" type="expand" width="1">
          <template #default="scope">
            <div class="expand-content" v-if="scope.row.item_count > 1">
              <div class="expand-two-columns">
                <div 
                  v-for="(item, index) in getExpandedItems(scope.row)" 
                  :key="item.assetid"
                  class="expand-item-card"
                >
                  <div class="expand-item-row">
                    <div class="expand-item-left">
                      <div class="expand-item-image">
                        <img
                          v-if="getWeaponImage(scope.row.steam_hash_name)"
                          :src="getWeaponImage(scope.row.steam_hash_name)"
                          :alt="scope.row.item_name"
                          class="weapon-img-small"
                          @error="(e) => e.target.style.display = 'none'"
                        />
                        <span v-else class="no-image">无图</span>
                        
                        <!-- 贴纸覆盖层 -->
                        <div v-if="item.sticker" class="sticker-overlay-expand">
                          <div
                            v-for="(sticker, sIdx) in parseStickers(item.sticker)"
                            :key="sIdx"
                            class="sticker-item-overlay-expand"
                            :title="sticker.name || '未知贴纸'"
                          >
                            <img
                              v-if="sticker.image"
                              :src="sticker.image"
                              :alt="sticker.name"
                              class="sticker-img-overlay"
                              @error="(e) => e.target.style.display = 'none'"
                            />
                            <div v-else class="sticker-placeholder-overlay">?</div>
                          </div>
                        </div>
                        
                        <!-- 挂件覆盖层 -->
                        <div v-if="item.pendant" class="pendant-overlay-expand">
                          <div
                            class="pendant-item-overlay-expand"
                            :title="parsePendant(item.pendant).name || '挂件'"
                          >
                            <img
                              v-if="parsePendant(item.pendant).image"
                              :src="parsePendant(item.pendant).image"
                              :alt="parsePendant(item.pendant).name"
                              class="pendant-img-overlay"
                              @error="(e) => e.target.style.display = 'none'"
                            />
                            <div v-else class="pendant-placeholder-overlay">🎗️</div>
                          </div>
                        </div>
                      </div>
                      <!-- 改名标签 -->
                      <div v-if="item.rename" class="expand-rename-tag">
                        <el-tag type="info" size="small" :title="item.rename">
                          🏷️
                        </el-tag>
                      </div>
                    </div>
                    <div class="expand-item-details">
                      <div class="expand-item-user">
                        <span class="expand-label">用户:</span>
                        <span class="expand-value">{{ item.persona_name }}</span>
                      </div>
                      <div class="expand-item-float" v-if="item.weapon_float && item.weapon_float !== '0' && item.weapon_float !== '0.0'">
                        <div class="float-text-row">
                          <span class="expand-label">磨损:</span>
                          <span class="expand-value-small">{{ item.weapon_float }}</span>
                        </div>
                        <div class="float-bar-mini">
                          <div class="float-segment fn"></div>
                          <div class="float-segment mw"></div>
                          <div class="float-segment ft"></div>
                          <div class="float-segment ww"></div>
                          <div class="float-segment bs"></div>
                          <div
                            class="float-pointer"
                            :style="{ left: `${parseFloat(item.weapon_float) * 100}%` }"
                          ></div>
                        </div>
                      </div>
                      <div class="expand-item-prices">
                        <div class="expand-price-item" v-if="item.market_price && item.market_price !== '0'">
                          <span class="expand-label">价格:</span>
                          <span class="expand-value">¥{{ parseFloat(item.market_price).toFixed(2) }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <!-- 分页器 -->
              <div v-if="getExpandedTotal(scope.row) > getItemsPerPage()" class="inline-pagination-below" @click.stop>
                <el-pagination
                  small
                  :current-page="expandedRowPages[scope.row.steam_hash_name] || 1"
                  :page-size="getItemsPerPage()"
                  :total="getExpandedTotal(scope.row)"
                  layout="prev, pager, next"
                  :hide-on-single-page="true"
                  @current-change="(page) => handleExpandPageChange(scope.row, page)"
                />
              </div>
            </div>
            <div v-else class="expand-content-empty">
              <span style="color: #999;">仅有1件物品，无需展开</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="图片" width="144" align="center" fixed="left">
          <template #default="scope">
            <div class="weapon-image-cell">
              <img
                v-if="getWeaponImage(scope.row.steam_hash_name)"
                :src="getWeaponImage(scope.row.steam_hash_name)"
                :alt="scope.row.item_name"
                class="weapon-img"
                @error="(e) => e.target.style.display = 'none'"
              />
              <span v-else class="no-image">无图</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="饰品名称" min-width="250" fixed="left">
          <template #default="scope">
            <div class="item-name-cell">
              <div class="item-title">{{ getItemTitle(scope.row) }}</div>
              <div class="item-extras" v-if="hasExtras(scope.row)">
                <!-- 印花图片 -->
                <div class="sticker-list" v-if="scope.row.sticker || (scope.row.stickers && scope.row.stickers[0])">
                  <div
                    v-for="(sticker, idx) in parseStickers(scope.row.sticker || scope.row.stickers[0])"
                    :key="idx"
                    class="sticker-item"
                    :title="sticker.name || '未知贴纸'"
                  >
                    <img
                      v-if="sticker.image"
                      :src="sticker.image"
                      :alt="sticker.name"
                      class="sticker-img"
                      @error="(e) => e.target.style.display = 'none'"
                    />
                    <div v-else class="sticker-placeholder">?</div>
                  </div>
                </div>
                <!-- 挂件图片 -->
                <div class="pendant-list" v-if="scope.row.pendant || (scope.row.pendants && scope.row.pendants[0])">
                  <img
                    v-if="parsePendant(scope.row.pendant || scope.row.pendants[0])?.image"
                    :src="parsePendant(scope.row.pendant || scope.row.pendants[0]).image"
                    :alt="parsePendant(scope.row.pendant || scope.row.pendants[0])?.name"
                    class="pendant-img"
                    @error="(e) => e.target.style.display = 'none'"
                  />
                </div>
                <!-- 改名显示 -->
                <div class="rename-text" v-if="scope.row.rename || (scope.row.renames && scope.row.renames[0])">
                  <span class="rename-value">{{ scope.row.rename || scope.row.renames[0] }}</span>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="weapon_type" label="武器类型" min-width="120" />
        
        <el-table-column v-if="!groupMode" prop="persona_name" label="所属用户" width="150" />
        
        <el-table-column label="数量" width="120" align="center">
          <template #default="scope">
            <span>{{ groupMode ? (scope.row.item_count || 0) : 1 }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="weapon_float" label="磨损值" width="200" align="left">
          <template #default="scope">
            <div v-if="groupMode && scope.row.item_count > 1" style="color: #888;">
              多个磨损值
            </div>
            <div v-else-if="scope.row.weapon_float && scope.row.weapon_float !== '0' && scope.row.weapon_float !== '0.0'">
              <div style="font-family: monospace; font-size: 0.85rem; margin-bottom: 4px;">
                {{ scope.row.weapon_float }}
              </div>
              <div class="float-bar">
                <div class="float-segment fn"></div>
                <div class="float-segment mw"></div>
                <div class="float-segment ft"></div>
                <div class="float-segment ww"></div>
                <div class="float-segment bs"></div>
                <div
                  class="float-pointer"
                  :style="{ left: `${parseFloat(scope.row.weapon_float) * 100}%` }"
                ></div>
              </div>
            </div>
            <span v-else style="color: #888;">N/A</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="float_range" label="磨损范围" min-width="120" />
        
        <el-table-column label="价格" min-width="150">
          <template #default="scope">
            <span v-if="groupMode && scope.row.total_value" style="color: #4CAF50; font-weight: bold;">
              ¥{{ scope.row.total_value.toFixed(2) }}
            </span>
            <span v-else-if="scope.row.market_price && scope.row.market_price !== '0'" style="color: #4CAF50; font-weight: bold;">
              ¥{{ parseFloat(scope.row.market_price).toFixed(2) }}
            </span>
            <span v-else style="color: #888;">-</span>
          </template>
        </el-table-column>
        
        <el-table-column v-if="!groupMode" prop="rarity" label="稀有度" width="120">
          <template #default="scope">
            <el-tag v-if="scope.row.rarity" size="small">{{ scope.row.rarity }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column v-if="!groupMode" prop="tradable" label="可交易" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.tradable ? 'success' : 'danger'" size="small">
              {{ scope.row.tradable ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script>
import { ref, computed, onUnmounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User } from '@element-plus/icons-vue'
import { API_CONFIG } from '@/config/api.js'

export default {
  name: 'InventoryMining',
  components: {
    User
  },
  setup() {
    const inputSteamId = ref('')
    const isMining = ref(false)
    const miningProgress = ref(null)
    const lastMiningTime = ref('')
    const miningResult = ref(null)
    const miningItems = ref([])
    const userTreeData = ref([])
    const selectedUser = ref('')
    const selectedWeaponType = ref('')
    const pollingTimer = ref(null)
    const currentMiningId = ref('')
    const groupMode = ref(true)  // 默认组合模式
    const groupedData = ref([])  // 组合后的数据
    const expandedRowPages = ref({})  // 展开行的分页状态
    const tableRef = ref(null)
    
    // Tree组件配置
    const treeProps = {
      children: 'children',
      label: 'label'
    }

    // 开始挖掘
    const startMining = async () => {
      // 验证Steam ID格式
      const steamId = inputSteamId.value.trim()
      if (!steamId) {
        ElMessage.warning('请输入 Steam ID')
        return
      }

      // 验证Steam ID格式（17位数字）
      if (!/^\d{17}$/.test(steamId)) {
        ElMessage.warning('Steam ID 格式不正确，应为17位数字')
        return
      }

      try {
        await ElMessageBox.confirm(
          `确定要开始挖掘 Steam ID: ${steamId} 及其好友的库存吗？\n\n⚠️ 注意：此操作将清空该Steam ID的历史挖掘数据！\n\n此操作将访问公开库存数据，可能需要几分钟时间。`,
          '确认挖掘',
          {
            confirmButtonText: '开始',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
      } catch {
        return
      }

      isMining.value = true
      currentMiningId.value = steamId
      miningProgress.value = {
        percentage: 0,
        processed: 0,
        total: 100,
        found: 0,
        status: 'success'
      }
      ElMessage.info('开始挖掘库存...')

      // 启动实时轮询更新
      startPolling(steamId)

      try {
        // 调用Spider的挖掘接口（异步执行）
        const response = await axios.post(`${API_CONFIG.SPIDER_BASE_URL}/steamSpiderV1/mineInventory`, {
          steamId: steamId,
          include_friends: true,
          max_friends: 10
        })

        if (response.data.success) {
          const data = response.data.data
          miningResult.value = {
            total_analyzed: data.total_items,
            potential_items: data.total_items,
            estimated_profit: 0,
            total_value: 0,
            self_value: 0,
            friends_value: 0
          }
          lastMiningTime.value = new Date().toLocaleString('zh-CN')
          
          miningProgress.value = {
            percentage: 100,
            processed: data.total_items,
            total: data.total_items,
            found: data.total_items,
            status: 'success'
          }
          
          // 最后一次加载完整数据
          await loadMiningResults(steamId)
          await loadMiningStats(steamId)
          
          ElMessage.success(`挖掘完成！共挖掘 ${data.total_users} 个用户，获取 ${data.total_items} 件物品`)
        } else {
          ElMessage.error(`挖掘失败: ${response.data.message}`)
          miningProgress.value.status = 'exception'
        }
      } catch (error) {
        console.error('挖掘失败:', error)
        miningProgress.value.status = 'exception'
        
        let errorMessage = '挖掘失败'
        if (error.response) {
          errorMessage = error.response.data?.message || errorMessage
        } else if (error.request) {
          errorMessage = '无法连接到服务器'
        }
        ElMessage.error(errorMessage)
      } finally {
        isMining.value = false
        stopPolling()
      }
    }
    
    // 启动轮询
    const startPolling = (steamId) => {
      // 清除之前的定时器
      stopPolling()
      
      // 立即执行一次
      pollMiningData(steamId)
      
      // 每2秒轮询一次
      pollingTimer.value = setInterval(() => {
        pollMiningData(steamId)
      }, 2000)
    }
    
    // 停止轮询
    const stopPolling = () => {
      if (pollingTimer.value) {
        clearInterval(pollingTimer.value)
        pollingTimer.value = null
      }
    }
    
    // 轮询挖掘数据
    const pollMiningData = async (steamId) => {
      try {
        // 同时获取数据和统计信息
        const [dataResponse, statsResponse] = await Promise.all([
          axios.post(`${API_CONFIG.BASE_URL}/api/v1/steam/inventory/mining/query`, {
            source_steam_id: steamId,
            limit: 1000,
            offset: 0
          }),
          axios.post(`${API_CONFIG.BASE_URL}/api/v1/steam/inventory/mining/stats`, {
            source_steam_id: steamId
          })
        ])

        if (dataResponse.data.success) {
          const items = dataResponse.data.data.items || []
          miningItems.value = items
          
          // 更新进度
          if (isMining.value && items.length > 0) {
            miningProgress.value.processed = items.length
            miningProgress.value.found = items.length
            // 估算进度（假设最多500件物品）
            miningProgress.value.percentage = Math.min(95, Math.floor((items.length / 500) * 100))
          }
          
          // 构建用户树形数据
          buildUserTree(items, steamId)
        }
        
        if (statsResponse.data.success) {
          const stats = statsResponse.data.data
          // 更新统计信息
          if (miningResult.value) {
            miningResult.value.total_analyzed = stats.total_items
            miningResult.value.total_value = stats.total_value
            miningResult.value.self_value = stats.self_value
            miningResult.value.friends_value = stats.friends_value
          } else {
            miningResult.value = {
              total_analyzed: stats.total_items,
              potential_items: stats.total_items,
              estimated_profit: 0,
              total_value: stats.total_value,
              self_value: stats.self_value,
              friends_value: stats.friends_value
            }
          }
        }
      } catch (error) {
        console.error('轮询数据失败:', error)
      }
    }

    // 加载挖掘结果
    const loadMiningResults = async (steamId) => {
      try {
        const response = await axios.post(`${API_CONFIG.BASE_URL}/api/v1/steam/inventory/mining/query`, {
          source_steam_id: steamId,
          limit: 1000,
          offset: 0
        })

        if (response.data.success) {
          const items = response.data.data.items || []
          miningItems.value = items
          
          // 构建用户树形数据
          buildUserTree(items, steamId)
        }
      } catch (error) {
        console.error('加载挖掘结果失败:', error)
      }
    }
    
    // 加载挖掘统计信息
    const loadMiningStats = async (steamId) => {
      try {
        const response = await axios.post(`${API_CONFIG.BASE_URL}/api/v1/steam/inventory/mining/stats`, {
          source_steam_id: steamId
        })

        if (response.data.success) {
          const stats = response.data.data
          // 更新结果统计
          if (miningResult.value) {
            miningResult.value.total_value = stats.total_value
            miningResult.value.self_value = stats.self_value
            miningResult.value.friends_value = stats.friends_value
          }
        }
      } catch (error) {
        console.error('加载统计信息失败:', error)
      }
    }
    
    // 构建用户树形数据（包含价值信息）
    const buildUserTree = (items, sourceSteamId) => {
      // 按用户分组并计算价值
      const userMap = new Map()
      
      items.forEach(item => {
        const steamId = item.target_steam_id
        if (!userMap.has(steamId)) {
          userMap.set(steamId, {
            steam_id: steamId,
            persona_name: item.persona_name || `用户_${steamId.slice(-4)}`,
            avatar_url: item.avatar_url,
            relationship: item.relationship,
            items: [],
            total_value: 0
          })
        }
        const user = userMap.get(steamId)
        user.items.push(item)
        
        // 累加价值
        if (item.market_price && item.market_price !== '0') {
          user.total_value += parseFloat(item.market_price)
        }
      })
      
      // 构建树形结构
      const treeData = []
      
      // 计算总价值
      let totalValue = 0
      items.forEach(item => {
        if (item.market_price && item.market_price !== '0') {
          totalValue += parseFloat(item.market_price)
        }
      })
      
      // 根节点
      const rootNode = {
        id: 'root',
        label: `Steam ID: ${sourceSteamId}`,
        count: items.length,
        value: totalValue.toFixed(2),
        type: 'primary',
        children: []
      }
      
      // 自己的库存
      const selfUsers = Array.from(userMap.values()).filter(u => u.relationship === 'self')
      if (selfUsers.length > 0) {
        selfUsers.forEach(user => {
          rootNode.children.push({
            id: `self_${user.steam_id}`,
            label: `我的库存 (${user.persona_name})`,
            count: user.items.length,
            value: user.total_value.toFixed(2),
            avatar: user.avatar_url,
            type: 'success',
            steam_id: user.steam_id
          })
        })
      }
      
      // 好友的库存
      const friendUsers = Array.from(userMap.values()).filter(u => u.relationship === 'friend')
      if (friendUsers.length > 0) {
        const friendsTotalValue = friendUsers.reduce((sum, u) => sum + u.total_value, 0)
        const friendsNode = {
          id: 'friends',
          label: `好友库存 (${friendUsers.length}人)`,
          count: friendUsers.reduce((sum, u) => sum + u.items.length, 0),
          value: friendsTotalValue.toFixed(2),
          type: 'info',
          children: []
        }
        
        // 按价值排序好友
        friendUsers.sort((a, b) => b.total_value - a.total_value)
        
        friendUsers.forEach(user => {
          friendsNode.children.push({
            id: `friend_${user.steam_id}`,
            label: user.persona_name,
            count: user.items.length,
            value: user.total_value.toFixed(2),
            avatar: user.avatar_url,
            type: 'warning',
            steam_id: user.steam_id
          })
        })
        
        rootNode.children.push(friendsNode)
      }
      
      userTreeData.value = [rootNode]
    }
    
    // 用户列表（用于筛选）
    const userList = computed(() => {
      const users = new Map()
      miningItems.value.forEach(item => {
        const steamId = item.target_steam_id
        if (!users.has(steamId)) {
          users.set(steamId, {
            steam_id: steamId,
            name: item.persona_name || `用户_${steamId.slice(-4)}`,
            count: 0
          })
        }
        users.get(steamId).count++
      })
      return Array.from(users.values())
    })
    
    // 武器类型列表（用于筛选）
    const weaponTypes = computed(() => {
      const types = new Set()
      miningItems.value.forEach(item => {
        if (item.weapon_type) {
          types.add(item.weapon_type)
        }
      })
      return Array.from(types)
    })
    
    // 筛选后的物品列表
    const filteredItems = computed(() => {
      let items = miningItems.value
      
      if (selectedUser.value) {
        items = items.filter(item => item.target_steam_id === selectedUser.value)
      }
      
      if (selectedWeaponType.value) {
        items = items.filter(item => item.weapon_type === selectedWeaponType.value)
      }
      
      // 更新组合数据
      if (groupMode.value) {
        groupedData.value = groupItemsByHashName(items)
      }
      
      return items
    })
    
    // 按用户筛选
    const filterByUser = () => {
      // 筛选逻辑已在 computed 中处理，会自动触发更新
    }
    
    // 按武器类型筛选
    const filterByWeaponType = () => {
      // 筛选逻辑已在 computed 中处理，会自动触发更新
    }

    // 查看历史记录
    const viewMiningHistory = () => {
      if (!inputSteamId.value.trim()) {
        ElMessage.warning('请先输入 Steam ID')
        return
      }
      ElMessage.info('历史记录功能开发中...')
    }

    // 获取建议类型
    const getRecommendationType = (recommendation) => {
      const typeMap = {
        '持有': 'info',
        '出售': 'success',
        '观察': 'warning',
        '谨慎': 'danger'
      }
      return typeMap[recommendation] || 'info'
    }

    // 获取武器图片
    const getWeaponImage = (steamHashName) => {
      if (!steamHashName) {
        return null
      }
      const imageName = steamHashName
        .replace(/\s*\|\s*/g, '___')
        .replace(/\s/g, '_')
        + '.png'
      return `${API_CONFIG.BASE_URL}/weapon_imgs/${imageName}`
    }
    
    // 组合数据 - 按steam_hash_name分组
    const groupItemsByHashName = (items) => {
      const grouped = new Map()
      
      items.forEach(item => {
        const key = item.steam_hash_name || item.item_name
        if (!grouped.has(key)) {
          grouped.set(key, {
            steam_hash_name: item.steam_hash_name,
            item_name: item.item_name,
            weapon_name: item.weapon_name,
            weapon_type: item.weapon_type,
            float_range: item.float_range,
            item_count: 0,
            items: [],
            assetids: [],
            weapon_floats: [],
            market_prices: [],
            stickers: [],
            pendants: [],
            renames: [],
            rarities: [],
            tradables: [],
            persona_names: [],
            total_value: 0
          })
        }
        
        const group = grouped.get(key)
        group.item_count++
        group.items.push(item)
        group.assetids.push(item.assetid)
        group.weapon_floats.push(item.weapon_float)
        group.market_prices.push(item.market_price)
        group.stickers.push(item.sticker)
        group.pendants.push(item.pendant)
        group.renames.push(item.rename)
        group.rarities.push(item.rarity)
        group.tradables.push(item.tradable)
        group.persona_names.push(item.persona_name)
        
        if (item.market_price && item.market_price !== '0') {
          group.total_value += parseFloat(item.market_price)
        }
      })
      
      return Array.from(grouped.values())
    }
    
    // 当数据更新时，重新组合
    const updateGroupedData = () => {
      if (groupMode.value) {
        groupedData.value = groupItemsByHashName(filteredItems.value)
      }
    }
    
    // 切换组合模式
    const handleToggleGroupMode = () => {
      if (groupMode.value) {
        updateGroupedData()
      }
    }
    
    // 当前显示的数据
    const currentDisplayData = computed(() => {
      return groupMode.value ? groupedData.value : filteredItems.value
    })
    
    // 获取展开行的详细数据（带分页）
    const getExpandedItems = (row) => {
      if (!row.items || !Array.isArray(row.items)) {
        return []
      }

      const currentPage = expandedRowPages.value[row.steam_hash_name] || 1
      const itemsPerPage = 10
      const totalPages = Math.ceil(row.items.length / itemsPerPage)
      
      if (currentPage > totalPages && totalPages > 0) {
        expandedRowPages.value = {
          ...expandedRowPages.value,
          [row.steam_hash_name]: 1
        }
        return row.items.slice(0, itemsPerPage)
      }
      
      const start = (currentPage - 1) * itemsPerPage
      const end = start + itemsPerPage
      
      return row.items.slice(start, end)
    }

    // 获取展开行的总数据量
    const getExpandedTotal = (row) => {
      if (!row.items || !Array.isArray(row.items)) {
        return 0
      }
      return row.items.length
    }
    
    // 每页显示数量
    const getItemsPerPage = () => {
      return 10
    }

    // 处理展开行的分页变化
    const handleExpandPageChange = (row, page) => {
      expandedRowPages.value = {
        ...expandedRowPages.value,
        [row.steam_hash_name]: page
      }
      
      if (tableRef.value) {
        const expandedRows = tableRef.value.store.states.expandRows.value || []
        const isExpanded = expandedRows.some(r => r.steam_hash_name === row.steam_hash_name)
        
        if (!isExpanded) {
          tableRef.value.toggleRowExpansion(row, true)
        }
      }
    }

    // 处理行点击事件
    const handleRowClick = (row, column, event) => {
      if (!groupMode.value) return
      if (row.item_count <= 1) return
      
      if (tableRef.value) {
        tableRef.value.toggleRowExpansion(row)
      }
    }
    
    // 获取物品标题
    const getItemTitle = (item) => {
      const weaponName = (item.weapon_name || '').trim()
      const itemName = (item.item_name || '').trim()
      const parts = []

      if (weaponName && itemName) {
        if (weaponName === itemName) {
          parts.push(itemName)
        } else {
          parts.push(weaponName)
          parts.push(itemName)
        }
      } else if (weaponName) {
        parts.push(weaponName)
      } else if (itemName) {
        parts.push(itemName)
      }

      let title = parts.join(' | ')
      if (item.float_range) {
        title += ` （${item.float_range}）`
      }
      return title
    }
    
    // 检查是否有额外信息
    const hasExtras = (item) => {
      return !!(item.sticker || item.pendant || item.rename)
    }
    
    // 解析印花数据
    const parseStickers = (stickerData) => {
      if (!stickerData) return []
      try {
        const parsed = typeof stickerData === 'string' ? JSON.parse(stickerData) : stickerData
        if (!Array.isArray(parsed)) return []

        return parsed.map(sticker => {
          const name = sticker.name || '未知贴纸'
          const hashName = sticker.hashName || sticker.steam_hash_name || sticker.steamHashName

          let imageUrl = null
          if (hashName) {
            const imageName = hashName
              .replace(/\s*\|\s*/g, '___')
              .replace(/\s/g, '_')
            imageUrl = `${API_CONFIG.BASE_URL}/weapon_imgs/Sticker___${imageName}.png`
          }

          return {
            name: name,
            image: imageUrl
          }
        })
      } catch (e) {
        console.error('解析印花数据失败:', e)
        return []
      }
    }

    // 解析挂件数据
    const parsePendant = (pendantData) => {
      if (!pendantData) return null
      try {
        const parsed = typeof pendantData === 'string' ? JSON.parse(pendantData) : pendantData
        let pendantObj = Array.isArray(parsed) ? parsed[0] : parsed

        if (!pendantObj || typeof pendantObj !== 'object') return null

        const hashName = pendantObj.hashName || pendantObj.steam_hash_name || pendantObj.steamHashName

        let imageUrl = null
        if (hashName) {
          const imageName = hashName
            .replace(/\s*\|\s*/g, '___')
            .replace(/\s/g, '_')
            + '.png'
          imageUrl = `${API_CONFIG.BASE_URL}/weapon_imgs/${imageName}`
        }

        return {
          name: pendantObj.name || '挂件',
          image: imageUrl
        }
      } catch (e) {
        console.error('解析挂件数据失败:', e)
        return null
      }
    }

    // 组件卸载时清理定时器
    onUnmounted(() => {
      stopPolling()
    })

    return {
      inputSteamId,
      isMining,
      miningProgress,
      lastMiningTime,
      miningResult,
      miningItems,
      userTreeData,
      treeProps,
      selectedUser,
      selectedWeaponType,
      userList,
      weaponTypes,
      filteredItems,
      groupMode,
      groupedData,
      currentDisplayData,
      expandedRowPages,
      tableRef,
      startMining,
      viewMiningHistory,
      getRecommendationType,
      filterByUser,
      filterByWeaponType,
      getWeaponImage,
      handleToggleGroupMode,
      getExpandedItems,
      getExpandedTotal,
      getItemsPerPage,
      handleExpandPageChange,
      handleRowClick,
      getItemTitle,
      hasExtras,
      parseStickers,
      parsePendant
    }
  }
}
</script>

<style scoped>
.inventory-mining-container {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.mining-section {
  background: linear-gradient(135deg, rgba(26, 26, 26, 0.98) 0%, rgba(35, 35, 35, 0.95) 100%);
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  border: 1px solid rgba(58, 58, 58, 0.8);
}

.section-title {
  font-size: 1.5rem;
  color: #ffffff;
  margin: 0 0 1.5rem 0;
  font-weight: 600;
}

.mining-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}

.steam-id-input {
  min-width: 400px;
  max-width: 500px;
}

.progress-info {
  background: rgba(45, 45, 45, 0.6);
  border-radius: 8px;
  padding: 1.5rem;
  margin-top: 1.5rem;
}

.progress-item {
  margin-bottom: 1rem;
}

.progress-item:last-child {
  margin-bottom: 0;
}

.progress-label {
  display: block;
  color: #b0b0b0;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.progress-value {
  color: #ffffff;
  font-size: 1.1rem;
  font-weight: 600;
}

.progress-value.highlight {
  color: #409eff;
  font-size: 1.3rem;
}

.mining-info {
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  background: rgba(64, 158, 255, 0.1);
  border-radius: 6px;
  border-left: 3px solid #409eff;
}

.mining-time {
  color: #b0b0b0;
  font-size: 0.9rem;
}

.result-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(58, 58, 58, 0.8);
}

.result-title {
  font-size: 1.2rem;
  color: #ffffff;
  margin: 0 0 1rem 0;
  font-weight: 600;
}

.result-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.stat-card {
  background: rgba(45, 45, 45, 0.6);
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
  border: 1px solid rgba(58, 58, 58, 0.6);
}

.stat-label {
  color: #b0b0b0;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.stat-value {
  color: #ffffff;
  font-size: 1.8rem;
  font-weight: 700;
}

.stat-value.highlight {
  color: #409eff;
}

.stat-value.success {
  color: #4CAF50;
}

.results-table-section {
  background: linear-gradient(135deg, rgba(26, 26, 26, 0.98) 0%, rgba(35, 35, 35, 0.95) 100%);
  border-radius: 12px;
  padding: 2rem;
  border: 1px solid rgba(58, 58, 58, 0.8);
}

.user-tree-section {
  background: linear-gradient(135deg, rgba(26, 26, 26, 0.98) 0%, rgba(35, 35, 35, 0.95) 100%);
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  border: 1px solid rgba(58, 58, 58, 0.8);
}

.user-tree {
  background: transparent;
  color: #ffffff;
  margin-top: 1rem;
}

.tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0;
}

.tree-node-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.tree-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid rgba(64, 158, 255, 0.3);
}

.tree-icon {
  color: #409eff;
}

.tree-label {
  color: #ffffff;
  font-size: 1rem;
  font-weight: 500;
}

.tree-tag {
  margin-left: 0.5rem;
}

.table-filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

/* 卡片视图样式 */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
  padding: 1rem 0;
}

.item-card {
  background: linear-gradient(135deg, rgba(45, 45, 45, 0.8) 0%, rgba(35, 35, 35, 0.9) 100%);
  border: 1px solid rgba(58, 58, 58, 0.8);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
  display: flex;
  flex-direction: column;
}

.item-card:hover {
  transform: translateY(-4px);
  border-color: rgba(76, 175, 80, 0.6);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}

.item-card-image {
  width: 100%;
  height: 180px;
  background: linear-gradient(135deg, rgba(26, 26, 26, 0.95) 0%, rgba(35, 35, 35, 0.9) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  border-bottom: 1px solid rgba(58, 58, 58, 0.6);
  position: relative;
}

.card-weapon-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.3));
}

.no-image-card {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 0.9rem;
}

.item-card-content {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  flex: 1;
}

.item-card-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #ffffff;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  min-height: 2.8em;
}

.item-card-info {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
}

.item-card-price {
  padding: 0.75rem;
  background: rgba(76, 175, 80, 0.1);
  border-radius: 6px;
  text-align: center;
  border: 1px solid rgba(76, 175, 80, 0.3);
}

.price-value {
  font-size: 1.2rem;
  font-weight: 700;
  color: #4CAF50;
}

.price-empty {
  font-size: 0.9rem;
  color: #888;
}

.item-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid rgba(58, 58, 58, 0.6);
  margin-top: auto;
}

/* 列表视图图片样式 */
.table-weapon-img {
  max-width: 80px;
  max-height: 60px;
  object-fit: contain;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.no-image-small {
  color: #666;
  font-size: 0.8rem;
}

/* 表格样式 */
.weapon-image-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
}

.weapon-img {
  max-width: 120px;
  max-height: 80px;
  object-fit: contain;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.no-image {
  color: #666;
  font-size: 0.85rem;
}

.item-name-cell {
  padding: 0.5rem 0;
}

.item-title {
  font-size: 0.95rem;
  font-weight: 500;
  color: #ffffff;
  margin-bottom: 0.5rem;
}

.item-extras {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}

.sticker-list {
  display: flex;
  gap: 0.25rem;
}

.sticker-item {
  width: 24px;
  height: 24px;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 3px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.sticker-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.sticker-placeholder {
  color: #999;
  font-size: 0.7rem;
}

.pendant-list {
  display: flex;
}

.pendant-img {
  width: 24px;
  height: 24px;
  object-fit: contain;
  border-radius: 3px;
  border: 1px solid rgba(255, 215, 0, 0.3);
}

.rename-text {
  font-size: 0.85rem;
  color: #409eff;
}

.rename-value {
  font-style: italic;
}

/* 展开行样式 */
:deep(.el-table__expand-column .cell) {
  display: none;
}

:deep(.el-table__expand-column) {
  width: 1px !important;
  padding: 0 !important;
}

:deep(.el-table__body-wrapper .el-table__row[style*="cursor: pointer"]:hover) {
  background-color: rgba(76, 175, 80, 0.1) !important;
}

.expand-content {
  padding: 1rem;
  background-color: var(--bg-secondary) !important;
}

.expand-two-columns {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.expand-item-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 0.75rem;
  transition: all 0.2s ease;
  cursor: pointer;
}

.expand-item-card:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(76, 175, 80, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.expand-item-row {
  display: flex;
  gap: 0.75rem;
}

.expand-item-left {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: center;
}

.expand-item-image {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border-radius: 4px;
  position: relative;
  overflow: visible;
}

.weapon-img-small {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.sticker-overlay-expand {
  position: absolute;
  bottom: 2px;
  left: 2px;
  display: flex;
  gap: 2px;
  z-index: 5;
  pointer-events: none;
}

.sticker-item-overlay-expand {
  position: relative;
  width: 16px;
  height: 16px;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  border-radius: 2px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
  transition: all 0.2s ease;
  pointer-events: auto;
  cursor: pointer;
}

.sticker-item-overlay-expand:hover {
  transform: scale(2);
  z-index: 10;
  border-color: rgba(76, 175, 80, 0.8);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.7);
}

.pendant-overlay-expand {
  position: absolute;
  top: 2px;
  right: 2px;
  z-index: 5;
  pointer-events: none;
}

.pendant-item-overlay-expand {
  position: relative;
  width: 18px;
  height: 18px;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  border-radius: 2px;
  overflow: hidden;
  border: 1px solid rgba(255, 215, 0, 0.4);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
  transition: all 0.2s ease;
  pointer-events: auto;
  cursor: pointer;
}

.pendant-item-overlay-expand:hover {
  transform: scale(2);
  z-index: 10;
  border-color: rgba(255, 215, 0, 0.8);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.7);
}

.sticker-img-overlay,
.pendant-img-overlay {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.5));
}

.sticker-placeholder-overlay,
.pendant-placeholder-overlay {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 0.8rem;
  font-weight: bold;
}

.expand-rename-tag {
  display: flex;
  justify-content: center;
  margin-top: 0.25rem;
}

.expand-rename-tag .el-tag {
  font-size: 0.85rem;
  padding: 2px 6px;
  cursor: help;
}

.expand-item-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 0;
}

.expand-item-user {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.expand-item-float {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.float-text-row {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.expand-value-small {
  color: #fff;
  font-weight: 500;
  font-size: 0.75rem;
  font-family: monospace;
}

.expand-item-prices {
  display: flex;
  gap: 0.5rem;
  font-size: 0.85rem;
}

.expand-price-item {
  display: flex;
  gap: 0.25rem;
  align-items: center;
}

.expand-label {
  color: #999;
  font-size: 0.8rem;
}

.expand-value {
  color: #fff;
  font-weight: 500;
  font-size: 0.85rem;
}

.float-bar-mini {
  position: relative;
  height: 4px;
  display: flex;
  border-radius: 2px;
  overflow: hidden;
  width: 100%;
  margin-top: 2px;
}

.float-bar-mini .float-segment {
  height: 100%;
}

.float-bar-mini .float-pointer {
  width: 2px;
  height: 8px;
  top: 50%;
  transform: translate(-50%, -50%);
}

.expand-content-empty {
  padding: 1rem;
  text-align: center;
  background-color: var(--bg-secondary);
}

.inline-pagination-below {
  margin-top: 0.5rem;
  display: flex;
  justify-content: center;
}

.inline-pagination-below :deep(.el-pagination) {
  padding: 0;
}

.inline-pagination-below :deep(.el-pager li) {
  min-width: 24px;
  height: 24px;
  line-height: 24px;
  font-size: 12px;
}

.inline-pagination-below :deep(.btn-prev),
.inline-pagination-below :deep(.btn-next) {
  padding: 0 4px;
  min-width: 24px;
  height: 24px;
  line-height: 24px;
}

/* 磨损值显示条 */
.float-bar {
  position: relative;
  height: 6px;
  display: flex;
  border-radius: 3px;
  overflow: hidden;
  width: 100%;
  margin: 0.25rem 0;
}

.float-segment {
  height: 100%;
  transition: opacity 0.2s;
}

.float-segment.fn {
  flex: 7;
  background: linear-gradient(90deg, #4CAF50, #66BB6A);
}

.float-segment.mw {
  flex: 8;
  background: linear-gradient(90deg, #8BC34A, #9CCC65);
}

.float-segment.ft {
  flex: 23;
  background: linear-gradient(90deg, #FFC107, #FFD54F);
}

.float-segment.ww {
  flex: 7;
  background: linear-gradient(90deg, #FF9800, #FFB74D);
}

.float-segment.bs {
  flex: 55;
  background: linear-gradient(90deg, #F44336, #E57373);
}

.float-pointer {
  position: absolute;
  width: 3px;
  height: 12px;
  background: #fff;
  border: 1px solid #000;
  border-radius: 2px;
  top: 50%;
  transform: translate(-50%, -50%);
  box-shadow: 0 0 4px rgba(0, 0, 0, 0.5);
  z-index: 10;
}

@media (max-width: 768px) {
  .inventory-mining-container {
    padding: 1rem;
  }

  .mining-section {
    padding: 1.5rem;
  }

  .mining-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .steam-id-input {
    width: 100%;
  }

  .result-stats {
    grid-template-columns: 1fr;
  }

  .table-filters {
    flex-direction: column;
  }

  .card-grid {
    grid-template-columns: 1fr;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}
</style>
