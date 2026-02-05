import { ref, watch } from 'vue'

// 采集状态持久化 key
const STORAGE_KEY = 'cs_weapon_manager_collecting_sources'

// 从 localStorage 加载采集状态
function loadCollectingState() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      const data = JSON.parse(stored)
      return new Set(data)
    }
  } catch (error) {
    console.error('加载采集状态失败:', error)
  }
  return new Set()
}

// 保存采集状态到 localStorage
function saveCollectingState(collectingIds) {
  try {
    const data = Array.from(collectingIds)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
  } catch (error) {
    console.error('保存采集状态失败:', error)
  }
}

// 🔧 页面加载时清除所有采集状态
function clearCollectingStateOnLoad() {
  try {
    // console.log('🧹 页面刷新，清除所有采集状态')
    localStorage.removeItem(STORAGE_KEY)
  } catch (error) {
    console.error('清除采集状态失败:', error)
  }
}

// 全局共享的采集状态
let globalCollectingSourceIds = null

// 🔧 页面加载时立即清除采集状态
clearCollectingStateOnLoad()

/**
 * 采集状态管理 Composable
 * 使用 localStorage 持久化采集状态，确保页面切换后状态保持
 */
export function useCollectionState() {
  // 使用全局单例，确保所有组件共享同一个状态
  if (!globalCollectingSourceIds) {
    globalCollectingSourceIds = ref(loadCollectingState())
    
    // 监听状态变化，自动保存到 localStorage
    watch(
      globalCollectingSourceIds,
      (newValue) => {
        saveCollectingState(newValue)
      },
      { deep: true }
    )
  }

  const collectingSourceIds = globalCollectingSourceIds

  /**
   * 开始采集
   * @param {string|number} sourceId - 数据源ID
   */
  const startCollecting = (sourceId) => {
    if (sourceId !== null && sourceId !== undefined) {
      collectingSourceIds.value.add(sourceId)
      // 手动触发保存（Set 的 add 方法不会触发 deep watch）
      saveCollectingState(collectingSourceIds.value)
    }
  }

  /**
   * 停止采集
   * @param {string|number} sourceId - 数据源ID
   */
  const stopCollecting = (sourceId) => {
    if (sourceId !== null && sourceId !== undefined) {
      collectingSourceIds.value.delete(sourceId)
      // 手动触发保存（Set 的 delete 方法不会触发 deep watch）
      saveCollectingState(collectingSourceIds.value)
    }
  }

  /**
   * 检查是否正在采集
   * @param {string|number} sourceId - 数据源ID
   * @returns {boolean}
   */
  const isCollecting = (sourceId) => {
    return collectingSourceIds.value.has(sourceId)
  }

  /**
   * 清空所有采集状态（仅在需要时使用）
   */
  const clearAllCollecting = () => {
    collectingSourceIds.value.clear()
    saveCollectingState(collectingSourceIds.value)
  }

  return {
    collectingSourceIds,
    startCollecting,
    stopCollecting,
    isCollecting,
    clearAllCollecting
  }
}

