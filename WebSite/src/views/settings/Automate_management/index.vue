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
            <el-option label="更新steam库存价格" value="auto_update" />
            <el-option label="获取平台交易记录" value="auto_fetch" />
            <el-option label="更新饰品平台映射价格" value="auto_platform_price" />
            <el-option label="自动搜素饰品" value="auto_search_weapon" />
            <el-option label="更新steam认证" value="auto_refresh_auth" />
          </el-select>
        </el-form-item>

        <!-- 任务名称 -->
        <el-form-item label="任务名称">
          <el-input 
            v-model="automateForm.taskName" 
            placeholder="请输入任务名称"
            style="width: 300px"
          />
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

        <!-- Steam账号选择 (仅在自动更新数据或更新Steam认证时显示) -->
        <el-form-item
          v-if="(automateForm.automateType === 'auto_update' && automateForm.selectedTask) || automateForm.automateType === 'auto_refresh_auth'"
          label="Steam账号"
        >
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
        <el-form-item v-if="['auto_fetch', 'auto_platform_price'].includes(automateForm.automateType)" label="数据源">
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

        <!-- 搜索配置选择 (仅在自动搜素饰品时显示) -->
        <el-form-item
          v-if="automateForm.automateType === 'auto_search_weapon' && automateForm.selectedTask"
          label="搜索配置"
        >
          <el-select
            v-model="automateForm.selectedSearchConfig"
            placeholder="请选择搜索配置"
            style="width: 300px"
            filterable
          >
            <el-option
              v-for="config in currentSearchConfigList"
              :key="config.dataID"
              :label="`${config.dataName}${config.platformType ? ' - ' + config.platformType : ''}`"
              :value="config.dataID"
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
            <el-option label="12小时" :value="720" />
            <el-option label="24小时" :value="1440" />
            <template #footer>
              <div class="custom-interval-footer">
                <span>手动输入(分钟)</span>
                <el-input-number 
                  v-model="customInterval"
                  :min="1"
                  :step="5"
                  controls-position="right"
                  size="small"
                  style="width: 160px"
                />
                <el-button type="primary" size="small" @click="applyCustomInterval">应用</el-button>
              </div>
            </template>
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
      <div class="task-list-header">
        <h3>定时任务列表</h3>
        <div class="task-list-actions">
          <el-button 
            type="success" 
            size="small" 
            :disabled="bulkStarting || runningTasks.length === 0"
            :loading="bulkStarting"
            @click="startAllTasks"
          >
            启动全部
          </el-button>
          <el-button 
            type="danger" 
            size="small" 
            plain
            :disabled="bulkStopping || runningTasks.length === 0"
            :loading="bulkStopping"
            @click="stopAllTasks"
          >
            停止全部
          </el-button>
        </div>
      </div>
      <el-table :data="runningTasks" style="width: 100%">
        <el-table-column prop="type" label="自动化类型" min-width="120" />
        <el-table-column prop="taskName" label="任务名称" min-width="150" />
        <el-table-column prop="targetInfo" label="使用账号" min-width="200" show-overflow-tooltip />
        <el-table-column prop="interval" label="间隔(分钟)" width="120" align="center">
          <template #default="{ row }">
            {{ formatInterval(row.interval) }}
          </template>
        </el-table-column>
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
import { useAutomateManagement } from './useAutomateManagement.js'

const {
  automateForm,
  customInterval,
  executing,
  bulkStarting,
  bulkStopping,
  isEditing,
  steamConfigList,
  youpinConfigList,
  buffConfigList,
  dataSources,
  runningTasks,
  renameSearchConfigList,
  pendantSearchConfigList,
  updateTasks,
  fetchTasks,
  platformPriceTasks,
  searchWeaponTasks,
  secondSelectLabel,
  currentSteamConfigList,
  currentSearchConfigList,
  availableTasks,
  filteredDataSources,
  formatInterval,
  handleTypeChange,
  applyCustomInterval,
  handleExecute,
  handleReset,
  startTask,
  stopTask,
  startAllTasks,
  stopAllTasks,
  editTask,
  deleteTask
} = useAutomateManagement()
</script>

<style scoped src="./styles.css"></style>
