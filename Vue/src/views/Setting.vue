<template>
  <div>
    <h1 class="page-title">⚙️ 设置</h1>
    
    <div class="settings-container">
      <el-tabs v-model="activeTab" type="border-card">
        <!-- 基本设置 -->
        <el-tab-pane label="基本设置" name="basic">
          <div class="settings-section">
            <h3>账户设置</h3>
            <el-form :model="basicSettings" label-width="120px">
              <el-form-item label="用户名">
                <el-input v-model="basicSettings.username" style="width: 300px;" />
              </el-form-item>
              <el-form-item label="邮箱">
                <el-input v-model="basicSettings.email" style="width: 300px;" />
              </el-form-item>
              <el-form-item label="Steam ID">
                <el-input v-model="basicSettings.steamId" style="width: 300px;" />
              </el-form-item>
              <el-form-item label="默认货币">
                <el-select v-model="basicSettings.currency" style="width: 300px;">
                  <el-option label="人民币 (CNY)" value="CNY" />
                  <el-option label="美元 (USD)" value="USD" />
                  <el-option label="欧元 (EUR)" value="EUR" />
                </el-select>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- API设置 -->
        <el-tab-pane label="API设置" name="api">
          <div class="settings-section">
            <h3>第三方平台API配置</h3>
            <el-form :model="apiSettings" label-width="120px">
              <el-form-item label="BUFF API Key">
                <el-input 
                  v-model="apiSettings.buffApiKey" 
                  type="password" 
                  show-password
                  style="width: 400px;" 
                  placeholder="请输入BUFF API Key"
                />
              </el-form-item>
              <el-form-item label="Steam API Key">
                <el-input 
                  v-model="apiSettings.steamApiKey" 
                  type="password" 
                  show-password
                  style="width: 400px;" 
                  placeholder="请输入Steam API Key"
                />
              </el-form-item>
              <el-form-item label="悠悠有品Token">
                <el-input 
                  v-model="apiSettings.youyoupinToken" 
                  type="password" 
                  show-password
                  style="width: 400px;" 
                  placeholder="请输入悠悠有品Token"
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="testApiConnections">测试API连接</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- 通知设置 -->
        <el-tab-pane label="通知设置" name="notification">
          <div class="settings-section">
            <h3>消息通知</h3>
            <el-form :model="notificationSettings" label-width="150px">
              <el-form-item label="价格变动通知">
                <el-switch v-model="notificationSettings.priceAlert" />
              </el-form-item>
              <el-form-item label="交易完成通知">
                <el-switch v-model="notificationSettings.tradeComplete" />
              </el-form-item>
              <el-form-item label="库存更新通知">
                <el-switch v-model="notificationSettings.inventoryUpdate" />
              </el-form-item>
              <el-form-item label="出租到期提醒">
                <el-switch v-model="notificationSettings.rentExpire" />
              </el-form-item>
              <el-form-item label="邮件通知">
                <el-switch v-model="notificationSettings.emailNotify" />
              </el-form-item>
              <el-form-item label="通知邮箱" v-if="notificationSettings.emailNotify">
                <el-input v-model="notificationSettings.notifyEmail" style="width: 300px;" />
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- 数据管理 -->
        <el-tab-pane label="数据管理" name="data">
          <div class="settings-section">
            <h3>数据备份与导出</h3>
            <div class="grid grid-2">
              <div class="action-card">
                <h4>数据备份</h4>
                <p>备份所有交易数据和设置</p>
                <el-button type="primary" @click="handleBackup">创建备份</el-button>
              </div>
              <div class="action-card">
                <h4>数据导出</h4>
                <p>导出交易记录为Excel文件</p>
                <el-button type="success" @click="handleExport">导出数据</el-button>
              </div>
              <div class="action-card">
                <h4>清理缓存</h4>
                <p>清理临时文件和缓存数据</p>
                <el-button type="warning" @click="handleClearCache">清理缓存</el-button>
              </div>
              <div class="action-card">
                <h4>重置设置</h4>
                <p>恢复所有设置为默认值</p>
                <el-button type="danger" @click="handleReset">重置设置</el-button>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 系统信息 -->
        <el-tab-pane label="系统信息" name="system">
          <div class="settings-section">
            <h3>系统状态</h3>
            <div class="system-info">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="应用版本">{{ systemInfo.version }}</el-descriptions-item>
                <el-descriptions-item label="最后更新">{{ systemInfo.lastUpdate }}</el-descriptions-item>
                <el-descriptions-item label="数据库状态">
                  <el-tag :type="systemInfo.dbStatus === '正常' ? 'success' : 'danger'">
                    {{ systemInfo.dbStatus }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="API状态">
                  <el-tag :type="systemInfo.apiStatus === '正常' ? 'success' : 'danger'">
                    {{ systemInfo.apiStatus }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="总交易记录">{{ systemInfo.totalTrades }}</el-descriptions-item>
                <el-descriptions-item label="数据库大小">{{ systemInfo.dbSize }}</el-descriptions-item>
              </el-descriptions>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>

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
  name: 'Setting',
  setup() {
    const activeTab = ref('basic')
    
    const basicSettings = ref({
      username: '',
      email: '',
      steamId: '',
      currency: 'CNY'
    })

    const apiSettings = ref({
      buffApiKey: '',
      steamApiKey: '',
      youyoupinToken: ''
    })

    const notificationSettings = ref({
      priceAlert: true,
      tradeComplete: true,
      inventoryUpdate: false,
      rentExpire: true,
      emailNotify: false,
      notifyEmail: ''
    })

    const systemInfo = ref({
      version: '1.0.0',
      lastUpdate: '2025-01-19',
      dbStatus: '正常',
      apiStatus: '正常',
      totalTrades: 245,
      dbSize: '15.6 MB'
    })

    const loadSettings = async () => {
      try {
        // 这里应该调用API加载设置
        // const response = await fetch('/api/settings')
        // const data = await response.json()
        
        // 临时模拟数据
        basicSettings.value = {
          username: 'CSPlayer123',
          email: 'user@example.com',
          steamId: '76561198123456789',
          currency: 'CNY'
        }
      } catch (error) {
        console.error('加载设置失败:', error)
        ElMessage.error('加载设置失败')
      }
    }

    const saveSettings = async () => {
      try {
        // 这里应该调用API保存设置
        // await fetch('/api/settings', {
        //   method: 'POST',
        //   body: JSON.stringify({
        //     basic: basicSettings.value,
        //     api: apiSettings.value,
        //     notification: notificationSettings.value
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

    const testApiConnections = async () => {
      ElMessage.info('正在测试API连接...')
      // 这里应该调用API测试连接
      setTimeout(() => {
        ElMessage.success('API连接测试完成')
      }, 2000)
    }

    const handleBackup = async () => {
      ElMessage.info('正在创建备份...')
      // 这里应该调用API创建备份
      setTimeout(() => {
        ElMessage.success('备份创建成功')
      }, 1500)
    }

    const handleExport = async () => {
      ElMessage.info('正在导出数据...')
      // 这里应该调用API导出数据
      setTimeout(() => {
        ElMessage.success('数据导出成功')
      }, 2000)
    }

    const handleClearCache = async () => {
      ElMessageBox.confirm('确定要清理缓存吗？', '确认清理', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        ElMessage.info('正在清理缓存...')
        // 这里应该调用API清理缓存
        setTimeout(() => {
          ElMessage.success('缓存清理完成')
        }, 1000)
      })
    }

    const handleReset = async () => {
      ElMessageBox.confirm(
        '此操作将恢复所有设置为默认值，确定要继续吗？',
        '确认重置',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'danger'
        }
      ).then(() => {
        // 重置所有设置为默认值
        basicSettings.value = {
          username: '',
          email: '',
          steamId: '',
          currency: 'CNY'
        }
        apiSettings.value = {
          buffApiKey: '',
          steamApiKey: '',
          youyoupinToken: ''
        }
        notificationSettings.value = {
          priceAlert: true,
          tradeComplete: true,
          inventoryUpdate: false,
          rentExpire: true,
          emailNotify: false,
          notifyEmail: ''
        }
        ElMessage.success('设置已重置为默认值')
      })
    }

    onMounted(() => {
      loadSettings()
    })

    return {
      activeTab,
      basicSettings,
      apiSettings,
      notificationSettings,
      systemInfo,
      saveSettings,
      resetForm,
      testApiConnections,
      handleBackup,
      handleExport,
      handleClearCache,
      handleReset
    }
  }
}
</script>

<style scoped>
.settings-container {
  width: 100%;
}

.settings-section {
  padding: clamp(1rem, 3vw, 1.25rem) 0;
}

.settings-section h3 {
  margin-bottom: clamp(1rem, 3vw, 1.25rem);
  color: #fff;
  font-size: clamp(1.125rem, 2vw, 1.25rem);
}

.action-card {
  background-color: #1e1e1e;
  padding: clamp(1rem, 2.5vw, 1.25rem);
  border-radius: 0.5rem;
  border: 1px solid #333;
  text-align: center;
}

.action-card h4 {
  margin-bottom: clamp(0.5rem, 1.5vw, 0.625rem);
  color: #fff;
  font-size: clamp(1rem, 1.8vw, 1.125rem);
}

.action-card p {
  color: #ccc;
  margin-bottom: clamp(0.75rem, 2vw, 0.9375rem);
  font-size: clamp(0.75rem, 1.2vw, 0.875rem);
  line-height: 1.5;
}

.system-info {
  margin-top: clamp(1rem, 3vw, 1.25rem);
}

.save-actions {
  margin-top: clamp(1.5rem, 4vw, 1.875rem);
  text-align: center;
  padding-top: clamp(1rem, 3vw, 1.25rem);
  border-top: 1px solid #333;
}

:deep(.el-tabs--border-card) {
  border: 1px solid #333;
  background-color: #1e1e1e;
}

:deep(.el-tabs--border-card > .el-tabs__header) {
  background-color: #2a2a2a;
  border-bottom: 1px solid #333;
}

:deep(.el-tabs--border-card .el-tabs__item) {
  color: #ccc;
  border-right: 1px solid #333;
  font-size: clamp(0.75rem, 1.2vw, 0.875rem);
  padding: clamp(0.75rem, 2vw, 1rem) clamp(1rem, 2.5vw, 1.25rem);
}

:deep(.el-tabs--border-card .el-tabs__item.is-active) {
  color: #4CAF50;
  background-color: #1e1e1e;
}

:deep(.el-tabs--border-card > .el-tabs__content) {
  padding: clamp(1rem, 2.5vw, 1.25rem);
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

:deep(.el-descriptions) {
  background-color: #1e1e1e;
}

:deep(.el-descriptions__header) {
  background-color: #2a2a2a;
}

:deep(.el-descriptions__body) {
  background-color: #1e1e1e;
}

:deep(.el-descriptions__label) {
  color: #ccc;
  font-size: clamp(0.75rem, 1.2vw, 0.875rem);
}

:deep(.el-descriptions__content) {
  color: #fff;
  font-size: clamp(0.75rem, 1.2vw, 0.875rem);
}

:deep(.el-button) {
  font-size: clamp(0.625rem, 1vw, 0.75rem);
  padding: clamp(0.375rem, 1vw, 0.5rem) clamp(0.75rem, 2vw, 1rem);
}

:deep(.el-form-item) {
  margin-bottom: clamp(1rem, 2.5vw, 1.125rem);
}

@media (max-width: 768px) {
  :deep(.el-tabs--border-card .el-tabs__item) {
    padding: 0.75rem 0.5rem;
    font-size: 0.75rem;
  }
  
  :deep(.el-tabs--border-card > .el-tabs__content) {
    padding: 1rem;
  }
  
  .action-card {
    padding: 1rem;
  }
  
  .action-card h4 {
    font-size: 1rem;
  }
  
  .action-card p {
    font-size: 0.75rem;
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
</style>