<template>
  <div class="automate-management">
    <div class="config-section">
      <el-form :model="automateForm" label-width="140px" label-position="left">
        <!-- 自动化类型选择 -->
        <el-form-item label="自动化类型">
          <el-select 
            v-model="automateForm.automateType" 
            placeholder="请选择自动化类型"
            style="width: 300px"
            @change="handleTypeChange"
          >
            <el-option label="自动更新数据" value="auto_update" />
            <el-option label="自动获取数据" value="auto_fetch" />
          </el-select>
        </el-form-item>

        <!-- 第二个下拉框 - 根据类型动态显示 -->
        <el-form-item v-if="automateForm.automateType" :label="secondSelectLabel">
          <el-select 
            v-model="automateForm.selectedTask" 
            placeholder="请选择任务"
            style="width: 300px"
          >
            <el-option 
              v-for="task in availableTasks" 
              :key="task.value" 
              :label="task.label" 
              :value="task.value" 
            />
          </el-select>
        </el-form-item>

        <!-- Steam ID 选择 (仅在自动更新数据时显示) -->
        <el-form-item v-if="automateForm.automateType === 'auto_update'" label="Steam账号">
          <el-select 
            v-model="automateForm.selectedSteamId" 
            placeholder="请选择Steam账号"
            style="width: 300px"
            filterable
          >
            <el-option 
              v-for="steamId in steamIdList" 
              :key="steamId" 
              :label="steamId" 
              :value="steamId" 
            />
          </el-select>
        </el-form-item>

        <!-- 数据源选择 (仅在自动获取数据时显示) -->
        <el-form-item v-if="automateForm.automateType === 'auto_fetch'" label="数据源">
          <el-select 
            v-model="automateForm.selectedDataSource" 
            placeholder="请选择数据源"
            style="width: 300px"
            filterable
          >
            <el-option 
              v-for="source in filteredDataSources" 
              :key="source.dataID" 
              :label="`${source.dataName} (${source.steamID || '无SteamID'})`" 
              :value="source.dataID" 
            />
          </el-select>
        </el-form-item>

        <!-- 定时设置 -->
        <el-form-item label="定时执行">
          <el-switch v-model="automateForm.isScheduled" />
        </el-form-item>

        <el-form-item v-if="automateForm.isScheduled" label="执行间隔(分钟)">
          <el-input-number 
            v-model="automateForm.interval" 
            :min="1" 
            :max="1440" 
            style="width: 300px"
          />
        </el-form-item>

        <!-- 操作按钮 -->
        <el-form-item>
          <el-button type="primary" @click="handleExecute" :loading="executing">
            {{ automateForm.isScheduled ? '启动定时任务' : '立即执行' }}
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 任务列表 -->
    <div class="task-list-section">
      <div class="section-header">
        <h3>运行中的定时任务</h3>
        <el-button size="small" type="danger" @click="stopAllTasks" v-if="runningTasks.length > 0">
          停止所有任务
        </el-button>
      </div>
      <el-table :data="runningTasks" style="width: 100%">
        <el-table-column prop="type" label="自动化类型" width="120" />
        <el-table-column prop="taskName" label="任务名称" width="180" />
        <el-table-column prop="targetInfo" label="目标" width="200" />
        <el-table-column prop="interval" label="间隔(分钟)" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === '运行中' ? 'success' : 'info'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastRun" label="最后执行时间" width="180" />
        <el-table-column prop="nextRun" label="下次执行时间" width="180" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button size="small" type="danger" @click="stopTask(row.id)">停止</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div v-if="runningTasks.length === 0" class="empty-placeholder">
        <el-empty description="暂无运行中的定时任务" />
      </div>
    </div>

    <!-- 执行历史 -->
    <div class="history-section">
      <h3>执行历史 (最近10条)</h3>
      <el-table :data="executionHistory" style="width: 100%">
        <el-table-column prop="time" label="执行时间" width="180" />
        <el-table-column prop="type" label="类型" width="120" />
        <el-table-column prop="taskName" label="任务" width="180" />
        <el-table-column prop="targetInfo" label="目标" width="200" />
        <el-table-column prop="result" label="结果" width="100">
          <template #default="{ row }">
            <el-tag :type="row.result === '成功' ? 'success' : 'danger'">
              {{ row.result }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="消息" />
      </el-table>
      <div v-if="executionHistory.length === 0" class="empty-placeholder">
        <el-empty description="暂无执行历史" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { API_CONFIG } from '@/config/api.js'

// 表单数据
const automateForm = ref({
  automateType: '',
  selectedTask: '',
  selectedSteamId: '',
  selectedDataSource: '',
  isScheduled: false,
  interval: 30
})

// 执行状态
const executing = ref(false)

// Steam ID 列表
const steamIdList = ref([])

// 数据源列表
const dataSources = ref([])

// 运行中的任务
const runningTasks = ref([])

// 执行历史
const executionHistory = ref([])

// 定时器映射
const timers = ref(new Map())

// 自动更新数据的任务选项
const updateTasks = [
  { label: '更新Steam库存', value: 'update_steam_inventory' },
  { label: '获取悠悠有品价格', value: 'fetch_yyyp_price' },
  { label: '获取BUFF价格', value: 'fetch_buff_price' }
]

// 自动获取数据的任务选项
const fetchTasks = [
  { label: 'BUFF数据采集', value: 'collect_buff' },
  { label: '悠悠有品数据采集', value: 'collect_youpin' }
]

// 第二个选择框标签
const secondSelectLabel = computed(() => {
  return automateForm.value.automateType === 'auto_update' ? '更新任务' : '采集任务'
})

// 可用的任务列表
const availableTasks = computed(() => {
  return automateForm.value.automateType === 'auto_update' ? updateTasks : fetchTasks
})

// 过滤后的数据源 (根据选择的任务类型)
const filteredDataSources = computed(() => {
  console.log('过滤数据源 - 选中任务:', automateForm.value.selectedTask)
  console.log('所有数据源:', dataSources.value)
  
  if (automateForm.value.selectedTask === 'collect_buff') {
    const filtered = dataSources.value.filter(s => s.type === 'buff' && s.enabled)
    console.log('过滤后的BUFF数据源:', filtered)
    return filtered
  } else if (automateForm.value.selectedTask === 'collect_youpin') {
    const filtered = dataSources.value.filter(s => s.type === 'youpin' && s.enabled)
    console.log('过滤后的悠悠有品数据源:', filtered)
    return filtered
  }
  console.log('未选择任务,返回空数组')
  return []
})

// 加载 Steam ID 列表
const loadSteamIds = async () => {
  try {
    const response = await axios.get(`${API_CONFIG.BASE_URL}/webInventoryV1/steam_ids`)
    if (response.data && Array.isArray(response.data)) {
      steamIdList.value = response.data
    }
  } catch (error) {
    console.error('加载Steam ID列表失败:', error)
  }
}

// 加载数据源列表
const loadDataSources = async () => {
  try {
    const response = await axios.get(`${API_CONFIG.BASE_URL}/dataSourcePageV1/api/datasources`)
    console.log('数据源API响应:', response.data)
    if (response.data.success && Array.isArray(response.data.data)) {
      dataSources.value = response.data.data
      console.log('已加载数据源:', dataSources.value)
      console.log('BUFF数据源:', dataSources.value.filter(s => s.type === 'buff'))
      console.log('悠悠有品数据源:', dataSources.value.filter(s => s.type === 'youpin'))
    }
  } catch (error) {
    console.error('加载数据源列表失败:', error)
  }
}

// 处理类型变化
const handleTypeChange = () => {
  automateForm.value.selectedTask = ''
  automateForm.value.selectedSteamId = ''
  automateForm.value.selectedDataSource = ''
}

// 执行任务
const handleExecute = async () => {
  // 验证表单
  if (!automateForm.value.automateType) {
    ElMessage.warning('请选择自动化类型')
    return
  }
  
  if (!automateForm.value.selectedTask) {
    ElMessage.warning('请选择任务')
    return
  }

  if (automateForm.value.automateType === 'auto_update') {
    if (!automateForm.value.selectedSteamId) {
      ElMessage.warning('请选择Steam账号')
      return
    }
  } else {
    if (!automateForm.value.selectedDataSource) {
      ElMessage.warning('请选择数据源')
      return
    }
  }

  if (automateForm.value.isScheduled) {
    // 启动定时任务
    startScheduledTask()
  } else {
    // 立即执行
    await executeTask()
  }
}

// 执行具体任务
const executeTask = async () => {
  executing.value = true
  const startTime = new Date().toLocaleString()
  
  try {
    let result
    const taskType = automateForm.value.selectedTask
    
    if (automateForm.value.automateType === 'auto_update') {
      // 自动更新数据任务
      const steamId = automateForm.value.selectedSteamId
      
      if (taskType === 'update_steam_inventory') {
        result = await updateSteamInventory(steamId)
      } else if (taskType === 'fetch_yyyp_price') {
        result = await fetchYYYPPrice(steamId)
      } else if (taskType === 'fetch_buff_price') {
        result = await fetchBuffPrice(steamId)
      }
    } else {
      // 自动获取数据任务
      const dataSourceId = automateForm.value.selectedDataSource
      const dataSource = dataSources.value.find(s => s.dataID === dataSourceId)
      
      if (taskType === 'collect_buff') {
        result = await collectBuffData(dataSource)
      } else if (taskType === 'collect_youpin') {
        result = await collectYoupinData(dataSource)
      }
    }
    
    // 添加到执行历史
    addExecutionHistory({
      time: startTime,
      type: automateForm.value.automateType === 'auto_update' ? '自动更新数据' : '自动获取数据',
      taskName: availableTasks.value.find(t => t.value === taskType)?.label || taskType,
      targetInfo: getTargetInfo(),
      result: result.success ? '成功' : '失败',
      message: result.message
    })
    
  } catch (error) {
    console.error('执行任务失败:', error)
    addExecutionHistory({
      time: startTime,
      type: automateForm.value.automateType === 'auto_update' ? '自动更新数据' : '自动获取数据',
      taskName: availableTasks.value.find(t => t.value === automateForm.value.selectedTask)?.label || automateForm.value.selectedTask,
      targetInfo: getTargetInfo(),
      result: '失败',
      message: error.message
    })
  } finally {
    executing.value = false
  }
}

// 更新Steam库存
const updateSteamInventory = async (steamId) => {
  try {
    const response = await axios.post(
      `${API_CONFIG.SPIDER_BASE_URL}/steamSpiderV1/getInventory`,
      { steamId }
    )
    
    if (response.data.success) {
      ElMessage.success(response.data.message || 'Steam库存更新成功')
      return { success: true, message: response.data.message || '库存更新成功' }
    } else {
      ElMessage.error(response.data.message || 'Steam库存更新失败')
      return { success: false, message: response.data.message || '库存更新失败' }
    }
  } catch (error) {
    ElMessage.error('更新失败: ' + error.message)
    throw error
  }
}

// 获取悠悠有品价格
const fetchYYYPPrice = async (steamId) => {
  try {
    const response = await axios.post(
      `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/getYYYPPrice`,
      { steamId }
    )
    
    if (response.data.success) {
      ElMessage.success(response.data.message || '悠悠有品价格获取成功')
      return { success: true, message: response.data.message || '价格获取成功' }
    } else {
      ElMessage.error(response.data.message || '悠悠有品价格获取失败')
      return { success: false, message: response.data.message || '价格获取失败' }
    }
  } catch (error) {
    ElMessage.error('获取失败: ' + error.message)
    throw error
  }
}

// 获取BUFF价格
const fetchBuffPrice = async (steamId) => {
  try {
    const response = await axios.post(
      `${API_CONFIG.SPIDER_BASE_URL}/buffSpiderV1/getBUFFPrice`,
      { steamId }
    )
    
    if (response.data.success) {
      ElMessage.success(response.data.message || 'BUFF价格获取成功')
      return { success: true, message: response.data.message || '价格获取成功' }
    } else {
      ElMessage.error(response.data.message || 'BUFF价格获取失败')
      return { success: false, message: response.data.message || '价格获取失败' }
    }
  } catch (error) {
    ElMessage.error('获取失败: ' + error.message)
    throw error
  }
}

// 采集BUFF数据
const collectBuffData = async (dataSource) => {
  try {
    const response = await axios.post(
      `${API_CONFIG.SPIDER_BASE_URL}/buffSpiderV1/NewData`,
      { steamID: dataSource.steamID || '' }
    )
    
    if (response.status === 200) {
      ElMessage.success(`${dataSource.dataName} BUFF数据采集完成`)
      return { success: true, message: 'BUFF数据采集完成' }
    } else {
      ElMessage.error('BUFF数据采集失败')
      return { success: false, message: 'BUFF数据采集失败' }
    }
  } catch (error) {
    ElMessage.error('采集失败: ' + error.message)
    throw error
  }
}

// 采集悠悠有品数据
const collectYoupinData = async (dataSource) => {
  try {
    const spiderData = {
      phone: dataSource.config?.yyyp_phone || '',
      sessionid: dataSource.config?.yyyp_Sessionid || '',
      token: dataSource.config?.yyyp_token || '',
      app_version: dataSource.config?.yyyp_app_version || '',
      app_type: dataSource.config?.yyyp_app_type || '',
      userId: dataSource.config?.yyyp_userId || '',
      steamId: dataSource.config?.yyyp_steamId || ''
    }
    
    const response = await axios.post(
      `${API_CONFIG.SPIDER_BASE_URL}/youping898SpiderV1/NewData`,
      spiderData
    )
    
    if (response.status === 200) {
      ElMessage.success(`${dataSource.dataName} 悠悠有品数据采集完成`)
      return { success: true, message: '悠悠有品数据采集完成' }
    } else {
      ElMessage.error('悠悠有品数据采集失败')
      return { success: false, message: '悠悠有品数据采集失败' }
    }
  } catch (error) {
    ElMessage.error('采集失败: ' + error.message)
    throw error
  }
}

// 启动定时任务
const startScheduledTask = async () => {
  // 先保存任务配置到数据库
  try {
    const config = {
      selectedTask: automateForm.value.selectedTask,
      selectedSteamId: automateForm.value.selectedSteamId,
      selectedDataSource: automateForm.value.selectedDataSource,
      interval: automateForm.value.interval,
      isScheduled: true
    }
    
    const response = await axios.post(
      `${API_CONFIG.BASE_URL}/autoManagerPageV1/api/auto-manager/task`,
      {
        taskName: availableTasks.value.find(t => t.value === automateForm.value.selectedTask)?.label || '未命名任务',
        automateType: automateForm.value.automateType,
        config: config,
        enabled: true
      }
    )
    
    if (!response.data.success) {
      ElMessage.error('保存任务配置失败: ' + response.data.message)
      return
    }
    
    const taskId = response.data.taskId
    
    const taskInfo = {
      id: taskId,
      type: automateForm.value.automateType === 'auto_update' ? '自动更新数据' : '自动获取数据',
      taskName: availableTasks.value.find(t => t.value === automateForm.value.selectedTask)?.label || '',
      targetInfo: getTargetInfo(),
      interval: automateForm.value.interval,
      status: '运行中',
      lastRun: '-',
      nextRun: calculateNextRun(automateForm.value.interval)
    }
    
    // 添加到运行任务列表
    runningTasks.value.push(taskInfo)
    
    // 创建定时器
    const timer = setInterval(async () => {
      await executeTask()
      
      // 更新任务信息
      const task = runningTasks.value.find(t => t.id === taskId)
      if (task) {
        task.lastRun = new Date().toLocaleString()
        task.nextRun = calculateNextRun(automateForm.value.interval)
      }
    }, automateForm.value.interval * 60 * 1000)
    
    timers.value.set(taskId, timer)
    
    ElMessage.success('定时任务已启动并保存')
  } catch (error) {
    console.error('启动定时任务失败:', error)
    ElMessage.error('启动任务失败: ' + error.message)
  }
}

// 停止单个任务
const stopTask = async (taskId) => {
  const timer = timers.value.get(taskId)
  if (timer) {
    clearInterval(timer)
    timers.value.delete(taskId)
  }
  
  // 从数据库删除任务
  try {
    await axios.delete(`${API_CONFIG.BASE_URL}/autoManagerPageV1/api/auto-manager/task/${taskId}`)
  } catch (error) {
    console.error('删除任务配置失败:', error)
  }
  
  runningTasks.value = runningTasks.value.filter(t => t.id !== taskId)
  ElMessage.success('任务已停止')
}

// 停止所有任务
const stopAllTasks = () => {
  timers.value.forEach(timer => clearInterval(timer))
  timers.value.clear()
  runningTasks.value = []
  ElMessage.success('所有任务已停止')
}

// 计算下次执行时间
const calculateNextRun = (intervalMinutes) => {
  const nextTime = new Date()
  nextTime.setMinutes(nextTime.getMinutes() + intervalMinutes)
  return nextTime.toLocaleString()
}

// 获取目标信息
const getTargetInfo = () => {
  if (automateForm.value.automateType === 'auto_update') {
    return `Steam ID: ${automateForm.value.selectedSteamId}`
  } else {
    const source = dataSources.value.find(s => s.dataID === automateForm.value.selectedDataSource)
    return source ? `${source.dataName} (${source.steamID || '无SteamID'})` : '-'
  }
}

// 添加执行历史
const addExecutionHistory = (record) => {
  executionHistory.value.unshift(record)
  if (executionHistory.value.length > 10) {
    executionHistory.value = executionHistory.value.slice(0, 10)
  }
}

// 重置表单
const handleReset = () => {
  automateForm.value = {
    automateType: '',
    selectedTask: '',
    selectedSteamId: '',
    selectedDataSource: '',
    isScheduled: false,
    interval: 30
  }
}

// 加载已保存的任务
const loadSavedTasks = async () => {
  try {
    const response = await axios.get(`${API_CONFIG.BASE_URL}/autoManagerPageV1/api/auto-manager/tasks`)
    
    if (response.data.success && Array.isArray(response.data.data)) {
      // 恢复已保存的定时任务
      for (const savedTask of response.data.data) {
        if (savedTask.enabled && savedTask.config.isScheduled) {
          // 重新启动定时任务
          const taskInfo = {
            id: savedTask.taskId,
            type: savedTask.automateType === 'auto_update' ? '自动更新数据' : '自动获取数据',
            taskName: savedTask.taskName,
            targetInfo: getTaskTargetInfo(savedTask),
            interval: savedTask.config.interval,
            status: '运行中',
            lastRun: '-',
            nextRun: calculateNextRun(savedTask.config.interval)
          }
          
          runningTasks.value.push(taskInfo)
          
          // 创建定时器
          const timer = setInterval(async () => {
            // 使用保存的配置执行任务
            await executeTaskWithConfig(savedTask)
            
            // 更新任务信息
            const task = runningTasks.value.find(t => t.id === savedTask.taskId)
            if (task) {
              task.lastRun = new Date().toLocaleString()
              task.nextRun = calculateNextRun(savedTask.config.interval)
            }
          }, savedTask.config.interval * 60 * 1000)
          
          timers.value.set(savedTask.taskId, timer)
        }
      }
      
      if (runningTasks.value.length > 0) {
        ElMessage.success(`已恢复 ${runningTasks.value.length} 个定时任务`)
      }
    }
  } catch (error) {
    console.error('加载已保存任务失败:', error)
  }
}

// 使用配置执行任务
const executeTaskWithConfig = async (savedTask) => {
  const startTime = new Date().toLocaleString()
  
  try {
    let result
    const taskType = savedTask.config.selectedTask
    
    if (savedTask.automateType === 'auto_update') {
      const steamId = savedTask.config.selectedSteamId
      
      if (taskType === 'update_steam_inventory') {
        result = await updateSteamInventory(steamId)
      } else if (taskType === 'fetch_yyyp_price') {
        result = await fetchYYYPPrice(steamId)
      } else if (taskType === 'fetch_buff_price') {
        result = await fetchBuffPrice(steamId)
      }
    } else {
      const dataSourceId = savedTask.config.selectedDataSource
      const dataSource = dataSources.value.find(s => s.dataID === dataSourceId)
      
      if (dataSource) {
        if (taskType === 'collect_buff') {
          result = await collectBuffData(dataSource)
        } else if (taskType === 'collect_youpin') {
          result = await collectYoupinData(dataSource)
        }
      }
    }
    
    // 添加到执行历史
    if (result) {
      addExecutionHistory({
        time: startTime,
        type: savedTask.automateType === 'auto_update' ? '自动更新数据' : '自动获取数据',
        taskName: savedTask.taskName,
        targetInfo: getTaskTargetInfo(savedTask),
        result: result.success ? '成功' : '失败',
        message: result.message
      })
    }
  } catch (error) {
    console.error('执行定时任务失败:', error)
    addExecutionHistory({
      time: startTime,
      type: savedTask.automateType === 'auto_update' ? '自动更新数据' : '自动获取数据',
      taskName: savedTask.taskName,
      targetInfo: getTaskTargetInfo(savedTask),
      result: '失败',
      message: error.message
    })
  }
}

// 获取任务目标信息
const getTaskTargetInfo = (savedTask) => {
  if (savedTask.automateType === 'auto_update') {
    return `Steam ID: ${savedTask.config.selectedSteamId}`
  } else {
    const source = dataSources.value.find(s => s.dataID === savedTask.config.selectedDataSource)
    return source ? `${source.dataName} (${source.steamID || '无SteamID'})` : '-'
  }
}

// 组件挂载时加载数据
onMounted(async () => {
  await loadSteamIds()
  await loadDataSources()
  await loadSavedTasks()
})

// 组件卸载时清理定时器
onUnmounted(() => {
  stopAllTasks()
})
</script>

<style scoped>
.automate-management {
  padding: 24px;
  background: transparent;
}

.config-section {
  background: rgba(26, 26, 26, 0.6);
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  border: 1px solid rgba(58, 58, 58, 0.8);
}

.task-list-section,
.history-section {
  background: rgba(26, 26, 26, 0.6);
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  border: 1px solid rgba(58, 58, 58, 0.8);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.task-list-section h3,
.history-section h3 {
  font-size: 18px;
  color: #e8e8e8;
  margin: 0 0 16px 0;
  font-weight: 600;
}

.empty-placeholder {
  padding: 20px 0;
}

/* Element Plus 表单样式调整 */
:deep(.el-form-item__label) {
  color: #e8e8e8;
}

:deep(.el-select) {
  width: 100%;
}

:deep(.el-input__wrapper) {
  background-color: rgba(35, 35, 35, 0.8);
  border-color: rgba(58, 58, 58, 0.8);
}

:deep(.el-input__inner) {
  color: #e8e8e8;
}

:deep(.el-select-dropdown) {
  background-color: rgba(26, 26, 26, 0.98);
  border-color: rgba(58, 58, 58, 0.8);
}

:deep(.el-select-dropdown__item) {
  color: #e8e8e8;
}

:deep(.el-select-dropdown__item:hover) {
  background-color: rgba(64, 158, 255, 0.2);
}

:deep(.el-table) {
  background-color: transparent;
  color: #e8e8e8;
}

:deep(.el-table th.el-table__cell) {
  background-color: rgba(35, 35, 35, 0.8);
  color: #e8e8e8;
  border-color: rgba(58, 58, 58, 0.8);
}

:deep(.el-table tr) {
  background-color: transparent;
}

:deep(.el-table td.el-table__cell) {
  border-color: rgba(58, 58, 58, 0.8);
}

:deep(.el-table__body tr:hover > td) {
  background-color: rgba(64, 158, 255, 0.1) !important;
}

:deep(.el-input-number) {
  width: 100%;
}

:deep(.el-input-number .el-input__wrapper) {
  background-color: rgba(35, 35, 35, 0.8);
  border-color: rgba(58, 58, 58, 0.8);
}

:deep(.el-empty) {
  padding: 20px 0;
}

:deep(.el-empty__description) {
  color: #909399;
}
</style>
