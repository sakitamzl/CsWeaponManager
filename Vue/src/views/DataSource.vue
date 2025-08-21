<template>
  <div>
    <h1 class="page-title">数据来源配置</h1>
    
    <div class="data-source-container">
      <div class="input-section">
        <div class="card">
          <h3>添加新数据源</h3>
          <el-form :model="inputForm" label-width="120px" @submit.prevent="handleSubmit">
            <el-form-item label="数据源名称">
              <el-input 
                v-model="inputForm.name" 
                placeholder="请输入数据源名称"
                style="width: 400px;"
              />
            </el-form-item>
            <el-form-item label="数据源类型">
              <el-select v-model="inputForm.type" placeholder="选择数据源类型" style="width: 400px;">
                <el-option label="BUFF" value="buff" />
                <el-option label="Steam市场" value="steam" />
                <el-option label="悠悠有品" value="youpin" />
                <el-option label="C5GAME" value="c5game" />
                <el-option label="IGXE" value="igxe" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
            <el-form-item label="API地址">
              <el-input 
                v-model="inputForm.apiUrl" 
                placeholder="请输入API地址"
                style="width: 400px;"
              />
            </el-form-item>
            <el-form-item label="API密钥">
              <el-input 
                v-model="inputForm.apiKey" 
                type="password"
                show-password
                placeholder="请输入API密钥"
                style="width: 400px;"
              />
            </el-form-item>
            <el-form-item label="更新频率">
              <el-select v-model="inputForm.updateFreq" placeholder="选择更新频率" style="width: 400px;">
                <el-option label="实时" value="realtime" />
                <el-option label="每5分钟" value="5min" />
                <el-option label="每15分钟" value="15min" />
                <el-option label="每小时" value="1hour" />
                <el-option label="每6小时" value="6hour" />
                <el-option label="每天" value="daily" />
              </el-select>
            </el-form-item>
            <el-form-item label="启用状态">
              <el-switch v-model="inputForm.enabled" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSubmit" :loading="submitting">
                添加数据源
              </el-button>
              <el-button @click="resetForm">重置</el-button>
              <el-button type="success" @click="testConnection" :loading="testing">
                测试连接
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>

      <div class="data-sources-list">
        <div class="card">
          <div class="card-header">
            <h3>已配置的数据源</h3>
            <el-button type="primary" @click="refreshAllSources" :loading="refreshing">
              刷新所有
            </el-button>
          </div>
          
          <div class="grid grid-auto">
            <div 
              v-for="source in dataSources" 
              :key="source.id" 
              class="source-card"
              :class="{ disabled: !source.enabled }"
            >
              <div class="source-header">
                <div class="source-info">
                  <h4>{{ source.name }}</h4>
                  <el-tag :type="getSourceTypeColor(source.type)">{{ getSourceTypeLabel(source.type) }}</el-tag>
                </div>
                <div class="source-status">
                  <el-tag :type="source.status === 'online' ? 'success' : 'danger'" size="small">
                    {{ source.status === 'online' ? '在线' : '离线' }}
                  </el-tag>
                </div>
              </div>
              
              <div class="source-details">
                <p><strong>更新频率:</strong> {{ getUpdateFreqLabel(source.updateFreq) }}</p>
                <p><strong>最后更新:</strong> {{ formatTime(source.lastUpdate) }}</p>
                <p><strong>今日请求:</strong> {{ source.todayRequests }}</p>
                <p><strong>成功率:</strong> {{ source.successRate }}%</p>
              </div>
              
              <div class="source-actions">
                <el-switch 
                  v-model="source.enabled" 
                  @change="toggleSource(source)"
                />
                <el-button type="primary" size="small" @click="editSource(source)">
                  编辑
                </el-button>
                <el-button type="success" size="small" @click="testSourceConnection(source)">
                  测试
                </el-button>
                <el-button type="danger" size="small" @click="removeSource(source)">
                  删除
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 数据源统计 -->
      <div class="stats-section">
        <div class="card">
          <h3>数据源统计</h3>
          <div class="grid grid-4">
            <div class="stat-item">
              <div class="stat-number">{{ sourceStats.total }}</div>
              <div class="stat-label">总数据源</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{{ sourceStats.online }}</div>
              <div class="stat-label">在线数量</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{{ sourceStats.todayRequests }}</div>
              <div class="stat-label">今日请求</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{{ sourceStats.avgSuccessRate }}%</div>
              <div class="stat-label">平均成功率</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'DataSource',
  setup() {
    const submitting = ref(false)
    const testing = ref(false)
    const refreshing = ref(false)
    
    const inputForm = ref({
      name: '',
      type: '',
      apiUrl: '',
      apiKey: '',
      updateFreq: '15min',
      enabled: true
    })

    const dataSources = ref([
      {
        id: 1,
        name: 'BUFF官方API',
        type: 'buff',
        apiUrl: 'https://api.buff.game',
        updateFreq: '5min',
        enabled: true,
        status: 'online',
        lastUpdate: new Date(),
        todayRequests: 1248,
        successRate: 98.5
      },
      {
        id: 2,
        name: 'Steam市场API',
        type: 'steam',
        apiUrl: 'https://steamcommunity.com/market',
        updateFreq: '15min',
        enabled: true,
        status: 'online',
        lastUpdate: new Date(Date.now() - 300000),
        todayRequests: 856,
        successRate: 96.2
      },
      {
        id: 3,
        name: '悠悠有品API',
        type: 'youpin',
        apiUrl: 'https://youpin898.com/api',
        updateFreq: '1hour',
        enabled: false,
        status: 'offline',
        lastUpdate: new Date(Date.now() - 3600000),
        todayRequests: 0,
        successRate: 0
      }
    ])

    const sourceStats = computed(() => {
      const total = dataSources.value.length
      const online = dataSources.value.filter(s => s.status === 'online').length
      const todayRequests = dataSources.value.reduce((sum, s) => sum + s.todayRequests, 0)
      const avgSuccessRate = total > 0 ? 
        (dataSources.value.reduce((sum, s) => sum + s.successRate, 0) / total).toFixed(1) : 0

      return {
        total,
        online,
        todayRequests,
        avgSuccessRate
      }
    })

    const getSourceTypeLabel = (type) => {
      const labels = {
        buff: 'BUFF',
        steam: 'Steam',
        youpin: '悠悠有品',
        c5game: 'C5GAME',
        igxe: 'IGXE',
        other: '其他'
      }
      return labels[type] || type
    }

    const getSourceTypeColor = (type) => {
      const colors = {
        buff: 'warning',
        steam: 'primary',
        youpin: 'success',
        c5game: 'info',
        igxe: 'danger',
        other: ''
      }
      return colors[type] || ''
    }

    const getUpdateFreqLabel = (freq) => {
      const labels = {
        realtime: '实时',
        '5min': '每5分钟',
        '15min': '每15分钟',
        '1hour': '每小时',
        '6hour': '每6小时',
        daily: '每天'
      }
      return labels[freq] || freq
    }

    const formatTime = (time) => {
      return new Date(time).toLocaleString('zh-CN')
    }

    const handleSubmit = async () => {
      if (!inputForm.value.name || !inputForm.value.type) {
        ElMessage.error('请填写必要信息')
        return
      }

      submitting.value = true
      try {
        // 这里应该调用API添加数据源
        const newSource = {
          id: Date.now(),
          ...inputForm.value,
          status: 'online',
          lastUpdate: new Date(),
          todayRequests: 0,
          successRate: 100
        }
        dataSources.value.push(newSource)
        
        ElMessage.success('数据源添加成功')
        resetForm()
      } catch (error) {
        console.error('添加数据源失败:', error)
        ElMessage.error('添加数据源失败')
      } finally {
        submitting.value = false
      }
    }

    const resetForm = () => {
      inputForm.value = {
        name: '',
        type: '',
        apiUrl: '',
        apiKey: '',
        updateFreq: '15min',
        enabled: true
      }
    }

    const testConnection = async () => {
      if (!inputForm.value.apiUrl) {
        ElMessage.error('请输入API地址')
        return
      }

      testing.value = true
      try {
        // 这里应该调用API测试连接
        await new Promise(resolve => setTimeout(resolve, 2000))
        ElMessage.success('连接测试成功')
      } catch (error) {
        ElMessage.error('连接测试失败')
      } finally {
        testing.value = false
      }
    }

    const testSourceConnection = async (source) => {
      ElMessage.info(`正在测试 ${source.name} 连接...`)
      // 这里应该调用API测试数据源连接
      setTimeout(() => {
        ElMessage.success(`${source.name} 连接正常`)
      }, 1500)
    }

    const toggleSource = async (source) => {
      try {
        // 这里应该调用API更新数据源状态
        ElMessage.success(`${source.name} ${source.enabled ? '已启用' : '已禁用'}`)
      } catch (error) {
        ElMessage.error('状态更新失败')
        source.enabled = !source.enabled
      }
    }

    const editSource = (source) => {
      ElMessage.info(`编辑数据源: ${source.name}`)
      // 这里应该打开编辑对话框或跳转到编辑页面
    }

    const removeSource = (source) => {
      ElMessageBox.confirm(
        `确定要删除数据源 "${source.name}" 吗？`,
        '确认删除',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'danger'
        }
      ).then(() => {
        const index = dataSources.value.findIndex(s => s.id === source.id)
        if (index > -1) {
          dataSources.value.splice(index, 1)
          ElMessage.success('数据源删除成功')
        }
      })
    }

    const refreshAllSources = async () => {
      refreshing.value = true
      try {
        // 这里应该调用API刷新所有数据源
        await new Promise(resolve => setTimeout(resolve, 2000))
        ElMessage.success('所有数据源已刷新')
      } catch (error) {
        ElMessage.error('刷新失败')
      } finally {
        refreshing.value = false
      }
    }

    onMounted(() => {
      // 初始化时可以加载数据源列表
    })

    return {
      submitting,
      testing,
      refreshing,
      inputForm,
      dataSources,
      sourceStats,
      getSourceTypeLabel,
      getSourceTypeColor,
      getUpdateFreqLabel,
      formatTime,
      handleSubmit,
      resetForm,
      testConnection,
      testSourceConnection,
      toggleSource,
      editSource,
      removeSource,
      refreshAllSources
    }
  }
}
</script>

<style scoped>
.data-source-container {
  width: 100%;
}

.input-section {
  margin-bottom: clamp(1.5rem, 4vw, 1.875rem);
}

.data-sources-list {
  margin-bottom: clamp(1.5rem, 4vw, 1.875rem);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: clamp(1rem, 3vw, 1.25rem);
  flex-wrap: wrap;
  gap: 1rem;
}

.source-card {
  background-color: #2a2a2a;
  border-radius: 0.5rem;
  padding: clamp(1rem, 2.5vw, 1.25rem);
  border: 1px solid #333;
  transition: all 0.3s;
}

.source-card:hover {
  border-color: #4CAF50;
}

.source-card.disabled {
  opacity: 0.6;
}

.source-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: clamp(0.75rem, 2vw, 0.9375rem);
  flex-wrap: wrap;
  gap: 0.5rem;
}

.source-info h4 {
  margin-bottom: clamp(0.5rem, 1vw, 0.5rem);
  color: #fff;
  font-size: clamp(1rem, 1.8vw, 1.125rem);
}

.source-details {
  margin-bottom: clamp(1rem, 3vw, 1.25rem);
}

.source-details p {
  margin: clamp(0.5rem, 1vw, 0.5rem) 0;
  color: #ccc;
  font-size: clamp(0.75rem, 1.2vw, 0.875rem);
  line-height: 1.5;
}

.source-actions {
  display: flex;
  align-items: center;
  gap: clamp(0.5rem, 1.5vw, 0.625rem);
  flex-wrap: wrap;
}

.stats-section {
  margin-bottom: clamp(1.5rem, 4vw, 1.875rem);
}

.stat-item {
  text-align: center;
  padding: clamp(1rem, 2.5vw, 1.25rem);
  background-color: #2a2a2a;
  border-radius: 0.5rem;
  border: 1px solid #333;
}

.stat-number {
  font-size: clamp(1.5rem, 4vw, 2rem);
  font-weight: bold;
  color: #4CAF50;
  margin-bottom: clamp(0.5rem, 1vw, 0.5rem);
}

.stat-label {
  color: #ccc;
  font-size: clamp(0.75rem, 1.2vw, 0.875rem);
}

:deep(.el-form-item__label) {
  color: #ccc;
  font-size: clamp(0.75rem, 1.2vw, 0.875rem);
}

:deep(.el-input__inner) {
  background-color: #2a2a2a;
  border-color: #333;
  color: #fff;
  font-size: clamp(0.75rem, 1.2vw, 0.875rem);
}

:deep(.el-select .el-input__inner) {
  background-color: #2a2a2a;
  border-color: #333;
  color: #fff;
}

:deep(.el-switch.is-checked .el-switch__core) {
  background-color: #4CAF50;
}

:deep(.el-button) {
  font-size: clamp(0.625rem, 1vw, 0.75rem);
  padding: clamp(0.375rem, 1vw, 0.5rem) clamp(0.5rem, 1.5vw, 0.75rem);
}

:deep(.el-form-item) {
  margin-bottom: clamp(1rem, 2.5vw, 1.125rem);
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .source-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .source-actions {
    justify-content: center;
  }
  
  .source-actions .el-button {
    flex: 1;
    min-width: 0;
    font-size: 0.625rem;
  }
  
  :deep(.el-button) {
    width: 100%;
    font-size: 0.75rem;
    padding: 0.5rem;
  }
  
  :deep(.el-form-item__label) {
    font-size: 0.75rem;
  }
  
  :deep(.el-input__inner) {
    font-size: 0.875rem;
  }
}

@media (max-width: 480px) {
  .source-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .source-actions .el-switch {
    align-self: center;
  }
}
</style>