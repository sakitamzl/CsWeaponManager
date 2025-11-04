<template>
  <div class="automate-management">
    <div class="config-section">
      <el-form :model="automateForm" label-width="140px" label-position="left">
        <!-- 任务名称 -->
        <el-form-item label="任务名称">
          <el-input 
            v-model="automateForm.taskName" 
            placeholder="请输入任务名称"
            style="width: 300px"
          />
        </el-form-item>

        <!-- 自动化类型选择 -->
        <el-form-item label="自动化类型">
          <el-select 
            v-model="automateForm.automateType" 
            placeholder="请选择自动化类型"
            style="width: 300px"
            @change="handleTypeChange"
          >
            <el-option label="更新steam库存价格" value="auto_update" />
            <el-option label="获取平台交易记录" value="auto_fetch" />
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

        <!-- Steam账号选择 (仅在自动更新数据时显示，且已选择具体任务) -->
        <el-form-item v-if="automateForm.automateType === 'auto_update' && automateForm.selectedTask" label="Steam账号">
          <el-select 
            v-model="automateForm.selectedSteamConfig" 
            placeholder="请选择Steam账号"
            style="width: 300px"
            filterable
          >
            <el-option 
              v-for="config in currentSteamConfigList" 
              :key="config.dataID" 
              :label="`${config.dataName} (${config.steamID || '无SteamID'})`" 
              :value="config.dataID" 
            />
          </el-select>
        </el-form-item>

        <!-- 数据源选择 (仅在自动获取数据时显示) - 单选 -->
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

        <!-- 执行间隔 -->
        <el-form-item label="执行间隔">
          <el-select 
            v-model="automateForm.interval" 
            placeholder="请选择执行间隔"
            style="width: 300px"
          >
            <el-option label="5分钟" :value="5" />
            <el-option label="15分钟" :value="15" />
            <el-option label="30分钟" :value="30" />
            <el-option label="1小时" :value="60" />
            <el-option label="3小时" :value="180" />
            <el-option label="6小时" :value="360" />
            <el-option label="8小时" :value="480" />
            <el-option label="10小时" :value="600" />
            <el-option label="12小时" :value="720" />
            <el-option label="16小时" :value="960" />
            <el-option label="20小时" :value="1200" />
            <el-option label="24小时" :value="1440" />
          </el-select>
        </el-form-item>

        <!-- 操作按钮 -->
        <el-form-item>
          <el-button type="primary" @click="handleExecute" :loading="executing">
            {{ isEditing ? '更新任务' : '保存定时任务' }}
          </el-button>
          <el-button @click="handleReset">{{ isEditing ? '取消编辑' : '重置' }}</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 任务列表 -->
    <div class="task-list-section">
      <h3>定时任务列表</h3>
      <el-table :data="runningTasks" style="width: 100%">
        <el-table-column prop="type" label="自动化类型" min-width="120" />
        <el-table-column prop="taskName" label="任务名称" min-width="150" />
        <el-table-column prop="targetInfo" label="目标" min-width="200" show-overflow-tooltip />
        <el-table-column prop="interval" label="间隔(分钟)" width="100" align="center" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === '运行中' ? 'success' : 'info'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastRun" label="最后执行时间" min-width="160" />
        <el-table-column prop="nextRun" label="下次执行时间" min-width="160" />
        <el-table-column label="操作" width="220" align="center" fixed="right">
          <template #default="{ row }">
            <el-button 
              v-if="row.status === '已停止'" 
              size="small" 
              type="success" 
              @click="startTask(row)"
            >
              启动
            </el-button>
            <el-button 
              v-else 
              size="small" 
              type="danger" 
              @click="stopTask(row.id)"
            >
              停止
            </el-button>
            <el-button 
              size="small" 
              type="primary" 
              @click="editTask(row)"
              plain
            >
              编辑
            </el-button>
            <el-button 
              size="small" 
              type="danger" 
              @click="deleteTask(row.id)"
              plain
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div v-if="runningTasks.length === 0" class="empty-placeholder">
        <el-empty description="暂无运行中的定时任务" />
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import { API_CONFIG } from '@/config/api.js'

// 表单数据
const automateForm = ref({
  taskName: '', // 任务名称
  automateType: '',
  selectedTask: '',
  selectedSteamConfig: '', // Steam配置的dataID
  selectedDataSource: '', // 单选数据源
  interval: 30
})

// 执行状态
const executing = ref(false)

// 编辑状态
const isEditing = ref(false)
const editingTaskId = ref(null)

// Steam配置列表（key1='steam' 的配置，用于"更新Steam库存"）
const steamConfigList = ref([])

// 悠悠有品配置列表（key1='youpin' 的配置，用于"获取悠悠有品价格"）
const youpinConfigList = ref([])

// BUFF配置列表（key1='buff' 的配置，用于"获取BUFF价格"）
const buffConfigList = ref([])

// 数据源列表
const dataSources = ref([])

// 运行中的任务
const runningTasks = ref([])

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

// 根据所选任务类型返回对应的Steam配置列表
const currentSteamConfigList = computed(() => {
  const selectedTask = automateForm.value.selectedTask
  
  if (selectedTask === 'update_steam_inventory') {
    // 更新Steam库存 - 使用 key1='steam' 的配置
    return steamConfigList.value
  } else if (selectedTask === 'fetch_yyyp_price') {
    // 获取悠悠有品价格 - 使用 key1='youpin' 的配置
    return youpinConfigList.value
  } else if (selectedTask === 'fetch_buff_price') {
    // 获取BUFF价格 - 使用 key1='buff' 的配置
    return buffConfigList.value
  }
  
  return []
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

// 加载 Steam 配置列表（key1='steam'，用于"更新Steam库存"）
const loadSteamConfigs = async () => {
  try {
    const response = await axios.get(`${API_CONFIG.BASE_URL}/webInventoryV1/steam_ids`)
    console.log('Steam配置API响应:', response.data)
    
    if (response.data && response.data.success && Array.isArray(response.data.data)) {
      // 保存完整的对象数组（包含 dataID, dataName, steamID, item_count）
      steamConfigList.value = response.data.data
      console.log('已加载Steam配置列表:', steamConfigList.value)
    }
  } catch (error) {
    console.error('加载Steam配置列表失败:', error)
    ElMessage.error('加载Steam账号列表失败: ' + error.message)
  }
}

// 加载悠悠有品配置列表（key1='youpin'）
const loadYoupinConfigs = async () => {
  try {
    const response = await axios.get(`${API_CONFIG.BASE_URL}/dataSourcePageV1/api/datasource`)
    console.log('数据源API响应:', response.data)
    
    if (response.data.success && Array.isArray(response.data.data)) {
      // 筛选 key1='youpin' 的配置
      youpinConfigList.value = response.data.data
        .filter(item => item.type === 'youpin')
        .map(item => ({
          dataID: item.dataID,
          dataName: item.dataName,
          steamID: item.steamID
        }))
      console.log('已加载悠悠有品配置列表:', youpinConfigList.value)
    }
  } catch (error) {
    console.error('加载悠悠有品配置列表失败:', error)
    ElMessage.error('加载悠悠有品配置列表失败: ' + error.message)
  }
}

// 加载BUFF配置列表（key1='buff'）
const loadBuffConfigs = async () => {
  try {
    const response = await axios.get(`${API_CONFIG.BASE_URL}/dataSourcePageV1/api/datasource`)
    console.log('数据源API响应:', response.data)
    
    if (response.data.success && Array.isArray(response.data.data)) {
      // 筛选 key1='buff' 的配置
      buffConfigList.value = response.data.data
        .filter(item => item.type === 'buff')
        .map(item => ({
          dataID: item.dataID,
          dataName: item.dataName,
          steamID: item.steamID
        }))
      console.log('已加载BUFF配置列表:', buffConfigList.value)
    }
  } catch (error) {
    console.error('加载BUFF配置列表失败:', error)
    ElMessage.error('加载BUFF配置列表失败: ' + error.message)
  }
}

// 加载数据源列表
const loadDataSources = async () => {
  try {
    const response = await axios.get(`${API_CONFIG.BASE_URL}/dataSourcePageV1/api/datasource`)
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
  automateForm.value.selectedSteamConfig = ''
  automateForm.value.selectedDataSource = ''
}

// 执行任务
const handleExecute = async () => {
  // 验证表单
  if (!automateForm.value.taskName || !automateForm.value.taskName.trim()) {
    ElMessage.warning('请输入任务名称')
    return
  }
  
  if (!automateForm.value.automateType) {
    ElMessage.warning('请选择自动化类型')
    return
  }
  
  if (!automateForm.value.selectedTask) {
    ElMessage.warning('请选择任务')
    return
  }

  if (automateForm.value.automateType === 'auto_update') {
    if (!automateForm.value.selectedSteamConfig) {
      ElMessage.warning('请选择Steam账号')
      return
    }
  } else {
    if (!automateForm.value.selectedDataSource) {
      ElMessage.warning('请选择数据源')
      return
    }
  }

  // 如果是编辑模式,执行更新;否则创建新任务
  if (isEditing.value) {
    updateTask()
  } else {
    startScheduledTask()
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
      // 自动获取数据任务 - 支持多个数据源
      const dataSourceIds = automateForm.value.selectedDataSources
      const results = []
      
      for (const dataSourceId of dataSourceIds) {
        const dataSource = dataSources.value.find(s => s.dataID === dataSourceId)
        
        if (dataSource) {
          let singleResult
          if (taskType === 'collect_buff') {
            singleResult = await collectBuffData(dataSource)
          } else if (taskType === 'collect_youpin') {
            singleResult = await collectYoupinData(dataSource)
          }
          results.push({ source: dataSource.dataName, ...singleResult })
        }
      }
      
      // 汇总结果
      const successCount = results.filter(r => r.success).length
      const totalCount = results.length
      result = {
        success: successCount > 0,
        message: `完成 ${successCount}/${totalCount} 个数据源采集`
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
  // 检查是否存在重复任务
  const isDuplicate = runningTasks.value.some(task => {
    // 比较自动化类型和具体任务
    if (task.config.selectedTask !== automateForm.value.selectedTask) {
      return false
    }
    
    // 比较目标账号/数据源
    if (automateForm.value.automateType === 'auto_update') {
      // 更新类型：比较Steam配置ID
      return task.config.selectedSteamConfig === automateForm.value.selectedSteamConfig
    } else {
      // 采集类型：比较数据源ID
      return task.config.selectedDataSource === automateForm.value.selectedDataSource
    }
  })
  
  if (isDuplicate) {
    ElMessage.warning('已存在相同的自动化任务（任务类型和目标账号相同），无法创建重复任务')
    return
  }
  
  // 先保存任务配置到数据库
  try {
    const config = {
      selectedTask: automateForm.value.selectedTask,
      selectedSteamConfig: automateForm.value.selectedSteamConfig, // Steam配置的dataID
      selectedDataSource: automateForm.value.selectedDataSource, // 单个数据源
      interval: automateForm.value.interval
    }
    
    const response = await axios.post(
      `${API_CONFIG.BASE_URL}/autoManagerPageV1/api/auto-manager/task`,
      {
        taskName: automateForm.value.taskName, // 使用用户输入的任务名称
        automateType: automateForm.value.automateType,
        config: config,
        enabled: false // 创建时默认停止状态
      }
    )
    
    if (!response.data.success) {
      ElMessage.error('保存任务配置失败: ' + response.data.message)
      return
    }
    
    const taskId = response.data.taskId
    
    const taskInfo = {
      id: taskId,
      type: automateForm.value.automateType === 'auto_update' ? '更新steam库存价格' : '获取平台交易记录',
      taskName: automateForm.value.taskName, // 使用用户输入的任务名称
      targetInfo: getTargetInfo(),
      interval: automateForm.value.interval,
      status: '已停止',
      lastRun: '-',
      nextRun: '-',
      config: config // 保存配置以便后续启动
    }
    
    ElMessage.success('定时任务已保存(停止状态)')
    
    // 清空表单
    handleReset()
    
    // 重新加载任务列表,获取完整的任务信息(包括真实ID)
    await loadSavedTasks()
  } catch (error) {
    console.error('保存定时任务失败:', error)
    ElMessage.error('保存任务失败: ' + error.message)
  }
}

// 启动单个任务
// 启动任务 (后端执行)
const startTask = async (task) => {
  try {
    // 验证任务ID
    if (!task.id || task.id === 0) {
      ElMessage.warning('任务正在初始化,请稍后再试')
      return
    }
    
    // 调用后端API切换状态为启用
    const response = await axios.post(`${API_CONFIG.BASE_URL}/autoManagerPageV1/api/auto-manager/task/${task.id}/toggle`)
    
    if (response.data.success) {
      // 更新前端显示
      task.status = '运行中'
      
      // 使用后端返回的执行时间
      if (response.data.nextRun) {
        task.nextRun = response.data.nextRun
      } else {
        task.nextRun = '即将执行'
      }
      
      if (response.data.lastRun) {
        task.lastRun = response.data.lastRun
      }
      
      ElMessage.success('任务已启用,后台将立即执行一次')
    } else {
      ElMessage.error('启动任务失败: ' + response.data.message)
    }
  } catch (error) {
    console.error('启动任务失败:', error)
    
    if (error.response && error.response.status === 404) {
      ElMessage.error('任务不存在,请刷新页面')
    } else {
      ElMessage.error('启动任务失败: ' + (error.response?.data?.message || error.message))
    }
  }
}

// 停止任务 (后端执行)
const stopTask = async (taskId) => {
  try {
    // 调用后端API停止任务
    const response = await axios.post(`${API_CONFIG.BASE_URL}/autoManagerPageV1/api/auto-manager/task/${taskId}/toggle`)
    
    if (response.data.success) {
      // 更新前端显示
      const task = runningTasks.value.find(t => t.id === taskId)
      if (task) {
        task.status = '已停止'
        task.nextRun = '-'
      }
      
      ElMessage.success('任务已停止')
    } else {
      ElMessage.error('停止任务失败: ' + response.data.message)
    }
  } catch (error) {
    console.error('停止任务失败:', error)
    ElMessage.error('停止任务失败: ' + error.message)
  }
}

// 编辑任务
const editTask = (task) => {
  // 填充表单
  automateForm.value = {
    taskName: task.taskName,
    automateType: task.type === '更新steam库存价格' ? 'auto_update' : 'auto_fetch',
    selectedTask: task.config.selectedTask,
    selectedSteamConfig: task.config.selectedSteamConfig || '',
    selectedDataSource: task.config.selectedDataSource || '',
    interval: task.interval
  }
  
  // 设置编辑状态
  isEditing.value = true
  editingTaskId.value = task.id
  
  // 滚动到表单顶部
  window.scrollTo({ top: 0, behavior: 'smooth' })
  
  ElMessage.info('已加载任务配置,修改后点击"更新任务"保存')
}

// 更新任务配置
const updateTask = async () => {
  executing.value = true
  
  // 检查是否存在重复任务（排除当前正在编辑的任务）
  const isDuplicate = runningTasks.value.some(task => {
    // 跳过当前正在编辑的任务
    if (task.id === editingTaskId.value) {
      return false
    }
    
    // 比较自动化类型和具体任务
    if (task.config.selectedTask !== automateForm.value.selectedTask) {
      return false
    }
    
    // 比较目标账号/数据源
    if (automateForm.value.automateType === 'auto_update') {
      // 更新类型：比较Steam配置ID
      return task.config.selectedSteamConfig === automateForm.value.selectedSteamConfig
    } else {
      // 采集类型：比较数据源ID
      return task.config.selectedDataSource === automateForm.value.selectedDataSource
    }
  })
  
  if (isDuplicate) {
    ElMessage.warning('已存在相同的自动化任务（任务类型和目标账号相同），无法更新为重复任务')
    executing.value = false
    return
  }
  
  try {
    const taskConfig = {
      taskName: automateForm.value.taskName,
      automateType: automateForm.value.automateType,
      config: {
        selectedTask: automateForm.value.selectedTask,
        selectedSteamConfig: automateForm.value.selectedSteamConfig,
        selectedDataSource: automateForm.value.selectedDataSource,
        interval: automateForm.value.interval
      }
    }
    
    const response = await axios.put(
      `${API_CONFIG.BASE_URL}/autoManagerPageV1/api/auto-manager/task/${editingTaskId.value}`,
      taskConfig
    )
    
    if (response.data.success) {
      // 更新任务列表中的任务信息
      const taskIndex = runningTasks.value.findIndex(t => t.id === editingTaskId.value)
      if (taskIndex !== -1) {
        const task = runningTasks.value[taskIndex]
        
        task.taskName = automateForm.value.taskName
        task.type = automateForm.value.automateType === 'auto_update' ? '更新steam库存价格' : '获取平台交易记录'
        task.targetInfo = getTaskTargetInfo({
          automateType: automateForm.value.automateType,
          config: taskConfig.config
        })
        task.interval = automateForm.value.interval
        task.config = taskConfig.config
        
        // 后端会自动重新加载任务(如果正在运行会重启)
        if (task.status === '运行中') {
          task.nextRun = calculateNextRun(automateForm.value.interval)
        }
      }
      
      ElMessage.success('任务配置已更新,后端已自动重新加载')
      handleReset()
    } else {
      ElMessage.error('更新任务失败: ' + (response.data.message || '未知错误'))
    }
  } catch (error) {
    console.error('更新任务失败:', error)
    ElMessage.error('更新任务失败: ' + error.message)
  } finally {
    executing.value = false
  }
}

// 删除任务
const deleteTask = async (taskId) => {
  // 二次确认
  ElMessageBox.confirm(
    '确定要删除这个定时任务吗？删除后将无法恢复。',
    '删除确认',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
      buttonSize: 'default'
    }
  ).then(async () => {
    try {
      // 调用后端API删除任务 (后端会自动停止定时器)
      const response = await axios.delete(`${API_CONFIG.BASE_URL}/autoManagerPageV1/api/auto-manager/task/${taskId}`)
      
      // 从列表中移除
      runningTasks.value = runningTasks.value.filter(t => t.id !== taskId)
      
      ElMessage.success('任务已删除')
    } catch (error) {
      console.error('删除任务失败:', error)
      
      // 如果是404错误,说明任务已经不存在了
      if (error.response && error.response.status === 404) {
        // 仍然从前端列表中移除
        runningTasks.value = runningTasks.value.filter(t => t.id !== taskId)
        ElMessage.warning('任务已不存在,已从列表中移除')
      } else {
        ElMessage.error('删除任务失败: ' + (error.response?.data?.message || error.message))
      }
    }
  }).catch(() => {
    // 用户取消删除
    ElMessage.info('已取消删除')
  })
}

// 移除：停止所有任务功能已从UI中删除

// 计算下次执行时间
const calculateNextRun = (intervalMinutes) => {
  const nextTime = new Date()
  nextTime.setMinutes(nextTime.getMinutes() + intervalMinutes)
  return nextTime.toLocaleString()
}

// 获取目标信息
const getTargetInfo = () => {
  if (automateForm.value.automateType === 'auto_update') {
    // 根据选择的任务类型从对应的配置列表查找
    const selectedTask = automateForm.value.selectedTask
    let configList = []
    
    if (selectedTask === 'update_steam_inventory') {
      configList = steamConfigList.value
    } else if (selectedTask === 'fetch_yyyp_price') {
      configList = youpinConfigList.value
    } else if (selectedTask === 'fetch_buff_price') {
      configList = buffConfigList.value
    }
    
    const config = configList.find(c => c.dataID === automateForm.value.selectedSteamConfig)
    return config ? `${config.dataName} (${config.steamID || '无SteamID'})` : '-'
  } else {
    const source = dataSources.value.find(s => s.dataID === automateForm.value.selectedDataSource)
    return source ? `${source.dataName} (${source.steamID || '无SteamID'})` : '-'
  }
}


// 重置表单
const handleReset = () => {
  automateForm.value = {
    taskName: '',
    automateType: '',
    selectedTask: '',
    selectedSteamConfig: '',
    selectedDataSource: '',
    interval: 30
  }
  
  // 清除编辑状态
  isEditing.value = false
  editingTaskId.value = null
}

// 加载已保存的任务 (任务在后端运行)
const loadSavedTasks = async () => {
  try {
    const response = await axios.get(`${API_CONFIG.BASE_URL}/autoManagerPageV1/api/auto-manager/tasks`)
    
    if (response.data.success && Array.isArray(response.data.data)) {
      let enabledCount = 0
      
      // 清空现有任务列表
      runningTasks.value = []
      
      // 加载所有任务 (包括已停止的)
      for (const savedTask of response.data.data) {
        const taskInfo = {
          id: savedTask.taskId,
          type: savedTask.automateType === 'auto_update' ? '更新steam库存价格' : '获取平台交易记录',
          taskName: savedTask.taskName,
          targetInfo: getTaskTargetInfo(savedTask),
          interval: savedTask.config.interval,
          status: savedTask.enabled ? '运行中' : '已停止',
          lastRun: savedTask.lastRun || '-',
          nextRun: savedTask.nextRun || (savedTask.enabled ? calculateNextRun(savedTask.config.interval) : '-'),
          config: savedTask.config // 保存配置供后续使用
        }
        
        runningTasks.value.push(taskInfo)
        
        if (savedTask.enabled) {
          enabledCount++
        }
      }
      
      // 只在首次加载时显示成功消息
      if (runningTasks.value.length > 0 && !isEditing.value) {
        console.log(`已加载 ${runningTasks.value.length} 个任务，其中 ${enabledCount} 个正在后台运行`)
      }
    }
  } catch (error) {
    console.error('加载已保存任务失败:', error)
  }
}

// 使用配置执行任务 (支持从数据库加载的任务和手动启动的任务)
const executeTaskWithConfig = async (taskOrSavedTask) => {
  const startTime = new Date().toLocaleString()
  
  try {
    let result
    // 兼容两种数据结构
    const config = taskOrSavedTask.config || taskOrSavedTask
    const taskType = config.selectedTask
    
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
      // 支持多个数据源
      const dataSourceIds = savedTask.config.selectedDataSources || []
      const results = []
      
      for (const dataSourceId of dataSourceIds) {
        const dataSource = dataSources.value.find(s => s.dataID === dataSourceId)
        
        if (dataSource) {
          let singleResult
          if (taskType === 'collect_buff') {
            singleResult = await collectBuffData(dataSource)
          } else if (taskType === 'collect_youpin') {
            singleResult = await collectYoupinData(dataSource)
          }
          if (singleResult) {
            results.push({ source: dataSource.dataName, ...singleResult })
          }
        }
      }
      
      // 汇总结果
      if (results.length > 0) {
        const successCount = results.filter(r => r.success).length
        const totalCount = results.length
        result = {
          success: successCount > 0,
          message: `完成 ${successCount}/${totalCount} 个数据源采集`
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

// 获取任务目标信息 (详细显示)
const getTaskTargetInfo = (savedTask) => {
  if (savedTask.automateType === 'auto_update') {
    // 更新类型:显示Steam配置名称和ID
    const selectedId = savedTask.config.selectedSteamConfig
    const selectedTask = savedTask.config.selectedTask
    
    if (!selectedId) {
      return '-'
    }
    
    // 根据任务类型从对应的配置列表查找
    let configList = []
    if (selectedTask === 'update_steam_inventory') {
      configList = steamConfigList.value
    } else if (selectedTask === 'fetch_yyyp_price') {
      configList = youpinConfigList.value
    } else if (selectedTask === 'fetch_buff_price') {
      configList = buffConfigList.value
    }
    
    const config = configList.find(c => c.dataID === selectedId)
    if (!config) {
      return '-'
    }
    
    // 显示格式: 配置名称 (SteamID)
    return config.steamID ? `${config.dataName} (${config.steamID})` : config.dataName
  } else {
    // 获取数据类型:只显示数据源名称和SteamID
    const selectedId = savedTask.config.selectedDataSource
    
    if (!selectedId) {
      return '-'
    }
    
    // 查找数据源
    const source = dataSources.value.find(s => s.dataID === selectedId)
    if (!source) {
      return '-'
    }
    
    // 显示格式: 数据源名称 (SteamID)
    return source.steamID ? `${source.dataName} (${source.steamID})` : source.dataName
  }
}

// 组件挂载时加载数据
onMounted(async () => {
  await loadSteamConfigs()
  await loadYoupinConfigs()
  await loadBuffConfigs()
  await loadDataSources()
  await loadSavedTasks()
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

.task-list-section h3 {
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
