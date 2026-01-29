<template>
  <el-dialog
    v-model="visible"
    :title="dialogTitle"
    width="500px"
    :close-on-click-modal="false"
    class="platform-select-dialog"
    @closed="handleClosed"
  >
    <div class="platform-select-content">
      <div class="platform-list">
        <!-- 悠悠有品 -->
        <div
          class="platform-card clickable"
          @click="handleCardClick('yyyp')"
        >
          <div class="platform-icon yyyp-icon">
            <span>悠</span>
          </div>
          <div class="platform-info">
            <div class="platform-name">悠悠有品</div>
            <div class="platform-desc" v-if="isRentMode">支持短租、长租多种模式</div>
          </div>
        </div>

        <!-- BUFF (预留) -->
        <div
          class="platform-card disabled"
          :title="`BUFF ${isRentMode ? '出租' : '出售'}功能开发中...`"
        >
          <div class="platform-icon buff-icon">
            <span>B</span>
          </div>
          <div class="platform-info">
            <div class="platform-name">BUFF</div>
            <div class="platform-desc">开发中，敬请期待...</div>
          </div>
          <div class="platform-badge">
            <el-tag type="info" size="small">开发中</el-tag>
          </div>
        </div>
      </div>

      <div class="item-count-info">
        <el-icon><Box /></el-icon>
        <span>已选择 {{ itemCount }} 件饰品</span>
      </div>
    </div>
  </el-dialog>
</template>

<script>
import { ref, watch, computed } from 'vue'
import { InfoFilled, Check, Box } from '@element-plus/icons-vue'

export default {
  name: 'PlatformSelectDialog',
  components: {
    InfoFilled,
    Check,
    Box
  },
  props: {
    modelValue: {
      type: Boolean,
      default: false
    },
    itemCount: {
      type: Number,
      default: 0
    },
    mode: {
      type: String,
      default: 'rent', // 'rent' 或 'sell'
      validator: (value) => ['rent', 'sell'].includes(value)
    }
  },
  emits: ['update:modelValue', 'select', 'cancel'],
  setup(props, { emit }) {
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
}
</script>

<style scoped>
.platform-select-dialog :deep(.el-dialog__header) {
  background: var(--bg-tertiary, #2a2a2a);
  border-bottom: 1px solid var(--border-color, #3a3a3a);
  padding: 1.25rem 1.5rem;
}

.platform-select-dialog :deep(.el-dialog__title) {
  color: #fff;
  font-weight: 600;
  font-size: 1.1rem;
}

.platform-select-dialog :deep(.el-dialog__body) {
  background: var(--bg-secondary, #1a1a1a);
  padding: 1.5rem;
}

.platform-select-dialog :deep(.el-dialog__footer) {
  background: var(--bg-secondary, #1a1a1a);
  border-top: 1px solid var(--border-color, #3a3a3a);
  padding: 1rem 1.5rem;
}

.platform-select-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.platform-tip {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: rgba(64, 158, 255, 0.1);
  border-left: 3px solid #409EFF;
  border-radius: 4px;
  color: #409EFF;
  font-size: 0.9rem;
}

.tip-icon {
  font-size: 1.2rem;
}

.platform-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.platform-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background: var(--bg-tertiary, #2a2a2a);
  border: 2px solid var(--border-color, #3a3a3a);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.platform-card.clickable {
  cursor: pointer;
}

.platform-card.clickable:hover {
  background: #333;
  border-color: #4a4a4a;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.platform-card.clickable:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

.platform-card.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.platform-icon {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: bold;
  color: #fff;
  flex-shrink: 0;
}

.platform-icon.yyyp-icon {
  background: linear-gradient(135deg, #67C23A, #85CE61);
}

.platform-icon.buff-icon {
  background: linear-gradient(135deg, #FFA500, #FFB733);
}

.platform-info {
  flex: 1;
}

.platform-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: #fff;
  margin-bottom: 0.25rem;
}

.platform-desc {
  font-size: 0.85rem;
  color: #999;
}

.platform-badge {
  position: absolute;
  top: 1rem;
  right: 1rem;
}

.item-count-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 6px;
  color: #ccc;
  font-size: 0.9rem;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .platform-card {
    padding: 1rem;
  }

  .platform-icon {
    width: 40px;
    height: 40px;
    font-size: 1.2rem;
  }

  .platform-name {
    font-size: 1rem;
  }

  .platform-desc {
    font-size: 0.8rem;
  }
}
</style>
