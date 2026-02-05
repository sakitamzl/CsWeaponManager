import { ref, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { Grid, Loading, CircleCheck } from '@element-plus/icons-vue'
import axios from 'axios'
import { apiUrls } from '@/config/api.js'

export default function usePerfectWorldForm(props, { emit }) {
    const perfectWorldTokenLoading = ref(false)
    const perfectWorldTokenStatus = ref('')
    const tokenCheckTimer = ref(null)
    const collapseState = ref([])

    // 更新表单数据
    const updateForm = (updates) => {
      emit('update:form', { ...props.form, ...updates })
    }

    // 更新代理地址
    const updateProxyAddress = (address) => {
      emit('update:proxyAddress', address)
    }

    // 开始完美世界令牌收集
    const startPerfectWorldTokenCollection = async () => {
      try {
        perfectWorldTokenLoading.value = true
        perfectWorldTokenStatus.value = 'waiting'
        
        const url = apiUrls.getAppTokenStartPerfectWorld()
        const response = await axios.post(url)
        
        if (response.data.code === 200) {
          if (response.data.data && response.data.data.proxy_address) {
            updateProxyAddress(response.data.data.proxy_address)
          }
          ElMessage.success('完美世界APP代理服务器已启动，请在手机上配置代理')
          if (response.data.data?.proxy_address) {
            ElMessage.info({
              message: `代理地址: ${response.data.data.proxy_address}`,
              duration: 5000
            })
          }
          
          startPerfectWorldTokenPolling()
        } else {
          ElMessage.error(response.data.msg || '启动完美世界APP代理失败')
          perfectWorldTokenLoading.value = false
          perfectWorldTokenStatus.value = 'failed'
        }
      } catch (error) {
        ElMessage.error('启动完美世界APP代理失败: ' + (error.message || '网络错误'))
        perfectWorldTokenLoading.value = false
        perfectWorldTokenStatus.value = 'failed'
      }
    }

    // 开始轮询获取令牌数据
    const startPerfectWorldTokenPolling = () => {
      if (tokenCheckTimer.value) {
        clearInterval(tokenCheckTimer.value)
      }
      
      tokenCheckTimer.value = setInterval(async () => {
        try {
          const url = apiUrls.getAppTokenGetPerfectWorldData()
          const response = await axios.get(url)
          
          if (response.data.code === 200) {
            const data = response.data.data
            
            updateForm({
              appversion: data.appversion,
              device: data.device,
              gameType: data.gameType,
              platform: data.platform,
              pwToken: data.token,
              tdSign: data.tdSign,
              pwSteamID: data.steamID
            })
            
            ElMessage.success('完美世界APP Token 获取成功!')
            perfectWorldTokenStatus.value = 'success'
            perfectWorldTokenLoading.value = false

            if (tokenCheckTimer.value) {
              clearInterval(tokenCheckTimer.value)
              tokenCheckTimer.value = null
            }

            stopPerfectWorldTokenCollection()

            // 发射令牌获取成功事件，触发自动保存
            emit('token-success')
          }
        } catch (error) {
          // 获取令牌数据失败时静默处理或由调用方提示
        }
      }, 3000)
    }

    // 停止令牌收集
    const stopPerfectWorldTokenCollection = async () => {
      try {
        await axios.post(apiUrls.getAppTokenStopPerfectWorld())
      } catch (error) {
        // 停止代理服务器失败时静默处理
      }
    }

    onBeforeUnmount(() => {
      if (tokenCheckTimer.value) {
        clearInterval(tokenCheckTimer.value)
      }
    })

    return {
      Grid,
      Loading,
      CircleCheck,
      perfectWorldTokenLoading,
      perfectWorldTokenStatus,
      collapseState,
      startPerfectWorldTokenCollection
    }
  }
