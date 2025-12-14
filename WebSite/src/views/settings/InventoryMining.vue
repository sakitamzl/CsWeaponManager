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

    <!-- 挖掘结果表格 -->
    <div v-if="miningItems.length > 0" class="results-table-section">
      <h3 class="section-title">物品列表</h3>
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
      <el-table
        :data="filteredItems"
        style="width: 100%"
        :header-row-style="{ backgroundColor: 'var(--bg-tertiary)' }"
        height="500"
      >
        <el-table-column prop="persona_name" label="所属用户" width="150" />
        <el-table-column prop="item_name" label="饰品名称" min-width="200" />
        <el-table-column prop="weapon_type" label="类型" width="100" />
        <el-table-column prop="weapon_name" label="武器" width="150" />
        <el-table-column prop="float_range" label="磨损" width="120" />
        <el-table-column prop="market_price" label="参考价格" width="120">
          <template #default="scope">
            <span v-if="scope.row.market_price && scope.row.market_price !== '0'" style="color: #4CAF50; font-weight: bold;">
              ¥{{ parseFloat(scope.row.market_price).toFixed(2) }}
            </span>
            <span v-else style="color: #888;">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="rarity" label="稀有度" width="120">
          <template #default="scope">
            <el-tag v-if="scope.row.rarity" size="small">{{ scope.row.rarity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="tradable" label="可交易" width="80">
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
import { ref, computed } from 'vue'
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
          `确定要开始挖掘 Steam ID: ${steamId} 及其好友的库存吗？\n\n此操作将访问公开库存数据，可能需要几分钟时间。`,
          '确认挖掘',
          {
            confirmButtonText: '开始',
            cancelButtonText: '取消',
            type: 'info'
          }
        )
      } catch {
        return
      }

      isMining.value = true
      miningProgress.value = {
        percentage: 0,
        processed: 0,
        total: 100,
        found: 0,
        status: 'success'
      }
      ElMessage.info('开始挖掘库存...')

      try {
        // 调用Spider的挖掘接口
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
            estimated_profit: 0
          }
          lastMiningTime.value = new Date().toLocaleString('zh-CN')
          
          miningProgress.value = {
            percentage: 100,
            processed: data.total_items,
            total: data.total_items,
            found: data.total_items,
            status: 'success'
          }
          
          // 加载挖掘结果和统计信息
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
      
      return items
    })
    
    // 按用户筛选
    const filterByUser = () => {
      // 筛选逻辑已在 computed 中处理
    }
    
    // 按武器类型筛选
    const filterByWeaponType = () => {
      // 筛选逻辑已在 computed 中处理
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
      startMining,
      viewMiningHistory,
      getRecommendationType,
      filterByUser,
      filterByWeaponType
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
}
</style>
