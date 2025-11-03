<template>
  <div class="automate-management">
    <div class="config-section">
      <el-form :model="automateForm" label-width="120px" label-position="left">
        <!-- 自动化类型选择 -->
        <el-form-item label="自动化类型">
          <el-select 
            v-model="automateForm.automateType" 
            placeholder="请选择自动化类型"
            style="width: 300px"
          >
            <el-option label="自动更新数据" value="auto_update" />
            <el-option label="自动获取数据" value="auto_fetch" />
          </el-select>
        </el-form-item>

        <!-- 第二个下拉框 - 待补充 -->
        <el-form-item label="[待定义]">
          <el-select 
            v-model="automateForm.secondOption" 
            placeholder="请选择"
            style="width: 300px"
          >
            <el-option label="选项1" value="option1" />
            <el-option label="选项2" value="option2" />
          </el-select>
        </el-form-item>

        <!-- 操作按钮 -->
        <el-form-item>
          <el-button type="primary" @click="handleSave">保存配置</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 任务列表 -->
    <div class="task-list-section">
      <h3>自动化任务列表</h3>
      <el-table :data="taskList" style="width: 100%">
        <el-table-column prop="type" label="类型" width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === '运行中' ? 'success' : 'info'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastRun" label="最后运行时间" width="180" />
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button size="small" type="primary">启动</el-button>
            <el-button size="small" type="danger">停止</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

// 表单数据
const automateForm = ref({
  automateType: '',
  secondOption: ''
})

// 任务列表
const taskList = ref([])

// 保存配置
const handleSave = () => {
  if (!automateForm.value.automateType) {
    ElMessage.warning('请选择自动化类型')
    return
  }
  
  ElMessage.success('配置保存成功')
  console.log('保存的配置:', automateForm.value)
}

// 重置表单
const handleReset = () => {
  automateForm.value = {
    automateType: '',
    secondOption: ''
  }
}
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

.task-list-section {
  background: rgba(26, 26, 26, 0.6);
  border-radius: 8px;
  padding: 24px;
  border: 1px solid rgba(58, 58, 58, 0.8);
}

.task-list-section h3 {
  font-size: 18px;
  color: #e8e8e8;
  margin: 0 0 16px 0;
  font-weight: 600;
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
</style>

