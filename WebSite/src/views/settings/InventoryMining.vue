<template>
  <div class="inventory-mining-container">
    <div class="mining-section">
      <h2 class="section-title">库存挖掘</h2>
      
      <div class="mining-controls">
        <el-select 
          v-model="selectedSteamId" 
          placeholder="选择Steam账号" 
          class="steam-id-select"
          :disabled="isMining"
        >
          <el-option 
            v-for="item in steamIdList" 
            :key="item.steamID || item.steam_id" 
            :label="`${item.dataName || '未命名'} (${item.steamID || item.steam_id || '无ID'})`" 
            :value="item.steamID || item.steam_id"
          />
        </el-select>
        
        <el-button 
          type="primary" 
          @click="startMining"
          :disabled="!selectedSteamId || isMining"
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
            <div class="stat-label">总计分析</div>
            <div class="stat-value">{{ miningResult.total_analyzed }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">潜力饰品</div>
            <div class="stat-value highlight">{{ miningResult.potential_items }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">预估收益</div>
            <div class="stat-value success">¥{{ miningResult.estimated_profit }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 挖掘结果表格 -->
    <div v-if="miningItems.length > 0" class="results-table-section">
      <h3 class="section-title">潜力饰品列表</h3>
      <el-table
        :data="miningItems"
        style="width: 100%"
        :header-row-style="{ backgroundColor: 'var(--bg-tertiary)' }"
        height="500"
      >
        <el-table-column prop="item_name" label="饰品名称" min-width="200" />
        <el-table-column prop="buy_price" label="购入价格" width="120">
          <template #default="scope">
            <span>¥{{ parseFloat(scope.row.buy_price).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="current_price" label="当前价格" width="120">
          <template #default="scope">
            <span>¥{{ parseFloat(scope.row.current_price).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="profit" label="预估收益" width="120">
          <template #default="scope">
            <span :style="{ color: scope.row.profit >= 0 ? '#4CAF50' : '#f56c6c' }">
              {{ scope.row.profit >= 0 ? '+' : '' }}¥{{ parseFloat(scope.row.profit).toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="profit_rate" label="收益率" width="100">
          <template #default="scope">
            <span :style="{ color: scope.row.profit_rate >= 0 ? '#4CAF50' : '#f56c6c' }">
              {{ scope.row.profit_rate >= 0 ? '+' : '' }}{{ scope.row.profit_rate }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="recommendation" label="建议" width="120">
          <template #default="scope">
            <el-tag :type="getRecommendationType(scope.row.recommendation)">
              {{ scope.row.recommendation }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { API_CONFIG } from '@/config/api.js'

export default {
  name: 'InventoryMining',
  setup() {
    const selectedSteamId = ref('')
    const steamIdList = ref([])
    const isMining = ref(false)
    const miningProgress = ref(null)
    const lastMiningTime = ref('')
    const miningResult = ref(null)
    const miningItems = ref([])

    // 加载Steam ID列表
    const loadSteamIdList = async () => {
      try {
        const response = await axios.get(`${API_CONFIG.BASE_URL}/webInventoryV1/steam_ids`)
        if (response.data.success && response.data.data.length > 0) {
          steamIdList.value = response.data.data
          if (steamIdList.value.length > 0) {
            const firstItem = steamIdList.value[0]
            selectedSteamId.value = firstItem.steamID || firstItem.steam_id || ''
          }
        }
      } catch (error) {
        console.error('加载Steam ID列表失败:', error)
        ElMessage.error('加载Steam ID列表失败')
      }
    }

    // 开始挖掘
    const startMining = async () => {
      if (!selectedSteamId.value) {
        ElMessage.warning('请先选择 Steam ID')
        return
      }

      try {
        await ElMessageBox.confirm(
          `确定要开始挖掘 Steam ID: ${selectedSteamId.value} 的库存吗？`,
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
        // TODO: 替换为实际的API端点
        const response = await axios.post(`${API_CONFIG.BASE_URL}/api/inventory/mining`, {
          steamId: selectedSteamId.value
        })

        if (response.data.success) {
          miningResult.value = response.data.data
          miningItems.value = response.data.data.items || []
          lastMiningTime.value = new Date().toLocaleString('zh-CN')
          
          miningProgress.value = {
            percentage: 100,
            processed: response.data.data.total_analyzed,
            total: response.data.data.total_analyzed,
            found: response.data.data.potential_items,
            status: 'success'
          }
          
          ElMessage.success(`挖掘完成！发现 ${response.data.data.potential_items} 个潜力饰品`)
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

    // 查看历史记录
    const viewMiningHistory = () => {
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

    onMounted(() => {
      loadSteamIdList()
    })

    return {
      selectedSteamId,
      steamIdList,
      isMining,
      miningProgress,
      lastMiningTime,
      miningResult,
      miningItems,
      startMining,
      viewMiningHistory,
      getRecommendationType
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

.steam-id-select {
  min-width: 300px;
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

  .steam-id-select {
    width: 100%;
  }

  .result-stats {
    grid-template-columns: 1fr;
  }
}
</style>
