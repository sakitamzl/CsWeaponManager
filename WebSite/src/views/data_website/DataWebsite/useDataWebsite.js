import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

export function useDataWebsite() {
  const router = useRouter()
  const sidebarCollapsed = ref(false)
  const isMainSidebarCollapsed = ref(false)

  const navigateTo = (path) => {
    router.push(path)
  }

  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  // 点击内容区域时收缩侧边栏
  const handleContentClick = () => {
    if (!sidebarCollapsed.value) {
      sidebarCollapsed.value = true
    }
  }

  // 监听主侧边栏的状态变化
  const checkMainSidebarState = () => {
    const mainSidebar = document.querySelector('.sidebar')
    if (mainSidebar) {
      isMainSidebarCollapsed.value = mainSidebar.classList.contains('collapsed')
    }
  }

  // 使用 MutationObserver 监听主侧边栏的 class 变化
  let observer = null

  onMounted(() => {
    checkMainSidebarState()

    const mainSidebar = document.querySelector('.sidebar')
    if (mainSidebar) {
      observer = new MutationObserver(() => {
        checkMainSidebarState()
      })

      observer.observe(mainSidebar, {
        attributes: true,
        attributeFilter: ['class']
      })
    }
  })

  onUnmounted(() => {
    if (observer) {
      observer.disconnect()
    }
  })

  return {
    sidebarCollapsed,
    isMainSidebarCollapsed,
    navigateTo,
    toggleSidebar,
    handleContentClick
  }
}
