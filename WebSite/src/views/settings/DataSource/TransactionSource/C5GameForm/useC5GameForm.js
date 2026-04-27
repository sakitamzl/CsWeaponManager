import { ref, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { Grid, Loading, CircleCheck } from '@element-plus/icons-vue'
import axios from 'axios'
import { apiUrls } from '@/config/api.js'

export default function useC5GameForm(props, { emit }) {
    const c5gameTokenLoading = ref(false)
    const c5gameTokenStatus = ref('')
    const tokenCheckTimer = ref(null)
    const basicCollapse = ref([])
    const deviceCollapse = ref([])
    const appCollapse = ref([])
    const signatureCollapse = ref([])
    const systemCollapse = ref([])

    // 更新表单数据
    const updateForm = (updates) => {
      emit('update:form', { ...props.form, ...updates })
    }

    // 更新代理地址
    const updateProxyAddress = (address) => {
      emit('update:proxyAddress', address)
    }

    // 开始C5 GAME令牌收集
    const startC5GameTokenCollection = async () => {
      try {
        c5gameTokenLoading.value = true
        c5gameTokenStatus.value = 'waiting'
        
        const url = apiUrls.getAppTokenStartC5Game()
        const response = await axios.post(url)
        
        if (response.data.code === 200) {
          if (response.data.data && response.data.data.proxy_address) {
            updateProxyAddress(response.data.data.proxy_address)
          }
          ElMessage.success('C5 GAME代理服务器已启动，请在手机上配置代理')
          if (response.data.data?.proxy_address) {
            ElMessage.info({
              message: `代理地址: ${response.data.data.proxy_address}`,
              duration: 5000
            })
          }
          
          startC5GameTokenPolling()
        } else {
          ElMessage.error(response.data.msg || '启动C5 GAME代理失败')
          c5gameTokenLoading.value = false
          c5gameTokenStatus.value = 'failed'
        }
      } catch (error) {
        ElMessage.error('启动C5 GAME代理失败: ' + (error.message || '网络错误'))
        c5gameTokenLoading.value = false
        c5gameTokenStatus.value = 'failed'
      }
    }

    // 开始轮询获取令牌数据
    const startC5GameTokenPolling = () => {
      if (tokenCheckTimer.value) {
        clearInterval(tokenCheckTimer.value)
      }
      
      tokenCheckTimer.value = setInterval(async () => {
        try {
          const url = apiUrls.getAppTokenGetC5GameData()
          const response = await axios.get(url)
          
          if (response.data.code === 200) {
            const data = response.data.data

            updateForm({
              steamID: data.steamid || data.steamID,
              c5gameAccessToken: data.x_access_token,
              c5gameDeviceId: data.x_device_id,
              c5gameDeviceModel: data.x_device_model,
              c5gameDeviceOs: data.x_device_os,
              c5gameUserAgent: data.user_agent,
              c5gameAppVersionCode: data.x_app_version_code,
              c5gameAppChannel: data.x_app_channel,
              c5gameSource: data.x_source,
              c5gameSign: data.x_sign,
              c5gameRdi: data.rdi,
              c5gameAcceptLanguage: data.accept_language,
              c5gameXUa: data.x_ua,
              c5gameStartReqTime: data.x_start_req_time,
              c5gameContentType: data.content_type,
              c5gameAcceptEncoding: data.accept_encoding
            })
            
            ElMessage.success('C5 GAME Token 获取成功!')
            c5gameTokenStatus.value = 'success'
            c5gameTokenLoading.value = false

            if (tokenCheckTimer.value) {
              clearInterval(tokenCheckTimer.value)
              tokenCheckTimer.value = null
            }

            await stopC5GameTokenCollection()

            // 发射令牌获取成功事件，触发自动保存
            emit('token-success')
          }
        } catch (error) {
          // 获取令牌数据失败时静默处理或由调用方提示
        }
      }, 3000)
    }

    // 停止令牌收集
    const stopC5GameTokenCollection = async () => {
      try {
        await axios.post(apiUrls.getAppTokenStopC5Game())
      } catch (error) {
        // 停止代理服务器失败时静默处理
      }
    }

    // 清理方法 - 用于对话框关闭时调用
    const cleanup = async () => {
      // 清除轮询定时器
      if (tokenCheckTimer.value) {
        clearInterval(tokenCheckTimer.value)
        tokenCheckTimer.value = null
      }

      // 停止SSL代理服务
      await stopC5GameTokenCollection()

      // 重置状态
      c5gameTokenLoading.value = false
      c5gameTokenStatus.value = ''
    }

    onBeforeUnmount(() => {
      cleanup()
    })

    return {
      Grid,
      Loading,
      CircleCheck,
      c5gameTokenLoading,
      c5gameTokenStatus,
      basicCollapse,
      deviceCollapse,
      appCollapse,
      signatureCollapse,
      systemCollapse,
      startC5GameTokenCollection,
      cleanup
    }
  }

