import { ref, watch, computed } from 'vue'

export function usePlatformSelectDialog(props, { emit }) {
  const visible = ref(props.modelValue)
  const selectedPlatform = ref('yyyp') // 默认选中悠悠有品

  // 计算属性
  const isRentMode = computed(() => props.mode === 'rent')
  const dialogTitle = computed(() => isRentMode.value ? '选择出租平台' : '选择出售平台')
  const tipText = computed(() => isRentMode.value ? '请选择要将饰品出租的平台' : '请选择要将饰品出售的平台')

  watch(() => props.modelValue, (newVal) => {
    visible.value = newVal
    if (newVal) {
      // 每次打开时重置为悠悠有品
      selectedPlatform.value = 'yyyp'
    }
  })

  watch(visible, (newVal) => {
    emit('update:modelValue', newVal)
  })

  const handleCancel = () => {
    visible.value = false
    emit('cancel')
  }

  const handleConfirm = () => {
    if (selectedPlatform.value) {
      visible.value = false
      emit('select', selectedPlatform.value)
    }
  }

  const handleClosed = () => {
    selectedPlatform.value = 'yyyp'
  }

  const handleCardClick = (platform) => {
    selectedPlatform.value = platform
    // 直接触发确认
    handleConfirm()
  }

  return {
    visible,
    selectedPlatform,
    isRentMode,
    dialogTitle,
    tipText,
    handleCancel,
    handleConfirm,
    handleClosed,
    handleCardClick
  }
}
