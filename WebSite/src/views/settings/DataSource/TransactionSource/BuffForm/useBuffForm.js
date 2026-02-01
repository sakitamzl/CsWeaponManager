import { ref, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import { Grid, Loading, CircleCheck } from '@element-plus/icons-vue'
import axios from 'axios'
import { apiUrls } from '@/config/api.js'

export default function useBuffForm(props, { emit }) {
    const buffTokenLoading = ref(false)
    const buffTokenStatus = ref('')
    const tokenCheckTimer = ref(null)
    const basicCollapse = ref([])
    const appCollapse = ref([])
    const deviceCollapse = ref([])
    const systemCollapse = ref([])
    const displayCollapse = ref([])
    const localeCollapse = ref([])

    // 更新表单数据
    const updateForm = (updates) => {
      emit('update:form', { ...props.form, ...updates })
    }

    // 更新代理地址
    const updateProxyAddress = (address) => {
      emit('update:proxyAddress', address)
    }

    // 开始BUFF令牌收集
    const startBuffTokenCollection = async () => {
      try {
        buffTokenLoading.value = true
        buffTokenStatus.value = 'waiting'
        
        const url = apiUrls.getAppTokenStartBuff()
        const response = await axios.post(url)
        
        if (response.data.code === 200) {
          if (response.data.data && response.data.data.proxy_address) {
            updateProxyAddress(response.data.data.proxy_address)
          }
          ElMessage.success('BUFF代理服务器已启动，请在手机上配置代理')
          if (response.data.data?.proxy_address) {
            ElMessage.info({
              message: `代理地址: ${response.data.data.proxy_address}`,
              duration: 5000
            })
          }
          
          startBuffTokenPolling()
        } else {
          ElMessage.error(response.data.msg || '启动BUFF代理失败')
          buffTokenLoading.value = false
          buffTokenStatus.value = 'failed'
        }
      } catch (error) {
        console.error('启动BUFF代理失败:', error)
        ElMessage.error('启动BUFF代理失败: ' + (error.message || '网络错误'))
        buffTokenLoading.value = false
        buffTokenStatus.value = 'failed'
      }
    }

    // 开始轮询获取令牌数据
    const startBuffTokenPolling = () => {
      if (tokenCheckTimer.value) {
        clearInterval(tokenCheckTimer.value)
      }
      
      tokenCheckTimer.value = setInterval(async () => {
        try {
          const url = apiUrls.getAppTokenGetBuffData()
          const response = await axios.get(url)
          
          if (response.data.code === 200) {
            const data = response.data.data
            
            updateForm({
              cookie: data.cookie,
              steamID: data.steamID,
              buffAppVersion: data['app-version'],
              buffAppVersionCode: data['app-version-code'],
              buffChannel: data.channel,
              buffUserAgent: data['user-agent'],
              buffDeviceId: data['device-id'],
              buffDeviceIdWeak: data['device-id-weak'],
              buffDevicename: data.devicename,
              buffBrand: data.brand,
              buffManufacturer: data.manufacturer,
              buffModel: data.model,
              buffProduct: data.product,
              buffBuildFingerprint: data['build-fingerprint'],
              buffSeed: data.seed,
              buffSystemType: data['system-type'],
              buffSystemVersion: data['system-version'],
              buffRom: data.rom,
              buffRomId: data['rom-id'],
              buffResolution: data.resolution,
              buffScreenDensity: data['screen-density'],
              buffScreenSize: data['screen-size'],
              buffNetwork: data.network,
              buffTimestamp: data.timestamp,
              buffTimezone: data.timezone,
              buffTimezoneOffset: data['timezone-offset'],
              buffTimezoneOffsetDst: data['timezone-offset-dst'],
              buffLocale: data.locale,
              buffLocaleSupported: data['locale-supported']
            })
            
            ElMessage.success('BUFF Token 获取成功!')
            buffTokenStatus.value = 'success'
            buffTokenLoading.value = false

            if (tokenCheckTimer.value) {
              clearInterval(tokenCheckTimer.value)
              tokenCheckTimer.value = null
            }

            stopBuffTokenCollection()

            // 发射令牌获取成功事件，触发自动保存
            emit('token-success')
          }
        } catch (error) {
          console.error('获取令牌数据失败:', error)
        }
      }, 3000)
    }

    // 停止令牌收集
    const stopBuffTokenCollection = async () => {
      try {
        await axios.post(apiUrls.getAppTokenStopBuff())
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
      buffTokenLoading,
      buffTokenStatus,
      basicCollapse,
      appCollapse,
      deviceCollapse,
      systemCollapse,
      displayCollapse,
      localeCollapse,
      startBuffTokenCollection
    }
  }
