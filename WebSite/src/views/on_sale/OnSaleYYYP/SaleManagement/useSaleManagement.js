import { apiUrls } from '@/config/api.js'

export default {
  name: 'SaleManagement',
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
    selectedTradeType: {
      type: String,
      default: 'sale'
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

    const formatOnSaleTime = (time) => {
      if (!time) return ''

      if (typeof time === 'string' && (time.includes('在售') || time.includes('天') || time.includes('小时'))) {
        return time
      }

      const date = new Date(time)

      if (isNaN(date.getTime())) {
        return ''
      }

      const now = new Date()
      const diff = now - date
      const days = Math.floor(diff / (1000 * 60 * 60 * 24))

      if (days === 0) return '今天上架'
      if (days === 1) return '昨天上架'
      if (days < 7) return `${days}天前`
      return date.toLocaleDateString('zh-CN')
    }

    const getPriceDiffClass = (salePrice, buyPrice) => {
      if (!salePrice || !buyPrice) return ''
      const diff = parseFloat(salePrice) - parseFloat(buyPrice)
      if (diff === 0) return 'price-equal'
      return diff > 0 ? 'price-profit' : 'price-loss'
    }

    // 获取售价的颜色类：比购入大显示红色（赔钱），小显示绿色（赚钱），相等白色
    const getSalePriceClass = (salePrice, buyPrice) => {
      if (!salePrice || !buyPrice) return ''
      const sale = parseFloat(salePrice)
      const buy = parseFloat(buyPrice)
      if (sale === buy) return 'price-equal'
      return sale > buy ? 'price-profit' : 'price-loss'  // 售价高=赔钱=红色(profit类), 售价低=赚钱=绿色(loss类)
    }

    // 获取市价的颜色类：售价比市价高显示红色，低显示绿色
    const getMarketPriceClass = (salePrice, referencePrice) => {
      if (!salePrice || !referencePrice) return ''
      const sale = parseFloat(salePrice)
      // 从市价字符串中提取数字（格式如 "¥239"）
      const match = String(referencePrice).match(/[\d.]+/)
      if (!match) return ''
      const market = parseFloat(match[0])
      if (sale === market) return 'price-equal'
      return sale > market ? 'price-profit' : 'price-loss'  // 售价>市价=红色(profit类), 售价<市价=绿色(loss类)
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
      formatOnSaleTime,
      getPriceDiffClass,
      getSalePriceClass,
      getMarketPriceClass,
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
