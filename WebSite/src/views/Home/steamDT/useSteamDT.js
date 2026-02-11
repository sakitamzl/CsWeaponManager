import { ref, onUnmounted } from 'vue'

export function useSteamDT() {
  // 状态
  const steamdtIframe = ref(null)
  const iframeLoading = ref(true)

  /**
   * 刷新 iframe
   */
  const refreshIframe = () => {
    if (steamdtIframe.value) {
      iframeLoading.value = true
      // 重新加载 iframe
      steamdtIframe.value.src = steamdtIframe.value.src
      console.log('刷新 SteamDT iframe')
    }
  }

  /**
   * iframe 加载完成回调
   */
  const onIframeLoad = () => {
    iframeLoading.value = false
    console.log('SteamDT iframe 加载完成')

    // 尝试监听 iframe 内的消息（如果 SteamDT 支持 postMessage）
    try {
      const iframeWindow = steamdtIframe.value?.contentWindow
      if (iframeWindow) {
        // 监听来自 iframe 的 postMessage
        window.addEventListener('message', handleIframeMessage)
      }
    } catch (error) {
      console.warn('无法访问 iframe 内容（跨域限制）:', error)
    }
  }

  /**
   * 处理来自 iframe 的消息
   * 注意：需要 SteamDT 页面支持 postMessage
   */
  const handleIframeMessage = (event) => {
    // 验证来源
    if (event.origin !== 'https://steamdt.com') {
      return
    }

    console.log('收到来自 SteamDT 的消息:', event.data)
  }

  // 组件卸载时清理事件监听
  onUnmounted(() => {
    window.removeEventListener('message', handleIframeMessage)
  })

  return {
    // 状态
    steamdtIframe,
    iframeLoading,

    // 方法
    refreshIframe,
    onIframeLoad
  }
}
