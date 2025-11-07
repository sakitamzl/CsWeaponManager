<template>
  <div>
    <div class="settings-container">
      <div class="settings-section">
        <h3>登录设置</h3>
        <el-form :model="basicSettings" label-width="150px">
          <el-form-item label="启用登录验证">
            <el-switch 
              v-model="basicSettings.enableLogin" 
              active-text="开启"
              inactive-text="关闭"
              @change="handleLoginToggle"
            />
            <div class="form-tip">开启后需要用户名和密码才能访问系统</div>
          </el-form-item>
          
          <el-form-item label="用户名" v-if="basicSettings.enableLogin">
            <el-input 
              v-model="basicSettings.username" 
              style="width: 300px;" 
              placeholder="请输入用户名"
            />
          </el-form-item>
          
          <el-form-item label="密码" v-if="basicSettings.enableLogin">
            <el-input 
              v-model="basicSettings.password" 
              type="password" 
              show-password
              style="width: 300px;" 
              placeholder="请输入密码"
            />
          </el-form-item>
          
          <el-form-item label="允许外网访问">
            <el-switch 
              v-model="basicSettings.allowExternalAccess" 
              active-text="开启"
              inactive-text="关闭"
              @change="handleExternalAccessToggle"
            />
            <div class="form-tip">开启后可以从外网访问系统（需要配置防火墙和端口转发）</div>
          </el-form-item>
        </el-form>
      </div>

      <!-- 保存按钮 -->
      <div class="save-actions">
        <el-button type="primary" size="large" @click="saveSettings">保存设置</el-button>
        <el-button size="large" @click="resetForm">重置</el-button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'SystemSettings',
  setup() {
    const basicSettings = ref({
      enableLogin: false,
      username: '',
      password: '',
      allowExternalAccess: false
    })

    const loadSettings = async () => {
      try {
        // 这里应该调用API加载设置
        // const response = await fetch('/api/settings')
        // const data = await response.json()
        
        // 临时模拟数据
        basicSettings.value = {
          enableLogin: false,
          username: '',
          password: '',
          allowExternalAccess: false
        }
      } catch (error) {
        console.error('加载设置失败:', error)
        ElMessage.error('加载设置失败')
      }
    }

    const handleLoginToggle = (value) => {
      if (value) {
        ElMessage.info('已开启登录验证，请设置用户名和密码')
      } else {
        ElMessage.warning('已关闭登录验证，系统将无需登录即可访问')
      }
    }

    const handleExternalAccessToggle = (value) => {
      if (value) {
        ElMessageBox.confirm(
          '开启外网访问可能存在安全风险，建议同时开启登录验证。确定要开启吗？',
          '安全提示',
          {
            confirmButtonText: '确定开启',
            cancelButtonText: '取消',
            type: 'warning'
          }
        ).then(() => {
          ElMessage.success('已开启外网访问')
        }).catch(() => {
          basicSettings.value.allowExternalAccess = false
        })
      } else {
        ElMessage.info('已关闭外网访问，仅允许局域网访问')
      }
    }

    const saveSettings = async () => {
      try {
        // 这里应该调用API保存设置
        // await fetch('/api/settings', {
        //   method: 'POST',
        //   body: JSON.stringify({
        //     basic: basicSettings.value
        //   })
        // })
        
        ElMessage.success('设置保存成功')
      } catch (error) {
        console.error('保存设置失败:', error)
        ElMessage.error('保存设置失败')
      }
    }

    const resetForm = () => {
      ElMessageBox.confirm('确定要重置当前设置吗？', '确认重置', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        loadSettings()
        ElMessage.success('设置已重置')
      })
    }

    onMounted(() => {
      loadSettings()
    })

    return {
      basicSettings,
      saveSettings,
      resetForm,
      handleLoginToggle,
      handleExternalAccessToggle
    }
  }
}
</script>

<style scoped>
.settings-container {
  width: 100%;
  padding: clamp(1rem, 3vw, 1.5rem);
}

.settings-section {
  padding: clamp(1rem, 3vw, 1.25rem) 0;
}

.settings-section h3 {
  margin-bottom: clamp(1rem, 3vw, 1.25rem);
  color: #fff;
  font-size: clamp(1.125rem, 2vw, 1.25rem);
}

.save-actions {
  margin-top: clamp(1.5rem, 4vw, 1.875rem);
  text-align: center;
  padding-top: clamp(1rem, 3vw, 1.25rem);
  border-top: 1px solid #333;
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

:deep(.el-button) {
  font-size: clamp(0.625rem, 1vw, 0.75rem);
  padding: clamp(0.375rem, 1vw, 0.5rem) clamp(0.75rem, 2vw, 1rem);
}

:deep(.el-form-item) {
  margin-bottom: clamp(1rem, 2.5vw, 1.125rem);
}

.form-tip {
  margin-top: 0.5rem;
  font-size: clamp(0.625rem, 1vw, 0.75rem);
  color: #999;
  line-height: 1.5;
}

:deep(.el-switch__label) {
  color: #ccc;
  font-size: clamp(0.75rem, 1.2vw, 0.875rem);
}

:deep(.el-switch__label.is-active) {
  color: #4CAF50;
}

@media (max-width: 768px) {
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
</style>

