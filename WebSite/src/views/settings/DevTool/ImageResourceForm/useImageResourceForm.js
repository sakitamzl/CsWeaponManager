import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { apiUrls } from '@/config/api.js'

export default function useImageResourceForm() {
  const isDownloadingIcons = ref(false)
  const iconDownloadResult = ref(null)

  const downloadWeaponIcons = async () => {
    if (isDownloadingIcons.value) {
      return
    }

    isDownloadingIcons.value = true
    iconDownloadResult.value = null

    try {
      const response = await axios.post(apiUrls.downloadWeaponIcons(), {
        limit: 200,
        skipExisting: true
      })

      if (response.data.success) {
        iconDownloadResult.value = response.data.data
        const downloaded = response.data.data?.downloaded || 0
        const total = response.data.data?.total || 0
        ElMessage.success(`已完成 ${downloaded}/${total} 张图片下载`)
      } else {
        ElMessage.error(response.data.message || '下载失败')
      }
    } catch (error) {
      console.error('下载武器图标失败:', error)
      let errorMessage = '下载失败'
      if (error.response) {
        errorMessage = error.response.data?.message || `下载失败 (${error.response.status})`
      } else if (error.request) {
        errorMessage = '无法连接到爬虫服务器，请检查服务是否运行'
      } else {
        errorMessage = error.message || errorMessage
      }
      ElMessage.error(errorMessage)
    } finally {
      isDownloadingIcons.value = false
    }
  }

  return {
    isDownloadingIcons,
    iconDownloadResult,
    downloadWeaponIcons
  }
}
