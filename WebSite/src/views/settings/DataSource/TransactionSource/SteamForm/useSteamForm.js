import { ref, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { Grid, Loading } from '@element-plus/icons-vue'
import axios from 'axios'
import { apiUrls } from '@/config/api.js'

export default function useSteamForm(props, { emit }) {
    const steamQRCode = ref('')
    const steamQRLoading = ref(false)
    const steamQRStatus = ref('')
    const steamQRCheckTimer = ref(null)
    const steamLoginLoading = ref(false)
    const collapseState = ref([])

    // 更新表单数据
    const updateForm = (updates) => {
      emit('update:form', { ...props.form, ...updates })
    }

    // 获取二维码状态文本
    const getSteamQRStatusText = () => {
      const statusMap = {
        'waiting': '等待扫码中...',
        'success': '✅ 登录成功',
        'expired': '❌ 二维码已过期'
      }
      return statusMap[steamQRStatus.value] || '未知状态'
    }

    // 开始轮询检查二维码状态
    const startQRCodePolling = (sessionId) => {
      if (steamQRCheckTimer.value) {
        clearInterval(steamQRCheckTimer.value)
      }

      steamQRCheckTimer.value = setInterval(async () => {
        try {
          const response = await axios.post(apiUrls.steamQRPoll(), {
            session_id: sessionId
          })
          
          if (response.data.success) {
            if (response.data.status === 'success') {
              steamQRStatus.value = 'success'
              
              const baseCookies = response.data.data?.base_cookies || response.data.data?.baseCookies || response.data.data?.cookies || ''
              const inventoryCookies = response.data.data?.inventory_cookies || response.data.data?.inventoryCookies || response.data.data?.cookies || ''
              
              updateForm({
                steamBaseCookies: baseCookies,
                steamInventoryCookies: inventoryCookies,
                cookies: inventoryCookies,
                steamID: response.data.data?.steam_id || props.form.steamID,
                steamLoginSuccess: true,
                steamLoginMessage: `✅ 扫码登录成功！${response.data.data?.account_name ? '账号: ' + response.data.data.account_name : ''}${response.data.data?.steam_id ? '（SteamID已自动填入）' : ''}`
              })
              
              clearInterval(steamQRCheckTimer.value)
              ElMessage.success('Steam扫码登录成功！已填入Cookie与SteamID')
            } else if (response.data.status === 'waiting') {
              steamQRStatus.value = 'waiting'
            }
          } else {
            steamQRStatus.value = 'expired'
            clearInterval(steamQRCheckTimer.value)
            ElMessage.warning(response.data.message || '二维码已过期，请重新生成')
          }
        } catch (error) {
          console.error('检查二维码状态失败:', error)
          clearInterval(steamQRCheckTimer.value)
          steamQRStatus.value = 'expired'
          ElMessage.error('检查二维码状态失败')
        }
      }, 3000)
    }

    // 生成Steam二维码
    const handleGenerateQRCode = async () => {
      steamQRLoading.value = true
      steamQRCode.value = ''
      steamQRStatus.value = ''

      try {
        ElMessage.info('正在生成Steam登录二维码...')
        
        const response = await axios.post(apiUrls.steamQRGenerate())
        
        if (response.data.success) {
          steamQRCode.value = response.data.data.qr_code
          steamQRStatus.value = 'waiting'
          updateForm({ steamQRSessionId: response.data.data.session_id })
          
          ElMessage.success('二维码生成成功，请使用Steam APP扫码')
          startQRCodePolling(response.data.data.session_id)
        } else {
          ElMessage.error(response.data.message || '生成二维码失败')
        }
      } catch (error) {
        console.error('生成二维码失败:', error)
        ElMessage.error('生成二维码失败，请检查网络连接')
      } finally {
        steamQRLoading.value = false
      }
    }

    // Steam账号密码登录
    const handleSteamLogin = async () => {
      if (!props.form.steamUsername || !props.form.steamPassword) {
        ElMessage.error('请输入Steam用户名和密码')
        return
      }

      steamLoginLoading.value = true
      updateForm({ steamLoginMessage: '', steamLoginSuccess: false })

      try {
        const loginData = {
          username: props.form.steamUsername,
          password: props.form.steamPassword,
          twofactor_code: props.form.steamTwofactorCode || '',
          save_to_db: false
        }

        const response = await axios.post(apiUrls.steamLogin(), loginData)
        const result = response.data

        if (result.success) {
          const baseCookies = result.base_cookies || result.baseCookies || result.cookies || ''
          const inventoryCookies = result.inventory_cookies || result.inventoryCookies || result.cookies || ''
          const steamIdFromResp = result.steam_id || result.steamId || result.data?.steam_id || result.data?.steamId
          
          updateForm({
            steamBaseCookies: baseCookies,
            steamInventoryCookies: inventoryCookies,
            cookies: inventoryCookies,
            steamID: steamIdFromResp || props.form.steamID,
            steamLoginMessage: steamIdFromResp
              ? '✅ Steam登录成功！Cookie与SteamID已获取'
              : '✅ Steam登录成功！Cookie已获取，请填写SteamID',
            steamLoginSuccess: true
          })
          
          ElMessage.success(steamIdFromResp ? 'Steam登录成功，已自动填入SteamID' : 'Steam登录成功！请手动输入SteamID')
        } else if (result.requires_twofactor) {
          updateForm({ steamLoginMessage: '', steamLoginSuccess: false })
        } else if (result.requires_emailauth) {
          updateForm({ 
            steamLoginMessage: '⚠️ 需要邮箱验证码，请查收邮件后输入',
            steamLoginSuccess: false 
          })
          ElMessage.warning('需要邮箱验证码')
        } else if (result.requires_captcha) {
          updateForm({ 
            steamLoginMessage: '⚠️ 需要图形验证码，请稍后重试或手动输入Cookie',
            steamLoginSuccess: false 
          })
          ElMessage.warning('需要图形验证码')
        } else {
          updateForm({ 
            steamLoginMessage: `❌ 登录失败: ${result.message}`,
            steamLoginSuccess: false 
          })
          ElMessage.error(result.message || '登录失败')
        }
      } catch (error) {
        console.error('Steam登录失败:', error)
        updateForm({ 
          steamLoginMessage: `❌ 登录失败: ${error.message || '网络错误'}`,
          steamLoginSuccess: false 
        })
        ElMessage.error('Steam登录失败，请检查网络连接')
      } finally {
        steamLoginLoading.value = false
      }
    }

    onBeforeUnmount(() => {
      if (steamQRCheckTimer.value) {
        clearInterval(steamQRCheckTimer.value)
      }
    })

    return {
      Grid,
      Loading,
      steamQRCode,
      steamQRLoading,
      steamQRStatus,
      steamLoginLoading,
      collapseState,
      getSteamQRStatusText,
      handleGenerateQRCode,
      handleSteamLogin
    }
  }
