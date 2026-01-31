/**
 * 在售商品通用逻辑 - Composable
 * 提供所有交易类型共享的状态和方法
 */
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { apiUrls } from '@/config/api.js'

export function useOnSaleCommon() {
  // 基础状态
  const loading = ref(false)
  const updating = ref(false)
  const displayMode = ref('card') // 'card' | 'list'
  const searchText = ref('')
  const weaponTypeFilter = ref('')
  const floatRangeFilter = ref('')

  // 图片404缓存
  const image404Cache = ref(new Set())

  // 多选模式相关
  const isMultiSelectMode = ref(true) // 默认开启多选模式
  const selectedItems = ref([])

  // 预览相关
  const previewVisible = ref(false)
  const previewItem = ref(null)

  // 获取武器图片URL
  const getWeaponImage = (steamHashName) => {
    if (!steamHashName) {
      return null
    }
    if (image404Cache.value.has(steamHashName)) {
      return null
    }
    const imageName = steamHashName
      .replace(/\s*\|\s*/g, '___')
      .replace(/\s/g, '_')
      + '.png'

    return apiUrls.weaponImage(imageName)
  }

  // 处理图片加载错误
  const handleImageError = (e, steamHashName) => {
    if (steamHashName) {
      image404Cache.value.add(steamHashName)
    }
    e.target.onerror = null
    e.target.style.display = 'none'
  }

  // 获取卡片标题
  const getCardTitle = (item) => {
    if (!item) return ''
    return item.item_name || item.steam_hash_name || '未知物品'
  }

  // 获取物品标题
  const getItemTitle = (item) => {
    return getCardTitle(item)
  }

  // 检查是否有额外信息（贴纸、挂件、改名）
  const hasExtras = (item) => {
    return item.sticker || item.pendant || item.rename
  }

  // 解析贴纸数据
  const parseStickers = (stickerData) => {
    if (!stickerData) return []
    try {
      if (typeof stickerData === 'string') {
        return JSON.parse(stickerData)
      }
      return Array.isArray(stickerData) ? stickerData : []
    } catch (e) {
      return []
    }
  }

  // 解析挂件数据
  const parsePendant = (pendantData) => {
    if (!pendantData) return null
    try {
      if (typeof pendantData === 'string') {
        return JSON.parse(pendantData)
      }
      return pendantData
    } catch (e) {
      return null
    }
  }

  // 获取平台标签
  const getPlatformLabel = (platform) => {
    const labels = {
      'yyyp': '悠悠有品',
      'buff': 'BUFF',
      'csfloat': 'CSFloat'
    }
    return labels[platform] || platform
  }

  // 获取平台标签类型
  const getPlatformTagType = (platform) => {
    const types = {
      'yyyp': 'success',
      'buff': 'warning',
      'csfloat': 'info'
    }
    return types[platform] || 'default'
  }

  // 获取价格差异样式类
  const getPriceDiffClass = (salePrice, buyPrice) => {
    const diff = parseFloat(salePrice) - parseFloat(buyPrice)
    return diff >= 0 ? 'price-profit' : 'price-loss'
  }

  // 格式化在售时间
  const formatOnSaleTime = (onSaleTime) => {
    if (!onSaleTime) return ''
    return onSaleTime
  }

  // 多选模式切换
  const toggleMultiSelectMode = () => {
    isMultiSelectMode.value = !isMultiSelectMode.value
    if (!isMultiSelectMode.value) {
      selectedItems.value = []
    }
  }

  // 检查物品是否被选中
  const isItemSelected = (itemId) => {
    return selectedItems.value.some(item => item.id === itemId)
  }

  // 处理卡片点击（多选模式）
  const handleCardClick = (item) => {
    if (isMultiSelectMode.value) {
      const index = selectedItems.value.findIndex(i => i.id === item.id)
      if (index > -1) {
        selectedItems.value.splice(index, 1)
      } else {
        selectedItems.value.push(item)
      }
    } else {
      openPreview(item)
    }
  }

  // 打开预览
  const openPreview = (item) => {
    previewItem.value = item
    previewVisible.value = true
  }

  // 重置筛选
  const handleReset = () => {
    searchText.value = ''
    weaponTypeFilter.value = ''
    floatRangeFilter.value = ''
  }

  return {
    // 状态
    loading,
    updating,
    displayMode,
    searchText,
    weaponTypeFilter,
    floatRangeFilter,
    image404Cache,
    isMultiSelectMode,
    selectedItems,
    previewVisible,
    previewItem,

    // 方法
    getWeaponImage,
    handleImageError,
    getCardTitle,
    getItemTitle,
    hasExtras,
    parseStickers,
    parsePendant,
    getPlatformLabel,
    getPlatformTagType,
    getPriceDiffClass,
    formatOnSaleTime,
    toggleMultiSelectMode,
    isItemSelected,
    handleCardClick,
    openPreview,
    handleReset
  }
}
