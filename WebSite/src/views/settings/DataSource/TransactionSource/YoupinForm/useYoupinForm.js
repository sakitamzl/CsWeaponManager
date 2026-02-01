import { ref, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { Grid, Loading, CircleCheck } from '@element-plus/icons-vue'
import axios from 'axios'
import { apiUrls } from '@/config/api.js'

export default function useYoupinForm(props, { emit }) {
    const yyypTokenLoading = ref(false)
    const yyypTokenStatus = ref('')
    const tokenCheckTimer = ref(null)
    const yyypSmsLoginLoading = ref(false)
    const yyypSmsLoginStatus = ref('')
    const sendingSmsCode = ref(false)
    const smsCodeCountdown = ref(0)
    const smsCodeTimer = ref(null)
    const generatingSessionId = ref(false)
    const generatingDeviceId = ref(false)
    const basicCollapse = ref([])
    const tokenCollapse = ref([])
    const deviceCollapse = ref([])
    const advancedCollapse = ref([])

    // 更新表单数据
    const updateForm = (updates) => {
      emit('update:form', { ...props.form, ...updates })
    }

    // 更新代理地址
    const updateProxyAddress = (address) => {
      emit('update:proxyAddress', address)
    }

    // 开始悠悠有品令牌收集
    const startYyypTokenCollection = async () => {
      try {
        yyypTokenLoading.value = true
        yyypTokenStatus.value = 'waiting'
        
        const url = apiUrls.getAppTokenStartYyyp()
        const response = await axios.post(url)
        
        if (response.data.code === 200) {
          if (response.data.data && response.data.data.proxy_address) {
            updateProxyAddress(response.data.data.proxy_address)
          }
          ElMessage.success('悠悠有品代理服务器已启动，请在手机上配置代理')
          if (response.data.data?.proxy_address) {
            ElMessage.info({
              message: `代理地址: ${response.data.data.proxy_address}`,
              duration: 5000
            })
          }
          
          startYyypTokenPolling()
        } else {
          ElMessage.error(response.data.msg || '启动悠悠有品代理失败')
          yyypTokenLoading.value = false
          yyypTokenStatus.value = 'failed'
        }
      } catch (error) {
        console.error('启动悠悠有品代理失败:', error)
        ElMessage.error('启动悠悠有品代理失败: ' + (error.message || '网络错误'))
        yyypTokenLoading.value = false
        yyypTokenStatus.value = 'failed'
      }
    }

    // 开始轮询获取令牌数据
    const startYyypTokenPolling = () => {
      if (tokenCheckTimer.value) {
        clearInterval(tokenCheckTimer.value)
      }
      
      tokenCheckTimer.value = setInterval(async () => {
        try {
          const url = apiUrls.getAppTokenGetYyypData()
          const response = await axios.get(url)
          
          if (response.data.code === 200) {
            const data = response.data.data
            
            updateForm({
              sessionid: data.Sessionid,
              token: data.authorization,
              deviceName: `${data.device_manu} ${data.device_model}`,
              appVersion: data.app_version,
              appType: data.apptype,
              userId: data.userId,
              steamId: data.steamId,
              devicetoken: data.devicetoken,
              deviceid: data.deviceid,
              deviceuk: data.deviceuk,
              uk: data.uk,
              sk: data.sk,
              tracestate: data.tracestate,
              deviceInfo: data.device_info,
              phone: data.phone || props.form.phone
            })
            
            ElMessage.success('悠悠有品 Token 获取成功!')
            yyypTokenStatus.value = 'success'
            yyypTokenLoading.value = false

            if (tokenCheckTimer.value) {
              clearInterval(tokenCheckTimer.value)
              tokenCheckTimer.value = null
            }

            stopYyypTokenCollection()

            // 发射令牌获取成功事件，触发自动保存
            emit('token-success')
          }
        } catch (error) {
          console.error('获取令牌数据失败:', error)
        }
      }, 3000)
    }

    // 停止令牌收集
    const stopYyypTokenCollection = async () => {
      try {
        await axios.post(apiUrls.getAppTokenStopYyyp())
      } catch (error) {
        console.error('停止代理服务器失败:', error)
      }
    }

    // 发送短信验证码
    const handleSendSmsCode = async () => {
      if (!props.form.yyypPhone) {
        ElMessage.error('请输入手机号')
        return
      }
      
      const phoneRegex = /^1[3-9]\d{9}$/
      if (!phoneRegex.test(props.form.yyypPhone)) {
        ElMessage.error('请输入正确的手机号')
        return
      }
      
      sendingSmsCode.value = true
      try {
        // TODO: 调用后端API发送短信验证码
        ElMessage.success('验证码已发送，请查收短信')
        
        smsCodeCountdown.value = 60
        smsCodeTimer.value = setInterval(() => {
          smsCodeCountdown.value--
          if (smsCodeCountdown.value <= 0) {
            clearInterval(smsCodeTimer.value)
            smsCodeTimer.value = null
          }
        }, 1000)
      } catch (error) {
        console.error('发送验证码失败:', error)
        ElMessage.error('发送验证码失败: ' + (error.response?.data?.message || error.message))
      } finally {
        sendingSmsCode.value = false
      }
    }

    // 短信登录
    const handleYyypSmsLogin = async () => {
      if (!props.form.yyypSessionId) {
        ElMessage.error('请先生成或输入Session ID')
        return
      }
      
      if (!props.form.yyypPhone) {
        ElMessage.error('请输入手机号')
        return
      }
      
      if (!props.form.yyypSmsCode) {
        ElMessage.error('请输入验证码')
        return
      }
      
      yyypSmsLoginLoading.value = true
      try {
        // TODO: 调用后端API进行短信登录
        ElMessage.success('登录成功！配置信息已自动填充')
        yyypSmsLoginStatus.value = 'success'
        
        updateForm({ sessionid: props.form.yyypSessionId })
        
        // 自动展开配置折叠面板
        basicCollapse.value = ['basic']
        tokenCollapse.value = ['token']
      } catch (error) {
        console.error('短信登录失败:', error)
        ElMessage.error('登录失败: ' + (error.response?.data?.message || error.message))
        yyypSmsLoginStatus.value = 'failed'
      } finally {
        yyypSmsLoginLoading.value = false
      }
    }

    // 生成SessionID
    const handleGenerateSessionId = async () => {
      generatingSessionId.value = true
      try {
        // TODO: 调用后端API生成SessionID
        const randomSessionId = 'SESSION_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15)
        updateForm({ yyypSessionId: randomSessionId })
        ElMessage.success('SessionID生成成功')
      } catch (error) {
        console.error('生成SessionID失败:', error)
        ElMessage.error('生成SessionID失败: ' + (error.response?.data?.message || error.message))
      } finally {
        generatingSessionId.value = false
      }
    }

    // 生成DeviceID
    const handleGenerateDeviceId = async () => {
      generatingDeviceId.value = true
      try {
        // TODO: 调用后端API生成DeviceID
        const randomDeviceId = 'DEVICE_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15)
        updateForm({ yyypDeviceId: randomDeviceId })
        ElMessage.success('DeviceID生成成功')
      } catch (error) {
        console.error('生成DeviceID失败:', error)
        ElMessage.error('生成DeviceID失败: ' + (error.response?.data?.message || error.message))
      } finally {
        generatingDeviceId.value = false
      }
    }

    onBeforeUnmount(() => {
      if (tokenCheckTimer.value) {
        clearInterval(tokenCheckTimer.value)
      }
      if (smsCodeTimer.value) {
        clearInterval(smsCodeTimer.value)
      }
    })

    return {
      Grid,
      Loading,
      CircleCheck,
      yyypTokenLoading,
      yyypTokenStatus,
      yyypSmsLoginLoading,
      yyypSmsLoginStatus,
      sendingSmsCode,
      smsCodeCountdown,
      generatingSessionId,
      generatingDeviceId,
      basicCollapse,
      tokenCollapse,
      deviceCollapse,
      advancedCollapse,
      startYyypTokenCollection,
      handleSendSmsCode,
      handleYyypSmsLogin,
      handleGenerateSessionId,
      handleGenerateDeviceId
    }
  }
