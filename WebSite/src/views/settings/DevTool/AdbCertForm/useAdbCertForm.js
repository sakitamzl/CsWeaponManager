import { ref } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { apiUrls } from '@/config/api.js'

export default function useAdbCertForm() {
  const devices = ref([])
  const selectedDevice = ref('')
  const deviceInfo = ref(null)
  const certStatus = ref(null)
  const isLoadingDevices = ref(false)
  const isConnectingManual = ref(false)
  const isCheckingCert = ref(false)
  const isInstallingCert = ref(false)
  const isUninstallingCert = ref(false)
  const adbMessage = ref('')
  const adbMessageType = ref('info')

  // 手动连接设备
  const connectManualDevice = async () => {
    try {
      const { value: address } = await ElMessageBox.prompt(
        '请输入设备地址（格式: IP:端口）',
        '手动连接设备',
        {
          confirmButtonText: '连接',
          cancelButtonText: '取消',
          inputPattern: /^[\d.]+:\d+$/,
          inputErrorMessage: '格式错误，请输入如: 192.168.123.50:5555',
          inputPlaceholder: '192.168.123.50:5555'
        }
      )
      
      isConnectingManual.value = true
      ElMessage.info(`正在连接到 ${address}...`)
      
      // 连接设备
      await axios.post(apiUrls.adbConnect(), { address })
      
      // 等待连接完成
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // 刷新设备列表
      const response = await axios.get(apiUrls.adbDevices())
      if (response.data.success && response.data.data.length > 0) {
        devices.value = response.data.data
        selectedDevice.value = devices.value[0].serial
        deviceInfo.value = devices.value[0]
        
        ElMessage.success('设备连接成功！')
        
        // 自动检测证书
        await checkCertStatus(true)
      }
    } catch (error) {
      if (error !== 'cancel') {
        console.error('手动连接失败:', error)
        ElMessage.error('连接失败，请检查设备地址和网络')
      }
    } finally {
      isConnectingManual.value = false
    }
  }
  
  // 扫描并加载设备
  const scanAndLoadDevices = async () => {
    isLoadingDevices.value = true
    adbMessage.value = ''
    
    try {
      // 1. 先扫描局域网设备
      adbMessage.value = '正在扫描局域网设备...'
      adbMessageType.value = 'info'
      
      const scanResponse = await axios.post(apiUrls.adbScan(), {
        timeout: 0.5,
        max_workers: 50
      })
      
      if (scanResponse.data.success && scanResponse.data.data.length > 0) {
        const discovered = scanResponse.data.data
        ElMessage.success(`发现 ${discovered.length} 个设备，正在连接...`)
        
        // 2. 连接发现的设备
        for (const address of discovered.slice(0, 3)) {  // 最多连接3个
          try {
            await axios.post(apiUrls.adbConnect(), { address })
          } catch (e) {
            console.warn(`连接设备 ${address} 失败:`, e)
          }
        }
        
        // 等待连接完成
        await new Promise(resolve => setTimeout(resolve, 1000))
      }
      
      // 3. 获取设备列表
      const response = await axios.get(apiUrls.adbDevices())
      
      if (response.data.success) {
        devices.value = response.data.data
        
        if (devices.value.length > 0) {
          // 默认选择第一个设备
          if (!selectedDevice.value) {
            selectedDevice.value = devices.value[0].serial
            deviceInfo.value = devices.value[0]
          } else {
            // 更新已选设备的信息
            const selected = devices.value.find(d => d.serial === selectedDevice.value)
            if (selected) {
              deviceInfo.value = selected
            }
          }
          
          adbMessage.value = `找到 ${devices.value.length} 个设备`
          adbMessageType.value = 'success'
          ElMessage.success(response.data.message)
          
          // 自动检测证书状态
          await checkCertStatus()
        } else {
          adbMessage.value = '未找到任何设备。请确保：\n1. 设备已开启ADB调试\n2. MuMu模拟器已启动'
          adbMessageType.value = 'warning'
          ElMessage.warning('未找到任何设备')
        }
      } else {
        adbMessage.value = `获取设备失败: ${response.data.message}`
        adbMessageType.value = 'error'
        ElMessage.error(response.data.message)
      }
    } catch (error) {
      console.error('扫描设备失败:', error)
      adbMessage.value = '扫描设备失败，请确保后端服务正在运行'
      adbMessageType.value = 'error'
      
      let errorMessage = '扫描设备失败'
      if (error.response) {
        errorMessage = error.response.data?.message || errorMessage
      } else if (error.request) {
        errorMessage = '无法连接到后端服务器'
      }
      ElMessage.error(errorMessage)
    } finally {
      isLoadingDevices.value = false
    }
  }

  // 检查证书状态（静默模式，不显示成功消息）
  const checkCertStatus = async (silent = false) => {
    if (!selectedDevice.value) {
      if (!silent) {
        ElMessage.warning('请先选择设备')
      }
      return
    }

    isCheckingCert.value = true
    if (!silent) {
      adbMessage.value = ''
    }

    try {
      const response = await axios.post(apiUrls.adbCertStatus(), {
        serial: selectedDevice.value
      })

      if (response.data.success) {
        certStatus.value = response.data.data
        if (!silent) {
          adbMessage.value = response.data.message
          adbMessageType.value = certStatus.value.installed ? 'success' : 'warning'
          ElMessage.success(response.data.message)
        }
      } else {
        if (!silent) {
          adbMessage.value = `检查失败: ${response.data.message}`
          adbMessageType.value = 'error'
          ElMessage.error(response.data.message)
        }
      }
    } catch (error) {
      console.error('检查证书状态失败:', error)
      if (!silent) {
        adbMessage.value = '检查证书状态失败'
        adbMessageType.value = 'error'
        
        let errorMessage = '检查证书状态失败'
        if (error.response) {
          errorMessage = error.response.data?.message || errorMessage
        }
        ElMessage.error(errorMessage)
      }
    } finally {
      isCheckingCert.value = false
    }
  }

  // 安装证书（强制重新安装）
  const installCert = async () => {
    if (!selectedDevice.value) {
      ElMessage.warning('请先选择设备')
      return
    }

    // 检查设备是否有root权限
    if (deviceInfo.value && !deviceInfo.value.is_root) {
      ElMessage.error('设备没有root权限，无法安装系统证书')
      return
    }

    try {
      const message = certStatus.value?.installed 
        ? '证书已安装，确定要重新安装Charles证书吗？此操作将覆盖现有证书。'
        : '确定要安装Charles证书到设备吗？此操作需要root权限。'
      
      await ElMessageBox.confirm(message, '确认安装', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
    } catch {
      return
    }

    isInstallingCert.value = true
    adbMessage.value = ''
    ElMessage.info('开始安装证书...')

    try {
      const response = await axios.post(apiUrls.adbCertInstall(), {
        serial: selectedDevice.value,
        force: true  // 强制重新安装
      })

      if (response.data.success) {
        adbMessage.value = '证书安装成功！请重启模拟器/设备以使证书生效'
        adbMessageType.value = 'success'
        ElMessage.success(response.data.message)
        
        // 显示重启提示
        ElMessageBox.alert(
          '证书已成功安装到设备！\n\n请手动重启模拟器或设备，以确保证书完全生效。',
          '安装成功 - 需要重启',
          {
            confirmButtonText: '知道了',
            type: 'success'
          }
        )
        
        // 刷新证书状态
        setTimeout(() => {
          checkCertStatus(true)  // 静默检查
        }, 1000)
      } else {
        adbMessage.value = `安装失败: ${response.data.message}`
        adbMessageType.value = 'error'
        ElMessage.error(response.data.message)
      }
    } catch (error) {
      console.error('安装证书失败:', error)
      adbMessage.value = '安装证书失败'
      adbMessageType.value = 'error'
      
      let errorMessage = '安装证书失败'
      if (error.response) {
        errorMessage = error.response.data?.message || errorMessage
      }
      ElMessage.error(errorMessage)
    } finally {
      isInstallingCert.value = false
    }
  }

  // 卸载证书
  const uninstallCert = async () => {
    if (!selectedDevice.value) {
      ElMessage.warning('请先选择设备')
      return
    }

    try {
      await ElMessageBox.confirm(
        '确定要卸载Charles证书吗？',
        '确认卸载',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
    } catch {
      return
    }

    isUninstallingCert.value = true
    adbMessage.value = ''
    ElMessage.info('开始卸载证书...')

    try {
      const response = await axios.post(apiUrls.adbCertUninstall(), {
        serial: selectedDevice.value
      })

      if (response.data.success) {
        adbMessage.value = '证书卸载成功'
        adbMessageType.value = 'success'
        ElMessage.success(response.data.message)
        
        // 刷新证书状态
        setTimeout(() => {
          checkCertStatus(true)  // 静默检查
        }, 1000)
      } else {
        adbMessage.value = `卸载失败: ${response.data.message}`
        adbMessageType.value = 'error'
        ElMessage.error(response.data.message)
      }
    } catch (error) {
      console.error('卸载证书失败:', error)
      adbMessage.value = '卸载证书失败'
      adbMessageType.value = 'error'
      
      let errorMessage = '卸载证书失败'
      if (error.response) {
        errorMessage = error.response.data?.message || errorMessage
      }
      ElMessage.error(errorMessage)
    } finally {
      isUninstallingCert.value = false
    }
  }

  return {
    devices,
    selectedDevice,
    deviceInfo,
    certStatus,
    isLoadingDevices,
    isConnectingManual,
    isInstallingCert,
    isUninstallingCert,
    adbMessage,
    adbMessageType,
    scanAndLoadDevices,
    connectManualDevice,
    checkCertStatus,
    installCert,
    uninstallCert
  }
}
