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
import { InfoFilled, Check, Box } from '@element-plus/icons-vue'
import { usePlatformSelectDialog } from './usePlatformSelectDialog.js'

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
  setup(props, context) {
    return usePlatformSelectDialog(props, context)
  }
}
</script>

<style scoped src="./styles.css"></style>
