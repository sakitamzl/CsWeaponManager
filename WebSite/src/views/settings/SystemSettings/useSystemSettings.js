import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import { apiUrls } from '@/config/api.js'

export function useSystemSettings() {
  const basicSettings = ref({
    enableLogin: false,
    username: '',
    password: '',
    allowExternalAccess: false
  })

  const loadSettings = async () => {
    try {
      const response = await axios.get(apiUrls.loginSettings())
      
      if (response.data.success) {
        basicSettings.value = {
          enableLogin: response.data.data.enableLogin || false,
          username: response.data.data.username || '',
          password: '',  // 不从服务器加载密码
          allowExternalAccess: response.data.data.allowExternalAccess || false
        }
      } else {
        ElMessage.error(response.data.message || '加载设置失败')
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
      // 验证：如果启用登录，必须填写用户名和密码
      if (basicSettings.value.enableLogin) {
        if (!basicSettings.value.username) {
          ElMessage.warning('请输入用户名')
          return
        }
        if (!basicSettings.value.password) {
          ElMessage.warning('请输入密码')
          return
        }
      }
      
      const response = await axios.post(apiUrls.loginSettingsSave(), {
        enableLogin: basicSettings.value.enableLogin,
        username: basicSettings.value.username,
        password: basicSettings.value.password,
        allowExternalAccess: basicSettings.value.allowExternalAccess
      })
      
      if (response.data.success) {
        ElMessage.success(response.data.message || '设置保存成功')
        // 清空密码输入框
        basicSettings.value.password = ''
      } else {
        ElMessage.error(response.data.message || '保存设置失败')
      }
    } catch (error) {
      console.error('保存设置失败:', error)
      ElMessage.error(error.response?.data?.message || '保存设置失败')
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
