import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { apiUrls } from '@/config/api.js'

export default function useWeaponMappingForm() {
  const selectedSteamIdYoupin = ref('')
  const selectedSteamIdBuff = ref('')
  const steamIdList = ref([])
  const isSyncing = ref(false)
  const isSyncingBuff = ref(false)
  const lastSyncTime = ref('')
  
  // Steam Hash Names 相关状态
  const isCollectingHashNames = ref(false)
  const lastCollectTime = ref('')
  const collectProgress = ref(null)

  // CSQAQ 相关状态
  const isCrawlingCsqaq = ref(false)
  const csqaqStatus = ref({
    status: 'idle',
    message: '',
    total_goods: 0,
    duration: null
  })
  const lastCsqaqTime = ref('')
  
  // CSQAQ上传相关
  const csqaqUploadRef = ref(null)
  const isUploadingCsqaq = ref(false)
  const csqaqFileSelected = ref(false)
  const csqaqUploadResult = ref(null)

  // 加载Steam ID列表
  const loadSteamIdList = async () => {
    try {
      const response = await axios.get(apiUrls.devToolsSteamAccounts())
      if (response.data.success && response.data.data.length > 0) {
        steamIdList.value = response.data.data
        console.log('已加载 Steam ID 列表:', steamIdList.value)
        // 默认选择第一个
        if (steamIdList.value.length > 0) {
          const firstItem = steamIdList.value[0]
          const defaultSteamId = firstItem.steamID || firstItem.steam_id || ''
          if (!selectedSteamIdYoupin.value) {
            selectedSteamIdYoupin.value = defaultSteamId
          }
          if (!selectedSteamIdBuff.value) {
            selectedSteamIdBuff.value = defaultSteamId
          }
        }
      }
    } catch (error) {
      console.error('加载Steam ID列表失败:', error)
      ElMessage.error('加载Steam ID列表失败')
    }
  }

  // 同步悠悠有品饰品映射
  const syncWeaponTemplates = async () => {
    if (!selectedSteamIdYoupin.value) {
      ElMessage.warning('请先选择 Steam ID')
      return
    }

    if (isSyncing.value) {
      return
    }

    try {
      await ElMessageBox.confirm(
        `确定要同步 Steam ID: ${selectedSteamIdYoupin.value} 的悠悠有品饰品映射吗？此操作可能需要一些时间。`,
        '确认同步',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
    } catch {
      return
    }

    isSyncing.value = true
    ElMessage.info('开始同步饰品映射...')
    
    try {
      console.log('开始同步悠悠有品饰品映射, Steam ID:', selectedSteamIdYoupin.value)

      const response = await axios.post(apiUrls.youpinSyncWeaponTemplates(), {
        steamId: selectedSteamIdYoupin.value
      })

      if (response.data.success) {
        ElMessage.success(`同步成功！${response.data.message}`)
        console.log('同步结果:', response.data)
        lastSyncTime.value = new Date().toLocaleString('zh-CN')
      } else {
        ElMessage.error(`同步失败: ${response.data.message}`)
      }
    } catch (error) {
      console.error('同步饰品映射失败:', error)
      let errorMessage = '同步失败'
      
      if (error.response) {
        errorMessage = error.response.data?.message || `同步失败 (${error.response.status})`
      } else if (error.request) {
        errorMessage = '无法连接到爬虫服务器，请检查服务是否运行'
      } else {
        errorMessage = error.message || '同步失败'
      }
      
      ElMessage.error(errorMessage)
    } finally {
      isSyncing.value = false
    }
  }

  // 同步BUFF饰品映射
  const syncBuffTemplates = async () => {
    if (!selectedSteamIdBuff.value) {
      ElMessage.warning('请先选择 Steam ID')
      return
    }

    if (isSyncingBuff.value) {
      return
    }

    try {
      await ElMessageBox.confirm(
        `确定要同步 Steam ID: ${selectedSteamIdBuff.value} 的BUFF饰品映射吗？此操作可能需要一些时间。`,
        '确认同步',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
    } catch {
      return
    }

    isSyncingBuff.value = true
    ElMessage.info('开始同步BUFF饰品映射...')

    try {
      console.log('开始同步BUFF饰品映射, Steam ID:', selectedSteamIdBuff.value)

      const response = await axios.post(apiUrls.buffSyncTemplates(), {
        steamId: selectedSteamIdBuff.value
      })

      if (response.data.success) {
        ElMessage.success(`同步成功！${response.data.message}`)
        console.log('同步结果:', response.data)
        lastSyncTime.value = new Date().toLocaleString('zh-CN')
      } else {
        ElMessage.error(`同步失败: ${response.data.message}`)
      }
    } catch (error) {
      console.error('同步BUFF饰品映射失败:', error)
      let errorMessage = '同步失败'

      if (error.response) {
        errorMessage = error.response.data?.message || `同步失败 (${error.response.status})`
      } else if (error.request) {
        errorMessage = '无法连接到爬虫服务器，请检查服务是否运行'
      } else {
        errorMessage = error.message || '同步失败'
      }

      ElMessage.error(errorMessage)
    } finally {
      isSyncingBuff.value = false
    }
  }

  // CSQAQ上传相关函数
  const handleCsqaqFileChange = (file, fileList) => {
    // 文件选择时触发
    if (fileList.length > 0) {
      const selectedFile = file.raw
      const isTxt = selectedFile.name.endsWith('.txt')
      const isLt50M = selectedFile.size / 1024 / 1024 < 50
      
      if (!isTxt) {
        ElMessage.error('只能上传.txt文件！')
        csqaqFileSelected.value = false
        // 清除文件
        if (csqaqUploadRef.value) {
          csqaqUploadRef.value.clearFiles()
        }
        return
      }
      
      if (!isLt50M) {
        ElMessage.error('文件大小不能超过50MB！')
        csqaqFileSelected.value = false
        // 清除文件
        if (csqaqUploadRef.value) {
          csqaqUploadRef.value.clearFiles()
        }
        return
      }
      
      csqaqFileSelected.value = true
      ElMessage.success('文件已选择，请点击"提交上传"按钮')
    } else {
      csqaqFileSelected.value = false
    }
  }

  const beforeCsqaqUpload = (file) => {
    const isTxt = file.name.endsWith('.txt')
    if (!isTxt) {
      ElMessage.error('只能上传.txt文件！')
      return false
    }
    
    const isLt50M = file.size / 1024 / 1024 < 50
    if (!isLt50M) {
      ElMessage.error('文件大小不能超过50MB！')
      return false
    }
    
    return true
  }

  const submitCsqaqUpload = () => {
    if (!csqaqUploadRef.value) {
      ElMessage.error('上传组件未初始化')
      return
    }
    
    isUploadingCsqaq.value = true
    csqaqUploadRef.value.submit()
  }

  const handleCsqaqUploadSuccess = (response, file) => {
    isUploadingCsqaq.value = false
    csqaqFileSelected.value = false
    
    if (response.success) {
      csqaqUploadResult.value = response
      ElMessage.success(response.message || '上传成功')
      
      // 清空文件列表
      if (csqaqUploadRef.value) {
        csqaqUploadRef.value.clearFiles()
      }
    } else {
      ElMessage.error(response.message || '上传失败')
    }
  }

  const handleCsqaqUploadError = (error, file) => {
    isUploadingCsqaq.value = false
    csqaqFileSelected.value = false
    
    console.error('上传失败:', error)
    
    let errorMessage = '上传失败'
    try {
      const response = JSON.parse(error.message)
      errorMessage = response.message || errorMessage
    } catch (e) {
      errorMessage = error.message || errorMessage
    }
    
    ElMessage.error(errorMessage)
  }

  // 组件挂载时加载Steam ID列表
  onMounted(() => {
    loadSteamIdList()
  })

  return {
    apiUrls,
    selectedSteamIdYoupin,
    selectedSteamIdBuff,
    steamIdList,
    isSyncing,
    isSyncingBuff,
    lastSyncTime,
    syncWeaponTemplates,
    syncBuffTemplates,
    isCollectingHashNames,
    lastCollectTime,
    collectProgress,
    isCrawlingCsqaq,
    csqaqStatus,
    lastCsqaqTime,
    csqaqUploadRef,
    isUploadingCsqaq,
    csqaqFileSelected,
    csqaqUploadResult,
    handleCsqaqFileChange,
    beforeCsqaqUpload,
    submitCsqaqUpload,
    handleCsqaqUploadSuccess,
    handleCsqaqUploadError
  }
}
