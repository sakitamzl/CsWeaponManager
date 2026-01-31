import { apiUrls } from '@/config/api.js'

export default {
  name: 'PresaleManagement',
  props: {
    loading: {
      type: Boolean,
      default: false
    },
    displayData: {
      type: Array,
      default: () => []
    },
    displayMode: {
      type: String,
      default: 'card'
    },
    isMultiSelectMode: {
      type: Boolean,
      default: false
    },
    selectedItems: {
      type: Array,
      default: () => []
    }
  },
  emits: [
    'update-price',
    'remove-from-sale',
    'batch-change-price',
    'batch-remove-from-sale',
    'card-click',
    'preview',
    'clear-selection'
  ],
  setup(props, { emit }) {
    // 工具函数
    const getWeaponImage = (steamHashName) => {
      if (!steamHashName) {
        return null
      }
      const imageName = steamHashName
        .replace(/\s*\|\s*/g, '___')
        .replace(/\s/g, '_')
        + '.png'
      return apiUrls.weaponImage(imageName)
    }

    const handleImageError = (e, steamHashName) => {
      e.target.onerror = null
      e.target.style.display = 'none'
    }

    const getCardTitle = (item) => {
      if (!item) return ''
      return item.item_name || item.steam_hash_name || '未知物品'
    }

    const getItemTitle = (item) => {
      return getCardTitle(item)
    }

    const hasExtras = (item) => {
      return item.sticker || item.pendant || item.rename
    }

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

    const getPlatformLabel = (platform) => {
      const labels = {
        'yyyp': '悠悠有品',
        'buff': 'BUFF',
        'csfloat': 'CSFloat'
      }
      return labels[platform] || platform
    }

    const getPlatformTagType = (platform) => {
      const types = {
        'yyyp': 'success',
        'buff': 'warning',
        'csfloat': 'info'
      }
      return types[platform] || 'default'
    }

    // 多选相关
    const isItemSelected = (itemId) => {
      return props.selectedItems.some(item => item.id === itemId)
    }

    // 事件处理
    const handleCardClick = (item) => {
      emit('card-click', item)
    }

    const handleUpdatePrice = (item) => {
      emit('update-price', item)
    }

    const handleRemoveFromSale = (item) => {
      emit('remove-from-sale', item)
    }

    const handleBatchChangePrice = () => {
      emit('batch-change-price')
    }

    const handleBatchRemoveFromSale = () => {
      emit('batch-remove-from-sale')
    }

    const handleClearSelection = () => {
      emit('clear-selection')
    }

    const openPreview = (item) => {
      emit('preview', item)
    }

    return {
      getWeaponImage,
      handleImageError,
      getCardTitle,
      getItemTitle,
      hasExtras,
      parseStickers,
      parsePendant,
      getPlatformLabel,
      getPlatformTagType,
      isItemSelected,
      handleCardClick,
      handleUpdatePrice,
      handleRemoveFromSale,
      handleBatchChangePrice,
      handleBatchRemoveFromSale,
      handleClearSelection,
      openPreview
    }
  }
}
