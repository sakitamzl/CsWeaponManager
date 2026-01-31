import { ref, computed } from 'vue'

export function useOnSaleYYYPIndex() {
  // 交易类型
  const selectedTradeType = ref('sale') // 默认选择"出售"
  const tradeTypes = ref([
    { value: 'sale', label: '出售', icon: '💰' },
    { value: 'lease', label: '租赁', icon: '🔄' },
    { value: 'sublease', label: '转租', icon: '🔁' },
    { value: 'presale', label: '预售', icon: '⏰' },
    { value: 'transfer', label: '过户', icon: '📝' },
    { value: 'rented-out', label: '已租出', icon: '📦' },
    { value: 'instant', label: '秒到账', icon: '⚡' }
  ])

  // 组件映射
  const componentMap = {
    'sale': 'OnSaleSale',
    'lease': 'OnSaleLease',
    'sublease': 'OnSaleSublease',
    'presale': 'OnSalePresale',
    'transfer': 'OnSaleTransfer',
    'rented-out': 'OnSaleRentedOut',
    'instant': 'OnSaleInstant'
  }

  // 当前组件
  const currentComponent = computed(() => {
    return componentMap[selectedTradeType.value] || 'OnSaleSale'
  })

  // 处理交易类型切换
  const handleTradeTypeChange = (tradeType) => {
    console.log('切换交易类型:', tradeType, '对应组件:', componentMap[tradeType])
    selectedTradeType.value = tradeType
    console.log('当前组件:', currentComponent.value)
  }

  return {
    selectedTradeType,
    tradeTypes,
    currentComponent,
    handleTradeTypeChange
  }
}
