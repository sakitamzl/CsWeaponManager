import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

export function useSteamDT() {
  // 状态
  const steamdtIframe = ref(null)
  const iframeLoading = ref(true)
  const dataLoading = ref(false)

  // 拦截到的数据
  const marketIndexData = ref(null)
  const categoryData = ref([])  // 品类数据
  const lastUpdate = ref(null)

  /**
   * 刷新 iframe
   */
  const refreshIframe = () => {
    if (steamdtIframe.value) {
      iframeLoading.value = true
      // 重新加载 iframe
      steamdtIframe.value.src = steamdtIframe.value.src
      console.log('[SteamDT] 刷新 iframe')
    }
  }

  /**
   * iframe 加载完成回调
   */
  const onIframeLoad = () => {
    iframeLoading.value = false
    console.log('[SteamDT] iframe 加载完成')
  }

  /**
   * 使用无头浏览器获取市场指数数据
   */
  const fetchMarketIndexData = async () => {
    dataLoading.value = true
    console.log('[SteamDT] 开始使用无头浏览器获取市场指数...')

    try {
      const response = await fetch('/spider/steamdtSpiderV1/getMarketIndexHeadless?timeout=30000')
      const result = await response.json()

      if (result.success && result.data) {
        // 解构数据
        marketIndexData.value = result.data.market_index
        categoryData.value = result.data.category_data || []
        lastUpdate.value = new Date()

        console.log('[SteamDT] 市场指数获取成功:', result.data.market_index)
        console.log('[SteamDT] 品类数据获取成功,品类数量:', categoryData.value.length)
        ElMessage.success('市场指数数据已更新')
      } else {
        console.error('[SteamDT] 获取失败:', result.message)
        ElMessage.error('获取市场指数失败: ' + result.message)
      }
    } catch (error) {
      console.error('[SteamDT] 请求失败:', error)
      ElMessage.error('网络请求失败')
    } finally {
      dataLoading.value = false
    }
  }


  // 组件挂载时
  onMounted(() => {
    // 自动获取数据
    fetchMarketIndexData()
  })

  return {
    // 状态
    steamdtIframe,
    iframeLoading,
    dataLoading,
    marketIndexData,
    categoryData,
    lastUpdate,

    // 方法
    refreshIframe,
    onIframeLoad,
    fetchMarketIndexData
  }
}
