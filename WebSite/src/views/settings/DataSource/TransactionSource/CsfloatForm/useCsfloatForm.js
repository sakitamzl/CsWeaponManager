import { ref, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { Grid, Loading, CircleCheck } from '@element-plus/icons-vue'
import axios from 'axios'
import { apiUrls } from '@/config/api.js'

export default function useCsfloatForm(props, { emit }) {
    const csfloatTokenLoading = ref(false)
    const csfloatTokenStatus = ref('')
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

    // 开始CSFloat令牌收集
    const startCsfloatTokenCollection = async () => {
      try {
        csfloatTokenLoading.value = true
        csfloatTokenStatus.value = 'waiting'
        
        const url = apiUrls.getAppTokenStartCsfloat()
        const response = await axios.post(url)
        
        if (response.data.code === 200) {
          if (response.data.data && response.data.data.proxy_address) {
            updateProxyAddress(response.data.data.proxy_address)
          }
          ElMessage.success('CsFloat代理服务器已启动，请在浏览器中配置代理')
          if (response.data.data?.proxy_address) {
            ElMessage.info({
              message: `代理地址: ${response.data.data.proxy_address}`,
              duration: 5000
            })
          }
          
          startCsfloatTokenPolling()
        } else {
          ElMessage.error(response.data.msg || '启动CsFloat代理失败')
          csfloatTokenLoading.value = false
          csfloatTokenStatus.value = 'failed'
        }
      } catch (error) {
        console.error('启动CsFloat代理失败:', error)
        ElMessage.error('启动CsFloat代理失败: ' + (error.message || '网络错误'))
        csfloatTokenLoading.value = false
        csfloatTokenStatus.value = 'failed'
      }
    }

    // 开始轮询获取令牌数据
    const startCsfloatTokenPolling = () => {
      if (tokenCheckTimer.value) {
        clearInterval(tokenCheckTimer.value)
      }
      
      tokenCheckTimer.value = setInterval(async () => {
        try {
          const url = apiUrls.getAppTokenGetCsfloatData()
          const response = await axios.get(url)
          
          if (response.data.code === 200) {
            const data = response.data.data
            
            updateForm({
              csfloatUserAgent: data['User-Agent'],
              csfloatReferer: data['Referer'],
              csfloatAccept: data['Accept'],
              csfloatXAppVersion: data['X-App-Version'],
              csfloatHost: data['Host'],
              csfloatConnection: data['Connection'],
              csfloatAcceptEncoding: data['Accept-Encoding'],
              csfloatCookie: data['Cookie'],
              csfloatSteamID: data.steamID
            })
            
            ElMessage.success('CsFloat Token 获取成功!')
            csfloatTokenStatus.value = 'success'
            csfloatTokenLoading.value = false

            if (tokenCheckTimer.value) {
              clearInterval(tokenCheckTimer.value)
              tokenCheckTimer.value = null
            }

            stopCsfloatTokenCollection()

            // 发射令牌获取成功事件，触发自动保存
            emit('token-success')
          }
        } catch (error) {
          console.error('获取令牌数据失败:', error)
        }
      }, 3000)
    }

    // 停止令牌收集
    const stopCsfloatTokenCollection = async () => {
      try {
        await axios.post(apiUrls.getAppTokenStopCsfloat())
      } catch (error) {
        console.error('停止代理服务器失败:', error)
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
      csfloatTokenLoading,
      csfloatTokenStatus,
      collapseState,
      startCsfloatTokenCollection
    }
  }
