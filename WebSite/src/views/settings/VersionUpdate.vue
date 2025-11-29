<template>
  <div>
    <div class="settings-container">
      <div class="settings-section">
        <h3>版本更新</h3>
        
        <!-- 当前版本信息 -->
        <div class="version-info">
          <el-card shadow="hover" class="version-card">
            <div class="current-version">
              <el-icon :size="24" class="version-icon">
                <Document />
              </el-icon>
              <div class="version-details">
                <div class="version-number">当前版本: v{{ currentVersion }}</div>
                <div class="version-date">{{ currentVersionDate }}</div>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 检查更新按钮 -->
        <div class="update-actions">
          <el-button 
            type="primary" 
            size="large" 
            :loading="checkingUpdate"
            @click="checkForUpdate"
          >
            <el-icon><Refresh /></el-icon>
            检查更新
          </el-button>
        </div>

        <!-- 更新日志 -->
        <div class="update-log-section">
          <h4>更新日志</h4>
          <el-timeline>
            <el-timeline-item
              v-for="(log, index) in updateLogs"
              :key="index"
              :timestamp="log.date"
              placement="top"
              :type="index === 0 ? 'primary' : ''"
            >
              <el-card shadow="hover">
                <div class="log-header">
                  <span class="log-version">{{ log.version }}</span>
                </div>
                <div class="log-content">
                  <ul class="log-items">
                    <li v-for="(item, itemIndex) in log.items" :key="itemIndex">
                      {{ item }}
                    </li>
                  </ul>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Document, Refresh } from '@element-plus/icons-vue'

export default {
  name: 'VersionUpdate',
  setup() {
    const currentVersion = ref('1.2.7')
    const currentVersionDate = ref('2025-11-28')
    const checkingUpdate = ref(false)
    const updateLogs = ref([
      {
        version: 'v1.2.7',
        date: '2025-11-28',
        items: [
          '表 buy sell steam_stockComponents steam_inventory steam_buy steam_sell 新增字段 steam_hash_name',
          'steam库存表添加 详细信息的获取',
          '修改yyyp 获取商品详情的时候 添加获取贴纸信息 挂件信息'
        ]
      },
      {
        version: 'v1.2.6',
        date: '2025-11-28',
        items: [
          'auto-manager自动化管理页面添加 启动全部 停止全部按钮',
          '修改csfloat的订单查询状态限制',
          '添加使用yyyp的URL进行ICON的下载 脱离在线图片库的依赖'
        ]
      },
      {
        version: 'v1.2.5',
        date: '2025-11-27',
        items: [
          '爬取改名中的 steam市场类型添加搜素参数'
        ]
      }
    ])

    const checkForUpdate = async () => {
      checkingUpdate.value = true
      try {
        // 这里可以添加检查更新的API调用
        // const response = await axios.get(apiUrls.checkUpdate())
        
        // 模拟检查更新
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        ElMessage.success('已是最新版本')
      } catch (error) {
        console.error('检查更新失败:', error)
        ElMessage.error('检查更新失败，请稍后重试')
      } finally {
        checkingUpdate.value = false
      }
    }

    onMounted(() => {
      // 可以在这里加载更新日志
    })

    return {
      currentVersion,
      currentVersionDate,
      checkingUpdate,
      updateLogs,
      checkForUpdate
    }
  },
  components: {
    Document,
    Refresh
  }
}
</script>

<style scoped>
.settings-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.settings-section {
  background: rgba(26, 26, 26, 0.6);
  border-radius: 12px;
  padding: 2rem;
  backdrop-filter: blur(10px);
}

.settings-section h3 {
  color: #ffffff;
  font-size: 1.5rem;
  margin-bottom: 2rem;
  font-weight: 600;
}

.version-info {
  margin-bottom: 2rem;
}

.version-card {
  background: rgba(35, 35, 35, 0.8);
  border: 1px solid rgba(58, 58, 58, 0.8);
}

.current-version {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.version-icon {
  color: #409eff;
}

.version-details {
  flex: 1;
}

.version-number {
  font-size: 1.25rem;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 0.5rem;
}

.version-date {
  font-size: 0.875rem;
  color: #b0b0b0;
}

.update-actions {
  margin-bottom: 2rem;
}

.update-log-section {
  margin-top: 2rem;
}

.update-log-section h4 {
  color: #ffffff;
  font-size: 1.25rem;
  margin-bottom: 1.5rem;
  font-weight: 600;
}

.log-header {
  margin-bottom: 1rem;
}

.log-version {
  font-size: 1.125rem;
  font-weight: 600;
  color: #409eff;
}

.log-content {
  color: #e0e0e0;
}

.log-items {
  margin: 0;
  padding-left: 1.5rem;
  list-style-type: disc;
}

.log-items li {
  margin-bottom: 0.5rem;
  line-height: 1.6;
}

.log-items li:last-child {
  margin-bottom: 0;
}

/* Element Plus Timeline 样式覆盖 */
:deep(.el-timeline-item__timestamp) {
  color: #b0b0b0;
  font-size: 0.875rem;
}

:deep(.el-card) {
  background: rgba(35, 35, 35, 0.8);
  border: 1px solid rgba(58, 58, 58, 0.8);
  color: #e0e0e0;
}

:deep(.el-timeline-item__node) {
  background-color: #409eff;
  border-color: #409eff;
}

:deep(.el-timeline-item__tail) {
  border-left-color: rgba(58, 58, 58, 0.8);
}
</style>

